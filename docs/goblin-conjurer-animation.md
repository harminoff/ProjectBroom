# Goblin conjurer: Higgsfield Blender and runtime verification

Presentation-only upgrade of BRG-M09 / `MK_GOBLIN_CONJURER`. The old static
model is preserved as a reference; the runtime now uses a connected IQM skin.

## Source-led design and authority

Pinned Brogue describes a goblin covered in glowing, pulsing sigils that can
summon phantom blades (`Globals.c`, catalog L1043 and prose L1197). The design
reuses the refined goblin's angular face, swept ears, sparse hair and plain
wrap, replaces the spear grip with two free hands, and uses ash-brown skin
with violet markings on chest, forehead, arms, back and nape. Mark shapes,
placement, clothing and numerical dimensions are artistic interpretations,
not additional Brogue lore or gameplay facts.

The sigils duplicate subsets of the actual baked skin triangles, offset by
0.035 units and using identical per-vertex weights. Transparent padding hides
patch boundaries. The RGBA atlas has a separate sigil tile; only that tile
receives emissive lighting and a renderer-time pulse. No added world lights,
particles, fake blades, collision, damage, AI, turns or gameplay RNG.

Six clips: `idle`, `walk`, `thump`, `whack`, `recoil`, `death`. Existing copied
attack/damage/death events select presentation clips. Thump/whack are cosmetic
variants, not claims that the bridge exposes the precise attack verb.
`Monsters.c::monsterSummons` and `summonMinions` remain wholly authoritative.
No summon event exists in the present animation interface, so the ambient
hand pose and pulse are deliberately not labeled as a synchronized cast.

## Authoring and reproducibility

The actual `higgsfield-use-blender` MCP server, `fnf-blender-mcp` 0.2.0, ran
locally with Node 24.19.0 and Blender 5.2.1 LTS. No cloud job, account credits
or third-party artwork were used. This reused the established local stdio
client; it did not register a new global Codex server or replace any open
desktop Blender scene. Higgsfield's Blender workflow guided isolated process
use, inspection, saving, fresh opening and renders.

Evidence lives under `artifacts/conjurer-higgsfield/`: MCP plans/results,
source renders, before-state backups, cold-bake hashes and engine captures.
The first source build exposed a missing `sub` import in the new module;
it was corrected before the successful fresh-open and rendering checks.
Blender's existing extension-cache permission warning was nonfatal; no
global security or preference changes were made to suppress it.

- 18 bones, 28 mesh parts, 6,509 runtime vertices and 10,161 triangles.
- Closed connected cage: 2,805 vertices, 5,606 faces, one component.
- Rest extents: 11.8988 / 19.342 / 39.2134 map units; animations remain within
  the tested 64-unit lateral envelope. These extents do not define collision.
- Fresh-opened `.blend`: six Actions, packed skin, no linked libraries.
- 18 sampled Blender poses matched the runtime solver within 0.000012 units.
- A second fresh Higgsfield process reproduced cage, IQM and PNG byte for byte.

```text
IQM  d3609c5df02eeea24e9e53f897355f85c2b4cec985252bd2aab71db05f5a9a4a
PNG  e464e829c0da1e723b6f46e10d85934f78290f662236dc789cf56ce63af1aa54
Cage cf847e22f36569195b533ed218585b4364e8836b3009a0524e99f111190878bf
```

## Separate verification gates

1. **Native build:** `python tools/run_native.py cmake --build .build/uzdoom --config Release -j4` passed.
   Only the generated skeletal presentation table adds K09; no simulation or
   frontend behavior was rewritten.
2. **Regression tests:** the six suites below pass 56 tests, including the
   existing goblin, all roster resources, cage seams, clip bounds, normalized
   weights, deterministic export and conjurer-only regressions.
3. **Packaging and real launches:** Vulkan and OpenGL each captured 34
   gallery views: original static reference, all six clips, front/side/rear,
   and 64/128/192-unit distances. The PK3 model, skin and binding bytes match
   source. Every gallery subject reports `blocking=0`. Representative front,
   rear, distance, attack and death images were inspected.
4. **Pulse proof:** eight frozen-pose, fixed-camera dark-room captures per
   backend. Only the sigil pixels changed (1,482 Vulkan; 1,483 OpenGL); no
   non-sigil pixel changed by more than three byte values. Blue-channel
   means range from approximately 109 to 239. See `pulse-verification.json`.
5. **Normal encounter:** seed 8, depth 3, 166 submitted movement/wait intents.
   Repeated headless runs and both real renderer runs finish at hash
   `e2e87855fd32531d`. The route sees conjurer ID47 and Brogue-created spectral
   blades IDs61–63 / kind55. `natural-clear-*` adds an earlier unobstructed
   view before the blades obscure the conjurer. The camera remains at the
   player's eye and turns toward the existing creature; no creature is
   spawned or repositioned by the observer. Brogue maintains distance, so
   the unobstructed capture shows the conjurer's back, not a forced frontal pose.
6. **Startup map verification:** seed-8 startup compiler/verifier passed.
   No map-generation code changed. The diagnostic route helper's original
   seed-27 pit/goblin mode still yields `cc14f9d0bbb31e67` after adding the
   opt-in `--visible` encounter stop.

```powershell
python -m unittest tools.monster_models.test_goblin_conjurer tools.monster_models.test_skeletal tools.test_broguedoom_resources tools.monster_models.test_connected_skin tools.monster_models.test_creatures tools.monster_models.test_goblin
python -m tools.monster_models.review_skeletal --symbol MK_GOBLIN_CONJURER --backend 1 --all-angles --distances --packaged --output artifacts/conjurer-higgsfield/vulkan
python -m tools.monster_models.review_conjurer --backend 1 --output artifacts/conjurer-higgsfield/natural-clear-vulkan --package artifacts/conjurer-higgsfield/vulkan/ProjectBroom-review.pk3
```

Repeat the renderer commands with backend `0` and OpenGL output/package paths.

## Preservation, licensing and remaining acceptance

All 67 other bestiary entries are preserved. Catalog data, player reference,
shared placeholder atlas and non-conjurer model bindings remain unchanged
relative to the task-start dirty baseline. Previous conjurer verification is
retained under `previousAssetVerification`. No commits, resets or cleaning.

Original Project Broom meshes, textures and sigil artwork are CC-BY-SA-4.0.
Higgsfield's local tool retains its MIT license; Blender remains a tool, not
an imported art source. Upstream Brogue text and notices are unchanged.

This is verified review packaging, not a new full player distribution.
Individual art approval, physical-input acceptance, standalone side-by-side
comparison, natural melee/death/captivity coverage and comparative frame-time
measurements remain unperformed. Close-up atlas/material boundaries inherited
from the connected goblin cage remain visible. Captive conjurers retain the
existing generic presentation; no new release animation is claimed.
