#!/usr/bin/env python3
"""Exact documentation-fixture witnesses; no external sampler or F115 execution."""
import argparse
import datetime
from fractions import Fraction
import gzip
import hashlib
import json
from math import factorial, prod
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = 'data/provenance/demand/F-115-interface-inspection-protocol.json'
DEFAULT = ROOT/'data/provenance/demand/F-115-interface-witness'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2)+'\n').encode()


def witness(protocol):
    tea = protocol['fixtures']['tea']
    row, col = tea['row'], tea['col']
    assert row == col == [4, 4] and tea['matrix'] == [[3, 1], [1, 3]]
    expected = [[Fraction(a*b, sum(row)) for b in col] for a in row]

    def statistic(table):
        return max((Fraction(table[i][k])-expected[i][k])**2/expected[i][k]
                   for i in range(2) for k in range(2))

    threshold = statistic(tea['matrix'])
    tables = []
    for x in range(5):
        table = [[x, 4-x], [4-x, x]]
        assert [sum(t) for t in table] == row
        assert [sum(t[k] for t in table) for k in range(2)] == col
        mass = Fraction(prod(factorial(v) for v in row+col),
                        factorial(sum(row))*prod(factorial(v) for t in table for v in t))
        tables.append(dict(table=table, factorial_mass=mass, uniform_mass=Fraction(1, 5),
                           event=statistic(table) >= threshold))
    assert sum(t['factorial_mass'] for t in tables) == 1
    assert sum(t['uniform_mass'] for t in tables) == 1
    tv = sum(abs(t['factorial_mass']-t['uniform_mass']) for t in tables)/2
    tails = {k: sum((t[k] for t in tables if t['event']), Fraction())
             for k in ('factorial_mass', 'uniform_mass')}
    assert tv > 0 and tails['factorial_mass'] != tails['uniform_mass']

    flow = protocol['fixtures']['mincost']
    assert flow['demand'] == {'a': -5, 'b': 0, 'c': 0, 'd': 5}
    capacities = {(a, b): cap for a, b, cap, cost in flow['edges']}
    costs = {(a, b): cost for a, b, cap, cost in flow['edges']}
    feasible = []
    for x in range(5):
        values = {('a', 'b'): x, ('a', 'c'): 5-x, ('b', 'd'): x, ('c', 'd'): 5-x}
        assert all(0 <= v <= capacities[e] for e, v in values.items())
        for vertex, demand in flow['demand'].items():
            inflow = sum(v for (a, b), v in values.items() if b == vertex)
            outflow = sum(v for (a, b), v in values.items() if a == vertex)
            assert inflow-outflow == demand
        feasible.append(dict(values={a+'->'+b: v for (a, b), v in values.items()},
                             cost=sum(costs[e]*v for e, v in values.items())))
    optimum = min(t['cost'] for t in feasible)
    optimal = [t for t in feasible if t['cost'] == optimum]
    assert len(optimal) == 1 and optimum == 24
    return dict(scope='Exact algebraic inspection of published documentation fixtures;not new application validation',
                tea=dict(tables=[{**t, 'factorial_mass': str(t['factorial_mass']),
                                  'uniform_mass': str(t['uniform_mass'])} for t in tables],
                         observed_statistic=str(threshold), total_variation=str(tv),
                         event_probability={k: str(v) for k, v in tails.items()}),
                mincost=dict(feasible_arc_vectors=feasible, count=len(feasible),
                             optimum_cost=optimum, optimum_vectors=optimal,
                             uniform_all_feasible_mass=str(Fraction(1, len(feasible)))),
                external_software_executed=[], F115_algorithm_executed=False,
                new_application_hypothesis=False, initial_card_credit=False)


def run(output, verify):
    protocol = json.loads((ROOT/PROTOCOL).read_text())
    for path_key, hash_key in [('source_ledger', 'source_ledger_sha256'),
                               ('source_archive', 'source_archive_sha256')]:
        assert digest((ROOT/protocol[path_key]).read_bytes()) == protocol[hash_key]
    archive = json.loads(gzip.decompress((ROOT/protocol['source_archive']).read_bytes()))
    for name, info in archive['sources'].items():
        assert digest(archive['files'][name].encode()) == info['sha256']
    raw = encoded(witness(protocol))
    snapshot = encoded({path: (ROOT/path).read_text() for path in
                        (PROTOCOL, 'scripts/inspect_table_flow_interfaces.py')})
    payloads = {'raw.json.gz': raw, 'source.json.gz': snapshot}
    if verify:
        manifest = json.loads((output/'manifest.json').read_text())
        for name, data in payloads.items():
            packed = (output/name).read_bytes()
            assert digest(packed) == manifest['outputs'][name]['compressed_sha256']
            assert digest(data) == manifest['outputs'][name]['uncompressed_sha256']
            assert gzip.decompress(packed) == data
        return {'status': 'matches_frozen_witness', 'payloads': len(payloads),
                'external_software_executed': False, 'new_application_check': False}
    output.mkdir(parents=True, exist_ok=False)
    manifest = dict(protocol_id=protocol['id'], recorded_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    purpose='Static contract witness;not an application experiment or new F115 prototype',
                    outputs={}, source_archive=protocol['source_archive'],
                    source_archive_sha256=protocol['source_archive_sha256'])
    for name, data in payloads.items():
        packed = gzip.compress(data, mtime=0)
        assert gzip.decompress(packed) == data
        (output/name).write_bytes(packed)
        manifest['outputs'][name] = dict(compressed_sha256=digest(packed),
                                        uncompressed_sha256=digest(data),
                                        compressed_bytes=len(packed), uncompressed_bytes=len(data))
    (output/'manifest.json').write_bytes(encoded(manifest))
    return {'status': 'saved_compressed_verified_witness', 'payloads': len(payloads),
            'external_software_executed': False, 'new_application_check': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--verify', action='store_true')
    parser.add_argument('--output', type=Path, default=DEFAULT)
    args = parser.parse_args()
    print(json.dumps(run(args.output, args.verify)))
