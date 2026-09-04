# Building Project Broom

## Supported host

The maintained development configuration is Windows 10/11 x64 using Windows
PowerShell 5.1 or newer. PowerShell 7 is optional.

Required tools:

- Git for Windows;
- Python 3.11;
- .NET 8 SDK;
- CMake;
- Visual Studio 2022 Build Tools with Desktop development with C++;
- MSYS2 MinGW-w64 GCC and GNU Make.

`scripts/bootstrap-dev.ps1` checks these tools and prints the exact missing
command. Set `PROJECTBROOM_MSYS2_ROOT` when MSYS2 is installed outside
`C:\msys64`. No setup script silently installs system software.

## First checkout

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap-dev.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\build-dev.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\test.ps1
```

Bootstrap creates ignored `.deps` and `.build` directories, checks out the
exact GZDoom revision from `dependencies.lock.json`, applies the Project Broom
integration patch, verifies the official GZDoom Windows runtime dependencies,
checks out their corresponding audio-library sources, and verifies Freedoom
before use.

Run a deterministic game:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-dev.ps1 -Seed 1
```

Run standalone Brogue and Project Broom side by side:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\launch-comparison.ps1 -Seed 1
```

## Test gates

`scripts/test.ps1` separates source validation, Python tests, bridge tests, and
long-run tests. Use `-Quick` while iterating and the default complete suite
before opening a pull request.

Presentation changes additionally require a fixed-seed GZDoom launch and
before/after evidence. Bridge changes require deterministic hashes, rejected
and cancelled action coverage where relevant, and a several-hundred-action
run. See `AGENTS.md` for the full matrix.

## Creating a release candidate

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\package-release.ps1 `
  -Version 0.1.0-alpha.1
```

The command builds a self-contained launcher and frozen map compiler, assembles
the portable runtime, produces complete corresponding source, writes hashes,
and runs `scripts/verify-release.ps1`. Outputs are placed under
`artifacts\release\<version>` and are never committed.

## Local data

Development builds default to repository-local generated data for compatibility
with existing tests. Packaged builds always write to
`%LOCALAPPDATA%\ProjectBroom`. Delete that directory only when you intentionally
want to clear generated campaigns, settings, logs, and future save data.

## Dependency updates

Dependency changes require a focused pull request updating
`dependencies.lock.json`, licenses, the GZDoom integration patch if needed,
and all build/runtime tests. Never silently follow an upstream branch or tag.
