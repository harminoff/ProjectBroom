# Goblin warlord model and animation

BRG-M51 / `MK_GOBLIN_CHIEFTAN` (Brogue kind 51, runtime class `BrogueMonsterK51`).
This is presentation-only phase-1 authoring under the v2 creature pipeline
([creature-pipeline.md](creature-pipeline.md)). The coordinator still has to
integrate, gate, and give art approval. The legacy static OBJ stays in place as
the gallery's "before" reference.

## Source facts and art interpretation

Pinned Brogue CE (`Globals.c` catalog L1127, prose L1333) describes the goblin
warlord as "taller, stronger and smarter than other goblins". It commands its
kind and can summon them (`MA_CAST_SUMMON`, the war-cry summon text). Its
attacks penetrate (`MA_ATTACKS_PENETRATE`), and it keeps its distance and
avoids corridors. Its glyph is blue. Horde rows L819/L847 make it the
summoner/leader of goblins, conjurers and mystics, including as a machine boss.

The model uses these facts as follows:

- **Taller and heavier.** The body was rebuilt in goblin-family units, not
  uniformly scaled from the goblin. The torso, trapezius, deltoids, arms and
  thighs are broader, the legs are longer, and the belly is heavier. The
  accepted goblin craniofacial surface (`goblin_animation.sculpted_head`,
  imported read-only) is reused with a heavier jaw and brow, lower tusks and
  larger amber irises. The final scale is 1.15. The rest height is 54.8 units
  (the goblin is 39.2).
- **Penetrating attacks.** The model carries the goblin family's spear, as a
  longer war spear with an iron leaf blade, lugs and a cord binding.
- **Leader cues.** These are artistic interpretation, not new lore:
  - an iron half-helm with a nasal guard and curved bone horns;
  - a stiff blue crest;
  - a fur mantle;
  - a blue war cloak with a pale edge;
  - a blue pennant on the spear;
  - a riveted left pauldron with trophy fangs;
  - a painted leather baldric;
  - a belt with a buckle and a small trophy skull;
  - layered hide flaps, bracers and shin wraps;
  - chest scars.
- **Blue.** Blue is used only as the glyph identity cue on the crest, cloak,
  pennant, eye paint, a bold chest chevron and bands on the upper arms. It does
  not imply any power.
- **Painted anatomy (after coordinator review).** The skin now carries:
  - pectoral, sternum and abdominal separation;
  - rib and oblique shadows;
  - lit deltoids and dark armpits;
  - elbow, knee and knuckle creases, and thigh grooves;
  - darker hands and feet;
  - high-contrast chest scars;
  - a crossed leather harness with an iron boss.

  Iron specular was toned down so the helm no longer shows a chrome spot.

## Rig and clips

The rig has 21 bones: the goblin-family chain plus `spear`, `pennant` and
`cape`. It has six clips (40/24/22/24/12/32 frames):

- **`idle`:** the left fist rests on the hip in a commander's stance, and the
  right hand holds the spear upright with the pennant fluttering.
- **`walk`:** the left fist stays on the hip. This shared pose avoids pops out
  of idle.
- **`thrust`:** a lunging spear thrust with a roaring jaw. The key pose is held
  across the middle frame. Torso yaw and the spear angle sit off the 3/4 camera
  axis so the thrust is not fully foreshortened.
- **`cleave`:** a war-cry raise is held across the middle frame. The spear arm
  is fully extended above the helm with the shaft held overhead, the other fist
  is raised, the chest arches back, the jaw roars, the stance widens and the
  cloak flares. The chop follows. The feet slide wider on the floor for this
  stance.
- **`recoil`:** a flinch.
- **`death`:** the knees buckle, then the body topples onto its right side,
  rolled face-up. The limbs go slack on the floor and the spear drops flat in
  front.

`thrust` and `cleave` are cosmetic alternatives. They do not claim to identify
the attack verb that Brogue selected. The roar is not a synchronized summon
event.

Arms use a forearm-aware IK. It chooses the hand twist and elbow so that wrist
bend stays under 45° in every non-death frame, and moves pronation into the
forearm. Legs use two-link IK. Attack and recoil feet stay planted exactly.

