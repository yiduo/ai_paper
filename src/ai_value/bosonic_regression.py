"""Finite-support passive-bosonic regression, not a proof or hardware model.

Channel reference: exact rational creation polynomials in an unnormalized
number basis. Candidate: an independent floating Hermitian generator.
NumPy is optional and imported only when spectral/channel evaluation runs.
"""
from __future__ import annotations

from collections import defaultdict
from decimal import Decimal as D, Context, ROUND_FLOOR, ROUND_CEILING
from fractions import Fraction as Q
from functools import lru_cache
import itertools
import math
import time

from . import binary_information as intervals
from .binary_information import I, rat, maximum


@lru_cache(maxsize=64)
def basis(modes: int, total: int) -> tuple[tuple[int, ...], ...]:
    if modes < 1 or total < 0:
        raise ValueError('Invalid finite support')
    return tuple(sorted((x for x in itertools.product(range(total+1), repeat=modes)
                         if sum(x) <= total), key=lambda x: (sum(x), x)))


def weight(k: tuple[int, ...]) -> int:
    return math.prod(math.factorial(j) for j in k)


def parse_components(spec: list[dict], n: int):
    result = []
    for item in spec:
        w = Q(item['weight'])
        v = {tuple(map(int, k.split(','))): Q(c)
             for k, c in item['unnormalized_creation_coefficients'].items()}
        if w < 0 or not v or any(len(k) != n or min(k) < 0 or sum(k) > 2 for k in v):
            raise ValueError('Ineligible finite input')
        norm = sum((c*c*weight(k) for k, c in v.items()), Q(0))
        if norm <= 0:
            raise ValueError('Zero pure vector')
        result.append((w, v, norm))
    if sum(x[0] for x in result) != 1:
        raise ValueError('Mixture weights must sum to one')
    return result


def zero_matrix(d):
    return [[Q(0) for _ in range(d)] for _ in range(d)]


def state_matrix(components, states):
    lookup = {k: i for i, k in enumerate(states)}
    out = zero_matrix(len(states))
    for w, v, norm in components:
        for a, x in v.items():
            for b, y in v.items():
                out[lookup[a]][lookup[b]] += w*x*y/norm
    check_trace(out, states)
    return out


def check_trace(q, states):
    if sum(q[i][i]*weight(k) for i, k in enumerate(states)) != 1:
        raise ArithmeticError('Exact density trace failure')
    if any(q[i][j] != q[j][i] for i in range(len(q)) for j in range(len(q))):
        raise ArithmeticError('Exact density symmetry failure')


def rotate_polynomial(a, b, t, s):
    """U a† U†=t*c†-s*d†; U b† U†=s*c†+t*d†."""
    if t*t+s*s != 1:
        raise ValueError('Rotation must have exact unit norm')
    n = len(a)
    polynomial = {((0,)*n, (0,)*n): Q(1)}
    for j, (ka, kb) in enumerate(zip(a, b)):
        local = defaultdict(Q)
        for u in range(ka+1):
            for v in range(kb+1):
                c = u+v
                d = ka+kb-c
                local[(c, d)] += (math.comb(ka, u)*math.comb(kb, v)
                                  *t**u*(-s)**(ka-u)*s**v*t**(kb-v))
        new = defaultdict(Q)
        for (cs, ds), x in polynomial.items():
            for (c, d), y in local.items():
                cc, dd = list(cs), list(ds)
                cc[j], dd[j] = c, d
                new[(tuple(cc), tuple(dd))] += x*y
        polynomial = {k: v for k, v in new.items() if v}
    return polynomial


