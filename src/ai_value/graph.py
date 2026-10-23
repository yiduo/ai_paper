"""Canonical graph checks, conservative dependency grades and human gates."""

from __future__ import annotations

import json
import math
import random
import re
import gzip
import hashlib
from pathlib import Path

from .corpus import digest
from .source_results import named_results
from .provenance import project_citations, validate_record_contract, validate_prior_archive

KINDS = {"claim", "method", "construction", "literature", "problem", "connection", "generation", "review", "withdrawal", "exploration", "family_analysis"}
EVIDENCE = {"source_claim", "source_content_checked", "hypothesis", "experiment_observation", "human_decision"}
CARD_FIELDS = {"title", "source_ids", "history_ids", "part_ids", "problem_id", "mechanism", "prediction",
               "test_spec", "run_ids", "opposition", "defense", "theoretical_grade", "sensitive", "resources",
               "owner", "workflow", "application_result", "limitations", "revisit_when", "dependency_closure_complete",
               "analogy", "dedup_key", "family_ids", "model_generation_id", "priority_reason"}


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def load(root: Path) -> tuple[dict[str, dict], list[dict]]:
    nodes = read_jsonl(root / "data/graph/nodes.jsonl")
    explicit_edges = read_jsonl(root / "data/graph/edges.jsonl")
    corpus = []
    for row in read_jsonl(root / "data/corpus/families.jsonl"):
        corpus.append({"id": row["id"], "kind": "family", "properties": row})
    for row in read_jsonl(root / "data/corpus/manuscripts.jsonl"):
        corpus.append({"id": row["id"], "kind": "manuscript", "properties": row})
    version_file = root / "data/corpus/historical_versions.jsonl"
    if version_file.exists():
        for row in read_jsonl(version_file):
            corpus.append({"id": row["id"], "kind": "historical_manuscript", "properties": row})
    derived_nodes, derived_edges = {}, []
    baseline = json.loads((root / "data/corpus/baseline.json").read_text())
    batch_id = "UPSTREAM-" + baseline["commit"].upper()
    derived_nodes[batch_id] = {"id": batch_id, "kind": "corpus_revision", "properties": baseline}
    def relation(a: str, name: str, b: str, locator: str) -> None:
        derived_edges.append({"id": "E-" + hashlib.sha256(f"{a}|{name}|{b}".encode()).hexdigest()[:16].upper(),
                              "source": a, "relation": name, "target": b, "version": 1,
                              "evidence_status": "source_content_checked", "source_locator": locator,
                              "source_commit": baseline["commit"], "created_at": "upstream-commit:" + baseline["commit"],
                              "derivation": "foreign-key projection from canonical corpus tables; no mathematical inference"})
    for node in corpus:
        prop = node["properties"]
        if node["kind"] == "historical_manuscript":
            relation(node["id"], "archived_member_of", prop["family_id"], prop["historical_path"])
            if prop.get("current_manuscript_id"):
                relation(prop["current_manuscript_id"], "supersedes", node["id"], prop["version_note"])
            continue
        if node["kind"] == "manuscript":
            relation(node["id"], "member_of", prop["family_id"], f'CONTENTS.md:{prop["catalogue_line"]}')
            relation(node["id"], "sourced_from_revision", batch_id, prop["path"])
        else:
            subject_id = "SUBJECT-" + hashlib.sha256(prop["subject"].encode()).hexdigest()[:12].upper()
            derived_nodes[subject_id] = {"id": subject_id, "kind": "subject", "properties": {"title": prop["subject"]}}
            relation(node["id"], "classified_as", subject_id, "overview.tex:cataloguesection/resultentry")
    source_nodes, source_edges = project_citations(nodes, baseline["commit"])
    derived_nodes.update(source_nodes)
    derived_edges.extend(source_edges)
    for node in nodes:
        if node["kind"] == "connection" or node["properties"].get("component_run_ids"):
            for run_id in node["properties"].get("run_ids", []) + node["properties"].get("component_run_ids", []):
                run_node_id = "RUN-" + run_id.upper()
                manifest_path = root / "experiments/runs" / run_id / "manifest.json"
                manifest = json.loads(manifest_path.read_text())
                derived_nodes[run_node_id] = {"id": run_node_id, "kind": "experiment_run", "properties": manifest}
                relation(node["id"], "externally_checked_by" if node['kind']=='connection' else 'component_checked_by', run_node_id, str(manifest_path.relative_to(root)))
                derived_edges[-1]["evidence_status"] = "experiment_observation"
    # Stage progress is projected from actual research records; registration alone
    # leaves all stages not_started, and a partial claim never completes a family.
    for family in (n for n in corpus if n["kind"] == "family"):
        fid = family["id"]
        claim_ids = {e["source"] for e in explicit_edges
                     if e["target"] == fid and e["relation"] == "member_of"}
        if claim_ids:
            family["properties"]["stages"]["1"] = "in_progress"
        for stage, present in (("2", any(e["source"] in claim_ids and e["relation"] == "historical_context" for e in explicit_edges)),
                               ("3", any(e["target"] in claim_ids and e["relation"] == "depends_on" for e in explicit_edges)),
                               ("4", any(fid in n["properties"].get("family_ids", []) for n in nodes if n["kind"] in {"connection", "exploration"})),
                               ("5", any(fid in n["properties"].get("family_ids", []) and n["properties"].get("run_ids") for n in nodes if n["kind"] == "connection"))):
            if present:
                family["properties"]["stages"][stage] = "in_progress"
    combined = corpus + nodes + list(derived_nodes.values())
    if len({n["id"] for n in combined}) != len(combined):
        raise ValueError("Duplicate graph node ID")
    return {n["id"]: n for n in combined}, explicit_edges + derived_edges


