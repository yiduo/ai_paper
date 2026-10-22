"""Exact finite block-polynomial certificate audit, not a theorem verifier.

All certificate arithmetic is rational.  The only square roots are enclosed
outward by integer arithmetic; boundary samples include a Lipschitz remainder.
"""

from fractions import Fraction as Q
from math import isqrt


def sqrt_interval(x, bits=64):
    x = Q(x)
    if x < 0:
        raise ValueError("Negative square-root input")
    scale = 1 << bits
    k = isqrt(x.numerator * scale * scale // x.denominator)
    lo = Q(k, scale)
    return lo, lo if lo * lo == x else Q(k + 1, scale)


def cadd(a, b):
    return a[0] + b[0], a[1] + b[1]


def cmul(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def abs2(a):
    return a[0] ** 2 + a[1] ** 2


def small_norm_interval(a, bits=64):
    """Singular norm of a complex-rational square matrix of order 1 or 2."""
    if len(a) == 1 and len(a[0]) == 1:
        return sqrt_interval(abs2(a[0][0]), bits)
    if len(a) != 2 or any(len(row) != 2 for row in a):
        raise ValueError("Only coefficient sizes 1 and 2 are in this specification")
    tr = sum(abs2(x) for row in a for x in row)
    left, right = cmul(a[0][0], a[1][1]), cmul(a[0][1], a[1][0])
    determinant_square = abs2((left[0] - right[0], left[1] - right[1]))
    dlo, dhi = sqrt_interval(tr * tr - 4 * determinant_square, bits)
    return sqrt_interval((tr + dlo) / 2, bits)[0], sqrt_interval((tr + dhi) / 2, bits)[1]


def eye(n):
    return [[Q(i == j) for j in range(n)] for i in range(n)]


def scale(a, c):
    return [[c * x for x in row] for row in a]


def add(a, b):
    return [[x + y for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def transpose(a):
    return [list(row) for row in zip(*a)]


def multiply(a, b):
    cols = transpose(b)
    return [[sum((x * y for x, y in zip(row, col)), Q(0)) for col in cols] for row in a]


def noncommuting(a, b):
    return multiply(a, b) != multiply(b, a)


def positive_definite(a):
    """Exact symmetric Schur elimination; zero pivot means not strictly PD."""
    b = [row[:] for row in a]
    n = len(b)
    if b != transpose(b):
        raise ValueError("Real Gram certificate must be symmetric")
    for k in range(n):
        pivot = b[k][k]
        if pivot <= 0:
            return False
        for i in range(k + 1, n):
            factor = b[i][k] / pivot
            for j in range(i, n):
                value = b[i][j] - factor * b[k][j]
                b[i][j] = b[j][i] = value
    return True


def block_norm_interval(a, steps=36, bits=64):
    gram = multiply(transpose(a), a)
    n = len(gram)
    lo, hi = Q(0), 1 + max(sum(abs(x) for x in row) for row in gram)
    for _ in range(steps):
        mid = (lo + hi) / 2
        shifted = [[Q(i == j) * mid - gram[i][j] for j in range(n)] for i in range(n)]
        if positive_definite(shifted):
            hi = mid
        else:
            lo = mid
    return sqrt_interval(lo, bits)[0], sqrt_interval(hi, bits)[1]


def polynomial_value(coefficients, z):
    m = len(coefficients[0])
    powers = [(Q(1), Q(0)), z, cmul(z, z)]
    return [[tuple(sum(coefficients[k][i][j] * powers[k][component] for k in range(3))
                   for component in range(2)) for j in range(m)] for i in range(m)]


def coefficient_norm(a, bits):
    return small_norm_interval([[(x, Q(0)) for x in row] for row in a], bits)


def boundary_certificate(coefficients, major, minor, grid, bits):
    """Ellipse/circle maximum interval, with a global derivative correction."""
    a, b = (major + minor) / 2, (major - minor) / 2
    samples = []
    roots = [(Q(1), Q(0)), (Q(0), Q(1)), (Q(-1), Q(0)), (Q(0), Q(-1))]
    for quadrant in range(4):
        for step in range(grid + 1):
            t = Q(step, grid)
            w = cmul(roots[quadrant], ((1 - t * t) / (1 + t * t), 2 * t / (1 + t * t)))
            z = ((a + b) * w[0], (a - b) * w[1])
            lo, hi = small_norm_interval(polynomial_value(coefficients, z), bits)
            samples.append({"quadrant": quadrant, "step": step,
                            "point": [str(z[0]), str(z[1])],
                            "norm_interval": [str(lo), str(hi)]})
    lower = max(Q(s['norm_interval'][0]) for s in samples)
    sampled_upper = max(Q(s['norm_interval'][1]) for s in samples)
    lipschitz = coefficient_norm(coefficients[1], bits)[1] + 2 * major * coefficient_norm(coefficients[2], bits)[1]
    correction = lipschitz * major / grid
    return {"lower": lower, "upper": sampled_upper + correction,
            "sampled_upper": sampled_upper, "lipschitz": lipschitz,
            "correction": correction, "samples": samples}


def evaluate_twice(a, coefficients):
    n, m = len(a), len(coefficients[0])
    powers = [eye(n), a, multiply(a, a)]
    first = [[sum(powers[k][i // m][j // m] * coefficients[k][i % m][j % m] for k in range(3))
              for j in range(n * m)] for i in range(n * m)]
    # Independently organize scalar entry polynomials as coefficient-first blocks
    # using Horner, then explicitly permute to the base-first tensor ordering.
    second = [[Q(0) for _ in range(n * m)] for _ in range(n * m)]
    for r in range(m):
        for s in range(m):
            block = add(multiply(add(scale(a, coefficients[2][r][s]),
                                     scale(eye(n), coefficients[1][r][s])), a),
                        scale(eye(n), coefficients[0][r][s]))
            for i in range(n):
                for j in range(n):
                    second[i * m + r][j * m + s] = block[i][j]
    return first, second


def run(spec):
    options = spec['input']
    grid, bits = options['grid_intervals_per_quarter'], options['sqrt_fraction_bits']
    steps = options['block_squared_norm_bisections']
    rows = []
    for fixture in options['fixtures']:
        diagonal = list(map(Q, fixture['diagonal']))
        n = len(diagonal)
        k_matrix = [[Q(0) for _ in range(n)] for _ in range(n)]
        for i, j, w in fixture['skew_edges']:
            k_matrix[i][j] += Q(w)
            k_matrix[j][i] -= Q(w)
        a_matrix = add([[diagonal[i] if i == j else Q(0) for j in range(n)] for i in range(n)], k_matrix)
        coefficients = [[[Q(x) for x in row] for row in b] for b in fixture['coefficients']]
        m, tau = len(coefficients[0]), Q(fixture['tolerance'])
        h = max(abs(x) for x in diagonal)
        k = max(sum(abs(x) for x in row) for row in k_matrix)
        normal = not noncommuting(a_matrix, transpose(a_matrix))
        coefficient_noncommuting = any(noncommuting(coefficients[i], coefficients[j])
                                      for i in range(3) for j in range(i + 1, 3))
        errors = []
        if fixture['stratum'] == 'core' and (n < 4 or m < 2 or normal or not coefficient_noncommuting):
            errors.append('Core fixture is already in an excluded simple scope')
        first, second = evaluate_twice(a_matrix, coefficients)
        if first != second:
            errors.append('Independent block evaluations disagree')
        direct_lo, direct_hi = block_norm_interval(first, steps, bits)
        budgets = {"direct_exact": direct_hi}
        lower_budgets = {"direct_exact": direct_lo}
        row = {"id": fixture['id'], "stratum": fixture['stratum'], "base_dimension": n,
               "coefficient_dimension": m, "nonnormal": not normal,
               "coefficient_noncommuting": coefficient_noncommuting,
               "A": [[str(x) for x in row] for row in a_matrix],
               "block_evaluation": [[str(x) for x in row] for row in first],
               "two_evaluations_agree": first == second,
               "direct_block_norm_interval": [str(direct_lo), str(direct_hi)],
               "tolerance": str(tau), "rectangle_h_k": [str(h), str(k)]}
        if k:
            major, minor = 5 * h / 4, 5 * k / 3
            if not (0 < minor < major and (h / major) ** 2 + (k / minor) ** 2 <= 1):
                raise ValueError('Invalid frozen ellipse enclosure')
            ellipse = boundary_certificate(coefficients, major, minor, grid, bits)
            disk = boundary_certificate(coefficients, major, major, grid, bits)
            blo, bhi = sqrt_interval(2, bits)
            budgets.update(new_complete_ellipse=2 * ellipse['upper'],
                           old_general=(1 + bhi) * ellipse['upper'],
                           old_complete_disk=2 * disk['upper'])
            lower_budgets.update(new_complete_ellipse=2 * ellipse['lower'],
                                 old_general=(1 + blo) * ellipse['lower'],
                                 old_complete_disk=2 * disk['lower'])
            ca, cb = (major + minor) / 2, (major - minor) / 2
            c0 = add(coefficients[0], scale(coefficients[2], 2 * ca * cb))
            c1, c2 = scale(coefficients[1], ca), scale(coefficients[2], ca * ca)
            identity_ok = (add(c0, scale(c2, -2 * cb / ca)) == coefficients[0]
                           and scale(c1, 1 / ca) == coefficients[1]
                           and scale(c2, 1 / (ca * ca)) == coefficients[2])
            if not identity_ok:
                errors.append('Faber coefficient reconstruction fails')
            intervals = [coefficient_norm(c, bits) for c in [c0, c1, c2]]
            budgets['old_faber_triangle'] = intervals[0][1] + 2 * intervals[1][1] + 2 * intervals[2][1]
            lower_budgets['old_faber_triangle'] = intervals[0][0] + 2 * intervals[1][0] + 2 * intervals[2][0]
            if m == 1 or n <= 3:
                budgets['old_prior_special_two'] = budgets['new_complete_ellipse']
                lower_budgets['old_prior_special_two'] = lower_budgets['new_complete_ellipse']
            def packed(cert):
                return {key: str(value) if isinstance(value, Q) else value for key, value in cert.items()}
            row.update(ellipse_semiaxes=[str(major), str(minor)],
                       ellipse_certificate=packed(ellipse), disk_certificate=packed(disk),
                       exact_faber_reconstruction=identity_ok)
        else:
            if not normal:
                raise ValueError('Zero skew control is not normal')
            eig_intervals = [small_norm_interval(polynomial_value(coefficients, (z, Q(0))), bits) for z in diagonal]
            budgets['old_normal_spectral_one'] = max(x[1] for x in eig_intervals)
            lower_budgets['old_normal_spectral_one'] = max(x[0] for x in eig_intervals)
            if direct_lo > budgets['old_normal_spectral_one'] or lower_budgets['old_normal_spectral_one'] > direct_hi:
                errors.append('Independent normal spectral interval disagrees with Gram interval')
            row['normal_control_new_bound_not_applied'] = True
        for name, upper in budgets.items():
            if direct_lo > upper:
                errors.append('Direct norm provably exceeds ' + name)
        old_names = [name for name in budgets if name.startswith('old_')]
        new_pass = budgets.get('new_complete_ellipse', Q(10 ** 6)) <= tau
        # This is a decision against the specified implementations, not the
        # assertion that the unknown optimal or all historical bounds exceed tau.
        strong_win = (fixture['stratum'] == 'core' and new_pass
                      and all(budgets[name] > tau for name in old_names))
        # A robust gap cannot be explained by outward arithmetic/grid slack.
        resolved_win = strong_win and all(lower_budgets[name] > tau for name in old_names)
        row.update(budgets={key: str(value) for key, value in budgets.items()},
                   budget_lower_endpoints={key: str(value) for key, value in lower_budgets.items()},
                   budget_passes={key: value <= tau for key, value in budgets.items()},
                   best_implemented_old_functional_budget=str(min(budgets[name] for name in old_names)),
                   core_budget_decision_win=strong_win,
                   core_budget_win_resolved_against_lower_endpoints=resolved_win,
                   incremental_credit=fixture['stratum'] == 'core' and resolved_win,
                   direct_old_method_already_certifies=direct_hi <= tau,
                   failure_reasons=errors,
                   deterministic_work={"block_dimension": n * m, "gram_bisections": steps,
                                       "boundary_sample_evaluations": 8 * (grid + 1) if k else 0})
        rows.append(row)
    failures = sum(bool(row['failure_reasons']) for row in rows)
    wins = sum(row['incremental_credit'] for row in rows)
    return rows, {"fixtures": len(rows), "structural_or_norm_failures": failures,
                  "core_strong_old_budget_decision_wins": wins,
                  "unresolved_grid_or_rounding_decision_wins": sum(row['core_budget_decision_win'] and not row['incremental_credit'] for row in rows),
                  "old_scope_controls_incremental_credit": sum(row['incremental_credit'] for row in rows if row['stratum'] != 'core'),
                  "direct_old_certifies": sum(row['direct_old_method_already_certifies'] for row in rows),
                  "new_certificate_passes": sum(row['budget_passes'].get('new_complete_ellipse', False) for row in rows),
                  "meets_prediction": len(rows) == spec['success']['fixtures'] and failures == 0
                  and wins >= spec['success']['core_strong_old_budget_decision_wins_minimum'],
                  "interpretation": "Finite synthetic certificate-budget comparison only. Stronger historical special scopes and exact direct alternatives retained;no theorem proof,no claim of exhaustive older certificates,no practical solver speed or real workload demonstrated."}
