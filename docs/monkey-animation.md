# Monkey presentation and captivity

Presentation-only implementation, 2026-09-06. Brogue CE remains authoritative.

## Delivered

The monkey now has an original reddish-brown fur skin, bare face, rounded ears,
fingers, long arms, short legs and a curling tail. Its connected body is weighted
to 23 bones. Both editable Blender sources contain all eight Actions and a packed
skin. The standing head is about 33 map units high; Brogue supplies no metric
height, so this is an artistic choice for a small monkey, not a gameplay size.

The normal IQM has 6112 UV-split vertices and 10098 triangles.
The captive variant adds visible iron wrist cuffs and an articulated chain to the same body.
Normal clips are idle, walk, bite, snatch, recoil and death. Captivity adds a bound
loop and a 21-tic release. The resting arms were separated from the torso before
voxel fusion to prevent a stretched skin web during reaching; shoulder attachment
remains continuous. A regression rejects forearm-to-torso weight bridges.

The shared skeletal registry now supports optional captivity profiles. This keeps
later captive enemies in the same model/clip/class selection path. The generated
native lookup and MODELDEF/ZScript bindings include the new variant. The separate
class is a presentation variant of Brogue kind 5, not a new monster.

## Authority and state

`BrogueBridgeCreatureState.bookkeepingFlags` already copies `MB_CAPTIVE` (bit 8).
No bridge ABI or simulation change was needed. The frontend chooses the bound
model from that snapshot flag. It removes the cuffs immediately when the flag
clears. An observed change from captive to ally plays the release only when the
creature was and remains directly visible and its presented identity matches its
actual identity. Repeated snapshots do not replay it. New attachment, saved games
and unseen changes settle. New movement can replace the cosmetic release clip.

Bumping the captive still follows `playerMoves()` in `Movement.c`: Brogue asks
“Free the captive monkey?”, handles its existing key/terrain promotion when
applicable, calls `freeCaptive()` / `becomeAllyWith()`, and ends the player turn.
Declining leaves it captive. Brogue decides allegiance, movement, attacks and RNG.
No Doom AI, damage, collision or turn gate was added. Existing terrain owns cages;
open-floor captives receive wrist restraints and the existing manacle terrain, not an invented cage. Closed/open cage assets
and key rules were retained without changes.

`brg_monsters` now reports proxy class, captivity, clip and remaining pose tics.
The development command `brg_confirm yes|no` feeds the same pending-command
confirmation handler as keyboard input. It cannot skip Brogue validation or the
stored revision check.

## Verification

Local evidence is under `artifacts/monkey-animation/` (not release content).

- Canonical source build: `scripts/build-source-bridge.ps1 -SkipTests`; native
  UZDoom and the self-contained ProjectBroom launcher build. NuGet restore requires
  network access. Initial local attempts and their failures remain in the logs.
- Full suite: `scripts/test.ps1` — 157 tests passed, including connected cages/UV seams, exact IQM
  regeneration, normalized weights, physical bindings and release endpoint poses.
  The new public-DLL fixture follows the natural seed-2 route, checks prompt and
  decline stability, rejects stale/duplicate confirmation, frees the ally, and
  repeats substantive continuation hashes. The monkey is freed at turn 17;
  hostile kobolds kill the player at turn 22 in this short continuation.
- Cold Blender cage bakes produce identical bytes. Both IQMs regenerate exactly;
  repeated mod PK3 generation is byte-identical. Rat, kobold and jackal IQMs,
  cage caches and animation manifests match the pre-monkey baseline byte for byte.
- Fresh reopen of both Blender sources verifies 23 bones, eight Actions, packed
  image, no linked library, and sampled deformation against the runtime solver.
- Actual UZDoom Vulkan and OpenGL: 31 normal/static-reference/angle samples plus
  seven bound/release samples per renderer. All gallery actors report non-solid.
- Packaged natural seed-2 encounter on both renderers: decline, confirm, immediate
  rope removal, release, settled ally and next action. Turn 17 matches bridge hash
  `891359fb198ed00f`; turn 18 matches `aed1b77be1e3f7e6`. Repeated `brg_monsters`
  reconciliation does not restart release. The two initial release log entries
  are attachment plus the one-time reapplication after Spawn initializes.
- Native save reconstruction on Vulkan: turn-16 captive restores bound, turn-18
  ally restores free, and neither load emits a release clip. Save animation state
  is neither written nor needed.
- Five naturally generated captive routes repeat byte-identically:

