"""Exact low-number physical reference checks; NumPy remains optional."""
import unittest
from fractions import Fraction as Q
from ai_value.bosonic_regression import (basis, parse_components, exact_channel,
                                         state_matrix, entanglement_minor,
                                         correlated_admission_control, weight,
                                         floors, I, inverse_g, g)


def pure(k):
    return parse_components([{'weight': '1', 'unnormalized_creation_coefficients': {k: '1'}}], len(k.split(',')))


class BosonicReferenceTests(unittest.TestCase):
    def test_binomial_single_photon_loss_and_two_photon_bunching(self):
        t, r = Q(3, 5), Q(4, 5)
        q, states, energy = exact_channel(pure('1'), pure('0'), 1, t, r)
        probabilities = {k[0]: q[i][i]*weight(k) for i, k in enumerate(states)}
        self.assertEqual(probabilities, {0: r*r, 1: t*t, 2: 0, 3: 0, 4: 0})
        q, states, _ = exact_channel(pure('1'), pure('1'), 1, t, r)
        probabilities = {k[0]: q[i][i]*weight(k) for i, k in enumerate(states)}
        self.assertEqual(probabilities[0], 2*t*t*r*r)
        self.assertEqual(probabilities[1], (t*t-r*r)**2)
        self.assertEqual(probabilities[2], 2*t*t*r*r)
        self.assertEqual(energy['input_total_energy'], '1')

    def test_creation_basis_factorials_and_invalid_input(self):
        self.assertEqual(len(basis(4, 4)), 70)
        self.assertEqual(len(basis(2, 4)), 15)
        q = state_matrix(pure('2'), basis(1, 2))
        self.assertEqual(q[2][2], Q(1, 2))
        with self.assertRaises(ValueError):
            pure('3')
        with self.assertRaises(ValueError):
            parse_components([{'weight': '1/2', 'unnormalized_creation_coefficients': {'0': '1'}}], 1)

    def test_npt_internal_modes_and_correlated_port_exclusion(self):
        component = parse_components([{'weight': '1', 'unnormalized_creation_coefficients': {'1,0': '1', '0,1': '1'}}], 2)
        port = basis(2, 2)
        witness = entanglement_minor(state_matrix(component, port), port)
        self.assertLess(Q(witness['negative_partial_transpose_minor']), 0)
        self.assertFalse(correlated_admission_control()['product_of_marginals_equal'])
        self.assertFalse(correlated_admission_control()['entropy_inequality_eligible'])

    def test_inverse_entropy_brackets_and_old_sharp_control(self):
        value = g(I(1))
        self.assertTrue(inverse_g(value).contains(1))
        new, old, _ = floors(I(0), I(0), 2, Q(9, 25), True)
        self.assertTrue(new.overlaps(old))
        endpoint, _, _ = floors(I('0.3'), I('0.7'), 2, Q(0), False)
        self.assertEqual(endpoint.data(), I('0.7').data())
