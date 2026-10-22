"""Exact small-group metadata QA, not a computation of chromatic homology.

All six fixtures are synthetic and preregistered. Two subgroup inventories
and two quotient/chain organizations preserve embedded element sets. The old
elementary-quotient bound is never relabeled an exact general spectral loss.
"""

from __future__ import annotations

from itertools import combinations, product


NAMES = ('C4', 'C2xC2', 'C4xC2', 'C2xC2xC2', 'D8', 'UT3F3')


def fixture(name: str) -> dict:
    if name == 'C4':
        labels = [(a,) for a in range(4)]
        multiply = lambda x, y: ((x[0] + y[0]) % 4,)
        prime = 2
    elif name in {'C2xC2', 'C2xC2xC2'}:
        labels = list(product(range(2), repeat=2 if name == 'C2xC2' else 3))
        multiply = lambda x, y: tuple((a + b) % 2 for a, b in zip(x, y))
        prime = 2
    elif name == 'C4xC2':
        labels = list(product(range(4), range(2)))
        multiply = lambda x, y: ((x[0] + y[0]) % 4, (x[1] + y[1]) % 2)
        prime = 2
    elif name == 'D8':
        labels = list(product(range(4), range(2)))
        multiply = lambda x, y: ((x[0] + (-1) ** x[1] * y[0]) % 4,
                                 (x[1] + y[1]) % 2)
        prime = 2
    elif name == 'UT3F3':
        labels = list(product(range(3), repeat=3))
        multiply = lambda x, y: ((x[0] + y[0]) % 3, (x[1] + y[1]) % 3,
                                 (x[2] + y[2] + x[0] * y[1]) % 3)
        prime = 3
    else:
        raise ValueError('Unregistered group fixture: ' + name)
    lookup = {x: i for i, x in enumerate(labels)}
    return {'name': name, 'prime': prime, 'labels': labels,
            'table': [[lookup[multiply(x, y)] for y in labels] for x in labels]}


def prime_log(value: int, prime: int) -> int:
    power = 0
    while value > 1 and value % prime == 0:
        value //= prime
        power += 1
    if value != 1:
        raise ValueError('Expected a prime power')
    return power


def validate_table(table: list[list[int]]) -> tuple[int, list[int]]:
    n = len(table)
    if not n or any(len(row) != n or any(x not in range(n) for x in row) for row in table):
        raise ValueError('Invalid multiplication table')
    units = [e for e in range(n) if all(table[e][x] == table[x][e] == x for x in range(n))]
    if len(units) != 1:
        raise ValueError('Missing unique identity')
    e = units[0]
    if any(table[table[a][b]][c] != table[a][table[b][c]]
           for a, b, c in product(range(n), repeat=3)):
        raise ValueError('Nonassociative table')
    inverses = []
    for a in range(n):
        candidates = [b for b in range(n) if table[a][b] == table[b][a] == e]
        if len(candidates) != 1:
            raise ValueError('Missing unique inverse')
        inverses.append(candidates[0])
    return e, inverses


def closure(table: list[list[int]], identity: int, generators) -> frozenset[int]:
    """Organization A: saturate all pair products, not a generator orbit."""
    current = {identity, *generators}
    while True:
        larger = current | {table[a][b] for a in current for b in current}
        if larger == current:
            return frozenset(current)
        current = larger


def orbit_closure(table: list[list[int]], identity: int, generators) -> frozenset[int]:
    """Organization B: right generator actions; finite monoid equals group."""
    seen, queue = {identity}, [identity]
    for x in queue:
        for g in generators:
            y = table[x][g]
            if y not in seen:
                seen.add(y)
                queue.append(y)
    return frozenset(seen)


def subgroup_key(subgroup):
    return len(subgroup), tuple(sorted(subgroup))


def inventory_adjoin(table, identity):
    start = frozenset({identity})
    seen, queue = {start}, [start]
    for h in queue:
        for a in range(len(table)):
            if a not in h:
                k = closure(table, identity, h | {a})
                if k not in seen:
                    seen.add(k)
                    queue.append(k)
    return sorted(seen, key=subgroup_key)