def validate_alternative_routes(nodes: dict[str, dict]) -> None:
    """Check explicit alternative-route references; never infer independence."""
    for owner, node in nodes.items():
        props = node.get("properties", {})
        if "alternative_proof_route_ids" not in props:
            continue
        routes = props["alternative_proof_route_ids"]
        if (node.get("kind") != "claim" or not isinstance(routes, list)
                or not routes or not all(isinstance(i, str) for i in routes)
                or len(set(routes)) != len(routes) or owner in routes
                or any(i not in nodes or nodes[i].get("kind") != "method" for i in routes)):
            raise ValueError("Invalid alternative proof routes: " + owner)


def affected_nodes(nodes: dict[str, dict], edges: list[dict], changed: set[str]) -> set[str]:
    """Route review after changes, including exhaustion of declared alternatives.

    Ordinary dependencies remain mandatory. An additional OR group triggers its
    owner only when every declared route is affected. An unaffected route is not
    evidence that it is correct, complete, independent, or verified. Cycles alone
    cannot initiate propagation: this computes the least fixed point from seeds.
    """
    validate_alternative_routes(nodes)
    if changed - nodes.keys():
        raise ValueError("Unknown changed node IDs: " + ", ".join(sorted(changed - nodes.keys())))
    affected = set(changed)
    while True:
        more = {e["source"] for e in edges if e["relation"] in {"depends_on", "uses", "derived_from", "cites"} and e["target"] in affected}
        more.update(owner for owner, node in nodes.items()
                    if node.get("properties", {}).get("alternative_proof_route_ids")
                    and set(node["properties"]["alternative_proof_route_ids"]) <= affected)
        if more <= affected:
            return affected
        affected |= more


