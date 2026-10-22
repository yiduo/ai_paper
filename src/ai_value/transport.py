"""Exact rational planar-cell integration and independent 3x3 transport LP."""

from fractions import Fraction as F
from itertools import combinations


def clip(polygon, ax, ay, bound):
    """Intersect convex polygon with ax*x+ay*y <= bound, exactly."""
    result = []
    if not polygon:
        return result
    previous = polygon[-1]
    pv = ax*previous[0]+ay*previous[1]-bound
    for current in polygon:
        cv = ax*current[0]+ay*current[1]-bound
        if (pv <= 0) != (cv <= 0):
            t = pv/(pv-cv)
            result.append(tuple(p+t*(c-p) for p,c in zip(previous,current,strict=True)))
        if cv <= 0:
            result.append(current)
        previous, pv = current, cv
    return result


def area(polygon):
    if len(polygon) < 3:
        return F(0)
    return abs(sum(p[0]*q[1]-p[1]*q[0] for p,q in zip(polygon,polygon[1:]+polygon[:1],strict=True)))/2


def first_moment(polygon):
    """Unnormalized integral of (x,y) over an oriented convex polygon."""
    if len(polygon) < 3:
        return (F(0), F(0))
    signed = sum(p[0]*q[1]-p[1]*q[0] for p,q in zip(polygon,polygon[1:]+polygon[:1],strict=True))
    sign = 1 if signed >= 0 else -1
    return tuple(sign*sum((p[j]+q[j])*(p[0]*q[1]-p[1]*q[0])
                          for p,q in zip(polygon,polygon[1:]+polygon[:1],strict=True))/6 for j in (0,1))


def cell_mass_moments(slopes, intercepts):
    polygons = [cell(cell_constraints(slopes,intercepts,i)) for i in range(len(slopes))]
    return ([area(p)/4 for p in polygons],
            [tuple(x/4 for x in first_moment(p)) for p in polygons], polygons)


def face_differentials(slopes, intercepts, direction):
    """Exact 2D face formulas from source cells:calculus, independent of finite differences."""
    n = len(slopes)
    masses, moments, polygons = cell_mass_moments(slopes,intercepts)
    if len(set(slopes)) != n or any(m <= 0 for m in masses):
        raise ValueError('Distinct sites and positive cell masses are required')
    weights = [[F(0) for _ in range(n)] for _ in range(n)]
    dm, db = [F(0)]*n, [[F(0),F(0)] for _ in range(n)]
    for i in range(n):
        for j in range(i+1,n):
            normal = tuple(slopes[i][k]-slopes[j][k] for k in (0,1))
            bound = intercepts[j]-intercepts[i]
            points = sorted(set(p for p in polygons[i] if sum(x*y for x,y in zip(normal,p,strict=True)) == bound))
            if len(points) < 2:
                continue
            start, end = points[0], points[-1]
            # A tangent is perpendicular to the normal, so length(tangent)/
            # length(normal) is a rational coordinate ratio in two dimensions.
            ratio = abs((end[0]-start[0])/normal[1]) if normal[1] else abs((end[1]-start[1])/normal[0])
            g = ratio/4
            weights[i][j] = weights[j][i] = g
            midpoint = tuple((x+y)/2 for x,y in zip(start,end,strict=True))
            mass_flow = g*(direction[i]-direction[j])
            dm[i] += mass_flow
            dm[j] -= mass_flow
            for k in (0,1):
                moment_flow = midpoint[k]*mass_flow
                db[i][k] += moment_flow
                db[j][k] -= moment_flow
    return masses, moments, dm, db, weights


def cell_constraints(slopes, intercepts, i):
    return [(slopes[j][0]-slopes[i][0], slopes[j][1]-slopes[i][1], intercepts[i]-intercepts[j])
            for j in range(len(slopes)) if j != i]


def cell(constraints):
    polygon = [(F(-1),F(-1)),(F(1),F(-1)),(F(1),F(1)),(F(-1),F(1))]
    for a,b,c in constraints:
        polygon = clip(polygon,a,b,c)
    return polygon


def solve_square(matrix, rhs):
    n = len(rhs)
    augmented = [list(map(F,row))+[F(b)] for row,b in zip(matrix,rhs,strict=True)]
    for column in range(n):
        pivot = next((i for i in range(column,n) if augmented[i][column]),None)
        if pivot is None:
            return None
        augmented[column],augmented[pivot] = augmented[pivot],augmented[column]
        value = augmented[column][column]
        augmented[column] = [x/value for x in augmented[column]]
        for i in range(n):
            if i != column:
                value = augmented[i][column]
                augmented[i] = [x-value*y for x,y in zip(augmented[i],augmented[column],strict=True)]
    return [row[-1] for row in augmented]


def transport_cost(source, source_masses, target, target_masses):
    """Enumerate all basic feasible solutions; five independent marginal rows."""
    if len(source) != 3 or len(target) != 3:
        raise ValueError('Independent LP oracle only supports 3x3')
    if sum(source_masses)!=1 or sum(target_masses)!=1:
        raise ValueError('Probability mass must be exactly one')
    arcs = [(i,j) for i in range(3) for j in range(3)]
    best = None
    rhs = list(source_masses)+list(target_masses[:2])
    for basis in combinations(arcs,5):
        matrix = [[int(i==r) for i,j in basis] for r in range(3)]
        matrix += [[int(j==r) for i,j in basis] for r in range(2)]
        flow = solve_square(matrix,rhs)
        if flow is None or any(x<0 for x in flow):
            continue
        if sum(x for (i,j),x in zip(basis,flow,strict=True) if j==2) != target_masses[2]:
            continue
        cost = sum(x*sum((a-b)**2 for a,b in zip(source[i],target[j],strict=True))
                   for (i,j),x in zip(basis,flow,strict=True))
        if best is None or cost < best:
            best = cost
    if best is None:
        raise ValueError('No feasible transport vertex')
    return best


def three_atom_example(a):
    a = F(a)
    if not 0 < a < F(1,2):
        raise ValueError('The construction requires 0<a<1/2')
    b = a/2
    source = [(F(-1),F(0)),(F(1),F(0)),(F(0),F(0))]
    target = source[:2]+[(F(0),b)]
    intercepts = [F(0),F(0),a]
    c0 = [cell_constraints(source,intercepts,i) for i in range(3)]
    c1 = [cell_constraints(target,intercepts,i) for i in range(3)]
    masses0 = [area(cell(c))/4 for c in c0]
    masses1 = [area(cell(c))/4 for c in c1]
    cost = F(0)
    overlaps = []
    for i in range(3):
        row = []
        for j in range(3):
            mass = area(cell(c0[i]+c1[j]))/4
            row.append(mass)
            cost += mass*sum((x-y)**2 for x,y in zip(source[i],target[j],strict=True))
        overlaps.append(row)
    w2_squared = transport_cost(source,masses0,target,masses1)
    return {"a":a,"source_masses":masses0,"target_masses":masses1,
            "overlap_masses":overlaps,"map_L2_squared":cost,"target_W2_squared":w2_squared}
