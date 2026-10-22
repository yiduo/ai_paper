"""Small antipodal rounding experiment with an exact, independent circle judge.

Float arithmetic selects words only. The judge uses integer Horner evaluation,
an independent autocorrelation identity, and an explicit mesh remainder.
Exhaustive searches are deliberately limited to six coordinates.
"""

import cmath
from fractions import Fraction as Q
from itertools import combinations, product
from math import gcd, lcm, pi

from .block_budget import sqrt_interval

TIE = 1e-12


def inputs(fixture, maximum_n=6):
    phases = [tuple(map(Q, row)) for row in fixture['phases']]
    radii = list(map(Q, fixture['magnitudes']))
    if not 1 <= len(radii) == len(phases) <= maximum_n:
        raise ValueError('Invalid or out-of-budget input length')
    for phase, radius in zip(phases, radii):
        if len(phase) != 2 or sum(x * x for x in phase) != 1 or not 0 <= radius <= 1:
            raise ValueError('Expected unit rational phases and radii in [0,1]')
        if radius == 0 and phase != (1, 0):
            raise ValueError('Zero input phase must follow source convention d=1')
    return phases, radii


def optimizer_matrix(phases, multiplier):
    n = len(phases)
    return [[complex(float(x), float(y)) * cmath.exp(2j * pi * j * ell / (multiplier * n))
             for j, (x, y) in enumerate(phases)] for ell in range(multiplier * n)]


def grid_score(matrix, coefficients, rectangular=False):
    values = [sum(a * float(c) for a, c in zip(row, coefficients)) for row in matrix]
    if rectangular:
        return max(max(abs(v.real), abs(v.imag)) for v in values)
    return max(map(abs, values))


def better(score, word, best_score, best_word):
    return (best_word is None or score < best_score - TIE
            or (abs(score - best_score) <= TIE and tuple(word) < tuple(best_word)))