def inventory_generators(table, identity, prime):
    # Each strict adjoin multiplies subgroup order by at least p, so at most
    # log_p(|G|) generators suffice for every subgroup, not only G itself.
    seen = set()
    for size in range(prime_log(len(table), prime) + 1):
        for generators in combinations(range(len(table)), size):
            seen.add(orbit_closure(table, identity, generators))
    return sorted(seen, key=subgroup_key)


def normal(table, inverse, lower, upper):
    return lower <= upper and all(table[table[x][h]][inverse[x]] in lower
                                  for x in upper for h in lower)


def cyclic_extension(table, identity, inverse, lower, upper):
    if not lower < upper or not normal(table, inverse, lower, upper):
        return False
    return any(closure(table, identity, lower | {a}) == upper for a in upper)


def coset_cyclic(table, identity, lower, upper):
    """Independent explicit quotient test, including normality and partition."""
    if not lower < upper:
        return False
    left = {frozenset(table[a][h] for h in lower) for a in upper}
    right = {frozenset(table[h][a] for h in lower) for a in upper}
    if left != right:
        return False
    if len(left) * len(lower) != len(upper) or set().union(*left) != set(upper):
        raise ArithmeticError('Cosets failed to partition the upper group')
    for a in upper:
        power, visited = identity, set()
        for _ in range(len(left)):
            visited.add(frozenset(table[power][h] for h in lower))
            power = table[power][a]
        if visited == left:
            return True
    return False


def shortest_chains(table, identity, inverse, subgroups):
    whole = frozenset(range(len(table)))
    paths = {whole: [whole]}
    edges = []
    for h in sorted(subgroups, key=subgroup_key, reverse=True):
        if h == whole:
            continue
        candidates = []
        for k in subgroups:
            if cyclic_extension(table, identity, inverse, h, k):
                edges.append((h, k))
                candidates.append([h] + paths[k])
        if not candidates:
            raise ArithmeticError('No normal-cyclic chain in a finite p-group')
        paths[h] = min(candidates, key=lambda chain: (len(chain), [subgroup_key(s) for s in chain]))
    return paths, edges


def exhaustive_chain_oracle(table, identity, subgroups):
    whole = frozenset(range(len(table)))
    # Compute this edge set with explicit cosets, not with A's generator test.
    following = {h: [k for k in subgroups if coset_cyclic(table, identity, h, k)]
                 for h in subgroups}

    def all_lengths(h):
        if h == whole:
            return [0]
        return [1 + length for k in following[h] for length in all_lengths(k)]

    answer = {}
    for h in subgroups:
        lengths = all_lengths(h)
        if not lengths:
            raise ArithmeticError('Exhaustive coset oracle found no chain')
        answer[h] = (min(lengths), len(lengths))
    return answer, following


