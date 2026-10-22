"""Small-instance SCS oracles and the family-128 occurrence-count lower bound.

The occurrence rules translate the pinned manuscript's Section 2. This does
NOT implement its complete 2-approximation connection algorithm.
"""

from __future__ import annotations

from collections import defaultdict
from itertools import permutations


def reduce_strings(strings: list[str]) -> list[str]:
    unique = sorted(set(strings) - {""})
    return [s for s in unique if not any(s != t and s in t for t in unique)]


def overlap(a: str, b: str) -> int:
    return next((k for k in range(min(len(a), len(b)), 0, -1) if a[-k:] == b[:k]), 0)


def merge_order(strings: tuple[str, ...] | list[str]) -> str:
    result = ""
    for item in strings:
        if item not in result:
            result += item[overlap(result, item):]
    return result


def exact_scs(strings: list[str]) -> str:
    """Independent permutation oracle; bounded to eight irredundant strings."""
    strings = reduce_strings(strings)
    if len(strings) > 8:
        raise ValueError("Exhaustive oracle is limited to eight strings")
    return min((merge_order(p) for p in permutations(strings)), key=lambda x: (len(x), x), default="")


def greedy_scs(strings: list[str]) -> str:
    strings = reduce_strings(strings)
    while len(strings) > 1:
        _, _, _, i, j = min((-overlap(a, b), a, b, i, j)
                            for i, a in enumerate(strings)
                            for j, b in enumerate(strings) if i != j)
        a, b = strings[i], strings[j]
        merged = a + b[overlap(a, b):]
        strings = sorted([s for k, s in enumerate(strings) if k not in {i, j}] + [merged])
    return strings[0] if strings else ""


def forced_counts(strings: list[str], *, periodic: bool = True) -> dict[str, int]:
    required = set(reduce_strings(strings))
    vertices = sorted({s[i:j] for s in required for i in range(len(s))
                       for j in range(i + 1, len(s) + 1)}, key=lambda s: (-len(s), s))
    alphabet = sorted(set("".join(required)))
    counts: dict[str, int] = {}
    rules: dict[str, list[tuple[str, str, int]]] = defaultdict(list)
    if periodic:
        for v in vertices:
            for p in range(1, len(v)):
                template = v[:p]
                if any(c != template[i % p] for i, c in enumerate(v)):
                    continue
                for k in range(1, (len(v) - 1) // p + 1):
                    rules[v[:-k*p]].append((v, template, k))

    def blocking(s: str, template: str) -> int:
        total = 0
        p = len(template)
        for r, count in counts.items():
            if not count or len(r) < len(s) + 2:
                continue
            for j in range(1, len(r) - len(s)):
                if r[j:j+len(s)] != s:
                    continue
                if (all(r[h] == template[(h-j) % p] for h in range(1, len(r)-1))
                        and r[0] != template[-j % p]
                        and r[-1] != template[(len(r)-1-j) % p]):
                    total += count
        return total

    for s in vertices:
        bounds = [int(s in required), sum(counts.get(c+s, 0) for c in alphabet),
                  sum(counts.get(s+c, 0) for c in alphabet)]
        for v, template, k in rules[s]:
            if counts[v] > blocking(v, template):
                bounds.append(blocking(s, template) + k + 1)
        counts[s] = max(bounds)
    return counts


def lower_bound(strings: list[str], *, periodic: bool = True) -> int:
    return sum(value for word, value in forced_counts(strings, periodic=periodic).items() if len(word) == 1)
