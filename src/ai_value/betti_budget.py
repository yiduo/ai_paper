"""Exact, small-domain lex-plus-powers budget calibration.

Construction consumes declared Hilbert data; it does not certify that a supplied
nonmonomial ideal contains a regular sequence. No floating-point rank decisions.
"""

from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
from functools import lru_cache
import itertools
import math


@lru_cache(maxsize=None)
def monomials(n: int, degree: int) -> tuple[tuple[int, ...], ...]:
    if degree < 0:
        return ()
    if n == 0:
        return ((),) if degree == 0 else ()
    return tuple((a,) + tail for a in range(degree, -1, -1)
                 for tail in monomials(n-1, degree-a))


def divides(a: tuple, b: tuple) -> bool:
    return all(x <= y for x, y in zip(a, b))


def inside(monomial: tuple, generators: list[tuple]) -> bool:
    return any(divides(g, monomial) for g in generators)


def lex_generators(n: int, prefix: list[int], tail: int, powers: list[int], limit: int) -> list[tuple]:
    generators, previous = [], set()
    for degree in range(limit+1):
        all_m = monomials(n, degree)
        forced = {m for m in all_m if any(m[i] >= a for i, a in enumerate(powers))}
        h = prefix[degree] if degree < len(prefix) else tail
        q = len(all_m)-h-len(forced)
        outside = [m for m in all_m if m not in forced]
        if not 0 <= q <= len(outside):
            raise ValueError('Hilbert data incompatible with prescribed powers')
        included = forced | set(outside[:q])
        for old in previous:
            for i in range(n):
                product = tuple(x+(j == i) for j, x in enumerate(old))
                if product not in included:
                    raise ValueError('Degreewise prescription is not an ideal')
        for m in sorted(included, reverse=True):
            if not any(tuple(x-(j == i) for j, x in enumerate(m)) in previous
                       for i in range(n) if m[i]):
                generators.append(m)
        previous = included
    return generators


def trim(poly: list[int]) -> list[int]:
    while poly and poly[-1] == 0:
        poly.pop()
    return poly


def convolution(a: list[int], b: list[int]) -> list[int]:
    out = [0]*(len(a)+len(b)-1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i+j] += x*y
    return trim(out)


def prescribed_numerator(n: int, prefix: list[int], tail: int) -> list[int]:
    # H(t) = prefix(t) + tail*t^len(prefix)/(1-t).
    numerator = convolution(prefix, [1,-1])
    numerator += [0]*(len(prefix)+1-len(numerator))
    numerator[len(prefix)] += tail
    return convolution(trim(numerator), [(-1)**i*math.comb(n-1,i) for i in range(n)])


def ideal_numerator(n: int, generators: list[tuple]) -> list[int]:
    # Inclusion-exclusion in the finite lcm monoid, collecting equal exponents.
    coefficients = {(0,)*n:1}
    for g in generators:
        changes = defaultdict(int)
        for exponent, coefficient in coefficients.items():
            changes[tuple(max(x,y) for x,y in zip(exponent,g))] -= coefficient
        for exponent, coefficient in changes.items():
            coefficients[exponent] = coefficients.get(exponent,0)+coefficient
            if coefficients[exponent] == 0:
                del coefficients[exponent]
    result = [0]*(max(map(sum,coefficients))+1)
    for exponent, coefficient in coefficients.items():
        result[sum(exponent)] += coefficient
    return trim(result)


