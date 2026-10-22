"""Import catalogue entries, never infer manuscript counts from PDF counts."""

from __future__ import annotations

import hashlib
import gzip
import json
import re
import subprocess
from collections import Counter
from pathlib import Path


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git(upstream: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(upstream), *args], text=True)


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows))


def parse_catalogue(text: str) -> tuple[list[dict], list[dict]]:
    families, papers = [], []
    current = None
    for line_number, line in enumerate(text.splitlines(), 1):
        match = re.match(r"\*\*(\d{3})\. (.*?)\*\*(.*)", line)
        if match:
            current = match[1]
            families.append({"id": "F-" + current, "number": current,
                             "title": match[2], "catalogue_claim": match[3].strip(),
                             "catalogue_line": line_number})
        # Greedy PDF target deliberately handles CAT(0) directory names.
        match = re.match(r"&emsp;\[(.*)\]\((preprints/.*\.pdf)\)", line)
        if match:
            if current is None:
                raise ValueError("Manuscript without a result family")
            papers.append({"family_id": "F-" + current, "title": match[1],
                           "path": match[2], "catalogue_line": line_number})
    if len({f["id"] for f in families}) != len(families):
        raise ValueError("Duplicate family identifier")
    if len({p["path"] for p in papers}) != len(papers):
        raise ValueError("Duplicate catalogue manuscript path")
    return families, papers


def subject_map(text: str) -> dict[str, str]:
    result, subject = {}, None
    for line in text.splitlines():
        match = re.match(r"\\cataloguesection\{([^}]+)\}", line)
        if match:
            subject = match[1]
        match = re.match(r"\\resultentry\{(\d{3})\}", line)
        if match:
            result["F-" + match[1]] = subject
    return result


def reconcile(old: list[dict], new: list[dict], upstream: Path) -> list[dict]:
    paths = {p["path"]: p for p in new}
    rows = []
    for paper in old:
        path = paper["path"]
        row = {"old_path": path, "family_id": paper["family_id"], "old_title": paper["title"]}
        if path in paths:
            row.update(status="unchanged_catalogue_path", new_path=path,
                       evidence=["CONTENTS.md:old-and-current-exact-path"])
        else:
            readme = upstream / Path(path).parent / "README.md"
            body = readme.read_text() if readme.exists() else ""
            if "**Withdrawn on" in body:
                row.update(status="withdrawn_proof", new_path=None,
                           evidence=[str(readme.relative_to(upstream)), "history.md:October-7-2026"],
                           statement_false=False)
            else:
                matches = []
                for candidate in new:
                    if candidate["family_id"] != paper["family_id"]:
                        continue
                    rp = upstream / Path(candidate["path"]).parent / "README.md"
                    # Explicit previous-version link, not merely a similar title.
                    if rp.exists() and ("../" + path.removeprefix("preprints/")) in rp.read_text():
                        matches.append((candidate, rp))
                if len(matches) == 1:
                    candidate, rp = matches[0]
                    row.update(status="revised_explicit_version_link", new_path=candidate["path"],
                               evidence=[str(rp.relative_to(upstream)) + ":Version-note"])
                else:
                    row.update(status="unresolved", new_path=None,
                               evidence=[], candidate_count=len(matches))
        rows.append(row)
    return rows


