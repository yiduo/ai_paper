import itertools
import unittest

from ai_value.cyclic_chain import (closure, coset_cyclic, cyclic_extension,
    exhaustive_chain_oracle, fixture, inventory_adjoin, inventory_generators,
    relabel, shortest_chains, validate_table)


class CyclicChainTests(unittest.TestCase):
    def test_inventory_against_literal_subsets_and_moved_identity(self):
        table = fixture('C4')['table']
        e, inverse = validate_table(table)
        literal = set()
        for mask in range(1 << len(table)):
            subset = frozenset(i for i in range(len(table)) if mask & (1 << i))
            if e in subset and all(table[a][b] in subset for a in subset for b in subset):
                literal.add(subset)
        self.assertEqual(set(inventory_adjoin(table, e)), literal)
        self.assertEqual(set(inventory_generators(table, e, 2)), literal)
        changed, permutation = relabel(table)
        unit, inv = validate_table(changed)
        self.assertNotEqual(unit, e)
        old, _ = shortest_chains(table, e, inverse, list(literal))
        new, _ = shortest_chains(changed, unit, inv, inventory_adjoin(changed, unit))
        for h, path in old.items():
            self.assertEqual(len(path), len(new[frozenset(permutation[a] for a in h)]))

    def test_coset_oracle_rejects_nonnormal_reflection(self):
        group = fixture('D8')
        table = group['table']
        e, inverse = validate_table(table)
        reflection = frozenset(group['labels'].index(x) for x in [(0, 0), (0, 1)])
        whole = frozenset(range(8))
        self.assertFalse(cyclic_extension(table, e, inverse, reflection, whole))
        self.assertFalse(coset_cyclic(table, e, reflection, whole))
        subgroups = inventory_adjoin(table, e)
        answer, _ = exhaustive_chain_oracle(table, e, subgroups)
        self.assertEqual(answer[reflection][0], 2)
        for h, k in itertools.product(subgroups, repeat=2):
            self.assertEqual(cyclic_extension(table, e, inverse, h, k),
                             coset_cyclic(table, e, h, k))

    def test_unitriangular_law_against_literal_matrix_product(self):
        group = fixture('UT3F3')
        def matrix(t):
            a, b, c = t
            return [[1, a, c], [0, 1, b], [0, 0, 1]]
        for i, left in enumerate(group['labels']):
            for j, right in enumerate(group['labels']):
                a, b = matrix(left), matrix(right)
                result = [[sum(a[x][z] * b[z][y] for z in range(3)) % 3
                           for y in range(3)] for x in range(3)]
                self.assertEqual(matrix(group['labels'][group['table'][i][j]]), result)
        validate_table(group['table'])

    def test_nonassociative_table_is_rejected(self):
        table = fixture('C4')['table']
        table[1][1] = 1
        with self.assertRaises(ValueError):
            validate_table(table)


if __name__ == '__main__':
    unittest.main()
