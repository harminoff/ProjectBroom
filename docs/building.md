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
exact UZDoom revision from `dependencies.lock.json`, applies the Project Broom
integration patch, verifies the official UZDoom Windows runtime dependencies,
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

Presentation changes additionally require a fixed-seed UZDoom launch and
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
`dependencies.lock.json`, licenses, the UZDoom integration patch if needed,
and all build/runtime tests. Never silently follow an upstream branch or tag.

## UZDoom integration

The canonical engine is UZDoom 5.0.0 in `.deps/uzdoom-source`, built in
`.build/uzdoom`. Bootstrap verifies the complete five-file patch and refuses
unexpected source edits. `PROJECT_BROOM_ROOT` explicitly locates the external
frontend. Release builds disable the updater and enable Vulkan; ZMusic is
built from bundled source. The build receipt binds the frontend inputs and
runtime outputs, and packaging rejects a stale or modified engine.

Development and packaged launchers use `config/uzdoom.ini`. An existing
Project Broom `config/gzdoom.ini` is copied only when the new file is absent.
Keep the original configuration for rollback; review controller bindings after
migration. Historical `src/gzdoom-bridge` and API names are retained.

For corresponding-source archives, the already patched engine is under
`third_party_source/uzdoom-5.0.0`. Configure it directly with CMake and
`-DPROJECT_BROOM_ROOT=<extracted Project Broom source directory>`,
`-DUSE_UPDATER=OFF`, and `-DHAVE_VULKAN=ON`; build Release with VS2022 x64.
The normal bootstrap workflow also remains available when network access is
available. See [migration acceptance](uzdoom-migration-handoff.md).
