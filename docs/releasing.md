# Releasing Project Broom

Project Broom releases are produced only from a clean tagged `main` commit.
The initial public format is a Windows x64 portable ZIP plus complete
corresponding source.

## Required assets

- `ProjectBroom-Windows-x64-<version>.zip`
- `ProjectBroom-Source-<version>.zip`
- `SHA256SUMS.txt`
- `release-manifest.json`

The runtime ZIP contains Project Broom, the custom GZDoom runtime, Brogue
bridge/exporter, Freedoom Phase 2, the static presentation PK3, map compiler,
and all license and credit files. It does not contain reference WADs, generated
campaigns, debug symbols, developer tools, or source-control metadata.

The source ZIP includes the exact patched GZDoom source used for the binary,
the pinned Brogue CE snapshot, corresponding ZMusic, libsndfile, and OpenAL
Soft source, all Project Broom preferred source, build scripts, and license
material.

## Staging checklist

1. Run `scripts/audit-public-tree.ps1`.
2. Run the complete test suite and multi-seed long-run matrix.
3. Package from a clean checkout.
4. Verify archive hashes and the internal release manifest.
5. Extract on a clean Windows x64 VM with no developer tools installed.
6. Start a random seed and seed 1, then relaunch to prove cache reuse.
7. Confirm writes occur only under `%LOCALAPPDATA%\ProjectBroom`.
8. Confirm the About/Licenses material and source archive are present.
9. Publish as a GitHub prerelease and attach checksums.

Initial binaries are unsigned. Release notes must say so and must link the
checksums and corresponding source.
