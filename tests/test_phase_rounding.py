import unittest
from fractions import Fraction as Q

from ai_value.phase_rounding import (
    circle_certificate, dyadic_round, eligible_word_oracle, inputs,
    optimizer_matrix, rational_circle_points,
)


class PhaseRoundingTests(unittest.TestCase):
    def test_circle_cover_and_exact_known_norms(self):
        for _, _, u, v, d in rational_circle_points(7):
            self.assertEqual(u*u+v*v, d*d)
        # The whole-circle maximum of 1-z is 2, although its value at 1 is 0.
        cert = circle_certificate([(Q(1), Q(0)), (Q(1), Q(0))],
                                  [Q(0), Q(0)], (1, -1), 7, 48, independent=True)
        self.assertEqual(Q(cert['lower']), 2)
        self.assertGreaterEqual(Q(cert['upper']), 2)
        self.assertEqual(cert['identity_mismatches'], 0)
        self.assertEqual(Q(cert['mesh_correction']), Q(1, 7))
        zero = circle_certificate([(Q(0), Q(1))], [Q(1)], (1,), 3, 48, independent=True)
        self.assertEqual(Q(zero['upper']), 0)

    def test_independent_complex_oracle_and_mass_invariant(self):
        phases = [(Q(4, 5), Q(3, 5)), (Q(0), Q(1)), (Q(-1), Q(0))]
        radii = [Q(1, 3), Q(2, 3), Q(1, 5)]
        word, trace = dyadic_round(optimizer_matrix(phases, 20), radii, 1024)
        self.assertFalse(trace['failure_reasons'])
        self.assertLessEqual(sum((Q(1-s, 2) for s in word)), Q(trace['mu']))
        oracle, optimum = eligible_word_oracle(phases, radii, 5, 48)
        self.assertEqual(len(oracle), 8)
        for item in oracle:
            checked = circle_certificate(phases, radii, item['word'], 5, 48, independent=True)
            self.assertEqual(checked['identity_mismatches'], 0)
            self.assertTrue(checked['parseval_consistent'])
            for key, value in item.items():
                self.assertEqual(checked[key], value)
        self.assertLessEqual(Q(optimum[0]), Q(optimum[1]))

    def test_reject_invalid_domain_and_phase_convention(self):
        for fixture in [
            {'phases': [['1', '1']], 'magnitudes': ['1/2']},
            {'phases': [['1', '0']], 'magnitudes': ['2']},
            {'phases': [['0', '1']], 'magnitudes': ['0']},
        ]:
            with self.assertRaises(ValueError):
                inputs(fixture)


if __name__ == '__main__':
    unittest.main()