| Seed | Freeing turn | Resulting hash |
|---|---:|---|
| 2 | 17 | `891359fb198ed00f` |
| 13 | 34 | `18054859085385e6` |
| 25 | 42 | `f8dad6398f533380` |
| 42 | 39 | `be66fe363b4cc4fe` |
| 57 | 38 | `cb261df8fe34c018` |

The full-suite seed-1 long run ends naturally at turn 195, killed by a rat; it is
not a completed 300-action survival scenario. No standalone graphical side-by-side
comparison, locked-cage/key release capture, multi-depth captive revisit, or fixed
frame-time benchmark was performed specifically for this monkey. The natural
release captures are open-floor captives. The full gallery covers clips in an
isolated scene, not every possible combat context. User art approval remains open.

## Reproduction and licensing

See [asset README](../assets/monsters/monkey/README.md) and
[shared authoring workflow](skeletal-enemy-workflow.md). Original mesh, skin, rig,
ropes and clips use the repository's CC-BY-SA-4.0 asset license. No external art
was imported. Static OBJ and its original skin remain available as references.

Normal IQM SHA-256: `a8448b4e54d87d99af6d44a25d573f6f574eab92429fa6de068bf4dd16bcc8e6`.
Captive IQM SHA-256: `e83a184e0fd7caeb66d39e240c623e5d8e95bc5da0b779955f00b17fb7a1b2c1`.

## Restraint repair (2026-09-07)

Research against pinned source found a missing terrain presentation: `drawManacles()`
in `Monsters.c` places up to four of eight `MANACLE_*` surface tiles around ordinary
captives. `Globals.c` describes thick iron manacles anchored to ceiling (TL/TR),
floor (BL/BR), or wall (cardinal variants). Every registry entry previously had an
empty actor, so these surrounding restraints were absent despite being exported
in copied appearance. The existing monkey wrist ropes were also thin and brown.

All eight symbols now have physical iron chain/cuff models. The reconciler uses
copied ground or remembered structure and real wall boundaries; ceiling attachment
compensates for OBJ pixel stretch. With no known adjacent wall, the cardinal
manacle has a documented floor-chain visual alias. These are noninteractive terrain
proxies with normal knowledge gating. The monkey's cuffs are thicker iron loops
with eleven connecting links, weighted to its wrist bones. Ordinary monkey mesh
and clips are byte-identical; the shared atlas's restraint swatch is now iron gray.

`freeCaptive()` calls `becomeAllyWith()` and does not erase manacle terrain. Therefore
the cuffs disappear on release, while abandoned terrain chains remain until Brogue
changes their cells. No ABI, gameplay, RNG, or turn-processing changes were made.
The public-DLL regression now checks copied visible manacles around the natural
seed-2 captive and verifies their persistence after release, alongside the existing
confirmation, stale command, duplicate command, and RNG-continuation assertions.

Current captive IQM SHA-256:
`839953982a17b228b72665afbc31d1f85ea9defe2f99ab2385913f6e3ec6ab47`.
The earlier hash above records the original rope variant. Both Blender sources
were regenerated and freshly reopened with 23 bones, eight Actions, packed skin,
and sampled runtime deformation checks. Evidence for this repair is separately
stored in `artifacts/monkey-restraint/` and `artifacts/monkey-restraint-*.log`.

Repair validation: canonical source/launcher build and engine fingerprint passed.
The updated six-test monkey suite passed, including deterministic IQM regeneration
and the natural public-DLL sequence (four visible copied manacles retained after
release). Both editable Blender files passed fresh reopen and sampled deformation.
Packaged mod assets were generated byte-identically on two successive runs.
Actual seed-2 encounters on Vulkan and OpenGL passed decline, confirmation, release,
settled ally and next-action checks: release turn 17 hash `891359fb198ed00f`, then
turn 18 `aed1b77be1e3f7e6`. Vulkan restored both the turn-16 captive and turn-18 ally
without replaying release. These are real natural encounters through the normal
bridge action path, with a presentation-only camera following the monkey.
No new standalone graphical comparison or locked-cage scenario was run.

Final repair verification: `scripts/test.ps1` passed all 166 tests after correcting
the generated bestiary's stale texture checksum. The seed-1 long run ended naturally
at turn 195 (rat), not a completed 300-action endurance scenario. Final native
runs in `final-vulkan` and `final-opengl` both repeated the seed-2 release hashes.
The additional native safeguard preserves a torch's mount when another surface
in the same cell needs a manacle wall mount. Final engine fingerprint validated.
