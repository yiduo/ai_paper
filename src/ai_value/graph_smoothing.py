"""Preregistered finite synthetic denoising comparison for F332.

All signal/kernel/risk arithmetic is rational. Performance measurements are
observations, not part of deterministic scientific replay comparison.
"""
from fractions import Fraction as Q
import hashlib
import itertools
import random
import resource
import sys
import time

from . import graph_smoothing_reference as judge


def inverse(m):
    n = len(m)
    a = [[Q(z) for z in row]+[Q(i == j) for j in range(n)]
         for i, row in enumerate(m)]
    for k in range(n):
        pivot = next((i for i in range(k, n) if a[i][k]), None)
        if pivot is None:
            raise ValueError('Singular finite matrix')
        a[k], a[pivot] = a[pivot], a[k]
        scale = a[k][k]
        a[k] = [v/scale for v in a[k]]
        for i in range(n):
            if i != k:
                factor = a[i][k]
                a[i] = [v-factor*w for v, w in zip(a[i], a[k])]
    return [row[n:] for row in a]


def validate_chain(a, pi):
    n = len(a)
    if (n == 0 or len(pi) != n or sum(pi) != 1 or min(pi) < 0
            or any(len(row) != n or min(row) < 0 or sum(row) != 1 for row in a)):
        raise ValueError('Not a finite stochastic chain/probability law')
    if any(sum((pi[i]*a[i][j] for i in range(n)), Q(0)) != pi[j] for j in range(n)):
        raise ValueError('Nonstationary input')


def chain(spec):
    n = spec['n']
    w = [[Q(0) for _ in range(n)] for _ in range(n)]
    for i, j, v in spec['edges']:
        if i == j or not 0 <= i < n or not 0 <= j < n or Q(v) <= 0:
            raise ValueError('Invalid graph edge')
        w[i][j] += Q(v)
        w[j][i] += Q(v)
    degrees = [sum(row) for row in w]
    maximum = max(degrees)
    if not maximum:
        raise ValueError('Empty graph')
    a = [[Q(i == j)-(Q(i == j)*degrees[i]-w[i][j])/(2*maximum)
          for j in range(n)] for i in range(n)]
    pi = [Q(1, n)]*n
    validate_chain(a, pi)
    if any(pi[i]*a[i][j] != pi[j]*a[j][i] for i in range(n) for j in range(n)):
        raise ValueError('Benchmark requires reversibility')
    return a, pi


def resolvent(a, coefficient):
    if coefficient <= 0:
        raise ValueError('Positive resolvent coefficient required')
    n = len(a)
    return inverse([[Q(i == j)+coefficient*(Q(i == j)-a[i][j])
                     for j in range(n)] for i in range(n)])


def linear(x, g):
    return [[sum((row[j]*x[j][c] for j in range(len(x))), Q(0))
             for c in range(len(x[0]))] for row in g]


def expected_median(x, g):
    out = [[Q(0) for _ in x[0]] for _ in g]
    for c in range(len(x[0])):
        levels = sorted({v[c] for v in x})
        for i, row in enumerate(g):
            value = levels[0]
            for low, high in zip(levels, levels[1:]):
                h = sum((row[j] for j in range(len(x)) if x[j][c] >= high), Q(0))
                value += (high-low)*(3*h*h-2*h*h*h)
            out[i][c] = value
    return out


def weighted_median(x, g):
    out = [[Q(0) for _ in x[0]] for _ in g]
    for c in range(len(x[0])):
        order = sorted(range(len(x)), key=lambda j: (x[j][c], j))
        for i, row in enumerate(g):
            mass = Q(0)
            for j in order:
                mass += row[j]
                if mass >= Q(1, 2):
                    out[i][c] = x[j][c]
                    break
    return out


