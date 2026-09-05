# Security policy

## Current binary-release status

Public binary releases remain blocked pending the complete UZDoom 5.0.0
migration acceptance matrix. The previous GZDoom 4.14.2 baseline was affected
by CVE-2025-54065 and must not be distributed as a fallback.

The release workflow requires the pinned UZDoom source and commit plus an
explicit `release.engineMigrationVerified` flag in `dependencies.lock.json`.
Changing the engine name alone does not open the release gate.

## Supported versions

Project Broom is pre-alpha. Security fixes are applied only to the newest
published prerelease and the current `main` branch.

## Reporting a vulnerability

Do not open a public issue for a vulnerability that could expose user data,
execute untrusted code, corrupt files outside Project Broom's data directory,
or compromise the release pipeline.

Use GitHub's **Report a vulnerability** private reporting feature on the
repository Security page. Include the affected version, reproduction steps,
impact, and any proposed mitigation. Maintainers will acknowledge a complete
report within seven days and coordinate disclosure after a fix is available.

Project Broom does not provide a bug bounty.
