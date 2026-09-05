# Held staff and wand presentation

Selecting a staff or wand for targeted use shows an original wooden staff or
brass wand with gloved hands. The model remains through Brogue confirmation
prompts. A successful turn-consuming use plays an 18-tic forward gesture and
restores the equipped weapon after 20 presentation tics. Cancel restores the
weapon without advancing Brogue. The next accepted action can interrupt the
gesture; cosmetic animation never delays input or consumes a turn.

This is presentation-only. Native `SyncWeaponView` projects the selected stable
item ID; `PerformCommandResult` triggers the gesture only from Brogue's result.
No bridge ABI, Brogue rule, equipment, charge, damage, sound, or RNG changes.
The two generic shapes do not disclose an unidentified effect or attempt to
represent every randomized device material. They use the existing original
CC-BY-SA-4.0 atlas and hand rig, with new procedural geometry by Project Broom
contributors in `tools/weapon_models/devices.py`.

## Verification

- Release GZDoom frontend compilation passed.
- `python -m unittest tools.weapon_models.test_devices tools.weapon_models.test_viewmodel tools.test_broguedoom_resources tools.mapcompiler.test_compile tools.test_brogue_bridge`: 80 tests passed.
- MD3 and OBJ bytes match regenerated source; animated topology and UVs remain
  stable, and recovery ends at the ready pose. Existing weapon assets still
  match their generator.
- `scripts/test-staff-ui.ps1` (seed 14) and `scripts/test-wand-ui.ps1` (seed 19)
  passed actual GZDoom targeting, cancellation, use, and restoration checks.
  Cancellation retained revision/turn; staff use advanced 43/42 to 44/43 and
  wand use advanced 48/47 to 49/48.
- Before captures remain in `artifacts/staff-ui` and `artifacts/wand-ui` from
  the targeted-use implementation. September 5 06:55 onward captures show the
  new models; phase 8 captures use and phase 10 restoration after the framebuffer
  has updated. `device-preview.jpg` and `restored-preview.jpg` provide compact
  views in each device's evidence folder.
- Static PK3 packaging passed after disk space was freed, using the existing
  `zip_tree` packager. `artifacts/ProjectBroom-devices.pk3` is 83,601,581 bytes;
  archive integrity and required device resource checks passed.
- Packaged runtime checks passed using `scripts/test-staff-ui.ps1
  -ResourcePackage artifacts/ProjectBroom-devices.pk3`, repeated with `-Wand`.
  Both loaded the PK3 in GZDoom and verified targeting, cancellation, use, and
  restoration. Captures and logs are in `artifacts/staff-ui-packaged` and
  `artifacts/wand-ui-packaged`; `artifacts/packaged-devices-review.jpg` shows
  both held devices and the restored sword.

No new standalone comparison was run for these cosmetic changes; simulation
parity remains covered by the existing bridge regression suite.
