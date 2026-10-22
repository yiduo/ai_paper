#!/usr/bin/env python3
"""Replay archived sources in a temporary directory and compare deterministic outputs."""

import argparse
import copy
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


def scientific_payload(experiment_id: str, name: str, payload):
    """Keep every scientific value; only EXP332's measured clocks/RSS vary.

    The frozen EXP332 specification explicitly separates timings from its
    deterministic calculation. Other archives retain exact payload comparison.
    """
    result = copy.deepcopy(payload)
    if experiment_id == 'EXP-332-001':
        if name == 'raw.json':
            for kernel in result[0]['kernels']:
                del kernel['build_seconds']
        elif name == 'summary.json':
            del result['runtime']
    return result


def replay(folder: Path) -> dict:
    manifest = json.loads((folder / "manifest.json").read_text())
    for name, expected in manifest["outputs"].items():
        if hashlib.sha256((folder / name).read_bytes()).hexdigest() != expected:
            raise ValueError("Corrupted archived output: " + name)
    snapshot = json.loads(gzip.decompress((folder / "inputs.json.gz").read_bytes()))
    with tempfile.TemporaryDirectory(prefix="ai-value-replay-") as temporary:
        root = Path(temporary)
        for relative, content in snapshot.items():
            target = root / relative
            if not target.resolve().is_relative_to(root.resolve()):
                raise ValueError("Unsafe snapshot path")
            if hashlib.sha256(content.encode()).hexdigest() != manifest["inputs"][relative]:
                raise ValueError("Corrupted archived source")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content)
        env = dict(os.environ, PYTHONPATH=str(root / "src"), PYTHONDONTWRITEBYTECODE="1")
        process = subprocess.run([sys.executable, "-m", "ai_value.cli", "experiment", manifest["experiment_id"]],
                                 cwd=root, env=env, text=True, capture_output=True, timeout=max(150, json.loads((root / "experiments/specs" / (manifest["experiment_id"]+".json")).read_text()).get("resource_limit_seconds", 120)+60), check=True)
        new_manifest = json.loads(process.stdout)
        new_folder = root / "experiments/runs" / new_manifest["run_id"]
        matched = {}
        for name in ("raw.json", "summary.json"):
            def payload(base, name):
                packed = base / (name + ".gz")
                return json.loads(gzip.decompress(packed.read_bytes())) if packed.exists() else json.loads((base / name).read_text())
            matched[name] = (scientific_payload(manifest['experiment_id'], name, payload(folder, name))
                             == scientific_payload(manifest['experiment_id'], name, payload(new_folder, name)))
        if not all(matched.values()):
            raise ValueError("Replay differs: " + str(matched))
        return {"run_id": manifest["run_id"], "replay_run_id": new_manifest["run_id"],
                "deterministic_outputs_match": matched,
                "comparison_scope": ("All exact inputs,outputs,risks,choices,judges and conclusions; only raw kernel build_seconds and summary runtime clocks/RSS excluded as preregistered"
                                     if manifest['experiment_id'] == 'EXP-332-001' else "Exact complete JSON payloads; no fields excluded"),
                "replay_resource_envelope_met": new_manifest.get('resource_envelope_met'),
                "runtime": sys.version, "isolation": "temporary directory; " + ("pinned optional packages from caller runtime; " if manifest.get("requires_optional_runtime") else "standard library; ") + "no upstream clone or credentials"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("run_folder", type=Path)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    result = replay(args.run_folder.resolve())
    if args.receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