def impact_report(nodes: dict[str, dict], edges: list[dict], changed: set[str]) -> dict:
    unknown = changed - nodes.keys()
    if unknown:
        raise ValueError("Unknown changed node IDs: " + ", ".join(sorted(unknown)))
    if not changed:
        raise ValueError("At least one changed node ID is required")
    affected = affected_nodes(nodes, edges, changed)
    groups = []
    for owner, node in sorted(nodes.items()):
        routes = node.get("properties", {}).get("alternative_proof_route_ids")
        if routes:
            hit = sorted(set(routes) & affected)
            groups.append({"claim_id": owner, "affected_routes": hit,
                           "unaffected_routes": sorted(set(routes) - affected),
                           "all_routes_affected": len(hit) == len(routes),
                           "claim_requires_review": owner in affected,
                           "claim_selected_as_changed": owner in changed})
    return {"changed": sorted(changed), "affected": sorted(affected),
            "additional_review": sorted(affected - changed), "alternative_routes": groups,
            "meaning": "Review routing from declared dependencies, not theorem refutation, proof verification, or a credibility upgrade. Unaffected does not mean verified."}


def theoretical_grade(nodes: dict[str, dict], edges: list[dict], node_id: str,
                      visiting: frozenset[str] = frozenset()) -> str:
    if node_id not in nodes or node_id in visiting:
        return "unknown"
    node = nodes[node_id]
    prop = node["properties"]
    own = prop.get("credibility", "unknown")
    if own == "D":
        return "D"
    deps = [e["target"] for e in edges if e["source"] == node_id and e["relation"] in {"depends_on", "uses", "derived_from"}]
    grades = [theoretical_grade(nodes, edges, target, visiting | {node_id}) for target in deps]
    if "D" in grades:
        return "D"
    if node["kind"] == "manuscript":
        # A manuscript catalogue entry is not a checked dependency closure.
        return own if prop.get("dependency_closure_complete") else "unknown"
    if not prop.get("dependency_closure_complete", False) or "unknown" in grades:
        return "unknown"
    known = [g for g in [own, *grades] if g in "ABCD" and g != "unknown"]
    return max(known, key="ABCD".index) if known else "unknown"


def human_gate(record: dict, reviews: list[dict], *, grade: str) -> None:
    relevant = [r for r in reviews if r.get("subject_id") == record["id"] and r.get("actor_type") == "human"
                and r.get("external_evidence") and r.get("reviewer_id")]
    props = record["properties"]
    if props.get("application_result") == "否定":
        reviewers = {r["reviewer_id"] for r in relevant if r.get("decision") == "confirm_rejection"}
        if len(reviewers) < 2:
            raise ValueError("Formal rejection requires two distinct real reviewers")
    if props.get("workflow") == "试点":
        if grade != "A" or not any(r.get("decision") == "approve_pilot" for r in relevant):
            raise ValueError("Pilot requires complete A dependencies and real human authorization")


def review_sample(ids: list[str], fraction: float, seed: int) -> list[str]:
    return sorted(random.Random(seed).sample(sorted(ids), math.ceil(len(ids)*fraction)))


