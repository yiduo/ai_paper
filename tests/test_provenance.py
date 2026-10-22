import json
import hashlib
from pathlib import Path
import unittest

from ai_value.provenance import (
    literature_identity_candidates, project_citations, validate_record_contract, validate_prior_archive,
)

ROOT = Path(__file__).resolve().parents[1]


class ProvenanceTests(unittest.TestCase):
    def test_shared_bytes_keep_every_scope_and_one_edge_per_pair(self):
        first = {"path": "math/paper.tex", "sha256": "a" * 64, "locator": "Lemma 1"}
        second = dict(first, locator="Theorem 2", checked_at="2026-10-20T00:00:00+00:00")
        research = [{"id": "CLAIM-A", "sources": [first, second]},
                    {"id": "CLAIM-B", "sources": [dict(first, locator="Appendix")] }]
        nodes, edges = project_citations(research, "f" * 40)
        self.assertEqual(len(nodes), 1)
        legacy_id = "SOURCE-" + hashlib.sha256((first["path"] + "|" + first["sha256"]).encode()).hexdigest()[:16].upper()
        self.assertEqual(set(nodes), {legacy_id})
        self.assertEqual(len(edges), 2)
        annotations = next(iter(nodes.values()))["properties"]["citation_annotations"]
        self.assertEqual([a["source"] for a in annotations], [first, second, research[1]["sources"][0]])
        edge = next(e for e in edges if e["source"] == "CLAIM-A")
        self.assertEqual(edge["citation_source_indices"], [0, 1])
        self.assertIn("Lemma 1", edge["source_locator"])
        self.assertIn("Theorem 2", edge["source_locator"])
        self.assertNotIn("content_checked", next(iter(nodes.values()))["properties"])

    def test_external_url_does_not_collapse_versions_or_checked_scopes(self):
        url = "https://arxiv.org/pdf/1234.56789"
        sources = [
            {"url": url, "locator": "v1; Theorem 1", "content_checked": True},
            {"url": url, "locator": "v2; Theorem 1 changed", "content_checked": True},
            {"url": url, "locator": "bibliography only", "content_checked": False},
            {"url": url, "locator": "pinned version", "source_revision": "rev1"},
            {"url": url, "locator": "pinned version", "source_revision": "rev2"},
            {"url": url, "locator": "byte evidence", "source_file_sha256": "b" * 64},
            {"url": url, "locator": "byte evidence", "source_file_sha256": "c" * 64},
        ]
        research = [{"id": "LIT-A", "sources": sources}]
        nodes, edges = project_citations(research, "f" * 40)
        self.assertEqual(len(nodes), len(sources))
        self.assertEqual(len(edges), len(sources))
        observed = [a["source"] for n in nodes.values() for a in n["properties"]["citation_annotations"]]
        self.assertCountEqual(observed, sources)
        bases = [n["properties"]["identity_basis"] for n in nodes.values()]
        self.assertEqual(bases.count("unresolved_external_observation"), 3)

    def test_identifier_groups_are_review_only_and_keep_distinct_versions(self):
        nodes = {
            "LIT-A": {"id": "LIT-A", "kind": "literature", "properties": {"doi": "10.1234/ABC"},
                      "sources": [{"url": "https://arxiv.org/pdf/math/0511647v1"}]},
            "LIT-B": {"id": "LIT-B", "kind": "literature", "properties": {"original_link": "https://doi.org/10.1234/abc"},
                      "sources": [{"url": "https://arxiv.org/abs/math/0511647v2"}]},
            "LIT-C": {"id": "LIT-C", "kind": "literature", "properties": {"title": "same title"}, "sources": []},
            "LIT-D": {"id": "LIT-D", "kind": "literature", "properties": {"title": "same title"}, "sources": []},
        }
        original = json.dumps(nodes, sort_keys=True)
        groups = literature_identity_candidates(nodes)
        self.assertEqual({g["identifier"] for g in groups}, {"doi:10.1234/abc", "arxiv-work:math/0511647"})
        self.assertTrue(all(g["node_ids"] == ["LIT-A", "LIT-B"] for g in groups))
        self.assertEqual(json.dumps(nodes, sort_keys=True), original)

    def test_node_contract_accepts_documented_history_but_rejects_silent_fields(self):
        schema = json.loads((ROOT / "schemas/graph-node.schema.json").read_text())
        node = dict(id="LIT-A", kind="literature", version=2, created_at="2026-10-20T00:00:00Z",
                    updated_at="2026-10-21T00:00:00+08:00", prior_version_archive="data/graph/history/LIT-A-v1.json.gz",
                    evidence_status="source_claim", properties={}, sources=[{"locator": "Bibliography"}])
        validate_record_contract(node, schema)
        with self.assertRaises(ValueError):
            validate_record_contract(dict(node, silently_promoted=True), schema)
        with self.assertRaises(ValueError):
            validate_record_contract(dict(node, version=True), schema)
        with self.assertRaises(ValueError):
            validate_record_contract(dict(node, updated_at="2026-10-21T00:00:00"), schema)

    def test_prior_archive_checks_single_and_both_existing_batch_formats(self):
        current = {"id": "LIT-A", "version": 3}
        old = {"id": "LIT-A", "version": 2}
        for payload in [old, {"reason": "repair", "records": [old]}, {"scope": "affected", "nodes": [old]}]:
            validate_prior_archive(current, payload)
        for payload in [{"id": "OTHER", "version": 1}, current, {"records": [old, old]}, {"nodes": []}]:
            with self.assertRaises(ValueError):
                validate_prior_archive(current, payload)


if __name__ == "__main__":
    unittest.main()
