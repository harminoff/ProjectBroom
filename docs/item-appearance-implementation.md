# Assigned item appearances

The v23 bridge copies `itemTable.flavor` into `BrogueBridgeItemState.appearance`
for potions, scrolls, staves, wands and rings. It is independent of effect kind,
identification, inscriptions and Call names. UZDoom never shuffles appearances,
parses display names or creates gameplay state to select art.

Implemented from the item appearance audit:

- 21 wood skins for floor staves and corresponding held staff models.
- 12 metal skins for floor wand shafts/ferrules and corresponding held wands.
- 18 gemstone skins for rings, including patterned opal, agate, malachite,
  jasper, bloodstone and alexandrite interpretations.
- Assigned scroll titles on the parchment, using original 5x7 uppercase ink
  geometry. Titles wrap at ten characters across three rows, matching Brogue's
  bounded 30-byte title storage. Spaces retain their position. Decorative
  repeated strokes and effect-specific seals are removed from this scroll model.
- Thrown flavored items retain their selected class/title before the item can
  disappear from the returned snapshot. The projectile no longer chooses an
  effect-specific model from its raw kind. Scroll lettering follows the proxy's
  position, yaw and visibility, and destroys itself with the parent.

RGB values and grain are artistic interpretations of Brogue's named materials;
there is no upstream 3D material palette. The skins, glyph meshes and lettering
are original Project Broom assets under CC-BY-SA-4.0. No third-party font or art
is imported. Brogue's titles remain upstream game data.

## Generation and verification

`python -m tools.pickup_models.generate` also invokes the flavor and scroll
generators. Standalone modules are `tools.pickup_models.flavors` and
`tools.pickup_models.scroll_letters`. Floor and held skins use different atlas
row heights; a regression checks the entire held material area.

`tools.test_item_flavors` covers catalog completeness, all title glyphs, skin
coverage and repeated five-seed exports across three naming states. Native
save smoke additionally compares every shuffled color, wood, metal, gemstone
and scroll title before/after loading the real recording. Existing command,
save, terrain, model and resource tests remain applicable.

The opt-in `brg_flavor_smoke` renderer fixture captures all 51 floor materials,
three scroll titles, two held examples, and a moving scroll proxy. It verifies
stable class selection after identification, unchanged authoritative hashes,
and removal of lettering after the projectile is destroyed. The gallery uses
copied presentation fixtures; it is not an interactive gameplay throw test.

Run `python -m tools.capture_terrain_overlays --label item-flavors-vulkan
--flavors --backend 1` (on one line), or use backend 0 for OpenGL. Captures and
logs are under `artifacts/terrain-overlays/`. Native DLL, engine and launcher
must all use ABI v23. Local builds are updated; online releases are unchanged.

Acceptance results: 105 bridge/resource/save/model/map tests passed; 14 focused
material/save checks passed after the final corrections. Vulkan and OpenGL each
captured 21 packaged-gallery views and passed projectile-lettering cleanup.
Regenerating 110 material/glyph assets produced byte-identical files. A seed-1
300-action run ended naturally at turn 195 with hash `36b2a00b6543c40a`, matching
the previous baseline. The gallery itself retained the turn-zero authoritative
hash `c92268ff6250781b`.
