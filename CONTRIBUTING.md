# Contributing to Project Broom

Thank you for helping Project Broom present Brogue CE faithfully in 3D.

Before planning or editing, read [AGENTS.md](AGENTS.md) completely. It is the
technical contribution policy for humans and coding agents.

## Accepted work

Every pull request must be one of:

1. Presentation-only work that cannot change Brogue outcomes.
2. Bridge/parity work that exposes behavior already implemented by Brogue CE.
3. Maintenance, tests, packaging, diagnostics, or documentation that protects
   the authority boundary.

New gameplay, balance changes, Doom-side rules, and unlicensed assets are not
accepted. Ask in GitHub Discussions before investing in work whose authority
or license is unclear.

## Development flow

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap-dev.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\build-dev.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\test.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\run-dev.ps1 -Seed 1
```

Work from a focused branch. Preserve unrelated local changes. Do not commit
`.deps`, `.build`, generated campaigns, binaries, crash reports, or reference
WADs.

## Pull requests

Use the repository pull-request template. State the contribution category,
authority analysis, gameplay declaration, verification commands, fixed seeds,
runtime evidence, and asset provenance. Visual changes need before/after
captures; parity changes need deterministic headless tests and a GZDoom smoke
test.

By contributing code you agree to license your contribution under
AGPL-3.0-or-later. By contributing original presentation assets you agree to
license them under CC BY-SA 4.0 unless a compatible third-party license and
complete provenance are explicitly documented.