def exact_channel(A, B, n: int, t: Q, s: Q):
    states = basis(n, 4)
    lookup = {k: i for i, k in enumerate(states)}
    out = zero_matrix(len(states))
    joint_energy = Q(0)
    input_energy = Q(0)
    components_checked = 0
    for wa, a, na in A:
        for wb, b, nb in B:
            vector = defaultdict(Q)
            for ka, ca in a.items():
                for kb, cb in b.items():
                    for key, value in rotate_polynomial(ka, kb, t, s).items():
                        vector[key] += ca*cb*value
            norm = sum((v*v*weight(c)*weight(d) for (c, d), v in vector.items()), Q(0))
            if norm != na*nb:
                raise ArithmeticError('Exact rotation does not preserve vector norm')
            initial = (sum((v*v*weight(k)*sum(k) for k, v in a.items()), Q(0))/na
                       +sum((v*v*weight(k)*sum(k) for k, v in b.items()), Q(0))/nb)
            final = sum((v*v*weight(c)*weight(d)*(sum(c)+sum(d))
                         for (c, d), v in vector.items()), Q(0))/norm
            if initial != final:
                raise ArithmeticError('Exact number conservation failure')
            input_energy += wa*wb*initial
            joint_energy += wa*wb*final
            grouped = defaultdict(dict)
            for (c, d), v in vector.items():
                grouped[d][c] = v
            for d, cs in grouped.items():
                for c, x in cs.items():
                    for cc, y in cs.items():
                        out[lookup[c]][lookup[cc]] += wa*wb*x*y*weight(d)/norm
            components_checked += 1
    check_trace(out, states)
    return out, states, {'pure_products_norm_and_energy_checked': components_checked,
                         'input_total_energy': str(input_energy),
                         'output_joint_total_energy': str(joint_energy)}


def midpoint_matrix(q, states):
    """A binary matrix with an outward entry error bound to exact density."""
    import numpy as np
    d = len(states)
    bounds = []
    matrix = np.empty((d, d), dtype=float)
    worst = Q(0)
    for i in range(d):
        row = []
        for j in range(d):
            w = weight(states[i])*weight(states[j])
            root = math.isqrt(w)
            if root*root == w:
                sq = I(root)
            else:
                val = intervals.C.sqrt(D(w))
                sq = I(intervals.C.next_minus(val), intervals.C.next_plus(val))
            x = rat(q[i][j])*sq
            matrix[i, j] = float(intervals.C.divide(intervals.C.add(x.lo, x.hi), D(2)))
            represented = Q(float(matrix[i, j]))
            err = max(abs(represented-Q(x.lo)), abs(represented-Q(x.hi)))
            worst = max(worst, err)
            row.append(x)
        bounds.append(row)
    return matrix, worst


@lru_cache(maxsize=2048)
def spectral_seed(flat, d):
    """Certified spectral error to represented A; no trusted eigenvalue oracle."""
    import numpy as np
    A = np.array(flat).reshape(d, d)
    vals, V = np.linalg.eigh(A)
    ar = [[Q(float(A[i, j])) for j in range(d)] for i in range(d)]
    vr = [[Q(float(V[i, j])) for j in range(d)] for i in range(d)]
    ls = [Q(float(x)) for x in vals]
    E = [[sum((vr[k][i]*vr[k][j] for k in range(d)), Q(0))-(i == j)
          for j in range(d)] for i in range(d)]
    delta = max(sum(map(abs, row)) for row in E)
    if delta >= Q(1, 2):
        raise ArithmeticError('Eigenvector matrix not sufficiently orthogonal')
    R = [[sum((ar[i][k]*vr[k][j] for k in range(d)), Q(0))-vr[i][j]*ls[j]
          for j in range(d)] for i in range(d)]
    residual = max(max(sum(map(abs, row)) for row in R),
                   max(sum(abs(R[i][j]) for i in range(d)) for j in range(d)))
    M = max(sum(map(abs, row)) for row in ar)
    L = max(map(abs, ls))
    error = 2*residual+(M+3*L)*delta
    return tuple(ls), error, delta, residual


def entropy_point(x: D) -> I:
    if x == 0 or x == 1:
        return I(0)
    return -I(x)*I(x).ln()


def entropy_of_matrix(q, states):
    A, entry_error = midpoint_matrix(q, states)
    d = len(states)
    ls, base_error, delta, residual = spectral_seed(tuple(map(float, A.flat)), d)
    error = base_error+d*entry_error
    er = rat(error)
    total = I(0)
    peak = I(-1).exp()
    eigen_intervals = []
    for value in ls:
        center = rat(value)
        lo = max(D(0), intervals.DOWN.subtract(center.lo, er.hi))
        hi = min(D(1), intervals.UP.add(center.hi, er.hi))
        if lo > hi:
            raise ArithmeticError('Certified eigen interval misses physical spectrum')
        ends = [entropy_point(lo), entropy_point(hi)]
        upper = max(x.hi for x in ends)
        if lo <= peak.hi and hi >= peak.lo:
            upper = max(upper, peak.hi)
        total += I(max(D(0), min(x.lo for x in ends)), upper)
        eigen_intervals.append([str(lo), str(hi)])
    return total, {'eigenvalues': eigen_intervals, 'spectral_error_upper': str(er.hi),
                   'orthogonality_row_norm': str(rat(delta).hi),
                   'residual_norm_upper': str(rat(residual).hi),
                   'entry_conversion_error_upper': str(rat(entry_error).hi)}


