"""Lossless citation projections; an unpinned URL is not a content identity."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from urllib.parse import unquote, urlparse
import re


def source_identity(source: dict) -> tuple[str, str]:
    address = source.get("path", source.get("url", ""))
    content_hash = source.get("sha256") or source.get("source_file_sha256")
    if content_hash:
        basis = "path_and_content_hash" if "path" in source else "url_and_content_hash"
        # Preserve the existing IDs for citations already keyed by actual bytes.
        return address + "|" + content_hash, basis
    if source.get("source_revision"):
        return address + "|revision:" + source["source_revision"], "url_and_explicit_revision"
    # Locators and check times can distinguish versions behind the same URL.
    # Keep the entire observation when no byte hash/revision resolves identity.
    observation = json.dumps(source, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return address + "|unresolved-observation:" + observation, "unresolved_external_observation"


def project_citations(research: list[dict], commit: str) -> tuple[dict, list[dict]]:
    artifacts, grouped = {}, {}
    for node in research:
        for index, source in enumerate(node["sources"]):
            identity, basis = source_identity(source)
            sid = "SOURCE-" + hashlib.sha256(identity.encode()).hexdigest()[:16].upper()
            if sid not in artifacts:
                properties = {
                    "title": source.get("path", source.get("url")),
                    "identity_basis": basis,
                    "content_check_scope": "Per citation annotation only; no global proof or version claim",
                    "citation_annotations": [],
                }
                for key in ("path", "url", "sha256", "source_file_sha256"):
                    if key in source:
                        properties[key] = source[key]
                if basis == "url_and_explicit_revision":
                    properties["source_revision"] = source["source_revision"]
                artifacts[sid] = {"id": sid, "kind": "source_artifact", "properties": properties}
            artifacts[sid]["properties"]["citation_annotations"].append(
                {"citing_node_id": node["id"], "source_index": index, "source": dict(source)}
            )
            grouped.setdefault((node["id"], sid), []).append((index, source["locator"]))
    edges = []
    for (nid, sid), citations in sorted(grouped.items()):
        edges.append({
            "id": "E-" + hashlib.sha256(f"{nid}|cites|{sid}".encode()).hexdigest()[:16].upper(),
            "source": nid, "relation": "cites", "target": sid, "version": 1,
            "evidence_status": "source_content_checked",
            "source_locator": " / ".join(dict.fromkeys(locator for _, locator in citations)),
            "citation_source_indices": [index for index, _ in citations],
            "source_commit": commit, "created_at": "upstream-commit:" + commit,
            "derivation": "Lossless canonical citation projection; identity does not certify mathematical content",
        })
    for artifact in artifacts.values():
        artifact["properties"]["citation_annotations"].sort(
            key=lambda a: (a["citing_node_id"], a["source_index"]))
    return artifacts, edges


def validate_record_contract(node: dict, schema: dict) -> None:
    """Enforce this repository's node envelope, not an arbitrary JSON Schema engine."""
    missing = set(schema["required"]) - node.keys()
    extra = node.keys() - schema["properties"].keys()
    if missing or extra:
        raise ValueError(f"Invalid research-node fields {node.get('id')}: missing={sorted(missing)}, extra={sorted(extra)}")
    if type(node["version"]) is not int or node["version"] < 1:
        raise ValueError("Node version must be a positive integer")
    if not isinstance(node["properties"], dict) or not isinstance(node["sources"], list):
        raise ValueError("Invalid node properties/sources types")
    if not node["sources"] or any(not isinstance(s, dict) or not isinstance(s.get("locator"), str)
                                   or not s["locator"].strip() for s in node["sources"]):
        raise ValueError("Node requires nonempty source locators")
    for key in ("prior_version_archive", "updated_by_generation_id"):
        if key in node and (not isinstance(node[key], str)
                            or not re.fullmatch(schema["properties"][key]["pattern"], node[key])):
            raise ValueError("Invalid node version metadata: " + key)
    for key in ("created_at", "updated_at"):
        if key in node:
            try:
                stamp = datetime.fromisoformat(node[key].replace("Z", "+00:00"))
            except (ValueError, TypeError, AttributeError) as exc:
                raise ValueError("Invalid node timestamp: " + key) from exc
            if stamp.tzinfo is None:
                raise ValueError("Node timestamp requires timezone: " + key)


def validate_prior_archive(node: dict, payload: dict) -> None:
    # Historical repairs used both a single-node file and compact batch wrappers.
    records = [payload] if "id" in payload else payload.get("records", payload.get("nodes", []))
    matches = [old for old in records if old.get("id") == node["id"]]
    if len(matches) != 1 or not 1 <= matches[0].get("version", 0) < node["version"]:
        raise ValueError("Prior-version archive identity/version mismatch: " + node["id"])


def literature_identity_candidates(nodes: dict) -> list[dict]:
    """Exact identifier groups for review; never merge works or source versions."""
    groups = {}
    for node in nodes.values():
        if node["kind"] != "literature":
            continue
        prop = node["properties"]
        identifiers = set()
        doi = prop.get("doi")
        if isinstance(doi, str) and re.fullmatch(r"10\.\d{4,9}/\S+", doi.strip(), re.I):
            identifiers.add("doi:" + doi.strip().lower())
        urls = [s.get("url", "") for s in node.get("sources", [])]
        urls.append(prop.get("original_link") or "")
        for url in urls:
            parsed = urlparse(url)
            path = unquote(parsed.path).strip("/")
            if parsed.hostname in {"doi.org", "dx.doi.org"} and re.fullmatch(r"10\.\d{4,9}/\S+", path, re.I):
                identifiers.add("doi:" + path.lower())
            if parsed.hostname in {"arxiv.org", "export.arxiv.org"}:
                match = re.fullmatch(r"(?:abs|pdf|html)/((?:\d{4}\.\d{4,5}|[a-zA-Z.-]+/\d{7}))(?:v\d+)?(?:\.pdf)?", path)
                if match:
                    identifiers.add("arxiv-work:" + match[1].lower())
        for identifier in identifiers:
            groups.setdefault(identifier, set()).add(node["id"])
    return [{"identifier": key, "node_ids": sorted(ids),
             "decision": "Review candidate only; no work/version merge or evidence promotion"}
            for key, ids in sorted(groups.items()) if len(ids) > 1]
