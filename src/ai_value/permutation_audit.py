"""Exact, small-domain full-law shuffle audit; no large-deck mixing claim."""

from collections import Counter
from fractions import Fraction as F
import itertools
import math


def physical_step(d, mask):
    n = 2**d
    half = n//2
    return tuple(2*(p % half) + ((p//half) ^ ((mask >> (p % half)) & 1))
                 for p in range(n))


def physical_deck_step(deck, mask):
    """Independent split/interleave encoding, with deck indexed by position."""
    half = len(deck)//2
    result = []
    for j in range(half):
        pair = [deck[j], deck[j+half]]
        if (mask >> j) & 1:
            pair.reverse()
        result.extend(pair)
    return tuple(result)


def inverse(permutation):
    result = [0]*len(permutation)
    for x,y in enumerate(permutation):
        result[y] = x
    return tuple(result)


def advance(counts, steps):
    result = Counter()
    for perm,count in counts.items():
        for step in steps:
            result[tuple(step[x] for x in perm)] += count
    return result


def fisher_yates(n):
    counts = Counter({tuple(range(n)):1})
    for i in range(n-1,0,-1):
        next_counts = Counter()
        for deck,count in counts.items():
            for j in range(i+1):
                out = list(deck)
                out[i],out[j] = out[j],out[i]
                next_counts[tuple(out)] += count
        counts = next_counts
    return Counter({inverse(deck):count for deck,count in counts.items()})


def statistics(counts, n, denominator, support_cap):
    factorial = math.factorial(n)
    full_tv = F(sum(abs(c*factorial-denominator) for c in counts.values())
                + (factorial-len(counts))*denominator, 2*denominator*factorial)
    marginals = [[0]*n for _ in range(n)]
    pairs = Counter()
    failures = int(sum(counts.values()) != denominator)
    for perm,count in counts.items():
        if sorted(perm) != list(range(n)) or count <= 0:
            failures += 1
        for card,position in enumerate(perm):
            marginals[card][position] += count
        pairs[perm[:2]] += count
    marginal_tv = max(F(sum(abs(c*n-denominator) for c in marginal),2*denominator*n)
                      for marginal in marginals)
    pair_space = n*(n-1)
    pair_tv = F(sum(abs(c*pair_space-denominator) for c in pairs.values())
                + (pair_space-len(pairs))*denominator,2*denominator*pair_space)
    bound = max(F(0),1-F(support_cap,factorial))
    return {'full_tv':str(full_tv),'max_one_card_tv':str(marginal_tv),
            'first_two_card_tv':str(pair_tv),'support_size':len(counts),
            'support_cap':support_cap,'support_lower_bound':str(bound),
            'support_bound_violation':bound>full_tv,'integrity_failures':failures}


def experiment(spec):
    dimensions = spec['input']['dimensions']
    if not dimensions or any(d not in (1,2,3) for d in dimensions) or len(set(dimensions)) != len(dimensions):
        raise ValueError('Exact audit is limited to unique dimensions 1,2,3 (N<=8)')
    if spec['input']['physical_time_max_multiple_of_d'] not in (1,2):
        raise ValueError('Exact audit permits at most two sweeps')
    rows = []
    disagreements = 0
    transition_checks = 0
    for deck in itertools.permutations(range(4)):
        for mask in range(4):
            before = inverse(deck)
            after = inverse(physical_deck_step(deck,mask))
            encoded = tuple(physical_step(2,mask)[p] for p in before)
            disagreements += encoded != after
            transition_checks += 1
    for d in dimensions:
        n = 2**d
        counts = Counter({tuple(range(n)):1})
        steps = [physical_step(d,m) for m in range(2**(n//2))]
        for t in range(spec['input']['physical_time_max_multiple_of_d']*d+1):
            if t:
                counts = advance(counts,steps)
            denominator = 2**(t*n//2)
            rows.append({'kind':'Thorp','dimension':d,'n':n,'physical_steps':t,
                         'fair_bits':t*n//2,'denominator':denominator,
                         **statistics(counts,n,denominator,denominator),
                         'permutation_path_counts':[[list(p),c] for p,c in sorted(counts.items())]})
        cyclic = Counter({tuple((x+shift)%n for x in range(n)):1 for shift in range(n)})
        for name,law,denominator,cap in [('cyclic',cyclic,n,n),
                                        ('Fisher-Yates',fisher_yates(n),math.factorial(n),math.factorial(n))]:
            rows.append({'kind':name,'dimension':d,'n':n,'physical_steps':None,
                         'denominator':denominator,**statistics(law,n,denominator,cap),
                         'permutation_path_counts':[[list(p),c] for p,c in sorted(law.items())]})
    regimes = [r for r in rows if r['dimension']>=2 and
               (r['kind']=='cyclic' or r['kind']=='Thorp' and r['physical_steps']==r['dimension'])]
    threshold = F(spec['success']['full_tv_threshold'])
    detected = sum(F(r['support_lower_bound'])>threshold and F(r['full_tv'])>threshold for r in regimes)
    marginal_detected = sum(F(r['max_one_card_tv'])>0 for r in regimes)
    false_alarms = sum(F(r['support_lower_bound'])>threshold for r in rows if r['kind']=='Fisher-Yates')
    violations = sum(r['support_bound_violation'] for r in rows)
    integrity = sum(r['integrity_failures'] for r in rows)
    references_uniform = all(F(r['full_tv'])==0 for r in rows if r['kind']=='Fisher-Yates')
    return rows, {'instances':len(rows),'declared_under_mixed_regimes':len(regimes),
                  'support_audit_detected':detected,'marginal_only_detected':marginal_detected,
                  'reference_false_alarms':false_alarms,'reference_laws_exactly_uniform':references_uniform,
                  'transition_cross_checks':transition_checks,'transition_disagreements':disagreements,
                  'support_bound_violations':violations,'integrity_failures':integrity,
                  'under_mixed_regimes':[{k:r[k] for k in ('kind','n','physical_steps','full_tv','max_one_card_tv','first_two_card_tv','support_lower_bound')} for r in regimes],
                  'meets_prediction':detected==spec['success']['under_mixed_regimes_detected']
                    and marginal_detected==spec['success']['marginal_only_under_mixed_regimes_detected']
                    and false_alarms==0 and disagreements==0 and violations==0 and integrity==0 and references_uniform,
                  'interpretation':'Finite exact QA fixture only. Support obstruction already elementary; no incremental algorithm benefit from the new asymptotic upper theorem or security claim.'}
