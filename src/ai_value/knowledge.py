"""Typed graph traversal and portable exports. All exports derive from graph.load."""

from __future__ import annotations

import gzip
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from .graph import load


def neighborhood(root: Path, node_id: str, depth: int = 2) -> dict:
    nodes, edges = load(root)
    if node_id not in nodes:
        raise ValueError("Unknown node ID: " + node_id)
    selected, frontier = {node_id}, {node_id}
    for _ in range(depth):
        adjacent = {e["target"] for e in edges if e["source"] in frontier} | {e["source"] for e in edges if e["target"] in frontier}
        # Do not expand global revision/subject hubs into every unrelated family.
        frontier = {i for i in adjacent-selected if nodes[i]["kind"] not in {"corpus_revision", "subject"}}
        selected |= adjacent
    return {"center": node_id, "nodes": [nodes[i] for i in sorted(selected)],
            "edges": [e for e in edges if e["source"] in selected and e["target"] in selected]}


def export(root: Path) -> dict:
    nodes, edges = load(root)
    out = root / "reports/graph"
    out.mkdir(parents=True, exist_ok=True)
    ns = "http://graphml.graphdrawing.org/xmlns"
    ET.register_namespace('', ns)
    tree = ET.Element("{"+ns+"}graphml")
    for id, target in (("kind", "node"), ("properties", "node"), ("relation", "edge"), ("evidence", "edge")):
        ET.SubElement(tree, "key", {"id": id, "for": target, "attr.name": id, "attr.type": "string"})
    graph = ET.SubElement(tree, "graph", {"id": "ai-math-value", "edgedefault": "directed"})
    for node in sorted(nodes.values(), key=lambda n: n["id"]):
        element = ET.SubElement(graph, "node", {"id": node["id"]})
        ET.SubElement(element, "data", {"key": "kind"}).text = node["kind"]
        ET.SubElement(element, "data", {"key": "properties"}).text = json.dumps(node, ensure_ascii=False, sort_keys=True)
    for edge in edges:
        element = ET.SubElement(graph, "edge", {k: edge[k] for k in ("id", "source", "target")})
        ET.SubElement(element, "data", {"key": "relation"}).text = edge["relation"]
        ET.SubElement(element, "data", {"key": "evidence"}).text = json.dumps(edge, ensure_ascii=False, sort_keys=True)
    packed = gzip.compress(ET.tostring(tree, encoding="utf-8", xml_declaration=True), mtime=0)
    (out / "knowledge.graphml.gz").write_bytes(packed)
    payload = json.dumps({"nodes": list(nodes.values()), "edges": edges}, ensure_ascii=False, separators=(',', ':'))
    (out / "knowledge.json.gz").write_bytes(gzip.compress(payload.encode(), mtime=0))
    # Interactive graph inspector uses a compact family -> manuscript/claim ->
    # part/application neighborhood, rather than drawing 1k unreadable nodes.
    template = (root / "src/ai_value/graph_view.html").read_text()
    impact_script = (root / "src/ai_value/impact.js").read_text()
    (out / "index.html").write_text(template.replace("__IMPACT_LOGIC__", impact_script)
                                  .replace("__GRAPH_DATA__", payload.replace('</', '<\\/')))
    from .navigation import export_navigation
    navigation = export_navigation(root)
    return {"nodes": len(nodes), "edges": len(edges), "graphml_gzip_bytes": len(packed),
            "viewer": "reports/graph/index.html", "navigation": navigation}
