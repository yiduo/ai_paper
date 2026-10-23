# MathWeave

[中文](README.md) · [English charter](CHARTER.en.md) · [Original Chinese charter](722篇AI数学论文应用价值挖掘纲领.md) · [Progress and limits](PROGRESS.en.md)

**Weaving mathematical results, historical methods, and testable applications into an evidence graph.**

This project connects a pinned mathematical manuscript corpus with historical literature, transferable methods, and concrete application problems. Its unit of research is **result family + historical lineage + application problem**. A versioned knowledge graph records the evidence, conditions, dependencies, experiments, and unresolved gaps.

**Phase one is incomplete.** The project has 44 candidate connections and 13 preliminary checks of distinct hypotheses. Five checks support narrowly defined predictions; eight retain adverse observations. These are not five new mathematical results or demonstrated engineering improvements. No family has completed the full research requirements or all six stages. Human review, independent checks by another model provider, and engineering pilots remain outstanding.

Current curated progress: 57 families actually read, 52 current-source decomposition drafts, 7,522 graph nodes and 20,986 relations, through WP-107 / retrospective 038. F239’s two current source bodies (24 TeX files / 8,083 lines including references and figure source) have also been read, but historical/formal checks and canonical curation remain pending; this journal does not increase those counts. See [progress](PROGRESS.en.md).

Repository: [yiduo/mathweave](https://github.com/yiduo/mathweave).

## Corpus and upstream boundary

The historical charter refers to 722 manuscripts. The pinned revision `1581d4cbdd69a0faf34b2089614fe2a814316a6a` contains 719 current manuscript records in 372 result families. Reconciliation preserves 692 unchanged paths, 27 linked version updates, and three proof withdrawals. PDF-file counts are not manuscript counts. The approximately 4,000 original questions mentioned in the charter were not fabricated into a dataset.

**OpenAI's official `math/` directory is not included, copied, hosted, or redeployed here.** Read the originals in [openai/math](https://github.com/openai/math/tree/1581d4cbdd69a0faf34b2089614fe2a814316a6a). This repository retains identifiers, source locations, version mappings, and checksums. Offline checks can use the pinned checksum manifest without downloading the upstream corpus; this is not a fresh reading of the originals.

This is an independent application-research project. It does not claim OpenAI endorsement or authorship of the upstream results.

## Run without downloading the corpus

Python 3.11+ and its standard library suffice for core checks and the historical standard-library experiment replays. JavaScript viewer tests also need an existing Node.js runtime. No model credentials or Lean installation are required. See the workflow for the actual CI environment; successful software checks do not certify the mathematics.

```sh
python3 scripts/check.py
python3 scripts/replay_run.py experiments/runs/EXP-332-001-b2607a9926c44586
PYTHONPATH=src python3 -m ai_value.cli query APP-332-01
PYTHONPATH=src python3 -m ai_value.cli export-graph
```

Open `reports/graph/index.html` locally to browse the graph. Download the repository ZIP, extract it, and open that file; GitHub's source viewer does not execute the HTML. Compressed JSON and GraphML exports are in the same directory.

The optional finite-bosonic experiment uses the separately documented, pinned Python/NumPy runtime. Do not run `experiment all` expecting a standard-library-only environment. See [runtime and scope](docs/bosonic-regression.md).

The Linux workflow covers 13 archived replays. EXP076 matched complete raw and summary payloads on its original macOS/Python 3.14.7 runtime, but failed raw equality on the first Linux run while its summary matched. It is not claimed portable. The original comparator and archive remain unchanged; [both outcomes and CI scope](docs/publication.md#actual-first-ci-and-platform-limit) are retained.

## Read the evidence

| Resource | Purpose |
| --- | --- |
| [English charter](CHARTER.en.md) | Full translated program, principles, stages, targets, and review gates |
| [Current progress](PROGRESS.en.md) | Evidence counts, adverse outcomes, remaining work, and next package |
| [Acceptance matrix](reports/acceptance.md) | Target-by-target status, generated from canonical records |
| [Machine-readable metrics](reports/metrics.json) | Current counts; registration and reading are kept separate |
| [Graph navigation](reports/graph/navigation.md) | Family and candidate index with explicit conditions and gaps |
| [Canonical graph](data/graph/) and [corpus records](data/corpus/) | Versioned source of records; exports and cards are derived |
| [Application cards](reports/cards/) | Hypotheses, dependencies, objections, and actual checks |
| [Experiment archives](experiments/runs/) | Specifications, compressed raw results, source snapshots, and manifests |
| [Retrospectives](reports/retrospectives/) | Comparisons of different routes and the possibility that old methods suffice |
| [F332 audit](reports/F332-family-acceptance-audit.md) | Actual proof reading and reasons complete-family credit remains zero |
| [F153 reading](reports/bernoulli-F153-reading.md) | Infinite classification, limited verifier scope, and the unestablished AR(1) benefit |
| [Real perturbation metadata](reports/F094-metadata-readiness.md) | Resolved decoding, actual label collisions, and remaining application prerequisites |

Most detailed research records are in Chinese. This release provides English entry documents, rather than claiming every historical record has been translated.

## Evidence and storage rules

Source assertions, selected proof statements, full dependency grades, external checks, and human decisions are separate records. A Lean catalogue entry is not a successful local build, and a model self-check is not human review or a second provider. Unknown prerequisites stay explicit. Formal rejection requires two real reviewers; pilots require complete A-grade dependencies and real authorization.

Register numerical specifications before running experiments. Retain adverse and failed results. Compress numerical payloads and source snapshots, verify decompression hashes, and remove temporary plaintext. Avoid duplicate upstream checkouts and large dependency downloads. Replays use isolated temporary directories that are cleaned afterward.

## License and publication

Original project code, documentation, and derived records are licensed under [Apache-2.0](LICENSE). Third-party items keep their own licenses and attribution in [NOTICE](NOTICE); this license does not relicense upstream manuscripts or external papers. Sensitive directions are represented only by necessary routing information in the public graph.

Publication status and its verification receipt are recorded in [state/publication.json](state/publication.json). Publication does not complete the research program, grant a mathematical credibility upgrade, or imply approval for engineering deployment. See [publication scope](docs/publication.md).

The [bounded symbolic-demand follow-up](reports/F025-demand-followup.md) distinguishes a real constrained old caller from the proposed single-marker feature. [Retrospective 032](reports/retrospectives/032-demand-constraints-and-next-counting-route.md) keeps all unmet phase-one targets. F113 is now read in full; [its scope report](reports/perfect-matching-F113-reading.md) separates relative counting, coarse deterministic counting, entropy, and sampling. The subsequent demand review qualifies actual counting consumers and strong old baselines; the next reading package covers F262 scalar/matrix spectral inequalities.

The [matching-count demand review](reports/F113-counting-demand.md) adds one conditional graph-probability calibration connection. The literal published replica schedule is not admitted for finite execution. No new preliminary check or general Gaussian-boson-sampling claim is counted.
