# Hero weapon presentation refactor

Presentation-only art, animation, tooling, and a narrow native view-selection
correction. **No gameplay outcomes change; Brogue CE remains authoritative.**
No ABI, damage, collision, AI, item statistics, movement legality, action
processing, or gameplay RNG was modified.

## Models and motion

The former models placed glove-like spheres beside a floating handle and ended
their cuffs inside the picture. The replacements have fingers around the grip,
opposing thumbs, palm heels, wrists, leather cuffs, and cloth sleeves extending
beyond the bottom of the view. Weapons and gripping hands share a transform;
forearms deform back to stationary offscreen anchors.

All 15 existing weapon kinds have original replacement meshes. Blades have
bevels; polearms continuous shafts; the rapier a knuckle bow; axes shaped cutting
heads; the mace flanges; the flail linked rings and a studded head; and the whip a
curved, deforming lash. Darts have points and flights; incendiary darts have
wrapping and an unlit fuse. Two-hand grips are artistic poses, not equipment rules.

Each MD3 has 16 compatible vertex poses, bound to ZScript frames A-P. Nine attack
poses cover ready, anticipation, windup, drive, contact, follow-through, and
recovery. Thrusts extend and aim forward; cuts rotate the weapon and gripping
hands together. The whip and flail also flex during the swing. Seven additional
throw poses cover loading, drawing back, forward motion, release, and return.

## Authority contract

- Only player entity 1's resolved `ATTACK_ATTEMPTED` enters `BridgeAttack`.
- `PROJECTILE_MOVED` supplies the copied thrown category/kind and resolved path.
- Native `VisualThrowKind` temporarily selects that weapon's model for 14
  presentation tics, then restores the authoritative equipped view. This fixes
  displaying the equipped dagger when a carried dart was actually thrown.
- The temporary view does not call equip/throw or add a command gate. Existing
  world projectile timing and input gates are unchanged.
- `Fire` is inert; `Ready` forbids Doom firing/switching. No damage, projectile,
  hitscan, ammo, AI, or RNG actions exist in these weapon classes.
- Whole-overlay rotation/translation and Doom bob were removed. Pose animation
  explicitly settles back to ready. Brogue resolves the action first; animation
  does not determine turn cost, hit timing, or damage.

## Source and regeneration

Editable source/provenance: [`assets/weapons/README.md`](../assets/weapons/README.md).

```powershell
python -m tools.weapon_models.generate
python -m unittest tools.weapon_models.test_viewmodel tools.test_broguedoom_resources tools.monster_models.test_rat tools.test_brogue_bridge tools.mapcompiler.test_compile
powershell -ExecutionPolicy Bypass -File scripts/build-source-bridge.ps1
```

The generator replaces held-weapon art, bindings, registry, and atlas. Pickup
models, the detailed rat, and target/path marker geometry retain their roles.
OBJ references remain available to existing tooling; MODELDEF selects the MD3s.

## Verification, 2026-09-04

- **Tests:** combined bridge, resource, rat, weapon, and map-compiler suites passed,
  81 tests. Seven new tests cover deterministic bytes, MD3 binary layout and
  indices/bounds, stable pose topology/UVs, stationary sleeve anchors,
  sleeve/wrist overlap, bindings, recovery, and native event selection.
- **Compile/link:** bridge was up to date and native frontend compiled. Canonical
  link initially failed with LNK1104: two existing sessions held `gzdoom.exe`
  open. They were not closed without approval. The same build tree successfully
  linked `gzdoom-weapon-review.exe` using:
  `cmake --build .build/gzdoom --config Release --target zdoom -- /p:TargetName=gzdoom-weapon-review /p:BuildProjectReferences=false`.
- **Actual GZDoom:** all 15 models loaded in a seed-1/depth-1 visual catalog with
  ready/attack captures. The diagnostic addon changes only frontend visual
  inventory, never Brogue equipment/turns, and is not shipped. This does not
  claim the normal player acquired every weapon.
- **Real combat:** seed 1, `N,N,N`, 25 times `W`, then `N,W,W`. The last `W`
  attacks the adjacent rat through the bridge. Repeated headless runs and GZDoom
  agree at turn 31, revision 32, player `(12,22)`, HP `28/30`, state hash
  `bdc4057f3c5d1dd7`; rat HP is 2/6. A capture addon adjusts angle/pitch only,
  retaining the real player camera and normal HUD weapon renderer.
