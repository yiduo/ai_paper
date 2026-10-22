"""Frozen finite binary-summary audit; outward Decimal bounds, no external packages.

The interval claim assumes Decimal's correctly rounded ln/exp. It does not
certify the runtime or the source theorem. Complete truth tables are tiny.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal as D, Context, ROUND_FLOOR, ROUND_CEILING
from fractions import Fraction as Q
from functools import lru_cache
import math

C = Context(prec=70)
DOWN = Context(prec=70, rounding=ROUND_FLOOR)
UP = Context(prec=70, rounding=ROUND_CEILING)
BITS = 72
COUNTS: dict[str, int] = {}


def bump(key: str, count: int = 1) -> None:
    COUNTS[key] = COUNTS.get(key, 0) + count


@dataclass(frozen=True, slots=True)
class I:
    lo: D
    hi: D

    def __init__(self, lo=0, hi=None):
        object.__setattr__(self, 'lo', D(lo))
        object.__setattr__(self, 'hi', D(lo if hi is None else hi))
        if self.lo > self.hi:
            raise ArithmeticError('Reversed interval')

    @staticmethod
    def cast(x):
        return x if isinstance(x, I) else I(x)

    def __add__(self, other):
        b = I.cast(other)
        return I(DOWN.add(self.lo, b.lo), UP.add(self.hi, b.hi))

    __radd__ = __add__

    def __neg__(self):
        # Decimal unary +/- use the ambient context; copy_negate is exact.
        return I(self.hi.copy_negate(), self.lo.copy_negate())

    def __sub__(self, other):
        return self + (-I.cast(other))

    def __rsub__(self, other):
        return I.cast(other) - self

    def __mul__(self, other):
        b = I.cast(other)
        pairs = [(x, y) for x in (self.lo, self.hi) for y in (b.lo, b.hi)]
        return I(min(DOWN.multiply(x, y) for x, y in pairs),
                 max(UP.multiply(x, y) for x, y in pairs))

    __rmul__ = __mul__

    def __truediv__(self, other):
        b = I.cast(other)
        if b.lo <= 0 <= b.hi:
            raise ArithmeticError('Division across zero')
        return self * I(DOWN.divide(D(1), b.hi), UP.divide(D(1), b.lo))

    def __rtruediv__(self, other):
        return I.cast(other) / self

    def ln(self):
        if self.lo <= 0:
            raise ArithmeticError('Log domain')
        return I(C.next_minus(C.ln(self.lo)), C.next_plus(C.ln(self.hi)))

    def exp(self):
        if self.lo == self.hi == 0:
            return I(1)
        return I(C.next_minus(C.exp(self.lo)), C.next_plus(C.exp(self.hi)))

    def power(self, n: int):
        if n < 0:
            return 1 / self.power(-n)
        out = I(1)
        for _ in range(n):
            out = out * self
        return out

    def data(self):
        return [str(self.lo), str(self.hi)]

    def overlaps(self, other):
        return max(self.lo, other.lo) <= min(self.hi, other.hi)

    def contains(self, x):
        return self.lo <= D(x) <= self.hi


def rat(x) -> I:
    x = Q(x)
    return I(x.numerator) / x.denominator


def maximum(*values: I) -> I:
    return I(max(x.lo for x in values), max(x.hi for x in values))


def minimum(*values: I) -> I:
    return I(min(x.lo for x in values), min(x.hi for x in values))


def entropy(r: I) -> I:
    if r.lo < -1 or r.hi > 1:
        raise ArithmeticError('Sign-entropy domain')
    def point(t: D) -> I:
        if t in (D(-1), D(1)):
            return I(0)
        p = (1 + I(t)) / 2
        q = (1 - I(t)) / 2
        return -(p * p.ln() + q * q.ln())
    ends = [point(r.lo), point(r.hi)]
    if r.lo <= 0 <= r.hi:
        ends.append(I(2).ln())
    return I(min(x.lo for x in ends), max(x.hi for x in ends))


@lru_cache(maxsize=16384)
def inverse_entropy_point(h: D) -> I:
    if not 0 < h < I(2).ln().lo:
        raise ArithmeticError('Inverse entropy needs a strict interior target')
    lo, hi = D(0), D(1)
    for _ in range(BITS):
        mid = C.divide(C.add(lo, hi), D(2))
        v = entropy(I(mid))
        bump('entropy_root_evaluations')
        if v.lo > h:
            lo = mid
        elif v.hi < h:
            hi = mid
        else:
            bump('ambiguous_root_signs')
            break
    return I(lo, hi)


def inverse_entropy(h: I) -> I:
    return I(inverse_entropy_point(h.hi).lo, inverse_entropy_point(h.lo).hi)


def rate_from_entropy(h: I) -> I:
    r = inverse_entropy(h)
    return r * ((1 + r) / (1 - r)).ln() / 2


@lru_cache(maxsize=16384)
def old_root_point(m: D, h: D) -> I:
    lo, hi = D(0), D(1)
    for _ in range(BITS):
        mid = C.divide(C.add(lo, hi), D(2))
        v = I(m) * entropy(I(mid)) - I(h) * mid
        bump('old_root_evaluations')
        if v.lo > 0:
            lo = mid
        elif v.hi < 0:
            hi = mid
        else:
            bump('ambiguous_root_signs')
            break
    return I(lo, hi)


def profiles(m: Q, h: I) -> tuple[I, I]:
    mean = rat(m)
    hm, ell = entropy(mean), I(2).ln()
    information = hm - h
    global_rate = rate_from_entropy(ell - information)
    if m == 0:
        return global_rate, global_rate
    alpha = rat(1-m*m)
    old_s = I(old_root_point(mean.lo, h.hi).lo,
              old_root_point(mean.hi, h.lo).hi)
    old_raw = rate_from_entropy(h) - mean * ((1+old_s)/(1-old_s)).ln()/2
    old = maximum(old_raw, global_rate)
    new_rate = rate_from_entropy(h / alpha)
    # Fixtures lie in the positive S branch; do not extrapolate its formula.
    if (ell-h/alpha).lo <= 0:
        raise ArithmeticError('Frozen fixture left the positive reserve branch')
    new_a = 2*information + alpha*(new_rate - 2*(ell-h/alpha))
    new_b = 2*(hm-alpha*ell) + alpha*new_rate
    if not new_a.overlaps(new_b):
        raise ArithmeticError('Independent production identities disagree')
    return old, maximum(old, new_a, global_rate)


def integrate(m: Q, h0: I, goal: I, cells: int) -> tuple[dict, dict]:
    times = {'old_hybrid': I(0), 'combined': I(0)}
    records = []
    for j in range(cells):
        u, v = Q(j, cells)**4, Q(j+1, cells)**4
        a = (1-rat(u))*h0 + rat(u)*goal
        b = (1-rat(v))*h0 + rat(v)*goal
        width = (goal-h0)*rat(v-u)
        whole = I(a.lo, b.hi)
        bounds = profiles(m, whole)
        if width.lo <= 0 or any(x.lo <= 0 for x in bounds):
            raise ArithmeticError('Nonpositive quadrature width or production')
        row = {'cell': j, 'entropy': whole.data(), 'width': width.data()}
        for name, bound in zip(times, bounds):
            contribution = width/bound
            times[name] = times[name]+contribution
            row[name] = {'profile': bound.data(), 'integral': contribution.data()}
        records.append(row)
    return times, {'cells': records}


def fixture(case: dict, a: Q):
    n = case['n']; size = 2**n
    if case['stratum'] == 'control':
        g = [-(1-a), 1-a]
        weights = [1-a/2, a/2]
        vertices = [[-1, 1], [1, -1]]
    else:
        g = [-1+(size-1)*a]+[1-a]*(size-1)
        weights = [1-(size-1)*a/2]+[a/2]*(size-1)
        vertices = [[-1 if j == k else 1 for j in range(size)] for k in range(size)]
    mean = sum(g, Q())/size
    assert mean == Q(case['mean']) and all(-1 < x < 1 for x in g)
    assert sum(weights) == 1 and min(weights) > 0
    assert all(sum(w*row[k] for w, row in zip(weights, vertices)) == g[k] for k in range(size))
    assert all(sum(row, Q())/size == mean for row in vertices)
    return g, mean, weights


def walsh_coefficients(g):
    size = len(g)
    return [sum(((-1 if (s & x).bit_count()%2 else 1)*v for x,v in enumerate(g)), Q())/size for s in range(size)]


def walsh_mi(g, coefficients, mean: Q, tau: I) -> I:
    rho = (-tau).exp(); size = len(g)
    total = I(0)
    for y in range(size):
        u = sum((rat(c)*rho.power(s.bit_count())*(-1 if (s&y).bit_count()%2 else 1)
                 for s,c in enumerate(coefficients)), I(0))
        total = total+entropy(u)
    bump('walsh_channel_outputs', size)
    return entropy(rat(mean))-total/size


def direct_mi(g, mean: Q, tau: I) -> tuple[I, I]:
    size = len(g); n = size.bit_length()-1; rho = (-tau).exp()
    same, different = (1+rho)/2, (1-rho)/2
    result, mass = I(0), I(0)
    for y in range(size):
        for sign in (-1, 1):
            joint = I(0)
            for x,v in enumerate(g):
                kernel = I(1)
                for k in range(n):
                    kernel = kernel*(different if (x^y)&(1<<k) else same)
                joint = joint+(1+sign*rat(v))/2*kernel/size
                bump('direct_joint_terms')
            denominator = (1+sign*rat(mean))/2/size
            result = result+joint*(joint/denominator).ln()
            mass = mass+joint
    return result, mass


def decreasing_root(fn, target: I) -> I:
    lo, hi = D(0), D(1)
    if not (fn(I(lo)).lo > target.hi and fn(I(hi)).hi < target.lo):
        raise ArithmeticError('Frozen [0,1] root bracket does not straddle target')
    for _ in range(BITS):
        mid = C.divide(C.add(lo, hi), D(2)); v = fn(I(mid))
        bump('time_root_evaluations')
        if v.lo > target.hi:
            lo = mid
        elif v.hi < target.lo:
            hi = mid
        else:
            bump('ambiguous_root_signs')
            break
    return I(lo, hi)


def older_times(mean, h0, goal):
    hm, ell, alpha = entropy(rat(mean)), I(2).ln(), rat(1-mean*mean)
    initial, target = hm-h0, hm-goal
    r0, rstar = inverse_entropy(ell-initial), inverse_entropy(ell-target)
    soft = (r0/rstar).ln()
    c = hm-alpha*ell
    def kramer(t):
        rho = (-t).exp()
        return c*rho.power(2)+alpha*(ell-entropy(rho))
    return soft, decreasing_root(kramer, target)


def midpoint_check(mean: Q, h0: float, goal: float, cells: int):
    m = float(mean); ell = math.log(2)
    def h(r):
        if abs(r) == 1: return 0.0
        p, q = (1+r)/2, (1-r)/2
        return -p*math.log(p)-q*math.log(q)
    hm, alpha = h(m), 1-m*m
    def inverse(target, old=False):
        lo, hi = 0.0, 1.0
        for _ in range(72):
            mid = (lo+hi)/2
            value = m*h(mid)-target*mid if old else h(mid)-target
            if value > 0: lo = mid
            else: hi = mid
        return (lo+hi)/2
    def rate(ent):
        r = inverse(ent)
        return r*math.atanh(r)
    result = [0.0, 0.0]
    for j in range(cells):
        u = (j+0.5)/cells; e = h0+(goal-h0)*u**4
        global_rate = rate(ell-hm+e)
        if m == 0: old = new = global_rate
        else:
            s = inverse(e, True)
            old = max(global_rate, rate(e)-m*math.atanh(s))
            new = max(old, global_rate, 2*(hm-alpha*ell)+alpha*rate(e/alpha))
        jacobian = 4*(goal-h0)*u**3/cells
        result[0] += jacobian/old; result[1] += jacobian/new
    return dict(zip(('old_hybrid','combined'), result))


def evaluate(spec: dict, precision: int):
    global C, DOWN, UP, COUNTS
    C = Context(prec=precision); DOWN = Context(prec=precision, rounding=ROUND_FLOOR); UP = Context(prec=precision, rounding=ROUND_CEILING)
    inverse_entropy_point.cache_clear(); old_root_point.cache_clear(); COUNTS = {}
    rows = []; failures = []
    for case in spec['input']['fixtures']:
        g,m,weights = fixture(case, Q(spec['input']['a']))
        h0 = sum((entropy(rat(v)) for v in g), I(0))/len(g)
        goal = rat(spec['input']['conditional_entropy_goal_nats'])
        hm = entropy(rat(m)); target = hm-goal
        if not (h0.hi < goal.lo < hm.lo): raise ArithmeticError('Infeasible initial/target information')
        times, detail = integrate(m,h0,goal,64)
        soft,kramer = older_times(m,h0,goal)
        times.update(old_soft=soft, old_kramer=kramer)
        best = minimum(times['old_hybrid'], soft, kramer)
        coefficients = walsh_coefficients(g)
        oracle = decreasing_root(lambda t: walsh_mi(g,coefficients,m,t), target)
        checks = []
        for name,time in list(times.items())+[('oracle_lower',I(oracle.lo)),('oracle_upper',I(oracle.hi))]:
            tau = I(time.hi)
            direct,mass = direct_mi(g,m,tau)
            walsh = walsh_mi(g,coefficients,m,tau)
            discrepancy = max(UP.subtract(direct.hi,walsh.lo).copy_abs(), UP.subtract(walsh.hi,direct.lo).copy_abs())
            judge_ok = direct.overlaps(walsh) and discrepancy <= D('1e-45') and mass.contains(1)
            sufficient = direct.hi <= DOWN.add(target.lo,D('1e-40'))
            if name == 'oracle_lower': sufficient = direct.lo >= target.hi
            if not judge_ok or not sufficient: failures.append(case['id']+':'+name)
            checks.append(dict(name=name,tau=tau.data(),direct_MI=direct.data(),walsh_MI=walsh.data(),joint_mass=mass.data(),discrepancy_upper=str(discrepancy),independent_check_pass=judge_ok,target_direction_check=sufficient))
        float_h0 = float(C.divide(C.add(h0.lo,h0.hi),D(2)))
        midpoint = midpoint_check(m,float_h0,float(goal.lo),1024)
        midpoint_ok = all(times[k].contains(D(str(v))) for k,v in midpoint.items())
        control_ok = case['stratum'] != 'control' or (times['old_hybrid'].overlaps(times['combined']) and times['old_hybrid'].lo<=soft.lo<=soft.hi<=times['old_hybrid'].hi and times['combined'].lo<=soft.lo<=soft.hi<=times['combined'].hi)
        if not midpoint_ok or not control_ok: failures.append(case['id']+':integral-consistency')
        win = times['combined'].hi <= DOWN.multiply(D('.9'),best.lo) and best.lo>0
        chen_win = times['combined'].hi <= DOWN.multiply(D('.9'),times['old_hybrid'].lo)
        rows.append(dict(id=case['id'],stratum=case['stratum'],precision=precision,field=[str(v)for v in g],mean=str(m),mixture_weights=[str(w)for w in weights],initial_entropy=h0.data(),initial_information=(hm-h0).data(),target_information=target.data(),times={k:v.data()for k,v in times.items()},best_old=best.data(),finite_table_oracle=oracle.data(),combined_to_oracle=(times['combined']/oracle).data(),best_old_to_oracle=(best/oracle).data(),midpoint=midpoint,midpoint_inside_intervals=midpoint_ok,balanced_control=control_ok,judges=checks,resolved_10percent_win=win,chen_only_10percent_win=chen_win,**detail))
    return rows,failures,dict(COUNTS)


def run(spec: dict):
    rows70,fail70,count70 = evaluate(spec,70)
    rows100,fail100,count100 = evaluate(spec,100)
    overlaps = True
    for a,b in zip(rows70,rows100):
        for key in ['initial_entropy','initial_information','target_information','best_old','finite_table_oracle']:
            overlaps = overlaps and I(*a[key]).overlaps(I(*b[key]))
        for key in a['times']:
            overlaps = overlaps and I(*a['times'][key]).overlaps(I(*b['times'][key]))
    failures = fail70+fail100+([] if overlaps else ['precision-enclosures-disjoint'])
    wins = sum(r['resolved_10percent_win'] for r in rows70 if r['stratum']=='core')
    summary = dict(fixtures=3,precision_enclosures_overlap=overlaps,structural_or_numerical_failures=len(failures),failures=failures,core_resolved_10percent_wins=wins,core_chen_only_wins=sum(r['chen_only_10percent_win']for r in rows70 if r['stratum']=='core'),meets_prediction=not failures and wins>=1,counts={'70digits':count70,'100digits':count100},interpretation='Finite synthetic aggregate budget audit; stronger old mixture bound included. No theorem verification or hardware/DP claim. Decimal elementary-function runtime guarantees assumed; not formal proof.')
    return rows70+rows100,summary
