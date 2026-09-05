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
- require `build-engine` when that path-filtered workflow runs;
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
8. Wait for `source-and-python`, `native-bridge`, and the path-filtered
   `build-engine` check when it applies. Fix failures on the same branch and
   squash-merge only after every required check passes.

Do not develop or commit directly on `main`. The GitHub merge commit is the
authoritative update to `main`; after merging, fast-forward the clean clone's
local `main` and leave the development/evidence workspace intact.
