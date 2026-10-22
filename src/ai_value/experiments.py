"""Preregistered small experiments with content-addressed, immutable run folders."""

from __future__ import annotations

import itertools
import gzip
import json
import math
import platform
import random
import statistics
import sys
import time
import tracemalloc
from datetime import datetime, timezone
from decimal import Decimal, localcontext
from pathlib import Path

from .corpus import digest, write_json
from .prefix import exact_order, greedy_order, normalized_peak, optimal_signs, peak_squared, transfer_order
from .superstring import exact_scs, forced_counts, greedy_scs, lower_bound


def scs_experiment(spec: dict) -> tuple[list[dict], dict]:
    words = ["".join(bits) for n in range(1, 4) for bits in itertools.product("01", repeat=n)]
    instances = [("exhaustive_binary", list(s)) for n in range(4) for s in itertools.combinations(words, n)]
    rng = random.Random(spec["input"]["seed"])
    instances += [("held_out_DNA_like", ["".join(rng.choice("ACGT") for _ in range(6))
                                         for _ in range(4)]) for _ in range(40)]
    rows = []
    for index, (stratum, strings) in enumerate(instances):
        optimum = exact_scs(strings)
        greedy = greedy_scs(strings)
        counts = forced_counts(strings)
        extension = lower_bound(strings, periodic=False)
        forced = sum(value for word, value in counts.items() if len(word) == 1)
        bad_occurrences = {s: count for s, count in counts.items()
                           if count > sum(optimum.startswith(s, i) for i in range(len(optimum)))}
        rows.append({"instance": index, "stratum": stratum, "strings": strings,
                     "exact_superstring": optimum, "greedy_superstring": greedy,
                     "exact_length": len(optimum), "greedy_length": len(greedy),
                     "extension_bound": extension, "forced_bound": forced,
                     "soundness_violation": forced > len(optimum) or bool(bad_occurrences),
                     "occurrence_violations": bad_occurrences,
                     "extension_certified": len(greedy) <= 2*extension,
                     "forced_certified": len(greedy) <= 2*forced,
                     "contains_inputs": all(s in greedy for s in strings)})
    n = len(rows)
    ext = sum(r["extension_certified"] for r in rows)
    forced = sum(r["forced_certified"] for r in rows)
    violations = sum(r["soundness_violation"] or not r["contains_inputs"] for r in rows)
    gain = 100*(forced-ext)/n
    by_stratum = {}
    for name in sorted({r["stratum"] for r in rows}):
        group = [r for r in rows if r["stratum"] == name]
        by_stratum[name] = {"n": len(group), "extension_certified": sum(r["extension_certified"] for r in group),
                            "forced_certified": sum(r["forced_certified"] for r in group),
                            "strictly_tighter_bounds": sum(r["forced_bound"] > r["extension_bound"] for r in group)}
    return rows, {"instances": n, "soundness_violations": violations,
                  "extension_certified": ext, "forced_certified": forced,
                  "certification_gain_percentage_points": gain, "strata": by_stratum,
                  "meets_prediction": violations == 0 and gain >= spec["success"]["certification_gain_percentage_points_min"],
                  "interpretation": "finite synthetic certificate evidence; neither general theorem verification nor full 2-approximation algorithm"}