No frame uses automatic floor compensation. Every frame stays inside the
centred cell (-32..+32 in X and Y).

## Surface

The fused anatomy is one closed connected cage: 3,100 vertices and 6,200 faces
(`SKIN_FACE_BUDGET=6200`), baked by `blender_skin.py`. `CONNECTED_SKIN` lives in
the module.

Every triangle of both the skin and the gear has its own padded 16 px island in
a 2048² atlas (`BRGWARLD.png`). Islands are laid out in Morton order of their
3D centroid. Paint is evaluated from rest position, normal, per-part parameters
and a baked proximity occlusion term. Painted light, occlusion and specular
pools compensate for flat engine light. The skin paint is continuous across limb
junctions.

The runtime model has 47,520 vertices and 15,840 triangles.

## Authority

This change is presentation only. It adds no new native, bridge, ZScript,
registry, collision, AI, RNG or gameplay changes. Summoning, the war cry,
distance keeping, corridor avoidance and penetration remain owned by Brogue
(`Monsters.c`). Gear is rigidly skinned and non-colliding.

## Files

- `tools/monster_models/goblin_chieftan_animation.py`, `goblin_chieftan_materials.py`, `test_goblin_chieftan.py`
- `assets/monsters/goblin_chieftan/` (manifest, `connected-skin.json.gz`, `goblin-chieftan-animated.blend`)
- `mod/BrogueDoom/models/monsters/51_goblin_chieftan.iqm`, `mod/BrogueDoom/graphics/BRGWARLD.png` (new lump; no collision)
- `assets/monsters/skeletal_pending/MK_GOBLIN_CHIEFTAN.json`

## Phase-1 verification

- Two cold `--threads 1` Blender 5.2 bakes produced identical output:
  - `connected-skin.json.gz` sha256 `d222df6c2e5ed3c196d73642ac09379f12a670c64b46cceb053123ea91cd3cd6`
  - cage hash `d99352cf…f9d775`
- Runtime file hashes:
  - IQM sha256 `1a20f5d69c408fdcbee56072b7cb126852a64a2dc2494c3e3b543266e41499a3`
  - PNG sha256 `1707d6f4a05d3dc9baa80f15a0b42836758740ad1bba899d691603673888a9a3`
- `blender_skeletal.py -- MK_GOBLIN_CHIEFTAN` passed with a fresh reopen
  (21 bones, six clips).
- `python -m unittest tools.monster_models.test_goblin_chieftan` ran 7 tests,
  all passing (about 50 s).
- Previews ran on both backends with `review_skeletal --preview --all-angles --distances` at 1920×1080:
  - Vulkan: `artifacts/creature-queue/BRG-M51/preview-vulkan{,-contact.jpg}`
  - OpenGL: `artifacts/creature-queue/BRG-M51/preview-opengl{,-contact.jpg}`

The coordinator has not yet run integration, gates or shared suites, and art
approval is still pending.

Original Project Broom mesh, texture and animation: CC-BY-SA-4.0. Brogue text
keeps its upstream license.

## Coordinator package archive

The coordinator returned the first delivery (flat olive torso reading as a jumpsuit, a cleave key pose indistinguishable from idle) and accepted the painted-anatomy/war-paint torso and overhead war-cry cleave. At gate time the creature test was changed to read its profile through `skeletal_registry.find`, because integration consumes the pending row. Round A was integrated and gated as pipeline batch `A` with the dar priestess, dar battlemage, goblin warlord, black jelly and unicorn (`artifacts/creature-queue/batches/A/gate-summary.json`: 87 tests OK, preservation audit with zero unexpected changes). Both final review packages (`761572a54dbd32a91407ca9cc82a4a7f5c6007f9919d70a01de10d5acc193dba`, 1,199 entries, shared by the batch) were compared entry-by-entry with current source (`parent-final-package-verification.json`) and losslessly archived after coordinator review of the final Vulkan and OpenGL galleries. Natural encounter gates are deferred to the later deeper-route census. Restore the exact Vulkan package with:

```powershell
python -m tools.monster_models.review_archive restore artifacts/creature-queue/BRG-M51/final-vulkan/ProjectBroom-review.pk3.archive.json
```
