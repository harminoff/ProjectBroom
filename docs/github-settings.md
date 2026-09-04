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