def dyadic_round(matrix, radii, budget):
    n = len(radii)
    original = [(1 - r) / 2 for r in radii]
    mu = sum(original, Q(0))
    j = max(1, (n - 1).bit_length())
    scale = 1 << j
    p = [Q((v * scale).__floor__(), scale) for v in original]
    initial = p[:]
    errors, stages, evaluations = [], [], 0
    if sum(p) > mu or sum(abs(x - y) for x, y in zip(original, p)) > 1:
        errors.append('Initial truncation violates source mass/error condition')
    for h in range(j, 0, -1):
        before = p[:]
        mass_before = sum(p)
        scale = 1 << h
        if any((x * scale).denominator != 1 for x in p):
            errors.append('Input to stage is not on its dyadic grid')
        active = [i for i, x in enumerate(p) if int(x * scale) % 2]
        if len(active) > min(n, scale * mu):
            errors.append('Source active-set mass bound fails')
        best_score, best_xi = None, None
        for xi in product((-1, 1), repeat=len(active)) if active else ():
            if evaluations >= budget:
                raise ValueError('Dyadic score budget exhausted')
            vector = [0] * n
            for i, sign in zip(active, xi):
                vector[i] = sign
            score = grid_score(matrix, vector, rectangular=True)
            evaluations += 1
            if better(score, xi, best_score, best_xi):
                best_score, best_xi = score, xi
        chosen = best_xi or ()
        if sum(chosen) > 0:
            chosen = tuple(-x for x in chosen)
        for i, sign in zip(active, chosen):
            p[i] += Q(sign, scale)
        if (any(not 0 <= x <= 1 or (x * (scale // 2)).denominator != 1 for x in p)
                or sum(p) > mass_before or sum(p) > mu):
            errors.append('Dyadic update violates grid, range or mass')
        stages.append({'h': h, 'active': active, 'xi': list(chosen),
                       'before': list(map(str, before)), 'after': list(map(str, p)),
                       'mass_before': str(mass_before), 'mass_after': str(sum(p)),
                       'matrix_infinity_score': best_score,
                       'enumerated_vectors': (1 << len(active)) if active else 0})
    word = tuple(int(1 - 2 * x) for x in p)
    if any(x not in (-1, 1) for x in word) or sum(p) > mu:
        errors.append('Final word or mass invalid')
    return word, {'mu': str(mu), 'J': j, 'truncated_p': list(map(str, initial)),
                  'stages': stages, 'objective_evaluations': evaluations,
                  'failure_reasons': errors}


def greedy_round(matrix, radii, budget):
    n, cache, hits = len(radii), {}, 0

    def evaluate(word):
        nonlocal hits
        if word in cache:
            hits += 1
            return cache[word]
        if len(cache) >= budget:
            return None
        value = grid_score(matrix, [s - r for s, r in zip(word, radii)])
        cache[word] = value
        return value

    starts = [(1,) * n, (-1,) * n, tuple(1 if i % 2 == 0 else -1 for i in range(n))]
    traces = []
    for start in starts:
        word, steps, reason = start, [], 'local_optimum_single_and_pair_flips'
        score = evaluate(word)
        if score is None:
            traces.append({'start': list(start), 'termination': 'budget', 'steps': []})
            break
        while True:
            best_word, best_score = word, score
            exhausted = False
            for size in (1, 2):
                for flip in combinations(range(n), size):
                    candidate = list(word)
                    for i in flip:
                        candidate[i] *= -1
                    candidate = tuple(candidate)
                    value = evaluate(candidate)
                    if value is None:
                        exhausted = True
                        break
                    if better(value, candidate, best_score, best_word):
                        best_word, best_score = candidate, value
                if exhausted:
                    break
            if best_score < score - TIE:
                word, score = best_word, best_score
                steps.append({'word': list(word), 'score': score})
            else:
                if exhausted:
                    reason = 'budget'
                break
            if exhausted:
                reason = 'budget'
                break
        traces.append({'start': list(start), 'final': list(word), 'score': score,
                       'steps': steps, 'termination': reason})
    best_word, best_score = None, None
    for word, score in sorted(cache.items()):
        if better(score, word, best_score, best_word):
            best_word, best_score = word, score
    return best_word, {'objective_evaluations': len(cache), 'cache_hits': hits,
                       'starts': traces, 'best_grid_score': best_score}


def gaussian_multiply(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def rational_circle_points(mesh):
    if mesh < 1:
        raise ValueError('Positive mesh required')
    rotations = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    for quadrant, rot in enumerate(rotations):
        for step in range(mesh + 1):
            a, b, d = mesh * mesh - step * step, 2 * step * mesh, mesh * mesh + step * step
            common = gcd(gcd(abs(a), abs(b)), d)
            a, b, d = a // common, b // common, d // common
            u, v = gaussian_multiply(rot, (a, b))
            yield quadrant, step, u, v, d


def integer_horner(coefficients, u, v, denominator):
    """Return numerator pair and denominator power for a Gaussian polynomial."""
    re, im = coefficients[-1]
    power = 1
    for a, b in reversed(coefficients[:-1]):
        re, im = re * u - im * v, re * v + im * u
        power *= denominator
        re, im = re + a * power, im + b * power
    return re, im, power


def gaussian_coefficients(phases, radii, word):
    coefficients = [((s - r) * x, (s - r) * y) for (x, y), r, s in zip(phases, radii, word)]
    common = lcm(*(v.denominator for c in coefficients for v in c))
    return [(int(x * common), int(y * common)) for x, y in coefficients], common


def autocorrelations(coefficients):
    return [tuple(sum(gaussian_multiply(coefficients[j + k],
                                       (coefficients[j][0], -coefficients[j][1]))[component]
                      for j in range(len(coefficients) - k)) for component in (0, 1))
            for k in range(len(coefficients))]


def circle_certificate(phases, radii, word, mesh, bits, independent=False):
    if len(word) != len(radii) or any(x not in (-1, 1) for x in word):
        raise ValueError('Ineligible word')
    integers, common = gaussian_coefficients(phases, radii, word)
    corr = autocorrelations(integers) if independent else None
    maximum, at = Q(0), None
    samples, mismatches = [], 0
    for quadrant, step, u, v, denominator in rational_circle_points(mesh):
        re, im, power = integer_horner(integers, u, v, denominator)
        numerator = re * re + im * im
        value = Q(numerator, common * common * power * power)
        if value > maximum or at is None:
            maximum, at = value, [quadrant, step]
        if independent:
            cre, _, cpower = integer_horner(corr, u, v, denominator)
            cross_ok = cpower == power and numerator == (2 * cre - corr[0][0] * power) * power
            mismatches += not cross_ok
            samples.append({'quadrant': quadrant, 'step': step,
                            'abs_squared': str(value), 'autocorrelation_matches': cross_ok})
    lo, sampled_hi = sqrt_interval(maximum, bits)
    derivative = sum((j * abs(s - r) for j, (s, r) in enumerate(zip(word, radii))), Q(0))
    correction = derivative / mesh
    upper = sampled_hi + correction
    energy = sum(((s - r) ** 2 for s, r in zip(word, radii)), Q(0))
    result = {'word': list(word), 'lower': str(lo), 'upper': str(upper),
              'sampled_upper': str(sampled_hi), 'derivative_bound': str(derivative),
              'mesh_correction': str(correction), 'max_sample_abs_squared': str(maximum),
              'max_sample_at': at, 'parseval_energy': str(energy),
              'parseval_consistent': energy <= upper * upper}
    if independent:
        result.update(identity_mismatches=mismatches, samples=samples)
    return result


def eligible_word_oracle(phases, radii, mesh, bits):
    """Exact finite arithmetic; continuum optimum is an interval, not a point."""
    words = [circle_certificate(phases, radii, word, mesh, bits)
             for word in product((-1, 1), repeat=len(radii))]
    return words, [str(min(Q(item['lower']) for item in words)),
                   str(min(Q(item['upper']) for item in words))]


def run(spec):
    options, rows = spec['input'], []
    mesh, bits = options['judge_intervals_per_quarter'], options['sqrt_fraction_bits']
    budget = options['candidate_budget_per_method']
    for fixture in options['fixtures']:
        phases, radii = inputs(fixture, options['maximum_n'])
        matrix = optimizer_matrix(phases, options['optimizer_grid_multiplier'])
        joint, trace = dyadic_round(matrix, radii, budget)
        greedy, greedy_trace = greedy_round(matrix, radii, budget)
        nearest = (1,) * len(radii)
        words, optimum = eligible_word_oracle(phases, radii, mesh, bits)
        lookup = {tuple(c['word']): c for c in words}
        failures = trace['failure_reasons'][:]
        certificates = {}
        for name, word in [('nearest', nearest), ('joint', joint), ('greedy', greedy)]:
            certificate = circle_certificate(phases, radii, word, mesh, bits, independent=True)
            if (certificate['identity_mismatches'] or not certificate['parseval_consistent']
                    or any(certificate[k] != v for k, v in lookup[word].items())):
                failures.append('Exact independent judge mismatch: ' + name)
            certificates[name] = certificate
        if any(not word['parseval_consistent'] for word in words):
            failures.append('Oracle Parseval check failed')
        if Q(optimum[0]) > min(Q(c['upper']) for c in certificates.values()):
            failures.append('Selected word contradicts oracle bound')
        if fixture['stratum'] == 'zero_defect_control' and any(
                Q(c['upper']) != 0 for c in certificates.values()):
            failures.append('Zero-defect control should have exact zero error')
        if Q(trace['mu']) < 1 and joint != nearest:
            failures.append('Sub-unit mass cannot leave any negative output sign')
        if (trace['objective_evaluations'] > budget or greedy_trace['objective_evaluations'] > budget):
            failures.append('Method exceeded objective budget')
        joint_lo, joint_hi = map(Q, (certificates['joint']['lower'], certificates['joint']['upper']))
        baseline_lows = [Q(certificates[k]['lower']) for k in ('nearest', 'greedy')]
        baseline_highs = [Q(certificates[k]['upper']) for k in ('nearest', 'greedy')]
        resolved = all(v > 0 and joint_hi <= Q(9, 10) * v for v in baseline_lows)
        possible = all(v > 0 and joint_lo <= Q(9, 10) * v for v in baseline_highs)
        rows.append({'id': fixture['id'], 'stratum': fixture['stratum'],
                     'n': len(radii), 'phases': [list(map(str, p)) for p in phases],
                     'magnitudes': list(map(str, radii)), 'dyadic': trace, 'greedy': greedy_trace,
                     'certificates': certificates, 'all_word_intervals': words,
                     'optimal_continuum_interval': optimum,
                     'grid_scores': {k: grid_score(matrix, [s - r for s, r in zip(c['word'], radii)])
                                     for k, c in certificates.items()},
                     'resolved_10percent_win': resolved,
                     'unresolved_10percent_comparison': possible and not resolved,
                     'incremental_credit': fixture['stratum'] == 'core' and resolved,
                     'greedy_certifiably_better_than_joint': Q(certificates['greedy']['upper']) < joint_lo,
                     'deterministic_work': {'optimizer_points': len(matrix),
                                            'dyadic_objectives': trace['objective_evaluations'],
                                            'greedy_objectives': greedy_trace['objective_evaluations'],
                                            'oracle_words': len(words), 'judge_points_per_word': 4 * (mesh + 1),
                                            'independent_identity_checks': 3 * 4 * (mesh + 1)},
                     'failure_reasons': failures})
    failures = sum(bool(r['failure_reasons']) for r in rows)
    wins = sum(r['incremental_credit'] for r in rows)
    return rows, {'fixtures': len(rows), 'structural_or_certificate_failures': failures,
                  'core_resolved_10percent_wins': wins,
                  'unresolved_10percent_comparisons': sum(r['unresolved_10percent_comparison'] for r in rows),
                  'old_greedy_certifiably_better': sum(r['greedy_certifiably_better_than_joint'] for r in rows),
                  'exhaustive_oracle_words': sum(len(r['all_word_intervals']) for r in rows),
                  'independent_identity_checks': sum(r['deterministic_work']['independent_identity_checks'] for r in rows),
                  'meets_prediction': len(rows) == spec['success']['fixtures'] and failures == 0
                  and wins >= spec['success']['core_resolved_10percent_wins_minimum'],
                  'interpretation': 'Fixed finite synthetic method comparison, with exact whole-circle intervals; not analytic continuous optimization, theorem verification, novel discrepancy theory, hardware benefit or practical speed superiority.'}
