from fractions import Fraction as Q
import unittest

from ai_value import graph_smoothing as fast
from ai_value import graph_smoothing_reference as judge


class GraphSmoothingTests(unittest.TestCase):
    def test_known_ambient_median_does_not_preserve_simplex(self):
        pi = [Q(1, 9), Q(4, 9), Q(4, 9)]
        a = [list(pi) for _ in pi]
        fast.validate_chain(a, pi)
        x = [[Q(i == j) for j in range(3)] for i in range(3)]
        g = fast.resolvent(a, Q(3))
        self.assertEqual(g[0], [Q(1, 3)]*3)
        y = fast.expected_median(x, g)
        self.assertEqual(y, judge.endpoint_median(x, g))
        self.assertEqual(y[0], [Q(7, 27)]*3)
        self.assertEqual(sum(y[0]), Q(7, 9))
        self.assertFalse(judge.energy(x, y, a, pi, 3)['violation'])

    def test_scalar_quadratic_reference_has_correct_factor_two(self):
        a = [[Q(1, 2)]*2 for _ in range(2)]
        x = [[Q(0)], [Q(1)]]
        y = fast.linear(x, fast.resolvent(a, Q(2)))
        self.assertEqual(y, [[Q(1, 3)], [Q(2, 3)]])
        self.assertTrue(judge.quadratic_residual(x, y, a, Q(1)))
        self.assertFalse(judge.quadratic_residual(x, y, a, Q(1, 2)))
        self.assertEqual(judge.energy(x, y, a, [Q(1, 2)]*2, 1)['left'], Q(1, 6))

    def test_weighted_median_ties_and_absolute_objective(self):
        x = [[Q(-3), Q(2)], [Q(7), Q(-1)], [Q(100), Q(4)]]
        g = [[Q(1, 2), Q(1, 4), Q(1, 4)],
             [Q(1, 4), Q(1, 2), Q(1, 4)],
             [Q(1, 4), Q(1, 4), Q(1, 2)]]
        y = fast.weighted_median(x, g)
        self.assertTrue(judge.weighted_absolute_minimum(x, g, y))
        self.assertEqual(y[0][0], Q(-3))
        self.assertEqual(y[2][0], Q(7))
        y[0][0] = Q(100)
        self.assertFalse(judge.weighted_absolute_minimum(x, g, y))

    def test_nonstationary_and_invalid_chain_inputs_rejected(self):
        a = [[Q(1), Q(0)], [Q(1, 2), Q(1, 2)]]
        with self.assertRaisesRegex(ValueError, 'Nonstationary'):
            fast.validate_chain(a, [Q(1, 2)]*2)
        fast.validate_chain(a, [Q(1), Q(0)])
        with self.assertRaises(ValueError):
            fast.validate_chain([[Q(-1), Q(2)], [Q(0), Q(1)]], [Q(1, 2)]*2)

    def test_exact_risk_thresholds_and_zero_reference(self):
        self.assertTrue(fast.outcome(Q(9), Q(10))['win'])
        self.assertFalse(fast.outcome(Q(901, 100), Q(10))['win'])
        self.assertFalse(fast.outcome(Q(21, 2), Q(10))['harmed'])
        self.assertTrue(fast.outcome(Q(1051, 100), Q(10))['harmed'])
        self.assertEqual(fast.outcome(Q(0), Q(0)),
                         dict(win=False, harmed=False, relative_reduction=None))
        self.assertTrue(fast.outcome(Q(1), Q(0))['harmed'])


if __name__ == '__main__':
    unittest.main()