def elementary_quotient_rank(table, identity, inverse, prime, subgroup):
    generators = set(subgroup)
    for a in range(len(table)):
        power = identity
        for _ in range(prime):
            power = table[power][a]
        generators.add(power)
        for b in range(len(table)):
            generators.add(table[table[table[a][b]][inverse[a]]][inverse[b]])
    kernel = closure(table, identity, generators)
    while True:
        conjugates = {table[table[g][a]][inverse[g]] for a in kernel for g in range(len(table))}
        larger = closure(table, identity, kernel | conjugates)
        if larger == kernel:
            return prime_log(len(table) // len(kernel), prime)
        kernel = larger


def relabel(table):
    n = len(table)
    permutation = list(reversed(range(n)))
    # This permutation is its own inverse and moves the old identity.
    changed = [[permutation[table[permutation[i]][permutation[j]]]
                for j in range(n)] for i in range(n)]
    return changed, permutation


def experiment(spec: dict) -> tuple[list[dict], dict]:
    if tuple(g['name'] for g in spec['input']['groups']) != NAMES:
        raise ValueError('Only the exact six preregistered group fixtures are implemented')
    rows, all_records = [], []
    totals = {'subgroup_inventory_disagreements': 0, 'chain_oracle_disagreements': 0,
              'invalid_witnesses': 0, 'relabeling_disagreements': 0,
              'index_surrogate_mismatches': 0, 'old_lower_bound_strict_cases': 0}
    controls = {}
    for definition in spec['input']['groups']:
        group = fixture(definition['name'])
        if definition['prime'] != group['prime']:
            raise ValueError('Fixture prime mismatch')
        table, prime = group['table'], group['prime']
        identity, inverse = validate_table(table)
        prime_log(len(table), prime)
        first = inventory_adjoin(table, identity)
        second = inventory_generators(table, identity, prime)
        totals['subgroup_inventory_disagreements'] += len(set(first) ^ set(second))
        paths, edges = shortest_chains(table, identity, inverse, first)
        oracle, following = exhaustive_chain_oracle(table, identity, second)
        changed, permutation = relabel(table)
        new_identity, new_inverse = validate_table(changed)
        new_subgroups = inventory_adjoin(changed, new_identity)
        new_paths, _ = shortest_chains(changed, new_identity, new_inverse, new_subgroups)
        records = []
        for h in first:
            path = paths[h]
            ell = len(path) - 1
            other, count = oracle.get(h, (-1, 0))
            mapped = frozenset(permutation[a] for a in h)
            relabeled = len(new_paths.get(mapped, [])) - 1
            valid = (path[0] == h and path[-1] == frozenset(range(len(table)))
                     and all(k in following.get(j, []) for j, k in zip(path, path[1:])))
            lower = elementary_quotient_rank(table, identity, inverse, prime, h)
            index = prime_log(len(table) // len(h), prime)
            record = {'group': group['name'], 'subgroup': sorted(h), 'ell': ell,
                      'exhaustive_ell': other, 'valid_strict_chain_count': count,
                      'chain_witness': [sorted(s) for s in path], 'witness_valid': valid,
                      'old_elementary_quotient_lower_bound': lower, 'log_index_surrogate': index,
                      'relabelled_ell': relabeled, 'old_bounds_consistent': lower <= ell <= index}
            totals['chain_oracle_disagreements'] += ell != other
            totals['invalid_witnesses'] += not valid
            totals['relabeling_disagreements'] += ell != relabeled
            totals['index_surrogate_mismatches'] += ell != index
            totals['old_lower_bound_strict_cases'] += lower < ell
            records.append(record)
            if group['name'] == 'C4' and h == frozenset({identity}):
                controls['C4_trivial_subgroup_ell'] = ell
            if group['name'] == 'C4xC2':
                labels = {group['labels'][a] for a in h}
                if labels == {(0, 0), (2, 0)}:
                    controls['C4xC2_H1_ell'] = ell
                if labels == {(0, 0), (0, 1)}:
                    controls['C4xC2_H2_ell'] = ell
            if group['name'] == 'D8' and {group['labels'][a] for a in h} == {(0, 0), (0, 1)}:
                controls['D8_reflection_ell'] = ell
                controls['D8_reflection_elementary_quotient_rank'] = lower
        rows.append({**group, 'identity': identity, 'inverses': inverse,
                     'subgroups': len(first), 'independent_inventory_count': len(second),
                     'normal_cyclic_edges': len(edges), 'records': records,
                     'element_relabeling': permutation, 'new_identity': new_identity})
        all_records.extend(records)
    success = spec['success']
    summary = {'groups': len(rows), 'instances': len(all_records),
               'subgroups_per_group': {row['name']: row['subgroups'] for row in rows},
               'normal_cyclic_edges': sum(row['normal_cyclic_edges'] for row in rows),
               **totals, **controls,
               'old_bounds_inconsistencies': sum(not row['old_bounds_consistent'] for row in all_records),
               'same_cyclic_order_two_embedding_distinguished':
                   controls.get('C4xC2_H1_ell') != controls.get('C4xC2_H2_ell'),
               'arithmetic': 'exact integer multiplication tables, embedded sets and quotient tests',
               'interpretation': 'Known-control metadata QA; no spectral sharpness validation or incremental new-theorem gain'}
    exact_keys = [k for k in success if k != 'index_surrogate_mismatches_minimum']
    summary['meets_prediction'] = (
        all(summary.get(key) == success[key] for key in exact_keys)
        and totals['index_surrogate_mismatches'] >= success['index_surrogate_mismatches_minimum']
        and summary['same_cyclic_order_two_embedding_distinguished']
        and summary['old_bounds_inconsistencies'] == 0)
    return rows, summary
