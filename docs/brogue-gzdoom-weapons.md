# Brogue CE weapon frontend

## Authority boundary

Brogue CE remains authoritative for equipment, attack legality, hit resolution,
damage, runics, weapon properties, throwing, projectile collision, turn cost,
monster responses, and RNG. GZDoom owns only input translation and presentation.
The generated first-person weapons contain no Doom hitscan, projectile, ammo, or
damage actions.

The public bridge contract is API version 13. `BrogueBridgeCommand` carries an
expected state revision and supports semantic action, equip, unequip, and throw
commands. Equipment is addressed by stable bridge item ID. A throw carries an
item ID and Brogue map coordinate; `brogue_bridge_preview_throw()` returns the
same line and maximum range used by the authoritative throw operation.

`BrogueBridgeItemState` includes copied presentation-safe names, quantity,
damage bounds, strength requirement, enchantment, knowledge flags, and equipped
state. `BrogueBridgePlayerState.equippedWeaponId` is the sole source used to
choose the visible weapon.

## Controls

- Left mouse: submit one camera-facing Brogue bump/move action. If a creature is
  in that cell, Brogue decides whether and how the attack occurs.
- Q (hold): open the compact equipment belt. Mouse wheel or 1-9 changes the
  selection; releasing Q asks Brogue to equip it. Empty hands asks Brogue to
  unequip the current weapon.
- T: open the throw selector. Mouse wheel or 1-9 selects a carried weapon;
  Enter/left mouse enters targeting.
- Targeting: movement controls move the Brogue-cell cursor, Tab cycles directly
  visible Brogue creatures, Enter/left mouse submits the throw, and Escape or
  right mouse cancels.
- Numpad 1-9 retains absolute eight-way movement and wait for parity testing.

One physical key-down creates at most one bridge request. The frontend blocks
normal Doom movement and clears Doom action buttons every tic.

## Presentation

`tools/weapon_models/generate.py` deterministically produces one animated MD3
hands-and-weapon viewmodel and an OBJ ready-pose reference for each of Brogue's
15 weapon kinds, plus target/path markers,
ZScript declarations, MODELDEF entries, and
`assets/weapons/brogue_weapon_registry.json`. The source build script regenerates
these resources before tests and compilation.

Attack presentation is event-driven. An authoritative player
`ATTACK_ATTEMPTED` event starts the weapon's thrust, slash, heavy, sweep, lash,
or flail vertex-pose sequence. `PROJECTILE_MOVED` events create an ordered visual
flight path using the corresponding pickup model. The simulation has already
resolved the throw before animation begins; presentation cannot change its
result.

## Build and verification

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\build-source-bridge.ps1
python -m unittest tools.test_brogue_bridge tools.test_broguedoom_resources
.\src\brogue-mapgen\bin\brogue-bridge.exe --seed 1 --weapon-smoke
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\launch-source-bridge.ps1 -Seed 1
```

The headless weapon smoke deterministically proves initial dagger ownership,
authoritative unequip/equip turn processing, a Brogue-derived throw preview,
dart stack decrement, and resulting state hash. Runtime verification remains a
separate gate because model loading and ZScript parsing occur only in GZDoom.

## Current limitations

- The compact selector is a development mid-screen overlay, not the final HUD.
- Original animated held-weapon models now replace the placeholders. See
  [hero-weapon-models.md](hero-weapon-models.md) for source, proof, and limits.
- Throw selection currently exposes carried weapons; the bridge command itself
  accepts other throwable carried items for later inventory UI work.
- Attack events preserve special weapon flags, but bespoke penetrate/sweep/
  lunge multi-target visual choreography is deferred.
- Equipment confirmation prompts use the bridge's explicit confirmation field;
  a polished prompt frontend is deferred.
