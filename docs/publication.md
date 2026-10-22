# GitHub publication scope

Authorized by the project owner on 2026-10-22: publish the existing Chinese charter, an English translation, and related research progress as an open-source GitHub repository. The owner explicitly excludes redeployment of OpenAI's official `math/` directory.

## Included

- Original Chinese charter, English charter, bilingual entry documentation, and English progress snapshot.
- Original project source, tests, schemas, research configurations, and workflow.
- Versioned corpus identifiers, reconciliation and checksum manifests; canonical research graph; generated cards, family drafts, navigation, and compressed exports.
- Registered experiments, compressed numerical outputs and source snapshots, adverse outcomes, attribution, and reproducibility receipts.
- Project checkpoints and backlog describing actual work and remaining requirements.

## Excluded

- `math/` in its entirety, including upstream manuscripts, formalization files, and Git metadata. Existing upstream links and pinned hashes identify original sources.
- External-paper downloads, temporary renders and replays, virtual environments, model or Lean caches, and local credentials.
- Local Git history as a bulk upload. The initial public branch is a snapshot with no parent commit, reusing the reviewed current tree. This keeps publication small and avoids publishing unreviewed historical files. Required research prior versions and experiment source snapshots remain included explicitly.

The local research branch retains its history. The public branch records the actual publication snapshot and future publication updates. This is a source repository publication, not a website hosting deployment, engineering pilot, or declaration of completed research. Open `reports/graph/index.html` after downloading the repository to use its existing offline viewer.

## License

Project code, original documentation, and original derived records use Apache-2.0. `NOTICE` identifies separately licensed third-party sample data and small source-inspection tools. Upstream mathematics and external papers are not relicensed. The public repository is an independent research effort with no claimed upstream endorsement.

## Verification

Before pushing: complete the core checks, graph/source/foreign-key checks, dependency-impact checks, compressed archive checks, and a clean-directory run without `math/`. Audit the exact publication tree for excluded paths, credentials, controlled material, and oversized files. Record the tree and commit identifiers.

After pushing: verify the repository's public visibility and remote branch commit. Save the observed URL, commit, and verification time in `state/publication.json`. A prepared tree is not a successful push; a push is not a successful CI run. Remote CI status is reported only after an actual run. Research completion and review counts remain independent of publication.