def gpoint(x: D):
    if x == 0:
        return I(0)
    if x < 0:
        raise ValueError('Negative photon parameter')
    return (1+I(x))*(1+I(x)).ln()-I(x)*I(x).ln()


def g(x: I):
    if x.lo < 0:
        raise ValueError('Negative photon interval')
    return I(gpoint(x.lo).lo, gpoint(x.hi).hi)


def inverse_g_point(h: D):
    if h == 0:
        return I(0)
    lo, hi = D(0), D(64)
    if h < 0 or h >= gpoint(hi).lo:
        raise ArithmeticError('Inverse g outside frozen bracket')
    for _ in range(96):
        mid = intervals.C.divide(intervals.C.add(lo, hi), D(2))
        val = gpoint(mid)
        if val.hi < h:
            lo = mid
        elif val.lo > h:
            hi = mid
        else:
            break
    return I(lo, hi)


def inverse_g(h: I):
    return I(inverse_g_point(h.lo).lo, inverse_g_point(h.hi).hi)


def floors(sa: I, sb: I, n: int, eta: Q, old_sharp: bool):
    e = rat(eta)
    if eta == 0:
        return sb, sb, {'endpoint_identity': True}
    if eta == 1:
        return sa, sa, {'endpoint_identity': True}
    linear = e*sa+(1-e)*sb
    old_exp = n*(e*(sa/n).exp()+(1-e)*(sb/n).exp()).ln()
    new = n*g(e*inverse_g(sa/n)+(1-e)*inverse_g(sb/n))
    best = maximum(I(0), linear, old_exp, new if old_sharp else I(0))
    return new, best, {'linear': linear.data(), 'exponential_qEPI': old_exp.data(),
                       'old_sharp_applicable': old_sharp}


@lru_cache(maxsize=16)
def generator_unitary(n: int, t: Q, s: Q):
    import numpy as np
    states = basis(2*n, 4)
    lookup = {k: i for i, k in enumerate(states)}
    K = np.zeros((len(states), len(states)), dtype=float)
    for column, k in enumerate(states):
        for j in range(n):
            if k[n+j]:
                z = list(k);z[j] += 1;z[n+j] -= 1
                K[lookup[tuple(z)], column] += math.sqrt((k[j]+1)*k[n+j])
            if k[j]:
                z = list(k);z[j] -= 1;z[n+j] += 1
                K[lookup[tuple(z)], column] -= math.sqrt(k[j]*(k[n+j]+1))
    if not np.array_equal(K.T, -K):
        raise ArithmeticError('Generator antisymmetry failure')
    eigenvalues, vectors = np.linalg.eigh(1j*K)
    theta = math.atan2(float(s), float(t))
    U = (vectors*np.exp(-1j*theta*eigenvalues))@vectors.conj().T
    return U, states


def candidate_channel(A, B, n, t, s):
    import numpy as np
    U, joint_states = generator_unitary(n, t, s)
    port = basis(n, 2)
    qa, qb = state_matrix(A, port), state_matrix(B, port)
    ra, _ = midpoint_matrix(qa, port);rb, _ = midpoint_matrix(qb, port)
    d = len(joint_states)
    joint = np.zeros((d, d), dtype=complex)
    look = {k: i for i, k in enumerate(joint_states)}
    for ia, a in enumerate(port):
        for ib, b in enumerate(port):
            for ja, aa in enumerate(port):
                for jb, bb in enumerate(port):
                    joint[look[a+b], look[aa+bb]] = ra[ia, ja]*rb[ib, jb]
    result = U@joint@U.conj().T
    states = basis(n, 4);where = {k: i for i, k in enumerate(states)}
    out = np.zeros((len(states), len(states)), dtype=complex)
    for i, k in enumerate(joint_states):
        for j, kk in enumerate(joint_states):
            if k[n:] == kk[n:]:
                out[where[k[:n]], where[kk[:n]]] += result[i, j]
    unitarity = float(np.max(np.abs(U.conj().T@U-np.eye(d))))
    energy_difference = float(abs(sum((joint[i, i]-result[i, i])*sum(k)
                                      for i, k in enumerate(joint_states))))
    return out, {'joint_dimension': d, 'unitarity_defect': unitarity,
                 'joint_energy_defect': energy_difference}


