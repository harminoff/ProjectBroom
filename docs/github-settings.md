# GitHub repository settings

Create `ProjectBroom` as a private staging repository first. After the release
gates in `docs/releasing.md` pass, change visibility to public.

Recommended settings:

- default branch: `main`;
- Issues and Discussions enabled;
- Wiki and Projects disabled initially;
- squash merging enabled; merge commits and rebase merging disabled;
- automatically delete merged branches;
- private vulnerability reporting enabled before public launch;
- secret scanning and push protection enabled where available.

Create a `main` ruleset after CI has completed once so the real check names can
be selected:

- require a pull request;
- require `source-and-python` and `native-bridge`;
- require `build-engine` (it reports success without compiling for changes
  outside native engine inputs);
- require conversations to be resolved;
- block force pushes and branch deletion;
- allow the maintainer to merge without an external approval while the project
  has a single maintainer.

Suggested repository description:

> Brogue CE as the authoritative game simulation, presented through a 3D GZDoom frontend.

Suggested topics:

`brogue`, `roguelike`, `gzdoom`, `doom`, `game-port`, `c`, `cpp`, `zscript`,
`procedural-generation`

Suggested labels:

- `bridge-parity`
- `presentation`
- `maintenance`
- `needs-authority-analysis`
- `needs-runtime-proof`
- `blocked-license`
- `dependencies`
- `good first issue`

## Development workspace to pull request

The `BrogueDoom2` working directory is the local development and evidence
workspace; it is not the GitHub checkout. Build products, captures, crash
reports, generated campaigns, and other ignored evidence remain there.

Use the clean `ProjectBroom` GitHub clone for commits and pull requests:

1. Update its local `main` from `origin/main` and confirm the checkout is clean.
2. Create a focused `codex/<topic>` branch from that current `main`.
3. Run `scripts/audit-public-tree.ps1 -WorkingTree` in the development workspace.
4. Export the curated source to a new empty directory with
   `scripts/export-public-source.ps1`; never copy the entire development tree.
5. Compare the export with the clean clone, then copy only the reviewed public
   additions and modifications. Do not interpret a file absent from the export
   as a deletion unless that deletion was intentional and separately reviewed.
6. Keep local captures such as root-level review screenshots out of Git. Stage
   explicit reviewed paths, inspect `git diff --cached --stat` and
   `git diff --cached --check`, then commit.
7. Push the topic branch, open a pull request targeting `main`, and complete the
   repository pull-request template with exact tests, hashes, runtime evidence,
   asset provenance, and known limitations.
8. Wait for `source-and-python`, `native-bridge`, and `build-engine`.
   The engine check decides whether native compilation is needed.
   Fix failures on the same branch and
   squash-merge only after every required check passes.

Operational safeguards proven by the repository workflow:

- Record user-excluded files before exporting and check those exact paths again
  before staging. Root-level screenshots and generated run history are evidence,
  not source.
- The public export destination must be a new empty directory outside the
  development workspace. The exporter intentionally rejects the source root,
  descendants of it, and non-empty destinations.
- A Windows generator run can leave Git status entries caused only by line
  endings or timestamps. Review `git diff --name-only`, `git diff --stat`, and
  `git diff --check`; never stage or reset files solely to silence status noise.
- Treat source tests, the complete native build, fixed-seed UZDoom smoke runs,
  and hosted GitHub checks as independent gates. A fresh
  `scripts/build-source-bridge.ps1` run stages the pinned runtime DLLs beside the
  built engine so the smoke scripts do not require a manual copy.
- Before merging, inspect a long-running `build-engine` job rather than assuming
  it is stalled. Merge only when every required check is green and GitHub reports
  no conflicts.
- After the squash merge, fast-forward the clean clone's `main` and verify its
  `HEAD` is identical to `origin/main`. Report the PR URL, merge SHA, excluded
  files, and any remaining local evidence.

Do not develop or commit directly on `main`. The GitHub merge commit is the
authoritative update to `main`; after merging, fast-forward the clean clone's
local `main` and leave the development/evidence workspace intact.

## Keep routine PRs fast

PR #9 took about 38 minutes on the hosted runner: about 3 minutes bootstrapping
dependencies and roughly 34 minutes compiling the complete UZDoom engine.
The source/Python and native Brogue checks each took about a minute. The merge
operation itself was quick. These are observations from the migration run,
not timing guarantees for subsequent runs.

Every PR runs source/asset/map tests, launcher compilation, and deterministic
Brogue bridge tests. The `build-engine` check also runs on every PR, but compiles
only when native frontend files, Brogue headers, the engine patch/pin, engine
build scripts, or engine validation code change. Assets, ZScript, maps, docs,
and Brogue C implementation changes do not require recompiling UZDoom: Brogue
is built independently as a DLL by `native-bridge`. Runtime smoke tests still
apply when behavior or presentation changes; compilation does not test ZScript.

The engine workflow enumerates all changed PR files, including previous names
for renames. API failures fail the check; exceptionally large diffs default to
building. Filtering occurs inside the job, so an irrelevant change does not
leave a required workflow check pending.

Engine CI uses `-SkipTests` because the two fast CI jobs run the full suite.
It runs before merge and on manual dispatch, without repeating the same cold
engine build on every squash merge. Fast CI still verifies `main` after merge;
release packaging retains its full build and acceptance gates. New PR commits
cancel superseded CI runs. Cold engine builds can still take 30–40 minutes.

Use verification proportional to the change: asset work needs relevant tests
and a local runtime check; a native integration change needs the engine build
too. Reuse the existing local `.deps` and `.build` directories. A fresh public
export is for source curation, not a reason to bootstrap a fresh engine for
every PR. Repeat clean builds for engine/toolchain migrations, release
verification, or a demonstrated reproducibility problem.
