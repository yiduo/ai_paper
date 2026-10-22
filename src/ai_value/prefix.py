"""Offline finite oracles; no efficient or online Steinitz claim is made."""

from __future__ import annotations

from itertools import product
from math import sqrt


def peak_squared(vectors: list[list[int]], order: list[int] | None = None,
                 signs: tuple[int, ...] | None = None) -> int:
    if not vectors:
        return 0
    total = [0] * len(vectors[0])
    peak = 0
    for position, index in enumerate(order if order is not None else range(len(vectors))):
        sign = signs[position] if signs else 1
        total = [a + sign*b for a, b in zip(total, vectors[index], strict=True)]
        peak = max(peak, sum(x*x for x in total))
    return peak


def optimal_signs(vectors: list[list[int]]) -> tuple[int, ...]:
    if len(vectors) > 16:
        raise ValueError("Finite signing oracle limited to sixteen vectors")
    return min(product((-1, 1), repeat=len(vectors)),
               key=lambda signs: (peak_squared(vectors, signs=signs), signs))


def transfer_order(vectors: list[list[int]]) -> list[int]:
    if vectors and any(sum(row[j] for row in vectors) for j in range(len(vectors[0]))):
        raise ValueError("Positive-forward negative-reverse transfer requires zero total")
    signs = optimal_signs(vectors)
    return ([i for i, s in enumerate(signs) if s == 1]
            + [i for i, s in reversed(list(enumerate(signs))) if s == -1])


def greedy_order(vectors: list[list[int]]) -> list[int]:
    order, remaining = [], set(range(len(vectors)))
    current = [0] * len(vectors[0]) if vectors else []
    while remaining:
        index = min(remaining, key=lambda i: (sum((a+b)**2 for a, b in zip(current, vectors[i], strict=True)), i))
        order.append(index)
        current = [a+b for a, b in zip(current, vectors[index], strict=True)]
        remaining.remove(index)
    return order


def exact_order(vectors: list[list[int]]) -> tuple[list[int], int]:
    """Subset dynamic programming for the minimax-prefix permutation oracle."""
    n = len(vectors)
    if n > 16:
        raise ValueError("Subset oracle limited to sixteen vectors")
    if not n:
        return [], 0
    totals = [[0]*len(vectors[0]) for _ in range(1 << n)]
    costs, parents = [0]*(1 << n), [0]*(1 << n)
    for mask in range(1, 1 << n):
        bit = mask & -mask
        index = bit.bit_length()-1
        totals[mask] = [a+b for a, b in zip(totals[mask ^ bit], vectors[index], strict=True)]
        norm = sum(x*x for x in totals[mask])
        costs[mask], parents[mask] = min((max(costs[mask ^ (1 << i)], norm), i)
                                        for i in range(n) if mask & (1 << i))
    order, mask = [], (1 << n)-1
    while mask:
        index = parents[mask]
        order.append(index)
        mask ^= 1 << index
    return order[::-1], costs[-1]


def normalized_peak(vectors: list[list[int]], order: list[int]) -> float:
    scale = max((sqrt(sum(x*x for x in row)) for row in vectors), default=1) or 1
    return sqrt(peak_squared(vectors, order)) / scale
