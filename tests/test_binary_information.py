"""Small analytic checks independent of the frozen experimental fixtures."""
import unittest
from decimal import Decimal
from fractions import Fraction
from ai_value import binary_information as b


class BinaryInformationTests(unittest.TestCase):
    def test_interval_arithmetic_encloses_exact_rationals_and_logs(self):
        v = b.rat('1/3')+b.rat('1/7')*b.rat('-4/5')
        exact = Fraction(1,3)-Fraction(4,35)
        self.assertLessEqual(Fraction(v.lo), exact)
        self.assertGreaterEqual(Fraction(v.hi), exact)
        self.assertTrue(b.I(2).ln().exp().contains(2))
        self.assertTrue((-b.I(2).ln()).exp().contains(Decimal('.5')))
        self.assertTrue(b.entropy(b.I(-1)).contains(0))
        self.assertTrue(b.entropy(b.I(1)).contains(0))
        self.assertTrue(b.entropy(b.I('-.2','.3')).contains(b.I(2).ln().lo))

    def test_analytic_coordinate_channel_joint_and_walsh(self):
        # g=+-1/2 and rho=1/2 gives conditional mean +-1/4 exactly.
        g = [Fraction(-1,2),Fraction(1,2)]
        tau = b.I(2).ln()
        expected = b.I(2).ln()-b.entropy(b.I('.25'))
        direct,mass = b.direct_mi(g,Fraction(0),tau)
        walsh = b.walsh_mi(g,b.walsh_coefficients(g),Fraction(0),tau)
        self.assertTrue(mass.contains(1))
        self.assertTrue(direct.overlaps(expected))
        self.assertTrue(walsh.overlaps(expected))
        self.assertLess(direct.hi-direct.lo,Decimal('1e-50'))

    def test_biased_joint_at_zero_recovers_original_information(self):
        g = [Fraction(-1,2),Fraction(1,4),Fraction(1,2),Fraction(3,4)]
        mean = Fraction(1,4)
        expected = b.entropy(b.rat(mean))-sum((b.entropy(b.rat(x))for x in g),b.I(0))/4
        direct,mass = b.direct_mi(g,mean,b.I(0))
        walsh = b.walsh_mi(g,b.walsh_coefficients(g),mean,b.I(0))
        self.assertTrue(direct.overlaps(expected))
        self.assertTrue(walsh.overlaps(expected))
        self.assertTrue(mass.contains(1))

    def test_balanced_production_matches_closed_form(self):
        h = b.entropy(b.I('.5'))
        old,new = b.profiles(Fraction(0),h)
        exact = b.I('.5')*b.I(3).ln()/2
        self.assertTrue(old.overlaps(exact))
        self.assertTrue(new.overlaps(exact))
