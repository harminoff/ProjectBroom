# UltimateClassicMinimap provenance

This project vendors the GZDoom minimap implementation from:

- Repository: https://github.com/Lewisk3/UltimateClassicMinimap
- Upstream commit: `0c690b839b333da1823b935e9d6db7fa9379cfd9`
- License: MIT; see `ULTIMATECLASSICMINIMAP-LICENSE.txt`

Integration adjustments:

- The upstream `ZScript/` directory is stored as `ucm/` because the Windows
  development tree already has a root `ZSCRIPT` file.
- The root `ZSCRIPT` includes the four vendored UCM source files after the
  Brogue runtime source.
- UCM event handlers are registered with `BrogueWorldHandler` in `MAPINFO`.
- `ucm_mapshowall` defaults to true for map-generation inspection, and the
  launchers also set it explicitly.

The minimap reads the generated UDMF line topology. It does not alter Brogue
generation, terrain snapshots, or gameplay rules.
