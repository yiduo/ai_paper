# Research progress

Snapshot: October 22, 2026, after WP-086. **The overall phase-one goal remains open.** Counts come from [canonical metrics](reports/metrics.json), the [acceptance matrix](reports/acceptance.md), and versioned reading and experiment records.

| Measure | Actual progress | Meaning and remaining gap |
| --- | --- | --- |
| Catalogue | 372 families; 719 current manuscripts | Registration is complete at the pinned revision; the historical 722 records are reconciled individually |
| Actual reading | 47/372 families, about 12.6% | Includes partial reading; at least one family in each of 17 subject categories |
| Full-source decomposition drafts | 41/372, about 11.0% | Drafts cover current source bodies; they do not establish complete historical lineages or reviewed proof specifications |
| Source-result bindings in those drafts | 1,037 labelled results plus two unlabelled main theorems | Source propositions, not application candidates; F238's partial 4/12-manuscript reading has a further 95 bindings |
| Fully completed families and historical lineages | 0/372 | Unread original inputs, unresolved dependencies, and review requirements remain explicit |
| Candidate application connections | 40/500 | Ten-domain attempts and search counts are not counted as candidates |
| Real human classification | 0/150 | Deferred by the project owner; never replaced by model self-review |
| Preliminary application checks | 13/100 | Thirteen distinct hypotheses; five narrowly supported predictions, eight adverse observations |
| Distinct reproducible hypothesis checks | 13, against a target of 10 | This numerical subtarget is met; the 100-card milestone and the overall phase are not |
| Separate component checks | 2 | Excluded from the application-hypothesis count |
| Complete experiment archives | 15 | Thirteen application checks plus two component checks, with compressed data and source snapshots |
| Independent second-provider reviews / human specification reviews / pilots | 0 / 0 / 0 | No engineering deployment or fully reviewed mathematical assurance is claimed |
| Knowledge graph | 5,842 nodes; 15,021 relations; 5,635 canonical citation annotations (5,625 in core-validated research types) | A mix of research records, corpus records, and projected source artifacts; size is not research completion |

## Latest substantive result

F332's preregistered finite feature-denoising check tested 18 core scenarios and two scalar controls. Only 9/18 core scenarios met the required improvement threshold, below the frozen 12/18 requirement; two scenarios incurred excess risk. The prediction was not supported. A weighted-median baseline reduced to the identity throughout the frozen regime. The project retains that adverse evidence and does not widen the grid to rescue the prediction. See [experiment and limits](reports/F332-finite-denoising-experiment.md) and [retrospective 030](reports/retrospectives/030-denoising-risk-and-old-baselines.md).

WP-086 then audited F332 against the unchanged complete-family criteria. It actually read the selected original Mendel–Naor finite-extension proof, checked five formula-page images, inspected the two-page Deza–Laurent definition preview, and recorded a failed, size-capped attempt to obtain Ball's original body. The required book theorem and Ball body remain unread; the global-extension bridge also depends on three unread original sources. Thus complete-family and full-lineage counts remain zero. Local notation observations are recorded without claiming an author-confirmed correction or declaring the source theorem false. See the [audit](reports/F332-family-acceptance-audit.md).

The audit adds 13 canonical nodes and 31 explicit relations, with exact prior versions for five revised records. It adds no application candidate, preliminary check, effective lead, or numerical run. The new dependencies are scoped to the extension branch rather than silently attached to the source's self-contained main inequality or denoising construction.

## How to interpret the five supported leads

Support is limited to the card's actual test: bounded regression diagnostics, exact finite probability or algebraic calculations, applicability screening, or metadata checks. It does not show that the original mathematics is wholly correct, that a new theorem has been established, or that a deployed system gains performance. Adverse tests remain searchable observation records; formal rejection requires real reviewers.

## Next research package

WP-087 will read the low-coverage F153 source bodies: five TeX files, the bibliography, and the included verifier. Reading a verifier is not executing it, and a source verification program is not an application benchmark. Any numerical application experiment still needs a registered specification before execution. The project continues global coverage alongside deeper checks, with a retrospective every three substantive packages or immediately after a major evidence issue.

Human review and another provider remain deferred rather than waived. Independent reading, graph maintenance, and qualified experiments continue without repeatedly asking for those resources.

## Reproducibility and public scope

The canonical graph, generated cards, compressed exports, experiment archives, and quality receipts are included. The official upstream `math/` directory, downloaded external full texts, local credentials, and temporary workspaces are excluded. Source revisions, locators, and hashes remain available without redeploying upstream content. [Publication scope and verification](docs/publication.md) distinguish local preparation, GitHub publication, and research acceptance.

The public snapshot was pushed and anonymously verified. Initial remote CI passed 68 core tests and 11 archived replays before EXP076 failed strict raw equality on Linux; its summary matched. A fresh strict replay on the original macOS/Python 3.14.7 runtime matched both complete payloads. The scoped Linux workflow covers 13 other archives; cross-platform equality for EXP076 is not claimed. Failed evidence and original criteria are preserved. [Retrospective 031](reports/retrospectives/031-publication-and-platform-scope.md) records this publication milestone and returns the next research allocation to F153.
