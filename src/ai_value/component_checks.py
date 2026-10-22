"""Low-cost checks of extracted source components, excluded from application counts."""

from fractions import Fraction as F
import random

from .transport import cell_mass_moments, face_differentials


def moments(spec):
    rng = random.Random(spec['input']['seed'])
    directions = [(1,0,0),(0,1,0),(0,0,1),(1,1,1)]
    while len(directions) < 12:
        q = tuple(rng.randint(-2,2) for _ in range(3))
        if len(set(q)) > 1:
            directions.append(q)
    rows = []
    threshold = F(spec['success']['derivative_absolute_error_max'])
    for k in range(spec['input']['k_min'],spec['input']['k_max']+1):
        epsilon = F(1,2**k)
        fixtures = [
            ('strip',[(F(-1),F(0)),(F(1),F(0)),(F(0),epsilon/2)],[F(0),F(0),epsilon]),
            ('corner',[(F(0),F(0)),(F(-1),F(0)),(F(1),F(1))],[F(0),F(0),-2+epsilon])]
        for stratum,slopes,intercepts in fixtures:
            for direction in directions:
                masses,_,dm,db,weights = face_differentials(slopes,intercepts,direction)
                h = epsilon**3/1024
                plus_m,plus_b,_ = cell_mass_moments(slopes,[c+h*q for c,q in zip(intercepts,direction,strict=True)])
                minus_m,minus_b,_ = cell_mass_moments(slopes,[c-h*q for c,q in zip(intercepts,direction,strict=True)])
                fd_m = [(p-m)/(2*h) for p,m in zip(plus_m,minus_m,strict=True)]
                fd_b = [[(p-m)/(2*h) for p,m in zip(pr,mr,strict=True)] for pr,mr in zip(plus_b,minus_b,strict=True)]
                error = max([abs(a-b) for a,b in zip(dm,fd_m,strict=True)]
                            + [abs(a-b) for ar,br in zip(db,fd_b,strict=True) for a,b in zip(ar,br,strict=True)])
                lhs = sum(sum(x*x for x in derivative)/mass for mass,derivative in zip(masses,db,strict=True))
                rhs_without_constant = 2*sum(x*x/mass for mass,x in zip(masses,dm,strict=True))
                ratio = lhs/rhs_without_constant if rhs_without_constant else F(0)
                a = sum(weights[1]);c = sum(weights[2]);b = -weights[1][2]
                determinant = a*c-b*b
                if determinant <= 0:
                    raise ValueError('Pinned Jacobian should be positive definite')
                proxy = (a+c)**2/determinant
                rows.append({'k':k,'stratum':stratum,'epsilon':str(epsilon),'direction':direction,
                             'minimum_mass':str(min(masses)), 'masses':list(map(str,masses)),
                             'mass_derivative':list(map(str,dm)),
                             'moment_derivative':[[str(x) for x in row] for row in db],
                             'weighted_ratio':str(ratio), 'condition_proxy':str(proxy),
                             'derivative_max_absolute_error':str(error),
                             'derivative_check_passes':error<=threshold,
                             'weighted_bound_passes':lhs<=spec['success']['weighted_ratio_bound']*rhs_without_constant,
                             'gauge_shift_violation':len(set(direction))==1 and (any(dm) or any(any(row) for row in db))})
    corner = [r for r in rows if r['stratum']=='corner']
    growth = F(corner[-1]['condition_proxy'])/F(corner[0]['condition_proxy'])
    failed = sum(not r['derivative_check_passes'] or not r['weighted_bound_passes'] or r['gauge_shift_violation'] for r in rows)
    return rows, {'component_check_only':True,'application_hypotheses_added':0,
                  'instances':len(rows),'configurations':len(rows)//len(directions),
                  'check_failures':failed,'maximum_weighted_ratio':str(max(F(r['weighted_ratio']) for r in rows)),
                  'maximum_derivative_error':str(max(F(r['derivative_max_absolute_error']) for r in rows)),
                  'corner_condition_proxy_growth':str(growth),
                  'minimum_mass':str(min(F(r['minimum_mass']) for r in rows)),
                  'meets_prediction':failed==0 and growth>=spec['success']['corner_condition_proxy_growth_min'],
                  'interpretation':'finite exact component evidence; ill-conditioned mass Jacobian is not a Newton speed claim, and this check is not another application card'}
