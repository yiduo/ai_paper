#!/usr/bin/env python3
"""Read-only APP09402 source qualification; never an embedding experiment.

Requires the optional, separately qualified h5py/NumPy reader environment.
The script does not fetch dependencies, install anything, or alter the source.
It writes only a verified gzip profile, without a second full matrix/ID copy.
"""
import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path
import sys


def digest(data):
    return hashlib.sha256(data).hexdigest()


def profile(source, specification):
    import h5py
    import numpy as np
    assert sys.version_info >= (3, 11)
    raw = source.read_bytes()
    assert len(raw) == specification['uncompressed_bytes']
    assert digest(raw) == specification['uncompressed_sha256']
    values, fields, errors = {}, {}, {}

    def strings(dataset):
        direct = dataset[()]
        decoded = [x.decode('utf-8', errors='strict') if isinstance(x, bytes) else str(x)
                   for x in direct.tolist()]
        via_api = dataset.asstr(encoding='utf-8', errors='strict')[()].tolist()
        assert decoded == via_api
        return decoded

    with h5py.File(source, 'r') as data:
        for name in specification['target_fields']:
            try:
                node = data[name]
                categories = None
                if isinstance(node, h5py.Group):
                    assert node.attrs['encoding-type'] == 'categorical'
                    categories = strings(node['categories'])
                    assert len(set(categories)) == len(categories)
                    codes = node['codes'][()]
                    assert np.issubdtype(codes.dtype, np.integer)
                    assert bool(np.all((codes >= -1) & (codes < len(categories))))
                    column = [None if code == -1 else categories[int(code)] for code in codes]
                else:
                    column = strings(node)
                expected = specification['expected_shape'][0 if name.startswith('obs/') else 1]
                assert len(column) == expected
                values[name] = column
                count = Counter(column)
                normalized = [x.strip().casefold() if x is not None else None for x in column]
                sentinel_counts = Counter(x for x in normalized if x in {'', 'na', 'n/a', 'nan', 'none', 'unknown'})
                barcode = 'barcode' in name or name.endswith('/_index')
                fields[name] = {
                    'rows': len(column), 'missing_category_code_count': count.get(None, 0),
                    'empty_or_sentinel_counts': dict(sentinel_counts),
                    'distinct_nonmissing': len(set(column) - {None}),
                    'normalized_distinct_nonmissing': len(set(normalized) - {None}),
                    'decoded_values_sha256': digest(json.dumps(column, ensure_ascii=False, separators=(',', ':')).encode()),
                    'direct_bytes_and_asstr_agree': True,
                    'category_count': len(categories) if categories is not None else None,
                    'value_counts': ({str(k): v for k, v in sorted(count.items(), key=lambda p: str(p[0]))}
                                     if not barcode and len(count) <= 100 else None),
                    'raw_cell_or_barcode_values_retained': False,
                }
            except Exception as error:
                errors[name] = {'type': type(error).__name__, 'message': str(error)}

        shape = tuple(int(x) for x in data['X'].attrs['shape'])
        assert shape == tuple(specification['expected_shape'])
        assert data['X'].attrs['encoding-type'] == 'csc_matrix'
        entries = data['X/data'][()]
        indices = data['X/indices'][()]
        indptr = data['X/indptr'][()]
        assert len(entries) == len(indices) == int(indptr[-1])
        assert len(indptr) == shape[1] + 1 and int(indptr[0]) == 0
        assert bool(np.all(indptr[1:] >= indptr[:-1]))
        matrix = np.zeros(shape, dtype=entries.dtype)
        for column in range(shape[1]):
            lo, hi = int(indptr[column]), int(indptr[column + 1])
            rows = indices[lo:hi]
            assert bool(np.all((rows >= 0) & (rows < shape[0])))
            assert len(set(map(int, rows))) == len(rows)
            matrix[rows, column] = entries[lo:hi]
        assert bool(np.isfinite(matrix).all()) and bool((matrix >= 0).all())
        numeric_checks = {
            'row_ncounts_equal': bool(np.array_equal(matrix.sum(axis=1), data['obs/ncounts'][()])),
            'row_ngenes_equal': bool(np.array_equal((matrix > 0).sum(axis=1), data['obs/ngenes'][()])),
            'protein_ncounts_equal': bool(np.array_equal(matrix.sum(axis=0), data['var/ncounts'][()])),
            'protein_ncells_equal': bool(np.array_equal((matrix > 0).sum(axis=0), data['var/ncells'][()])),
        }
        nperts = data['obs/nperts'][()]
        nperts_counts = {str(k): v for k, v in Counter(map(int, nperts)).items()}

    unique, inverse, counts = np.unique(matrix, axis=0, return_inverse=True, return_counts=True)
    duplicates = [int(i) for i in np.flatnonzero(counts > 1)]
    grouping = defaultdict(list)
    for row, group in enumerate(inverse):
        grouping[int(group)].append(row)
    duplicate_labels = {}
    for label in ['obs/perturbation', 'obs/guide_id']:
        if label not in values:
            continue
        conflicted, affected, min_errors, examples = 0, 0, 0, []
        for group in duplicates:
            rows = grouping[group]
            count = Counter(values[label][i] for i in rows if values[label][i] is not None)
            if len(count) > 1:
                conflicted += 1
                affected += len(rows)
                min_errors += sum(count.values()) - max(count.values())
                if len(examples) < 3:
                    examples.append({'protein_counts': unique[group].tolist(), 'label_counts': dict(count)})
        duplicate_labels[label] = {
            'conflicting_duplicate_groups': conflicted, 'rows_in_conflicting_groups': affected,
            'empirical_minority_rows': min_errors,
            'empirical_minority_fraction_of_all_cells': min_errors / shape[0],
            'examples': examples,
            'meaning': 'Descriptive exact-feature ambiguity,not a compression result,causal claim or out-of-sample prediction bound',
        }
    relations = {}
    if 'obs/guide_id' in values and 'obs/perturbation' in values:
        mapping = defaultdict(set)
        for guide, label in zip(values['obs/guide_id'], values['obs/perturbation'], strict=True):
            mapping[guide].add(label)
        relations = {
            'guide_to_perturbation': {str(k): sorted(v, key=str) for k, v in sorted(mapping.items(), key=lambda p: str(p[0]))},
            'guides_with_multiple_perturbation_labels': sum(len(v) > 1 for v in mapping.values()),
        }
    index = values.get('obs/_index', [])
    return {
        'specification_id': specification['id'], 'scope': specification['scope'],
        'source_sha256': digest(raw), 'source_bytes': len(raw),
        'runtime': {'python': sys.version, 'executable': sys.executable, 'numpy': np.__version__,
                    'h5py': h5py.__version__, 'HDF5': h5py.version.hdf5_version},
        'shape': list(shape), 'grain': 'Individual cells;neither distinct feature vectors nor perturbation-level profiles',
        'protein_coordinate_order': values.get('var/protein'),
        'fields_decoded': fields, 'field_errors': errors,
        'all_14_fields_read': len(fields) == 14 and not errors,
        'cell_identifiers': {'observed': len(index), 'unique': len(set(index)),
                             'duplicate_beyond_first': len(index) - len(set(index)), 'raw_values_retained': False},
        'numeric_checks': numeric_checks, 'nperts_counts': nperts_counts,
        'exact_feature_groups': len(unique), 'duplicate_feature_rows_beyond_first': shape[0] - len(unique),
        'duplicate_feature_groups': len(duplicates), 'duplicate_group_rows': int(sum(counts[i] for i in duplicates)),
        'duplicate_label_profiles': duplicate_labels, 'annotation_relation': relations,
        'matrix_copy_retained': False, 'embedding_or_application_experiment': False,
        'limitations': specification['limits'],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--spec', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    specification = json.loads(args.spec.read_text())
    result = profile(args.source, specification)
    raw = (json.dumps(result, ensure_ascii=False, indent=2) + '\n').encode()
    packed = gzip.compress(raw, mtime=0)
    assert gzip.decompress(packed) == raw
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(packed)
    print(json.dumps({'output': str(args.output), 'sha256_uncompressed': digest(raw),
                      'fields_read': len(result['fields_decoded']), 'field_errors': result['field_errors'],
                      'shape': result['shape'], 'numeric_checks': result['numeric_checks'],
                      'new_application_run': False}))


if __name__ == '__main__':
    main()
