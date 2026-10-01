# Pit bloat: descent-order model update

The pit bloat is the next remaining ordinary encounter after bloat: the pinned
`GlobalsBrogue.c` rows 752–755 put both forms at depths 2–13, while the normal
goblin row begins at depth 3. Special machines, captivity and out-of-depth
selection can differ; this order does not promise identical encounters per seed.

BRG-M07 uses the same original connected membrane and seven-bone deformation as
the bloat, appropriately for a subspecies. A dedicated blue diffuse texture uses
the pinned light-blue glyph identity, in contrast to the ordinary purple bloat.
There are no invented limbs, eyes, emission or visibility overrides. The six
clips are idle, drift, bump, bump_alt, recoil and collapse. Rest extents are
28 x 26.3268 x 32 units with a 16-unit hover gap: artistic dimensions, not rules.
The model has 1,521 vertices and 2,976 triangles. The static reference is preserved.

## Authority and integration

Presentation only. `MK_PIT_BLOAT` is added to the skeletal registry and existing
MODELDEF/proxy/native clip table. No simulation code, ABI, Doom AI, collision,
damage, RNG, turn processing or terrain logic changes. Brogue's existing
`MA_KAMIKAZE` / `MA_DF_ON_DEATH` path invokes `DF_HOLE_POTION`; the frontend does
not create a pit. Level replacement retains its normal cleanup behavior rather
than forcing an old-floor collapse pose into the new level.

## Verification — September 13, 2026

- Blender MCP authored and reopened the source. A separate clean background
  rebuild saved only this asset and verified seven bones, six Actions, packed
  texture and 18 sampled poses against runtime deformation. Evidence:
  `artifacts/pit_bloat-animation/blender-verification.json` and studio captures.
- `python -m unittest tools.monster_models.test_pit_bloat tools.monster_models.test_bloat tools.monster_models.test_skeletal tools.test_broguedoom_resources`
  passed 42 tests: manifold seams, hover/collapse, shared subspecies anatomy,
  blue RGB identity, deterministic bytes and shared integration/resource checks.
- `python tools/run_native.py cmake --build .build/uzdoom --config Release -j 4`
  passed; the build fingerprint was refreshed.
- `python -m tools.monster_models.review_skeletal --symbol MK_PIT_BLOAT --backend 1 --all-angles --distances --packaged`
  and backend `0` each captured 34 images. Packed model, skin and bindings match
  source. Representative studio and runtime distance images were inspected.
  Evidence: `artifacts/skeletal-review/MK_PIT_BLOAT/{vulkan,opengl}/`.
- Seed-27 startup map compilation and verification passed: 6,873 sectors.
- `python -m tools.monster_models.review_bloat_encounter --pit --backend 1`
  and backend `0` replay the natural seed-27 encounter, pit bloat ID 38 at depth 2.
  Two headless runs match. Brogue resolves the burst, floor removal and player
  fall to depth 3; UZDoom logs departure, arrival and completion, with final
  hash `51456a766cb43c62` matching the headless route. Before/landing captures
  were inspected. The observer camera only aims from the player's eye and
  never reveals or relocates monsters. Evidence:
  `artifacts/pit-bloat-encounter/{1,0}/`. The shared script's `gas.png` filename
  is the settled landing capture for this variant, not a gas effect. Because
  this encounter replaces the level, it proves the fall transition, not a
  retained source-floor collapse animation; collapse is separately captured
  in the gallery. No fall behavior was implemented or changed for this model.

Runtime IQM SHA-256:
`3570b4edca6adc68a4ed59534a700e2f4f19ee1392a723c5a510f854c6932bd6`.

## Remaining acceptance

Individual art approval, physical-input acceptance, full release packaging,
standalone visual comparison and comparative frame-time benchmarking remain
unperformed. Gallery poses alone do not prove a natural encounter. No third-party
artwork was imported; new content is original Project Broom work, CC-BY-SA-4.0.