def prefix_experiment(spec: dict) -> tuple[list[dict], dict]:
    rng = random.Random(spec["input"]["seed"])
    rows = []
    for dimension in (2, 4, 8):
        for trial in range(20):
            half = [[rng.randint(-4, 4) for _ in range(dimension)] for _ in range(4)]
            if trial % 3 == 2:
                half = [[rng.randint(1, 4)] + [0]*(dimension-1) for _ in range(4)]
            vectors = half + [[-x for x in vector] for vector in half]
            stratum = ["random", "sorted", "collinear"][trial % 3]
            if stratum == "random":
                rng.shuffle(vectors)
            elif stratum == "sorted":
                vectors.sort()
            signs = optimal_signs(vectors)
            transfer = transfer_order(vectors)
            greedy = greedy_order(vectors)
            exact, optimum_squared = exact_order(vectors)
            fifo = list(range(len(vectors)))
            transfer_squared = peak_squared(vectors, transfer)
            rhs = (math.sqrt(peak_squared(vectors)) + math.sqrt(peak_squared(vectors, signs=signs)))/2
            rows.append({"instance": len(rows), "dimension": dimension, "stratum": stratum,
                         "vectors": vectors, "signs": signs, "transfer_order": transfer,
                         "greedy_order": greedy, "optimal_order": exact,
                         "fifo_peak": normalized_peak(vectors, fifo),
                         "transfer_peak": normalized_peak(vectors, transfer),
                         "greedy_peak": normalized_peak(vectors, greedy),
                         "optimal_peak": normalized_peak(vectors, exact),
                         "optimal_squared": optimum_squared,
                         "permutation_integrity": sorted(transfer) == fifo,
                         "transfer_inequality_violation": math.sqrt(transfer_squared) > rhs + 1e-10})
    mean = lambda key: statistics.mean(r[key] for r in rows)
    reduction = 1-mean("transfer_peak")/mean("fifo_peak")
    ratio = mean("transfer_peak")/mean("greedy_peak")
    violations = sum(r["transfer_inequality_violation"] or not r["permutation_integrity"] for r in rows)
    return rows, {"instances": len(rows), "mean_fifo_peak": mean("fifo_peak"),
                  "mean_transfer_peak": mean("transfer_peak"), "mean_greedy_peak": mean("greedy_peak"),
                  "mean_optimal_peak": mean("optimal_peak"), "mean_reduction_vs_fifo": reduction,
                  "mean_transfer_vs_greedy": ratio, "transfer_inequality_violations": violations,
                  "strata": {name: {"n": len([r for r in rows if r["stratum"] == name]),
                                     "mean_transfer_minus_greedy": statistics.mean(r["transfer_peak"]-r["greedy_peak"] for r in rows if r["stratum"] == name)}
                             for name in ("random", "sorted", "collinear")},
                  "meets_prediction": reduction >= spec["success"]["mean_reduction_vs_fifo_min"] and ratio <= spec["success"]["mean_transfer_vs_greedy_max"] and violations == 0,
                  "interpretation": "finite offline transfer test; historical technique; incremental application gain from new sqrt(d) theorem not demonstrated"}


def fourier_experiment(spec: dict) -> tuple[list[dict], dict]:
    rows = []
    with localcontext() as ctx:
        ctx.prec = spec["input"]["precision_decimal_digits"]
        delta = Decimal(spec["input"]["delta"])
        for k in range(spec["input"]["k_min"], spec["input"]["k_max"]+1):
            n = 2**k
            saving = 1-(-delta*Decimal(n).ln().ln()).exp()
            rows.append({"k": k, "n": n, "favorable_proxy_relative_saving": str(saving)})
        maximum = max(Decimal(r["favorable_proxy_relative_saving"]) for r in rows)
        threshold = -(1-Decimal("0.01")).ln()/delta
        return rows, {"instances": len(rows), "maximum_relative_saving": str(maximum),
                      "one_percent_threshold_ln_ln_n": str(threshold),
                      "materialized_W_roles": str(2**71),
                      "conditional_minimum_16_byte_scalar_storage_bytes": str(16*2**71),
                      "meets_prediction": maximum >= Decimal(spec["success"]["maximum_relative_saving_min"]),
                      "interpretation": "practical speedup prediction unsupported even under favorable exponent-only proxy; not a theorem refutation or measured speed benchmark"}


RUNNERS = {"EXP-128-001": scs_experiment, "EXP-097-001": prefix_experiment, "EXP-130-001": fourier_experiment}


