"""Exact finite judges for EXP332, independent of threshold-cubic evaluation.

Grouped endpoint triples use the distribution of three independent draws.
These checks certify this finite calculation, not the general source theorem.
"""
from fractions import Fraction as Q
from functools import lru_cache
from itertools import combinations_with_replacement


def multiply(a, b):
    return [[sum((a[i][k]*b[k][j] for k in range(len(b))), Q(0))
             for j in range(len(b[0]))] for i in range(len(a))]


def inverse_residual(a, g, coefficient):
    n = len(a)
    m = [[Q(i == j)+coefficient*(Q(i == j)-a[i][j])
          for j in range(n)] for i in range(n)]
    return multiply(g, m) == [[Q(i == j) for j in range(n)] for i in range(n)]


@lru_cache(maxsize=32)
def triple_weights(g):
    n = len(g)
    indices = list(combinations_with_replacement(range(n), 3))
    return tuple(tuple((j, k, l, row[j]*row[k]*row[l]*
                        (1 if j == l else 3 if j == k or k == l else 6))
                       for j, k, l in indices) for row in g)


def endpoint_median(x, g):
    weights = triple_weights(tuple(tuple(row) for row in g))
    return [[sum((w*(x[j][c]+x[k][c]+x[l][c]
                      -min(x[j][c], x[k][c], x[l][c])
                      -max(x[j][c], x[k][c], x[l][c]))
                  for j, k, l, w in row), Q(0))
             for c in range(len(x[0]))] for row in weights]


def clean_risk(clean, y, pi):
    # Flattened independent organization; no candidate distance helper.
    return sum((pi[i]*abs(y[i][c]-clean[i][c])
                for c in range(len(clean[0])) for i in range(len(clean))), Q(0))


def weighted_absolute_minimum(x, g, y):
    for i, row in enumerate(g):
        for c in range(len(x[0])):
            objective = lambda z: sum((row[j]*abs(z-x[j][c])
                                       for j in range(len(x))), Q(0))
            if objective(y[i][c]) != min(objective(v[c]) for v in x):
                return False
    return True


def quadratic_residual(x, y, a, alpha):
    for i in range(len(a)):
        for c in range(len(x[0])):
            residual = y[i][c]-x[i][c]+2*alpha*sum(
                (a[i][j]*(y[i][c]-y[j][c]) for j in range(len(a))), Q(0))
            if residual:
                return False
    return True


def energy(x, y, a, pi, t):
    n = len(a)
    distance = lambda u, v: sum((abs(z-w) for z, w in zip(u, v)), Q(0))**2
    fidelity = sum((pi[i]*distance(x[i], y[i]) for i in range(n)), Q(0))
    variation = sum((pi[i]*a[i][j]*distance(y[i], y[j])
                     for i in range(n) for j in range(n)), Q(0))
    power = [[Q(i == j) for j in range(n)] for i in range(n)]
    total = Q(0)
    for _ in range(t):
        power = multiply(power, a)
        total += sum((pi[i]*power[i][j]*distance(x[i], x[j])
                      for i in range(n) for j in range(n)), Q(0))
    cesaro = total/t
    left = fidelity+t*variation
    return dict(fidelity=fidelity, variation=variation, left=left,
                cesaro=cesaro, bound=3024*cesaro, violation=left > 3024*cesaro)