def mutate(q, states, name, A, n, swapped):
    out = [row[:] for row in q]
    if name.startswith('vacuum-leak-'):
        parts = name.split('-');leak = Q(int(parts[-2]), int(parts[-1]))
        out = [[(1-leak)*v for v in row] for row in out];out[0][0] += leak
    elif name == 'wrong-transmissivity':
        out = swapped
    elif name == 'per-mode-cap-one-renormalize':
        allowed = [max(k) <= 1 for k in states]
        mass = sum(q[i][i]*weight(k) for i, k in enumerate(states) if allowed[i])
        if mass == 0:
            return None
        out = [[q[i][j]/mass if allowed[i] and allowed[j] else Q(0)
                for j in range(len(states))] for i in range(len(states))]
    elif name == 'dephase-number-basis':
        out = [[q[i][j] if i == j else Q(0) for j in range(len(states))]
               for i in range(len(states))]
    elif name == 'missing-mixing-return-A':
        out = state_matrix(A, states)
    else:
        raise ValueError('Unregistered fault')
    check_trace(out, states)
    return out


def entanglement_minor(q, states):
    if len(states[0]) != 2:
        return None
    lookup = {k: i for i, k in enumerate(states)}
    for k in (1, 2):
        a, b, z, zz = (k, 0), (0, k), (0, 0), (k, k)
        if a not in lookup or b not in lookup:
            continue
        # Factorial weights of a and b are equal; unnormalized determinant sign
        # is unchanged by positive diagonal basis scaling.
        pzz = q[lookup[zz]][lookup[zz]] if zz in lookup else Q(0)
        minor = q[lookup[z]][lookup[z]]*pzz-q[lookup[a]][lookup[b]]**2
        if minor < 0:
            return {'coherence': [list(a), list(b)], 'negative_partial_transpose_minor': str(minor)}
    return None