def transport_experiment(spec: dict) -> tuple[list[dict], dict]:
    from fractions import Fraction
    from .transport import three_atom_example
    rows = []
    for k in range(spec['input']['k_min'],spec['input']['k_max']+1):
        a = Fraction(1,2**k)
        exact = three_atom_example(a)
        map2, w2 = exact['map_L2_squared'], exact['target_W2_squared']
        map_distance, target_distance = math.sqrt(map2), math.sqrt(w2)
        mismatches = map2 != a/4+a**3/4 or w2 != a**3/4
        mass_bad = (exact['source_masses'] != exact['target_masses'] or sum(exact['source_masses'])!=1
                    or sum(sum(row) for row in exact['overlap_masses'])!=1)
        rows.append({'k':k,'a':str(a),'map_L2_squared':str(map2),'target_W2_squared':str(w2),
                     'source_masses':list(map(str,exact['source_masses'])),
                     'target_masses':list(map(str,exact['target_masses'])),
                     'overlap_masses':[[str(x) for x in row] for row in exact['overlap_masses']],
                     'half_power_ratio':map_distance/target_distance**0.5,
                     'one_third_ratio':map_distance/target_distance**(1/3),
                     'formula_mismatch':mismatches,'mass_violation':mass_bad})
    growth = rows[-1]['half_power_ratio']/rows[0]['half_power_ratio']
    ratios = [r['one_third_ratio'] for r in rows]
    variation = max(ratios)/min(ratios)
    bad = sum(r['formula_mismatch'] or r['mass_violation'] for r in rows)
    return rows, {'instances':len(rows),'exact_formula_or_mass_mismatches':bad,
                  'half_power_ratio_growth':growth,'one_third_ratio_max_over_min':variation,
                  'meets_prediction':bad==0 and growth>=spec['success']['half_power_ratio_growth_min'] and variation<=spec['success']['one_third_ratio_max_over_min'],
                  'interpretation':'finite-scale exact source-derived regression fixture supports the declared diagnostic, not a general theorem proof or production solver benefit'}


RUNNERS['EXP-374-001'] = transport_experiment

from .component_checks import moments as moments_component_check

RUNNERS['CHK-374-MOMENTS-001'] = moments_component_check

from .permutation_audit import experiment as permutation_audit_experiment

RUNNERS['EXP-238-001'] = permutation_audit_experiment

from .betti_budget import experiment as betti_budget_experiment
from .betti_budget import lex_source_audit

RUNNERS['EXP-200-001'] = betti_budget_experiment
RUNNERS['CHK-200-LEX-001'] = lex_source_audit

from .pressure_audit import experiment as pressure_audit_experiment

RUNNERS['EXP-221-001'] = pressure_audit_experiment

from .cyclic_chain import experiment as cyclic_chain_experiment

RUNNERS['EXP-314-001'] = cyclic_chain_experiment

from .block_budget import run as block_budget_experiment

RUNNERS['EXP-325-001'] = block_budget_experiment

from .phase_rounding import run as phase_rounding_experiment

RUNNERS['EXP-076-002'] = phase_rounding_experiment

from .binary_information import run as binary_information_experiment
RUNNERS['EXP-119-001'] = binary_information_experiment


def bosonic_experiment(spec: dict):
    # Keep the standard-library core and historic experiments dependency free.
    from .bosonic_regression import run as evaluate
    return evaluate(spec)


RUNNERS['EXP-273-001'] = bosonic_experiment

from .graph_smoothing import run as graph_smoothing_experiment
RUNNERS['EXP-332-001'] = graph_smoothing_experiment


