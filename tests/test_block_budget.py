import unittest
from fractions import Fraction as Q

from ai_value.block_budget import (
    block_norm_interval, evaluate_twice, positive_definite,
    small_norm_interval, sqrt_interval,
)


class BlockBudgetTests(unittest.TestCase):
    def test_outward_roots_and_invalid_input(self):
        for x in [Q(0), Q(1), Q(2), Q(1, 3), Q(81, 49), Q(10 ** 24 + 1, 7)]:
            lo, hi = sqrt_interval(x, 48)
            self.assertLessEqual(lo * lo, x)
            self.assertGreaterEqual(hi * hi, x)
            self.assertLessEqual(hi - lo, Q(1, 1 << 48))
        with self.assertRaises(ValueError):
            sqrt_interval(-1)

    def test_independent_gram_and_analytic_singular_norms(self):
        fixtures = [
            [[Q(0), Q(2)], [Q(0), Q(0)]],
            [[Q(1), Q(1)], [Q(1), Q(1)]],
            [[Q(1), Q(2)], [Q(3), Q(4)]],
            [[Q(3), Q(0)], [Q(0), Q(4)]],
        ]
        for a in fixtures:
            analytic = small_norm_interval([[(v, Q(0)) for v in row] for row in a])
            gram = block_norm_interval(a)
            self.assertLessEqual(analytic[0], gram[1])
            self.assertLessEqual(gram[0], analytic[1])
        self.assertEqual(small_norm_interval([[(Q(0), Q(1)), (Q(0), Q(0))],
                                             [(Q(0), Q(0)), (Q(1), Q(0))]]), (Q(1), Q(1)))
        self.assertFalse(positive_definite([[Q(1), Q(1)], [Q(1), Q(1)]]))
        self.assertFalse(positive_definite([[Q(1), Q(2)], [Q(2), Q(1)]]))
        self.assertTrue(positive_definite([[Q(2), Q(1)], [Q(1), Q(2)]]))

    def test_base_first_evaluation_preserves_noncommuting_coefficients(self):
        a = [[Q(0), Q(1)], [Q(0), Q(0)]]
        coefficients = [[[Q(1), Q(0)], [Q(0), Q(2)]],
                        [[Q(0), Q(3)], [Q(4), Q(0)]],
                        [[Q(5), Q(0)], [Q(0), Q(6)]]]
        first, second = evaluate_twice(a, coefficients)
        self.assertEqual(first, second)
        self.assertEqual(first, [[1, 0, 0, 3], [0, 2, 4, 0],
                                 [0, 0, 1, 0], [0, 0, 0, 2]])


if __name__ == '__main__':
    unittest.main()
