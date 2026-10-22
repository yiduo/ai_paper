#!/usr/bin/env python3
"""Check lossless citation projection and list unmerged literature identifiers."""
from pathlib import Path
import collections
import gzip
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from ai_value.graph import load, read_jsonl, validate
from ai_value.provenance import literature_identity_candidates


def main():
    nodes, edges = load(ROOT)
    research = read_jsonl(ROOT / "data/graph/nodes.jsonl")
    expected = {(n["id"], i): s for n in research for i, s in enumerate(n["sources"])}
    observed = {}
    artifacts = [n for n in nodes.values() if n["kind"] == "source_artifact"]
    for artifact in artifacts:
        for annotation in artifact["properties"]["citation_annotations"]:
            key = (annotation["citing_node_id"], annotation["source_index"])
            assert key not in observed, key
            observed[key] = annotation["source"]
    assert observed == expected, "A source locator/version/hash was dropped or changed"
    edge_indices = collections.Counter()
    for edge in edges:
        if edge["relation"] == "cites":
            for index in edge["citation_source_indices"]:
                edge_indices[edge["source"], index] += 1
    assert set(edge_indices) == set(expected) and all(v == 1 for v in edge_indices.values())
    legacy = collections.defaultdict(set)
    for source in expected.values():
        if "url" in source:
            key = source["url"] + "|" + source.get("sha256", "external-version-in-locator")
            legacy[key].add(json.dumps(source, ensure_ascii=False, sort_keys=True))
    ambiguities = [{"legacy_identity": k, "distinct_annotations": len(v)}
                   for k, v in sorted(legacy.items()) if len(v) > 1]
    groups = literature_identity_candidates(nodes)
    result = {
        "validation": validate(ROOT), "canonical_citations": len(expected),
        "exact_source_annotation_roundtrip": True, "each_citation_has_one_projected_edge": True,
        "source_artifacts": len(artifacts),
        "shared_artifacts_with_all_annotations_retained": sum(len(n["properties"]["citation_annotations"]) > 1 for n in artifacts),
        "identity_basis_counts": dict(collections.Counter(n["properties"]["identity_basis"] for n in artifacts)),
        "legacy_external_annotation_collisions": ambiguities,
        "literature_nodes": sum(n["kind"] == "literature" for n in nodes.values()),
        "literature_nodes_with_explicit_doi_field": sum(n["kind"] == "literature" and bool(n["properties"].get("doi")) for n in nodes.values()),
        "literature_exact_identifier_review_groups": groups,
        "automatic_work_or_version_merges": 0, "mathematical_grade_promotions": 0,
        "new_research_results_or_experiment_hypotheses": 0,
        "limitations": "Exact identifier groups are review routing,not verified work identity or proof independence. Unknown external bytes remain unresolved observations.",
    }
    raw = (json.dumps(result, ensure_ascii=False, indent=2) + "\n").encode()
    packed = gzip.compress(raw, mtime=0)
    assert gzip.decompress(packed) == raw
    out = ROOT / "reports/graph/provenance-audit.json.gz"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(packed)
    print(json.dumps({"canonical_citations": len(expected), "source_artifacts": len(artifacts),
                      "legacy_external_collisions": len(ambiguities), "unmerged_identifier_groups": len(groups),
                      "gzip_bytes": len(packed), "decompressed_sha256": hashlib.sha256(raw).hexdigest()}))


if __name__ == "__main__":
    main()