def run(root: Path, experiment_id: str) -> dict:
    spec_path = root / "experiments/specs" / (experiment_id + ".json")
    spec = json.loads(spec_path.read_text())
    code_paths = sorted((root / "src/ai_value").glob("*.py"))
    inputs = {str(p.relative_to(root)): digest(p) for p in [spec_path, *code_paths, root / "configs/research.json"]}
    if (root / "data/corpus/baseline.json").exists():
        inputs["data/corpus/baseline.json"] = digest(root / "data/corpus/baseline.json")
    optional_versions = {}
    if spec.get("optional_dependencies"):
        from importlib.metadata import version
        if platform.python_version() != spec["required_python"]:
            raise RuntimeError("This optional experiment requires pinned Python " + spec["required_python"])
        for package, required in spec["optional_dependencies"].items():
            observed = version(package)
            if observed != required:
                raise RuntimeError("Pinned optional dependency mismatch: " + package)
            optional_versions[package] = observed
    # Include runtime version: exact result provenance must not silently cross environments.
    fingerprint = __import__("hashlib").sha256(json.dumps([inputs, platform.python_version()], sort_keys=True).encode()).hexdigest()[:16]
    if optional_versions:
        fingerprint = __import__("hashlib").sha256(json.dumps(
            [inputs, platform.python_version(), optional_versions], sort_keys=True).encode()).hexdigest()[:16]
    run_id = experiment_id + "-" + fingerprint
    target = root / "experiments/runs" / run_id
    if target.exists():
        manifest = json.loads((target / "manifest.json").read_text())
        for name, expected in manifest["outputs"].items():
            if digest(target / name) != expected:
                raise ValueError("Cached experiment output changed: " + name)
        return manifest
    started = datetime.now(timezone.utc).isoformat()
    tracemalloc.start()
    start = time.perf_counter()
    try:
        rows, summary = RUNNERS[experiment_id](spec)
        elapsed = time.perf_counter()-start
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    runtime_metrics = summary.pop("_runtime_metrics", None)
    envelope_met = elapsed <= spec["resource_limit_seconds"] and peak <= spec["resource_limit_mb"]*1024**2
    process_peak_rss_bytes = None
    if spec.get("resource_limit_rss_mb"):
        import resource
        observed_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        process_peak_rss_bytes = int(observed_rss if sys.platform == "darwin" else observed_rss*1024)
        envelope_met = envelope_met and process_peak_rss_bytes <= spec["resource_limit_rss_mb"]*1024**2
    compression_started = time.perf_counter()
    target.mkdir(parents=True)
    write_json(target / "spec.json", spec)
    compressed_payloads = {}
    for name, value in (("raw.json", rows), ("summary.json", summary)):
        payload = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode()
        packed = gzip.compress(payload, mtime=0)
        if gzip.decompress(packed) != payload:
            raise ValueError("Compression roundtrip failed")
        (target / (name + ".gz")).write_bytes(packed)
        compressed_payloads[name + ".gz"] = {"uncompressed_name": name, "uncompressed_sha256": __import__("hashlib").sha256(payload).hexdigest()}
    snapshot = {name: (root / name).read_text() for name in inputs}
    (target / "inputs.json.gz").write_bytes(gzip.compress(json.dumps(snapshot, ensure_ascii=False, sort_keys=True).encode(), mtime=0))
    manifest = {"run_id": run_id, "experiment_id": experiment_id, "started_utc": started,
                "specification_written_utc": datetime.fromtimestamp(spec_path.stat().st_mtime, timezone.utc).isoformat(),
                "finished_utc": datetime.now(timezone.utc).isoformat(),
                "inputs": inputs, "outputs": {name: digest(target / name) for name in ("spec.json", "raw.json.gz", "summary.json.gz", "inputs.json.gz")},
                "compressed_payloads": compressed_payloads,
                "source_snapshot": "inputs.json.gz",
                "command": "PYTHONPATH=src python3 -m ai_value.cli experiment " + experiment_id,
                "environment": {"python": sys.version, "platform": platform.platform(), "dependencies": "Python standard library only"},
                "elapsed_seconds": elapsed, "peak_traced_python_bytes": peak,
                "resource_envelope_met": envelope_met,
                "memory_scope": "Python allocations only; not process RSS or child processes",
                "result": ("resource_envelope_exceeded" if not envelope_met else
                           "passes_preregistered_prediction" if summary["meets_prediction"] else "prediction_not_supported"),
                "formal_rejection": False}
    if optional_versions:
        manifest["environment"]["dependencies"] = {"standard_library": True, **optional_versions}
        manifest["optional_dependencies_pinned"] = True
        manifest["process_peak_rss_bytes"] = process_peak_rss_bytes
        manifest["memory_scope"] = "Python traced allocations AND whole-process peak RSS including NumPy/native libraries; not child processes"
        manifest["stage_runtime_metrics"] = runtime_metrics
        manifest["archive_compression_seconds"] = time.perf_counter()-compression_started
        manifest["requires_optional_runtime"] = True
    write_json(target / "manifest.json", manifest)
    return manifest