def integer_rank(columns: list[dict[int,int]]) -> int:
    pivots = {}
    for vector in columns:
        row = dict(vector)
        while row:
            k = min(row)
            if k not in pivots:
                pivots[k] = row
                break
            pivot = pivots[k]
            a,b = pivot[k],row[k]
            keys = row.keys() | pivot.keys()
            row = {i:a*row.get(i,0)-b*pivot.get(i,0) for i in keys}
            row = {i:v for i,v in row.items() if v}
            common = math.gcd(*row.values()) if row else 1
            if common > 1:
                row = {i:v//common for i,v in row.items()}
    return len(pivots)


def fraction_rank(columns: list[dict[int,int]], rows: int) -> int:
    # Separate dense row-elimination implementation for tiny multidegree blocks.
    matrix = [[Fraction(column.get(i,0)) for column in columns] for i in range(rows)]
    rank = 0
    for j in range(len(columns)):
        pivot = next((i for i in range(rank,rows) if matrix[i][j]),None)
        if pivot is None:
            continue
        matrix[rank],matrix[pivot] = matrix[pivot],matrix[rank]
        a = matrix[rank][j]
        matrix[rank] = [x/a for x in matrix[rank]]
        for i in range(rank+1,rows):
            if matrix[i][j]:
                a = matrix[i][j]
                matrix[i] = [x-a*y for x,y in zip(matrix[i],matrix[rank])]
        rank += 1
        if rank == rows:
            break
    return rank


def masks(n: int, p: int) -> list[tuple[int,...]]:
    return list(itertools.combinations(range(n),p))


def graded_betti(n: int, generators: list[tuple]) -> dict[str,int]:
    max_degree = sum(max(g[i] for g in generators) for i in range(n))
    standard = {d:[m for m in monomials(n,d) if not inside(m,generators)]
                for d in range(max_degree+1)}
    result = {}
    for degree in range(max_degree+1):
        bases = [[(m,sigma) for m in standard.get(degree-p,[]) for sigma in masks(n,p)]
                 for p in range(n+1)]
        ranks = [0]*(n+2)
        for p in range(1,n+1):
            target = {item:i for i,item in enumerate(bases[p-1])}
            columns = []
            for monomial,sigma in bases[p]:
                column = {}
                for position,i in enumerate(sigma):
                    product = tuple(x+(k == i) for k,x in enumerate(monomial))
                    key = (product,sigma[:position]+sigma[position+1:])
                    if key in target:
                        column[target[key]] = (-1)**position
                columns.append(column)
            ranks[p] = integer_rank(columns)
        for p in range(n+1):
            beta = len(bases[p])-ranks[p]-ranks[p+1]
            if beta < 0:
                raise ValueError('Negative homology dimension')
            if beta:
                result[f'{p}:{degree}'] = beta
    return result


def multigraded_betti(n: int, generators: list[tuple], limit: int) -> tuple[dict[str,int],int]:
    bounds = [max(g[i] for g in generators) for i in range(n)]
    count = math.prod(b+1 for b in bounds)
    if count > limit:
        raise ValueError('Multidegree resource envelope exceeded before enumeration')
    result = defaultdict(int)
    for alpha in itertools.product(*(range(b+1) for b in bounds)):
        bases = []
        for p in range(n+1):
            basis = []
            for sigma in masks(n,p):
                exponent = tuple(a-(i in sigma) for i,a in enumerate(alpha))
                if min(exponent) >= 0 and not inside(exponent,generators):
                    basis.append(sigma)
            bases.append(basis)
        ranks = [0]*(n+2)
        for p in range(1,n+1):
            columns = []
            for sigma in bases[p]:
                column = {}
                for k,i in enumerate(sigma):
                    target = sigma[:k]+sigma[k+1:]
                    if target in bases[p-1]:
                        column[bases[p-1].index(target)] = (-1)**k
                columns.append(column)
            ranks[p] = fraction_rank(columns,len(bases[p-1]))
        for p in range(n+1):
            beta = len(bases[p])-ranks[p]-ranks[p+1]
            if beta:
                result[f'{p}:{sum(alpha)}'] += beta
    return dict(result),count


def ideal_table(quotient: dict[str,int]) -> dict[str,int]:
    return {f'{int(k.split(":")[0])-1}:{k.split(":")[1]}':value
            for k,value in quotient.items() if int(k.split(':')[0]) >= 1}


def experiment(spec: dict) -> tuple[list[dict],dict]:
    data = spec['input'];rows = [];bad = 0;hilbert_bad = 0;gains = [];control = []
    if data.get('characteristic',0) != 0:
        raise ValueError('General regular-sequence application requires characteristic zero')
    for case in data['cases']:
        tables = {}
        for name,powers in [('ordinary_lex',[]),('old_growth_lpp',case['baseline_degrees']),('exact_degree_lpp',case['degrees'])]:
            generators = lex_generators(case['variables'],case['hilbert_prefix'],case['hilbert_tail'],powers,data['max_generator_degree'])
            numerator = ideal_numerator(case['variables'],generators)
            numerator_match = numerator == prescribed_numerator(case['variables'],case['hilbert_prefix'],case['hilbert_tail'])
            first = graded_betti(case['variables'],generators)
            second,blocks = multigraded_betti(case['variables'],generators,data['max_multidegrees'])
            agrees = first == second
            table = ideal_table(first)
            totals = [sum(v for k,v in table.items() if int(k.split(':')[0]) == p) for p in range(case['variables'])]
            row = {'case':case['id'],'variant':name,'powers':powers,'generators':generators,'hilbert_numerator':numerator,
                   'entire_hilbert_sequence_matches':numerator_match,'quotient_betti':first,'ideal_betti':table,
                   'ideal_betti_totals':totals,'total_budget':sum(totals),'independent_multigraded_betti':second,
                   'multidegrees_enumerated':blocks,'oracle_agrees':agrees}
            rows.append(row);tables[name]=row;bad += not agrees;hilbert_bad += not numerator_match
        old=tables['old_growth_lpp']['total_budget'];new=tables['exact_degree_lpp']['total_budget']
        if case['expect_gain']:
            gains.append(Fraction(old-new,old))
        else:
            control.append(abs(old-new))
    return rows,{'instances':len(data['cases']),'computed_tables':len(rows),'oracle_disagreements':bad,
                 'hilbert_numerator_mismatches':hilbert_bad,'budget_reduction_fractions':list(map(str,gains)),
                 'covered_scope_budget_differences':control,
                 'meets_prediction':bad==0 and hilbert_bad==0 and min(gains)>=Fraction(str(spec['success']['budget_reduction_fraction_min'])) and all(x==0 for x in control),
                 'interpretation':'Known published conditional-input budget calibration and old-scope control. Exact table calculation is not an independent certificate of the original regular sequence, proof of the2026 theorem, blind discovery, or solver time/memory improvement.'}


def lex_source_audit(spec: dict) -> tuple[list[dict],dict]:
    data=spec['input'];n=data['variables']
    generators=lex_generators(n,data['hilbert_prefix'],data['hilbert_tail'],[],data['max_generator_degree'])
    stable=all(inside(tuple(x+(k==i)-(k==j) for k,x in enumerate(g)),generators)
               for g in generators for j in range(n) if g[j] for i in range(j))
    if not stable:
        raise ValueError('Generator formula requires stability')
    formula=defaultdict(int)
    for g in generators:
        last=max(i for i,e in enumerate(g) if e)
        for p in range(last+1):
            formula[f'{p}:{sum(g)+p}'] += math.comb(last,p)
    computed=ideal_table(graded_betti(n,generators))
    key=f'{data["source_ideal_homological_degree"]}:{data["source_internal_degree"]}'
    mutant=dict(computed);mutant[key]=data['source_printed_value']
    def numerator(table):
        out=[1]+[0]*max(int(k.split(':')[1]) for k in table)
        for k,v in table.items():
            p,j=map(int,k.split(':'));out[j] -= (-1)**p*v
        return trim(out)
    expected=prescribed_numerator(n,data['hilbert_prefix'],data['hilbert_tail'])
    computed_euler=sum((-1)**int(k.split(':')[0])*v for k,v in computed.items())
    printed_euler=sum((-1)**int(k.split(':')[0])*v for k,v in mutant.items())
    row={'strong_stability_checked':stable,'computed_cell':computed[key],'source_printed_cell':data['source_printed_value'],
         'formula_cell':formula[key],'generator_formula_matches_entire_computed_table':dict(formula)==computed,
         'computed_hilbert_numerator_matches':numerator(computed)==expected,
         'printed_cell_substitution_hilbert_numerator_matches':numerator(mutant)==expected,
         'computed_rank_euler':computed_euler,'printed_cell_substitution_rank_euler':printed_euler,
         'degree_six_generators_with_last_variable':[g for g in generators if sum(g)==6 and g[-1]],
         'computed_table':computed,'independent_generator_formula':dict(formula)}
    return [row],{'instances':1,'application_hypotheses_added':0,'computed_cell':computed[key],
                 'source_printed_cell':data['source_printed_value'],
                 'generator_formula_disagreements':int(dict(formula)!=computed),
                 'source_cell_disagreements':int(computed[key]!=data['source_printed_value']),
                 'printed_cell_substitution_breaks_hilbert_identity':numerator(mutant)!=expected,
                 'meets_prediction':dict(formula)==computed and computed[key]!=data['source_printed_value'] and numerator(computed)==expected and numerator(mutant)!=expected and computed_euler==1 and printed_euler!=1,
                 'interpretation':'Exact evidence for a single illustrative-cell inconsistency in a pinned preprint. No main-theorem rejection, author confirmation, or additional application hypothesis.'}
