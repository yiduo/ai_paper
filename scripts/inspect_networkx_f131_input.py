#!/usr/bin/env python3
"""Inspect a pinned public graph and a state-space witness without executing NetworkX.

This is input/contract inspection, not a mixing experiment or application result.
The source bundle retains the upstream BSD license. No imported third-party code
is executed, and no graph state space is enumerated.
"""
import argparse
import ast
import gzip
import hashlib
import json
from collections import Counter
from math import comb
from pathlib import Path


def inspect(bundle_path: Path) -> dict:
    bundle = json.loads(gzip.decompress(bundle_path.read_bytes()))
    files = bundle['files']
    for path, content in files.items():
        assert hashlib.sha256(content.encode()).hexdigest() == bundle['source_sha256'][path], path
    code = files['networkx/generators/social.py']
    tree = ast.parse(code)
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                    and n.name == 'florentine_families_graph')
    pairs = []
    for call in ast.walk(function):
        if not isinstance(call, ast.Call):
            continue
        if (isinstance(call.func, ast.Attribute) and isinstance(call.func.value, ast.Name)
                and call.func.value.id == 'G' and call.func.attr == 'add_edge'):
            assert len(call.args) == 2 and not call.keywords
            u, v = (ast.literal_eval(a) for a in call.args)
            assert isinstance(u, str) and isinstance(v, str) and u != v
            pairs.append(tuple(sorted((u, v))))
    assert len(pairs) == len(set(pairs)) == 20
    edges = set(pairs)
    vertices = sorted({u for edge in edges for u in edge})
    assert len(vertices) == 15

    def degree(es):
        counts = Counter(u for e in es for u in e)
        return {v: counts[v] for v in vertices}

    def components(es):
        adjacency = {v: set() for v in vertices}
        for u, v in es:
            adjacency[u].add(v)
            adjacency[v].add(u)
        unseen, answer = set(vertices), []
        while unseen:
            todo = [min(unseen)]
            component = set()
            while todo:
                v = todo.pop()
                if v in component:
                    continue
                component.add(v)
                todo.extend(adjacency[v] - component)
            unseen -= component
            answer.append(sorted(component))
        return sorted(answer)

    removed = {tuple(sorted(e)) for e in [('Acciaiuoli', 'Medici'),
                                          ('Guadagni', 'Lamberteschi')]}
    added = {tuple(sorted(e)) for e in [('Acciaiuoli', 'Lamberteschi'),
                                        ('Medici', 'Guadagni')]}
    assert len({v for e in removed for v in e}) == 4
    assert removed <= edges and not (added & edges)
    changed = (edges - removed) | added
    assert degree(changed) == degree(edges)
    assert len(components(edges)) == 1 and len(components(changed)) == 2
    assert ['Acciaiuoli', 'Lamberteschi'] in components(changed)
    n, m = len(vertices), len(edges)
    return {
        'classification': 'Static public input and finite graph witness inspection; not a numerical mixing experiment or initial application check',
        'repository': bundle['repository'], 'revision': bundle['revision'],
        'source_path': 'networkx/generators/social.py',
        'function': function.name, 'source_lines': [function.lineno, function.end_lineno],
        'input': {'vertices': vertices, 'edges': [list(e) for e in sorted(edges)],
                  'nodes': n, 'edge_count': m, 'degrees': degree(edges),
                  'components': components(edges), 'weighted': False,
                  'directed': False, 'self_loops': False, 'parallel_edges': False},
        'witness': {'removed_edges': [list(e) for e in sorted(removed)],
                    'added_edges': [list(e) for e in sorted(added)],
                    'four_distinct_vertices': True, 'same_labelled_degree_vector': True,
                    'result_components': components(changed),
                    'valid_in_F131_full_state_space': True,
                    'invalid_for_connected_only_target': True},
        'exact_integer_formula_evaluation': {
            'F131_universal_quarter_TV_upper_steps_2n8': 2 * n**8,
            'F131_inverse_gap_bound_24n2choose4': 24 * n*n * comb(n, 4),
            'source_encoding_B_choose_n2': comb(n, 2),
            'networkx_random_reference_outer_rounds_niter_1': m,
            'networkx_sigma_default_outer_rounds_per_reference': 100 * m,
            'networkx_random_reference_counted_retry_limit_per_outer_round':
                (2 * m) // (n - 1),
            'warning': 'Different step units; these integers are not runtime observations, tight lower bounds, or a speed ratio'},
        'original_historical_paper_checked': False,
        'third_party_software_executed': False,
        'chain_simulated': False, 'exact_sampler_executed': False,
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source_bundle', type=Path)
    args = parser.parse_args()
    print(json.dumps(inspect(args.source_bundle), ensure_ascii=False, sort_keys=True, indent=2))