def profile(name, n):
    u = [Q(i, n-1) for i in range(n)]
    if name == 'constant2':
        return [[Q(1), Q(-1)] for _ in range(n)]
    if name == 'ramp2':
        return [[v, 1-v] for v in u]
    if name == 'step4':
        return [[Q(i >= n//2), Q(2*(i >= n//2)-1), Q(1), u[i]] for i in range(n)]
    if name == 'constant1':
        return [[Q(1)] for _ in range(n)]
    if name == 'ramp1':
        return [[v] for v in u]
    raise ValueError('Unregistered profile')


def observed(clean, seed, graph_id, profile_id, scale):
    key = f'{seed}|{graph_id}|{profile_id}|{scale}'.encode()
    rng = random.Random(int.from_bytes(hashlib.sha256(key).digest(), 'big'))
    noise, largest = [], 0
    for row in clean:
        values = []
        for _ in row:
            k = 0
            while rng.getrandbits(1):
                k += 1
                if k > 64:
                    raise ValueError('Frozen noise guard exceeded;do not clip/reselect')
            largest = max(largest, k)
            values.append(Q(scale)*(1 if rng.getrandbits(1) else -1)*2**k)
        noise.append(values)
    x = [[v+e for v, e in zip(row, errors)] for row, errors in zip(clean, noise)]
    return x, noise, largest


def risk(clean, y, pi):
    return sum((w*sum((abs(a-b) for a, b in zip(c, z)), Q(0))
                for w, c, z in zip(pi, clean, y)), Q(0))


def outcome(new, old):
    return dict(win=bool(old > 0 and 10*new <= 9*old),
                harmed=bool(new > 0 if old == 0 else 20*new > 21*old),
                relative_reduction=None if old == 0 else str(1-new/old))


def encode(v):
    if isinstance(v, Q):
        return str(v)
    if isinstance(v, dict):
        return {k: encode(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [encode(x) for x in v]
    return v


def run(spec):
    started = time.perf_counter()
    params = spec['input']['parameters']
    families = ['candidate', 'identity', 'linear_resolvent', 'weighted_median', 'quadratic']
    choices = dict(candidate=params['candidate_t'], identity=[None],
                   linear_resolvent=params['linear_resolvent_t'],
                   weighted_median=params['weighted_median_t'], quadratic=params['quadratic_alpha'])
    timings = {f: dict(training_seconds=0.0, test_seconds=0.0, calls=0) for f in families}
    generation_seconds = judge_seconds = 0.0
    kernels, kernel_rows, cases, rows = {}, [], [], []
    judge_counts = dict(constructor_checks=0, weighted_median_checks=0,
                        quadratic_checks=0, energy_checks=0, risk_checks=0,
                        scalar_optimality_checks=0, mismatches=0, energy_violations=0)
    maximum_noise_k = max_bits = 0
    for graph in spec['input']['graphs']:
        a, pi = chain(graph)
        coefficients = sorted(set(map(Q, params['candidate_t']+params['linear_resolvent_t']
                                      +params['weighted_median_t']))
                              | {2*Q(v) for v in params['quadratic_alpha']})
        for coefficient in coefficients:
            clock = time.perf_counter()
            g = resolvent(a, coefficient)
            elapsed = time.perf_counter()-clock
            clock = time.perf_counter()
            valid = (all(min(row) >= 0 and sum(row) == 1 for row in g)
                     and judge.inverse_residual(a, g, coefficient))
            judge_seconds += time.perf_counter()-clock
            if not valid:
                raise ArithmeticError('Kernel residual/stochasticity mismatch')
            kernels[(graph['id'], coefficient)] = g
            kernel_rows.append(dict(graph=graph['id'], coefficient=str(coefficient),
                                    matrix=g, build_seconds=elapsed, exact_residual_passed=valid))
        for name, scale in itertools.product([p['id'] for p in spec['input']['profiles']],
                                             spec['input']['noise_scales']):
            cases.append((graph, name, scale, 'core'))
    graph = spec['input']['graphs'][0]
    cases += [(graph, name, '1/4', 'scalar_control') for name in ['constant1', 'ramp1']]
    for graph, name, scale, stratum in cases:
        a, pi = chain(graph)
        clean = profile(name, graph['n'])
        records = dict(train=[], test=[])
        train = {f: {str(p): Q(0) for p in choices[f]} for f in families}
        selected = {}
        heldout = {f: Q(0) for f in families}
        for phase in ['train', 'test']:
            seeds = spec['input'][phase+'_seeds']
            if stratum == 'scalar_control' and phase == 'test':
                seeds = seeds[:2]
            if phase == 'test':
                selected = {f: min(choices[f], key=lambda p: train[f][str(p)]) for f in families}
            for seed in seeds:
                clock = time.perf_counter()
                x, noise, k = observed(clean, seed, graph['id'], name, scale)
                generation_seconds += time.perf_counter()-clock
                maximum_noise_k = max(maximum_noise_k, k)
                outputs, losses, energy_records = {}, {}, {}
                for f in families:
                    for parameter in choices[f] if phase == 'train' else [selected[f]]:
                        key = f+'|'+str(parameter)
                        coefficient = 2*Q(parameter) if f == 'quadratic' else Q(parameter or 1)
                        g = kernels[(graph['id'], coefficient)]
                        clock = time.perf_counter()
                        y = (expected_median(x, g) if f == 'candidate' else
                             weighted_median(x, g) if f == 'weighted_median' else
                             [list(row) for row in x] if f == 'identity' else linear(x, g))
                        timings[f][phase+'ing_seconds' if phase == 'train' else 'test_seconds'] += time.perf_counter()-clock
                        timings[f]['calls'] += 1
                        clock = time.perf_counter()
                        loss = risk(clean, y, pi)
                        judge_counts['risk_checks'] += 1
                        judge_counts['mismatches'] += loss != judge.clean_risk(clean, y, pi)
                        if f == 'candidate':
                            judge_counts['constructor_checks'] += 1
                            judge_counts['mismatches'] += y != judge.endpoint_median(x, g)
                            en = judge.energy(x, y, a, pi, int(parameter))
                            energy_records[key] = en
                            judge_counts['energy_checks'] += 1
                            judge_counts['energy_violations'] += en['violation']
                        elif f == 'weighted_median':
                            judge_counts['weighted_median_checks'] += 1
                            judge_counts['mismatches'] += not judge.weighted_absolute_minimum(x, g, y)
                        elif f == 'quadratic':
                            judge_counts['quadratic_checks'] += 1
                            judge_counts['mismatches'] += not judge.quadratic_residual(x, y, a, Q(parameter))
                        judge_seconds += time.perf_counter()-clock
                        for row in y:
                            for v in row:
                                max_bits = max(max_bits, v.numerator.bit_length(), v.denominator.bit_length())
                        outputs[key], losses[key] = y, loss
                        if phase == 'train':
                            train[f][str(parameter)] += loss/len(seeds)
                        else:
                            heldout[f] += loss/len(seeds)
                scalar = None
                if stratum == 'scalar_control' and phase == 'test':
                    clock = time.perf_counter()
                    t = selected['candidate']
                    yopt = linear(x, kernels[(graph['id'], Q(2*t))])
                    opt = judge.energy(x, yopt, a, pi, t)
                    other = {key: judge.energy(x, y, a, pi, t)['left'] for key, y in outputs.items()}
                    valid = (judge.quadratic_residual(x, yopt, a, Q(t))
                             and all(opt['left'] <= v for v in other.values()))
                    judge_counts['scalar_optimality_checks'] += 1
                    judge_counts['mismatches'] += not valid
                    scalar = dict(output=yopt, source_energy=opt['left'], other_source_energies=other,
                                  exact_quadratic_optimality_passed=valid)
                    judge_seconds += time.perf_counter()-clock
                records[phase].append(dict(seed=seed, observed=x, noise=noise, maximum_noise_k=k,
                                           outputs=outputs, risks=losses, candidate_energy=energy_records,
                                           scalar_source_optimum=scalar))
        best = min(families[1:], key=lambda f: heldout[f])
        decision = outcome(heldout['candidate'], heldout[best])
        rows.append(dict(case_id=graph['id']+'|'+name+'|'+scale,stratum=stratum, graph_id=graph['id'],
                         profile=name,scale=scale,clean=clean,pi=pi,transition=a,selected_parameters=selected,
                         training_mean_risks=train,heldout_mean_risks=heldout,best_old_oracle_family=best,
                         best_old_oracle_risk=heldout[best],decision=decision,records=records))
    core = [r for r in rows if r['stratum'] == 'core']
    wins, harms = sum(r['decision']['win'] for r in core), sum(r['decision']['harmed'] for r in core)
    elapsed = time.perf_counter()-started
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    rss = int(rss if sys.platform == 'darwin' else rss*1024)
    complete = len(core) == spec['success']['core_case_count']
    met = (complete and wins >= spec['success']['minimum_cases_with_ten_percent_risk_reduction']
           and harms <= spec['success']['maximum_harmed_cases'] and not judge_counts['mismatches']
           and not judge_counts['energy_violations'])
    summary = dict(core_cases=len(core),scalar_controls=len(rows)-len(core),cases_with_ten_percent_gain=wins,
                   harmed_cases=harms,judges=judge_counts,maximum_noise_k=maximum_noise_k,
                   maximum_output_rational_bit_length=max_bits,all_fixtures_complete=complete,
                   meets_prediction=met,case_decisions=[{k:r[k] for k in ['case_id','stratum','heldout_mean_risks','best_old_oracle_family','decision']} for r in rows],
                   runtime=dict(algorithm_evaluation=timings,kernel_preprocessing_seconds=sum(k['build_seconds'] for k in kernel_rows),
                                independent_judges_seconds=judge_seconds,generation_seconds=generation_seconds,
                                full_evaluation_seconds=elapsed,process_peak_rss_bytes=rss,
                                cache_scope='Exact kernels shared across draws and related method parameters;all graph/parameter builds and full training/testing work measured. No free-kernel speed claim.'),
                   interpretation='Finite synthetic heavy-tail feature denoising risk comparison against qualified old pool;source energy checks and scalar identities do not establish incremental theorem value,whole-paper validity or deployment. Best heldout old family is an oracle diagnostic,not deployable test-label selection.')
    return encode([dict(kind='kernel_preprocessing',kernels=kernel_rows)]+rows), encode(summary)
