# Security policy

## Current binary-release status

Public binary releases are intentionally blocked while Project Broom remains
based on GZDoom 4.14.2. That version is affected by CVE-2025-54065. The source
repository may be reviewed and developed privately or publicly, but do not
publish runtime archives until the bridge has migrated to and passed its full
test matrix on UZDoom 4.14.3 or a later patched engine baseline.

The release workflow enforces this rule from `dependencies.lock.json`.

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