- **Headless weapon smoke:** existing equip, unequip, throw preview, and dart
  decrement (15 to 14) passed; hash `68796dba55c83bc7`.
- **Package:** static PK3 contains all 15 MD3s, atlas, and bindings. This is not a
  full installer/release build. It was launched with the rebuilt review engine
  for the real combat sequence above; MD3 frames 1-8 and return to 0 were logged.
- **Blender reopen:** saved file opens in Blender 5.2.1 with 15 scenes, 764
  animated mesh objects, one packed file texture, and no linked libraries.
  Every mesh has 16 editable shape keys. Source SHA-256:
  `130c2ebee945da42733a179994d2bb29d4dc43f681d3e3dbcc2d8774e34b7252`.
- **Budgets:** 3,880-8,060 triangles per ready-pose viewmodel; all 15 animated
  MD3s together occupy 8,118,764 bytes. Only the selected viewmodel is drawn.

Ignored local evidence: `artifacts/weapon-models/before.png`, `gallery-*.png`,
`motion-*.png`, real `combat-*.png`, private configs/logs, preserved original
source/model baseline, and `ProjectBroom-weapons.pk3`.
`held-contact.png` holds the actual event-triggered contact frame for inspection
using a non-shipped diagnostic addon. It proves grip/framing at contact, not
normal animation duration. The regular combat run and frame log do not hold
poses. Closely spaced screenshot commands can coalesce onto one rendered frame.

Static PK3 SHA-256:
`5ffa473eb804bd1ad10d2f19f9eafbdce8906d3a54fa6c431664bdc494d82fbf`.

## Follow-up verification

With the user's approval, the remaining old Project Broom process (PID 42680)
was closed; the other previously identified session had already exited.
`scripts/build-source-bridge.ps1` then passed its bridge/resource tests and
successfully rebuilt the canonical `.build/gzdoom/Release/gzdoom.exe`. The normal
launcher now uses the updated presentation code; the alternate review binary is
no longer needed to exercise it.

Canonical executable SHA-256:
`c0420de130c123c64c62d34924ebd251d534c7231fc85a40f18f484bf177ced3`.
The complete 81-test suite passed again after this rebuild.

Computer Use approval subsequently succeeded. A private seed-1 game launched
with the canonical executable and a read-only PSprite logger
(`artifacts/weapon-models/throw-observer`, log `throw.log`). Live captures confirm
the dagger grip and continuous sleeve at the normal camera. Automated `t`, `T`,
and Escape key presses produced no visible menu response, including after
explicit activation. Mouse input did reach the game and advanced one movement
turn, from `(38,26)` to `(38,25)`. No throw was submitted. This establishes a
keyboard-automation limitation in this run, not a verified throw failure or a
verified throw animation. No input-system changes were made to work around it.
The private test process was closed afterward; no GZDoom sessions remain.

## Remaining limits

- Direct UI throw/re-equip verification remains open: Computer Use can capture
  the game and deliver mouse input, but its keyboard presses did not open the
  required menus in this run. Headless throw behavior, compilation, and the
  separately recorded real combat animation remain verified.
- Empty hands and non-weapon consumable/staff/wand use retain existing behavior.
  This replaces the 15 existing held-weapon kinds, not potion/scroll use models.
- Sleeves are a first-person rig, not a full-body skeleton. Framing was checked
  at FOV 70; unusual FOV/aspect combinations need review.
- Original stylized diffuse-atlas art, not photoreal scans/PBR. No performance
  speedup is claimed.
- World projectile flight still starts from the resolved event immediately;
  exact release-to-flight choreography and bespoke multi-target swings remain
  presentation refinements, not changes to Brogue behavior.

## Documentation basis

Context7 returned unrelated examples for GZDoom model animation, so the pinned
GZDoom 4.14.2 source supplied the verified contract:

- `.deps/gzdoom-source/src/common/models/models_md3.cpp`: MD3 v15 layout,
  quantized positions, normals, and buffer axes.
- `.deps/gzdoom-source/src/r_data/models.cpp`: HUD/FOV transforms, frame binding,
  interpolation.
- `.deps/gzdoom-source/wadsrc/static/zscript/actors/inventory/weapons.zs`:
  PSprite ready/raise/state behavior.
- `src/gzdoom-bridge/brogue_bridge_frontend.cpp`: view selection and event paths.

General reference: [`gzdoom-model-authoring.md`](gzdoom-model-authoring.md).
