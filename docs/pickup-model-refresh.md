# Pickup model refresh

Contribution category: presentation only. Brogue CE owns item identity,
placement, visibility, pickup, inventory, effects, RNG and turns. No native
frontend or simulation code changed in this pass. Enemies, the rat timing,
hands and held-weapon animations remain untouched.

## Delivered scope

All **100 item kinds and five unidentified forms** have updated OBJ geometry,
UVs and normals, using one original 1024×1024 diffuse atlas (`BRGPICKS.png`).
The legacy `BRGITEMS.png` is preserved for held-weapon targeting markers.

| Family | Construction |
| --- | --- |
| Food | Wrapped ration with twine; shaped mango with stem and leaf |
| Floor weapons | Existing original weapon components without hands, laid down and grounded; bevels, bindings, chains and heads |
| Armor | Leather seams and belts, bronze scales, mail links, horizontal bands, vertical splints, breastplate and rivets |
| Potions | Shaped bottle, thick lip, cork, neck cord, parchment label and known-kind seal |
| Scrolls | Thick curled parchment, horizontal rolls with visible spirals, ink strokes and wax seal |
| Staves and wands | Tapered shafts, wraps, ferrules and crystal terminals |
| Rings, charms, amulet | Bands, settings, claws, medallion rims and connected-looking necklace loops |
| Treasure and keys | Coin piles with rims/stamps, painted crystal facets, notched iron keys and the door key's leather lanyard |

The [105-entry model index](pickup-model-index.md) records class, file,
dimensions and triangle count. The [machine-readable index](../assets/items/pickup-model-index.json)
includes exact Brogue descriptions and source lines for 97 table-defined items.
Gold, amulet and lumenstone entries have no invented catalog quote. Seven stale
display labels were corrected to the pinned catalog names; category/kind IDs,
classes and runtime filenames remain stable.

`assets/items/pickups.blend` contains 105 origin-centered scenes, named editable
parts, one packed image and a shared preview-only 64-unit floor/camera/light rig.
Select the scene named for the runtime class. Only its ASSET collection is game
geometry. Python definitions are the reproducible master; reconcile manual
Blender edits before rebuilding. Context7's current Blender mesh/UV/packing API
references informed this source builder, validated in installed Blender 5.2.1.

## Authority, scale and visual limits

Every model is grounded at 0.12 map units. Floor footprints fit within 56 units
on each horizontal axis; long weapons are uniformly reduced to fit the 64-unit
cell. These are art/readability decisions, not Brogue physical measurements.
Actor collision dimensions and all item rules are unchanged.

The existing `PresentationItemKind` / `PickupClassName` path still selects one
generic class for each unknown potion, scroll, staff, wand or ring. Known-kind
ornaments are artistic cues, not authoritative randomized bottle colors, scroll
titles, wood species or gemstones. No hidden kind is used by the generic model.

The runtime materials are opaque diffuse, including glass and crystal. Painted
value ramps/facets improve readability under GZDoom's ambient model lighting;
there is no transparent-glass, PBR, emissive-light or dynamic-material claim.
The flattened floor armor is a pickup representation, not wearable character
armor. Model geometry ranges from 80 to 6,732 triangles; no frame-time benchmark
or final user art approval is claimed.

## Verification

- Runtime generator and focused mesh checks cover all 105 models: finite
  positions, triangle indices, normals, UV range, footprint and floor clearance.
- Full Python suite: **101 tests passed**, including bridge, resources, rat,
  creatures, weapons, pickup geometry/catalog labels, and map compiler tests.
- Repeated generation is checked byte-for-byte for OBJ, bindings and PNG.
- Blender source saved and freshly reopened: 105 scenes, one packed image,
  matching part/vertex counts, no linked libraries; 21 studio views rendered.
- Static package contains matching runtime model/skin bytes and no `.blend`.
- Actual pinned GZDoom launch: all 105 classes captured before and after in the
  same private `ART01` gallery. The gallery is not a Brogue level and spawns only
  non-interacting visual proxies. Each shot explicitly selects its model.
- Separate normal seed-one review walks eight steps east to the existing sword,
  captures it, then takes a ninth east step to pick it up. The item is not spawned
  or moved by the review. Before/after runs and repeated headless Brogue states
  are compared turn-for-turn. The diagnostic camera uses the player's eye
  position, looks only at a Brogue-visible pickup and hides the player's own
  reference mesh; it does not reveal or reposition pickups.
- C++ compilation was not rerun because no native source changed. GZDoom loaded
  and compiled the runtime resources. No release installer or standalone
  side-by-side UI session was built; headless comparison is a separate gate.

The initial gallery setup failed on a missing required CVARINFO scope flag;
the isolated review was corrected and rerun. That failed launch is not counted
as runtime evidence. Blender's optional user-profile extension-cache write was
denied at shutdown; source save, reopen verification and renders succeeded.

Local evidence (ignored, not release content):

- [Scrolls and potions in GZDoom](../artifacts/pickup-models/after-sheet-4.png).
- [Equipment in GZDoom](../artifacts/pickup-models/after-sheet-2.png).
- [Jewelry and treasure](../artifacts/pickup-models/after-sheet-9.png).
- [Blender studio overview](../artifacts/pickup-models/studio-sheet-1.png).
- [Normal floor, before](../artifacts/pickup-models/normal-before/start.png)
  and [after](../artifacts/pickup-models/normal-after/start.png).
- [Persistent verification record](../assets/items/pickup-verification.json).

## Reproduction

```powershell
python -m tools.pickup_models.generate
python -m tools.pickup_models.index
python -m unittest tools.pickup_models.test_detailed tools.test_broguedoom_resources
python -m tools.pickup_models.review
powershell -ExecutionPolicy Bypass -File scripts/review-pickups.ps1 -Phase before
powershell -ExecutionPolicy Bypass -File scripts/review-pickups.ps1 -Phase after
powershell -ExecutionPolicy Bypass -File scripts/review-pickups.ps1 -Phase normal-before
powershell -ExecutionPolicy Bypass -File scripts/review-pickups.ps1 -Phase normal-after
python -m tools.pickup_models.review --sheets
python -m tools.pickup_models.verify_review
```

Normal review requires the preserved seed-one map-only
`artifacts/rat-model/floor1.pk3`; baseline review requires the preserved old
pickup folder and atlas under `artifacts/pickup-models/baseline/`. Inspect
captures before running the verification recorder. Original art and required
attribution are documented in [the pickup README](../assets/items/README.md).