def validate(root: Path) -> dict:
    nodes, edges = load(root)
    validate_alternative_routes(nodes)
    research = [n for n in nodes.values() if n["kind"] in KINDS]
    schema = json.loads((root / "schemas/graph-node.schema.json").read_text())
    # Clean-checkout checks can validate citations against the pinned complete
    # checksum manifest without downloading 3 GB. This is not a fresh content check.
    source_hashes = {}
    if any(s.get("path", "").startswith("math/") and not (root/s["path"]).exists()
           for n in research for s in n["sources"]):
        with gzip.open(root / "data/corpus/files.jsonl.gz", "rt") as stream:
            for line in stream:
                row = json.loads(line)
                source_hashes["math/" + row["path"]] = row["sha256"]
    reviews = [n["properties"] for n in research if n["kind"] == "review"]
    seen_edges, seen_connections = set(), set()
    source_count = 0
    for node in research:
        validate_record_contract(node, schema)
        updater = node.get("updated_by_generation_id")
        if updater and (updater not in nodes or nodes[updater]["kind"] != "generation"):
            raise ValueError("Invalid updating generation reference: " + node["id"])
        archive = node.get("prior_version_archive") or node["properties"].get("prior_version_archive")
        if archive:
            path = (root / archive).resolve()
            if not path.is_relative_to((root / "data/graph/history").resolve()) or not path.is_file():
                raise ValueError("Invalid prior-version archive: " + str(archive))
            previous = json.loads(gzip.decompress(path.read_bytes()))
            validate_prior_archive(node, previous)
        if not re.fullmatch(r"[A-Z][A-Z0-9-]*", node["id"]):
            raise ValueError("Invalid stable node ID: " + node["id"])
        if node["kind"] not in KINDS or node["evidence_status"] not in EVIDENCE:
            raise ValueError("Invalid graph type/evidence status")
        if node['properties'].get('credibility', 'unknown') not in {'A','B','C','D','unknown'}:
            raise ValueError('Invalid mathematical grade')
        if node["properties"].get("credibility") == "A":
            if not any(r.get("subject_id") == node["id"] and r.get("actor_type") == "human"
                       and r.get("decision") == "confirm_specification" and r.get("external_evidence") for r in reviews):
                raise ValueError("A grade requires an actual human specification-review record")
        if not node.get("created_at") or node.get("version", 0) < 1 or not node.get("sources"):
            raise ValueError("Missing version, timestamp or sources: " + node["id"])
        for source in node["sources"]:
            if not source.get("locator"):
                raise ValueError("Source requires precise locator")
            if "path" in source:
                path = (root / source["path"]).resolve()
                actual = digest(path) if path.exists() else source_hashes.get(source["path"])
                if not path.is_relative_to(root.resolve()) or actual != source["sha256"]:
                    raise ValueError("Changed or invalid cited file: " + source["path"])
            elif not source.get("url", "").startswith("https://") or source.get("content_checked") not in {True, False}:
                raise ValueError("Invalid external citation record")
            source_count += 1
        if node['kind']=='family_analysis':
            prop = node['properties']
            references = prop['result_ids_by_label'].values()
            if any(ref not in nodes for ref in references):
                raise ValueError('Family decomposition references a missing result')
            unlabelled = prop.get('unlabelled_result_ids', [])
            if len(unlabelled) != len(set(unlabelled)) or set(unlabelled) & set(references):
                raise ValueError('Duplicate labelled or unlabelled source result')
            for ref in unlabelled:
                if ref not in nodes or nodes[ref]['kind'] != 'claim':
                    raise ValueError('Unlabelled source result must reference a claim')
                if prop['family_id'] not in nodes[ref]['properties'].get('family_ids', []):
                    raise ValueError('Unlabelled source result belongs to another family')
                if not any(source.get('path') in prop['source_sections']
                           for source in nodes[ref]['sources']):
                    raise ValueError('Unlabelled source result has no declared source module')
            if prop.get('full_family_complete') and not prop.get('historical_lineage_complete'):
                raise ValueError('Complete family cannot omit historical lineage')
            if prop.get('source_decomposition_draft_complete') or prop.get('manuscript_source_drafts_complete_ids'):
                manuscript_ids = set(prop['manuscript_ids'])
                read_ids = set(prop.get('manuscript_source_drafts_complete_ids',manuscript_ids))
                if not read_ids or not read_ids <= manuscript_ids:
                    raise ValueError('Read manuscript IDs must belong to the analyzed family')
                if prop.get('source_decomposition_draft_complete') and read_ids != manuscript_ids:
                    raise ValueError('A partial manuscript set cannot complete a family source draft')
                covered = set()
                for section in prop['source_sections']:
                    owners = {i for i in read_ids if i in nodes and
                              section.startswith('math/'+str(Path(nodes[i]['properties']['path']).parent)+'/')}
                    if len(owners) != 1:
                        raise ValueError('Source module must belong to one declared read manuscript')
                    covered.update(owners)
                if covered != read_ids:
                    raise ValueError('Read manuscript has no declared source module')
                labels = set()
                by_source = prop.get('result_ids_by_source')
                if len(prop.get('manuscript_ids', [])) > 1 and not by_source:
                    raise ValueError('Multi-manuscript decomposition requires per-source result bindings')
                for source in prop['source_sections']:
                    path = root/source
                    if path.exists():
                        found = {item['label'] for item in named_results(path.read_text())}
                        if by_source is not None and found != set(by_source.get(source, {})):
                            raise ValueError('Per-source decomposition omits or adds named results: '+source)
                        labels.update(found)
                if by_source is not None:
                    bound = [ref for mapping in by_source.values() for ref in mapping.values()]
                    if set(by_source) != set(prop['source_sections']) or set(bound) != set(references):
                        raise ValueError('Invalid per-source result bindings')
                elif labels and labels != set(prop['result_ids_by_label']):
                    raise ValueError('Family decomposition omits or adds named source results')
        for run_id in node['properties'].get('component_run_ids', []):
            folder = root/'experiments/runs'/run_id
            manifest = json.loads((folder/'manifest.json').read_text())
            for name,expected in manifest['outputs'].items():
                if digest(folder/name) != expected:
                    raise ValueError('Component check evidence changed')
        if node["kind"] == "connection":
            props = node["properties"]
            missing = CARD_FIELDS-props.keys()
            if missing:
                raise ValueError("Missing card fields: " + str(missing))
            if props["dedup_key"] in seen_connections:
                raise ValueError("Duplicate application hypothesis")
            seen_connections.add(props["dedup_key"])
            for ref in props["source_ids"] + props["history_ids"] + props["part_ids"] + props["family_ids"] + [props["problem_id"], props["model_generation_id"]]:
                if ref not in nodes:
                    raise ValueError("Dangling card reference: " + ref)
            if props["application_result"] not in {"通过", "待定", "观察", "否定"}:
                raise ValueError("Invalid application result")
            if props["sensitive"]:
                raise ValueError("Controlled material must not be placed in the public graph")
            for run_id in props["run_ids"]:
                folder = root / "experiments/runs" / run_id
                manifest = json.loads((folder / "manifest.json").read_text())
                run_spec = json.loads((folder / "spec.json").read_text())
                if run_spec["connection_id"] != node["id"]:
                    raise ValueError("Experiment belongs to a different hypothesis")
                if props["application_result"] == "通过" and manifest["result"] != "passes_preregistered_prediction":
                    raise ValueError("Supported application result needs a supporting preregistered run")
                for name, expected in manifest["outputs"].items():
                    if digest(folder / name) != expected:
                        raise ValueError("Experiment evidence changed")
            if props["application_result"] == "通过" and not props["run_ids"]:
                raise ValueError("Supported card has no actual external check")
            grade = theoretical_grade(nodes, edges, node["id"])
            if props["theoretical_grade"] != grade:
                raise ValueError("Card overstates dependency grade")
            human_gate(node, reviews, grade=grade)
    for edge in edges:
        if edge["id"] in seen_edges or edge["source"] not in nodes or edge["target"] not in nodes:
            raise ValueError("Duplicate or dangling graph edge")
        if edge.get("evidence_status") not in EVIDENCE or not edge.get("source_locator") or not edge.get("created_at"):
            raise ValueError("Edge lacks evidence or timestamp")
        seen_edges.add(edge["id"])
    cards = [n for n in research if n["kind"] == "connection"]
    return {"nodes": len(nodes), "research_nodes": len(research), "edges": len(edges),
            "citations_checked": source_count, "candidate_connections": len(cards),
            "externally_checked_cards": sum(bool(n["properties"]["run_ids"]) for n in cards),
            "effective_leads": sum(n["properties"]["application_result"] == "通过" for n in cards),
            "distinct_validation_hypotheses": len({n["properties"]["dedup_key"] for n in cards if n["properties"]["run_ids"]}),
            "human_grading_records": sum(r.get("actor_type") == "human" and r.get("decision") == "grade_connection" and bool(r.get("external_evidence")) for r in reviews),
            "pilots": sum(n["properties"]["workflow"] == "试点" for n in cards)}