def inventory(root: Path) -> dict:
    upstream = root / "math"
    config = json.loads((root / "configs/research.json").read_text())
    commit = git(upstream, "rev-parse", "HEAD").strip()
    if commit != config["baseline_commit"]:
        raise ValueError("Upstream changed; create and review an explicit new batch before importing")
    if git(upstream, "status", "--porcelain"):
        raise ValueError("Upstream has local changes; baseline evidence must be clean")
    tracked = git(upstream, "ls-files", "-z").split("\0")
    files = []
    for relative in sorted(filter(None, tracked)):
        path = upstream / relative
        files.append({"path": relative, "bytes": path.stat().st_size, "sha256": digest(path)})
    hashes = {f["path"]: f["sha256"] for f in files}
    text = (upstream / "CONTENTS.md").read_text()
    families, papers = parse_catalogue(text)
    old_text = git(upstream, "show", config["historical_commit"] + ":CONTENTS.md")
    old_families, old_papers = parse_catalogue(old_text)
    reconciliation = reconcile(old_papers, papers, upstream)
    subjects = subject_map((upstream / "overview.tex").read_text())
    formal = (upstream / "lean/formalization.yaml").read_text()
    formal_paths = set(re.findall(r"^    id: \.\./(preprints/.*\.pdf)$", formal, re.M))
    scope_paths: dict[str, list[str]] = {}
    for scope in sorted((upstream / "lean/docs").glob("*.md")):
        for path in re.findall(r"\]\(\.\./\.\./(preprints/.*\.pdf)\)", scope.read_text()):
            scope_paths.setdefault(path, []).append(str(scope.relative_to(upstream)))
    for paper in papers:
        paper.update(id="P-" + hashlib.sha256(paper["path"].encode()).hexdigest()[:16],
                     commit=commit, sha256=hashes[paper["path"]],
                     status="catalogued_not_withdrawn", upstream_formalization_claim=paper["path"] in formal_paths,
                     local_lean_build="not_run", comparator="not_run", human_spec_review="missing",
                     formalization_scope_notes=scope_paths.get(paper["path"], []),
                     credibility="unknown", scope_review="not_assessed",
                     credibility_basis="Automated source registration does not establish per-claim main/support coverage. See graph claims for reviewed scopes.",
                     readme=str(Path(paper["path"]).parent / "README.md"))
    for family in families:
        members = [p for p in papers if p["family_id"] == family["id"]]
        family.update(subject=subjects.get(family["id"], "unknown"),
                      manuscript_ids=[p["id"] for p in members],
                      credibility_distribution=dict(Counter(p["credibility"] for p in members)),
                      family_credibility="not_assessed_as_a_whole",
                      withdrawn_paths=[r["old_path"] for r in reconciliation
                                       if r["family_id"] == family["id"] and r["status"] == "withdrawn_proof"],
                      stages={str(i): "not_started" for i in range(1, 7)},
                      gaps=["full-text decomposition", "verified historical lineage", "method extraction",
                            "ten-domain exploration", "external application check", "human review"],
                      source={"commit": commit, "path": "CONTENTS.md", "line": family["catalogue_line"]})
    counts = Counter(r["status"] for r in reconciliation)
    covered = {r["new_path"] for r in reconciliation if r["new_path"]}
    summary = {"schema_version": "1.0", "upstream_url": git(upstream, "remote", "get-url", "origin").strip(),
               "commit": commit, "historical_commit": config["historical_commit"],
               "families": len(families), "historical_families": len(old_families),
               "catalogued_manuscripts": len(papers), "historical_manuscripts": len(old_papers),
               "reconciliation": dict(counts),
               "unmapped_new_paths": sorted(set(p["path"] for p in papers) - covered),
               "formalization_catalogue_sources": len(formal_paths),
               "processing_version": "2-scope-aware-conservative-grading",
               "scope_notes_linked_current_manuscripts": sum(p["path"] in scope_paths for p in papers),
               "catalogued_sources_in_formalization_catalogue": sum(p["upstream_formalization_claim"] for p in papers),
               "tracked_files": len(files), "preprint_pdfs": sum(f["path"].startswith("preprints/") and f["path"].endswith(".pdf") for f in files),
               "subject_distribution": dict(Counter(f["subject"] for f in families)),
               "unavailable": ["approximately 4000 evaluation prompts are not a supplied public question dataset",
                               "human specification reviews", "independent second-provider mapping reviews"],
               "count_basis": "catalogue manuscript entries; PDF files and directories are not paper counts"}
    out = root / "data/corpus"
    write_json(out / "baseline.json", summary)
    # The upstream includes >100k vendored TeX runtime files. A deterministic
    # compressed manifest preserves full checksums without duplicating the corpus.
    with (out / "files.jsonl.gz").open("wb") as target:
        with gzip.GzipFile(filename="", mode="wb", fileobj=target, mtime=0) as zipped:
            for row in files:
                zipped.write((json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n").encode())
    write_jsonl(out / "manuscripts.jsonl", papers)
    write_jsonl(out / "families.jsonl", families)
    write_jsonl(out / "reconciliation.jsonl", reconciliation)
    return summary