def correlated_admission_control():
    # Basis |00>,|01>,|10>,|11>. The pure two-port Bell state has I/2 marginals.
    rho = [[Q(1, 2) if i in (1, 2) and j in (1, 2) else Q(0) for j in range(4)]
           for i in range(4)]
    left = [[sum((rho[2*i+k][2*j+k] for k in range(2)), Q(0)) for j in range(2)] for i in range(2)]
    right = [[sum((rho[2*k+i][2*k+j] for k in range(2)), Q(0)) for j in range(2)] for i in range(2)]
    product = [[left[i//2][j//2]*right[i%2][j%2] for j in range(4)] for i in range(4)]
    return {'joint_trace': str(sum(rho[i][i] for i in range(4))),
            'product_of_marginals_equal': rho == product,
            'entropy_inequality_eligible': False, 'both_qEPI_and_EPnI_skipped': True}


def set_precision(p):
    intervals.C = Context(prec=p)
    intervals.DOWN = Context(prec=p, rounding=ROUND_FLOOR)
    intervals.UP = Context(prec=p, rounding=ROUND_CEILING)


def matrix_data(q):
    return [[str(x) for x in row] for row in q]


def run(spec):
    import numpy as np
    begun = time.perf_counter()
    rows = []
    failures = []
    times = defaultdict(float)
    counts = defaultdict(int)
    margin = D('1e-9')
    try:
        for fixture in spec['input']['fixtures']:
            n = fixture['n'];A = parse_components(fixture['A'], n);B = parse_components(fixture['B'], n)
            port = basis(n, 2);qa = state_matrix(A, port);qb = state_matrix(B, port)
            for amplitudes in spec['input']['amplitude_pairs']:
                case = fixture['id']+'@'+amplitudes['t']
                t, s = Q(amplitudes['t']), Q(amplitudes['r']);eta = t*t
                tick = time.perf_counter();q, states, energy = exact_channel(A, B, n, t, s)
                swapped, _, _ = exact_channel(A, B, n, s, t)
                times['exact_channel_seconds'] += time.perf_counter()-tick
                tick = time.perf_counter();candidate, cm = candidate_channel(A, B, n, t, s)
                ref, conversion = midpoint_matrix(q, states)
                discrepancy = float(np.max(np.abs(candidate-ref)))
                imag = float(np.max(np.abs(candidate.imag)))
                trace = float(abs(np.trace(candidate)-1))
                hermitian = float(np.max(np.abs(candidate-candidate.conj().T)))
                ce = np.linalg.eigvalsh((candidate+candidate.conj().T)/2)
                candidate_bad = (discrepancy > 1e-10 or imag > 1e-11 or trace > 1e-10
                                 or hermitian > 1e-10 or float(min(ce)) < -1e-10
                                 or cm['unitarity_defect'] > 1e-10 or cm['joint_energy_defect'] > 1e-9)
                times['candidate_channel_seconds'] += time.perf_counter()-tick
                if candidate_bad:
                    failures.append(case+':candidate_reference_or_state_failure')
                defects = []
                for f in spec['judge']['faults']:
                    mutated = mutate(q, states, f['id'], A, n, swapped)
                    defects.append((f['id'], mutated))
                passes = []
                primary_spectra = None
                for precision in (70, 100):
                    set_precision(precision);tick = time.perf_counter()
                    sa, ca = entropy_of_matrix(qa, port);sb, cb = entropy_of_matrix(qb, port)
                    sc, cc = entropy_of_matrix(q, states)
                    # A diagnostic entropy of the real symmetric candidate, with a
                    # priori scalar continuity allowance from its measured matrix
                    # error to the exactly physical independent reference. Small
                    # candidate negative eigenvalues are not made physical claims.
                    real_candidate = (candidate.real+candidate.real.T)/2
                    cls, cerr, _, _ = spectral_seed(tuple(map(float, real_candidate.flat)), len(states))
                    delta_entry = max(abs(Q(float(real_candidate[i, j]))-Q(float(ref[i, j])))
                                      for i in range(len(states)) for j in range(len(states)))
                    perturb = len(states)*(delta_entry+conversion)+cerr
                    candidate_entropy = sum((entropy_point(D.from_float(float(max(Q(0), min(Q(1), v)))))
                                             for v in cls), I(0))
                    pe = rat(perturb).hi
                    if pe > 0 and pe < I(-1).exp().lo:
                        allowance = len(states)*entropy_point(pe)
                    elif pe == 0:
                        allowance = I(0)
                    else:
                        allowance = I(100)
                        failures.append(case+':candidate_entropy_perturbation_too_large')
                    candidate_consistent = (candidate_entropy.hi >= intervals.DOWN.subtract(sc.lo, allowance.hi)
                                            and candidate_entropy.lo <= intervals.UP.add(sc.hi, allowance.hi))
                    if not candidate_consistent:
                        failures.append(case+':candidate_entropy_outside_continuity_allowance')
                    old_sharp = fixture['stratum'] == 'old_sharp_control' 
                    new, old, fd = floors(sa, sb, n, eta, old_sharp)
                    if intervals.UP.subtract(sc.hi, sc.lo) > D('1e-8'):
                        failures.append(case+':entropy_interval_too_wide')
                    alarm = sc.hi < intervals.DOWN.subtract(new.lo, margin)
                    if alarm:
                        failures.append(case+':valid_resolved_entropy_alarm')
                    eligible = (fixture['stratum'] == 'core' and 0 < eta < 1
                                and (sa.hi < sb.lo or sb.hi < sa.lo) and not old_sharp)
                    outcomes = []
                    for name, m in defects:
                        if m is None:
                            outcomes.append({'fault': name, 'defined': False});continue
                        sm, cert = entropy_of_matrix(m, states)
                        caught_new = sm.hi < intervals.DOWN.subtract(new.lo, margin)
                        caught_old = sm.hi < intervals.DOWN.subtract(old.lo, margin)
                        old_nonviolating = sm.lo >= intervals.UP.add(old.hi, margin)
                        different = m != q
                        extra = different and eligible and caught_new and old_nonviolating
                        mat, fault_conversion = midpoint_matrix(m, states)
                        direct_difference = float(np.max(np.abs(mat-ref)))
                        outcomes.append({'fault': name, 'defined': True, 'matrix_distinct_exactly': different,
                                         'entropy': sm.data(), 'caught_EPnI': caught_new,
                                         'caught_strongest_old_entropy': caught_old,
                                         'certified_nonviolating_old': old_nonviolating,
                                         'extra_entropy_only_detection': extra,
                                         'direct_max_entry_difference': direct_difference,
                                         'direct_detected': Q(direct_difference) > Q('1e-9')+conversion+fault_conversion,
                                         'certificate': cert if precision == 70 else None})
                    passes.append({'precision': precision, 'SA': sa.data(), 'SB': sb.data(),
                                   'SC': sc.data(), 'EPnI_floor': new.data(), 'best_old_floor': old.data(),
                                   'old_components': fd, 'valid_alarm': alarm, 'gain_eligible': eligible,
                                   'candidate_diagnostic_entropy': candidate_entropy.data(),
                                   'candidate_entropy_continuity_allowance': allowance.data(),
                                   'candidate_entropy_consistent': candidate_consistent,
                                   'faults': outcomes})
                    if precision == 70:
                        primary_spectra = {'A': ca, 'B': cb, 'C': cc}
                    times['certified_entropy_seconds'] += time.perf_counter()-tick
                left, right = passes
                overlap = all(max(D(left[k][0]), D(right[k][0])) <= min(D(left[k][1]), D(right[k][1]))
                              for k in ('SA', 'SB', 'SC', 'EPnI_floor', 'best_old_floor'))
                for l, h in zip(left['faults'], right['faults']):
                    if l['defined']:
                        overlap &= max(D(l['entropy'][0]), D(h['entropy'][0])) <= min(D(l['entropy'][1]), D(h['entropy'][1]))
                        overlap &= all(l[k] == h[k] for k in ('caught_EPnI', 'caught_strongest_old_entropy', 'extra_entropy_only_detection'))
                if not overlap:
                    failures.append(case+':precision_disagreement')
                counts['valid_cases'] += 1
                counts['valid_resolved_false_alarms'] += int(left['valid_alarm'])
                counts['candidate_reference_mismatches'] += int(candidate_bad)
                for f in left['faults']:
                    counts['undefined_faults'] += int(not f['defined'])
                    if f['defined']:
                        counts['defined_faults'] += 1
                        counts['exactly_distinct_output_faults'] += int(f['matrix_distinct_exactly'])
                        counts['EPnI_detections'] += int(f['caught_EPnI'])
                        counts['old_entropy_detections'] += int(f['caught_strongest_old_entropy'])
                        counts['core_extra_entropy_only_detections'] += int(f['extra_entropy_only_detection'])
                        counts['direct_matrix_detections'] += int(f['direct_detected'])
                # Matrix values are represented as full raw IEEE outputs, not discarded.
                row = {'case': case, 'fixture': fixture['id'], 'stratum': fixture['stratum'], 'n': n,
                       'eta': str(eta), 'states': [list(k) for k in states],
                       'input_A_exact_Q': matrix_data(qa), 'input_B_exact_Q': matrix_data(qb),
                       'reference_exact_Q': matrix_data(q),
                       'candidate_real': candidate.real.tolist(), 'candidate_imag': candidate.imag.tolist(),
                       'fault_exact_Q': {name: matrix_data(m) if m is not None else None for name, m in defects},
                       'candidate_reference_max_entry_difference': discrepancy,
                       'candidate_trace_defect': trace, 'candidate_hermitian_defect': hermitian,
                       'candidate_min_eigenvalue': float(min(ce)), 'candidate_metadata': cm,
                       'reference_exact_energy': energy, 'spectral_certificates_70': primary_spectra,
                       'A_entanglement_witness': entanglement_minor(qa, port),
                       'B_entanglement_witness': entanglement_minor(qb, port),
                       'precision_intervals_overlap': bool(overlap), 'checks': passes}
                rows.append(row)
        control = correlated_admission_control()
        if control['product_of_marginals_equal'] or control['entropy_inequality_eligible']:
            failures.append('Correlated port admission failed')
        if counts['valid_cases'] != spec['success']['valid_cases']:
            failures.append('Frozen case count mismatch')
        summary = {'counts': dict(counts), 'failures': failures,
                   'structural_or_numerical_failures': len(failures),
                   'correlated_port_negative_control': control,
                   'meets_prediction': not failures and counts['core_extra_entropy_only_detections'] >= 1,
                   'all_precision_enclosures_overlap': all(r['precision_intervals_overlap'] for r in rows),
                   'max_candidate_reference_entry_difference': max(r['candidate_reference_max_entry_difference'] for r in rows),
                   'old_direct_reference_superiority_claimed': False,
                   'theorem_validation': False, 'human_review': False, 'cross_provider_review': False,
                   'interpretation': 'Finite synthetic simulator regression with exact channel reference and residual-validated entropy intervals; extra catches only versus eligible old scalar entropy floors, never versus full matrix reference. Not a theorem proof or observed external-library defect.',
                   '_runtime_metrics': {**dict(times), 'runner_seconds': time.perf_counter()-begun,
                                        'spectral_cache': str(spectral_seed.cache_info())}}
        return rows, summary
    finally:
        set_precision(70)
