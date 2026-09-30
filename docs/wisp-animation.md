# Will-o'-the-wisp model and animation

Presentation-only BRG-M23 / MK_WILL_O_THE_WISP. Brogue CE remains authoritative.

## Source, art and planned proof

The pinned source describes an ethereal blue flame dancing through the air,
flickering and pulsing. It supplies no eyes, limbs or solid body. This original
art uses interleaved curved flame tongues, a pale cyan heart, cobalt edges and
small detached flickers. Hover height, size and shape are art decisions.
Self-emission is confined to the mesh; it creates no world light or fire.
Burning, flight, flitting, negation, health, RNG and all action outcomes remain
in Brogue. No bridge or simulation change is planned.

Six cosmetic roles: idle, drift, flare, lash, recoil and extinguish. Only the
first two loop. Death contracts the licking tongues below visible size;
the native lifecycle removes the already-dead proxy. No gameplay burn effect
or target selection is added.

Planned proof: normalized weights, closed flame volumes, cyclic motion,
every-frame centered cell clearance, unit-scale extinction; deterministic
two builds; fresh-open background Blender sampled deformation; focused tests,
native compile/fingerprint; early engine review then final packaged 1920x1080
34-view Vulkan/OpenGL galleries using the same accepted bytes. Natural encounter
remains separate: the unchanged conservative route found none in seeds 1–2000.
User art approval remains open. Original assets are CC-BY-SA-4.0; no imports.

## Delivered art

Master source is `tools/monster_models/wisp_animation.py`. Runtime resources
are `mod/BrogueDoom/models/monsters/23_will_o_the_wisp.iqm`,
`graphics/BRGWISP.png` and `shaders/wisp-flame.fp`. Editable source and manifest
are `assets/monsters/wisp/wisp-animated.blend` and `animation.json`.
The old static OBJ, skin and Blender source remain byte-identical.

Nine closed curved flame volumes have 12,177 runtime vertices and 22,320
triangles, a 1024-square original blue/cyan atlas, 29 bones and six clips.
The flame has no eyes, limbs or humanoid anatomy. Tetrahedral interpolation
uses at most four normalized weights and reproduces rest coordinates exactly.
Translation of the field cage bends and contracts the flame without unsupported
bone scaling. The settled death is 0.0034 map units tall and visually extinguished.

Rest extents are 17.2263 / 17.0042 / 34 map units. Across all animation frames,
X stays -12.5793 to 16.3626, Y -10.1582 to 11.0055, and Z 15.7372 to 53.7478.
No floor compensation is needed. These are presentation dimensions, never
collision or flight rules. Mesh-local emission and additive transparency create
a pale core through overlapping surfaces; renderer-time brightness flicker
uses no Brogue input or RNG and emits no world light.

The early opaque version looked crystalline and left a flattened blue remnant.
The frozen refinement combines transparent curved tongues into a coherent flame
heart and fully extinguishes the death pose. Coordinator technical art review
accepted that refinement. Close views still show layered mesh boundaries and
banding; individual user art approval is open. Blender uses a packed emissive
transparent preview material; it is not a pixel-identical engine shader preview.

## Native visibility correction

Actual `ApplyMonsterVisibility` previously reset directly visible proxies to
Normal/1.0, overriding the wisp's Add/0.65 class defaults. The narrow correction
reads `GetDefaultByType(proxy.actor->GetClass())` for direct restoration. This is
the displayed actor class, so it cannot reveal the underlying hallucinated kind.
Hidden remains RF_INVISIBLE/0; sensed remains Translucent/0.38; ordinary opaque
classes retain Normal/1.0. No Brogue command, state, ABI, timing or collision changes.
The pending-map lifetime barrier and wall-mount selection remain intact.

The explicitly invoked `brg_monster_visibility_smoke` command only runs on ART01
with no active Brogue session and omniscience disabled. It creates transient
presentation proxies, calls the actual native visibility function for both rat
and wisp through direct, hidden, sensed and direct again, checks style/alpha/
invisibility/nonblocking, and destroys its own proxies. Its deliberately wrong
presentation-kind field checks that defaults come from the displayed class.
Both backends passed all eight transitions with failures=0 and Brogue_session=0.
The command makes no API call. The guard-before-spawn test covers rejection
conditions; an active-session invocation was not performed.

These are synthetic native-function assertions, not natural encounters. Images
in `visibility-native-1` and `visibility-native-0` show the gallery after the
transient probes have been destroyed; visibility assertions are the log evidence.
The fixture include participates in the engine build fingerprint and its mutation
is covered by the stale-build regression.

## Verification

Evidence root: `artifacts/creature-queue/BRG-M23/`.

- `tests-final.log`: 54 tests passed in 181.534 seconds using
  `python -m unittest tools.monster_models.test_wisp tools.monster_models.test_skeletal tools.monster_models.test_connected_skin tools.monster_models.test_creatures tools.test_broguedoom_resources`.
  This includes five initial wisp tests. After adding the guard regression,
  all six wisp tests passed in 18.949 seconds (`tests-wisp-final.log`).
- Six engine source/fingerprint tests passed in 2.174 seconds
  (`tests-engine-source-final.log`). These runs cover 61 distinct tests in total.
- `native-visibility-build-final.log`: native compilation and linking passed
  with `python tools/run_native.py cmake --build .build/uzdoom --config Release -j4`.
  `fingerprint-final.log` records the subsequent successful fingerprint refresh.
  An initial constructor mismatch against pinned FRenderStyle was corrected to
  `LegacyRenderStyles`; the earlier failure log is retained as superseded evidence.
- Blender 5.2.1 background rebuild passed with 29 bones and six Actions.
  A separate process freshly opened the final file, checked 18 sampled poses
  against the runtime solver (maximum error 0.000005462), exact packed texture
  bytes and no linked libraries. See `blender-fresh-verification.json`.
- Two final runtime builds reproduced IQM, diffuse, manifest, shader and GLDEFS
  byte-for-byte (`determinism.json`). This flame has no connected organic cage
  bake and no normal/specular maps. Blender file bytes are not deterministic.
- `final-vulkan` and `final-opengl`: actual packaged launches, 34 1920x1080
  screenshots each, 34 nonblocking actors per backend, static before, six clips,
  oblique/front/side/rear and 64/128/192-unit distances. Representative before,
  idle, attack, final death, side and far captures were inspected on both renderers.
  No new shader/resource errors occurred. These are isolated gallery checks.
- Both final PK3s are byte-identical and every archive entry matches current
  source, including shader, GLDEFS and bindings (`package-verification.json`).
  Native probes used this same final package.

Final SHA256 values:

| Asset | SHA256 |
| --- | --- |
| IQM | `a20ce0ab7d061bf673ac62d5f7fa31109d62d372391ba0659abf348219903fb6` |
| Diffuse | `0355777799eb688c283c2e9a112e622a84f17d13a618e03b3836f7bcbd51fb44` |
| Shader | `5bd540a210658425a03cc320bd1f3e861b740f86e29843cae3b0cd72a0efc051` |
| Final PK3 | `bee5c27d1705e66a3f04a2a7403e2b08c6e6c99ac76bc0475249d5617cb5b430` |

Reproduce the gallery with:

```powershell
python -m tools.monster_models.review_skeletal --symbol MK_WILL_O_THE_WISP --backend 1 --packaged --all-angles --distances --width 1920 --height 1080 --output artifacts/creature-queue/BRG-M23/reproduction-vulkan
```

Use backend 0 and a fresh directory for OpenGL. The artifact-local
`review-visibility.py` reproduces the native-function checks using the final
Vulkan package and fixture. `verify-fresh-blender.py` runs against the saved
Blend in a separate background process.

## Preservation and remaining gates

`preservation.json` records 517 baseline file hashes: 509 unchanged, eight
expected shared/assigned changes, zero missing. Every unrelated creature card
was restored from its immediate raw-byte backup and matches it exactly. All
previous creature assets/manifests, static references and wall_mount.h are
unchanged. The frontend's only intended edits are the direct material restoration
and fixture include. No cleanup, commit, publication or global settings changes.
`semantic-preservation.json` additionally reverses only the assigned entry and
reproduces the immediate baseline whole-file SHA256 for all three JSON registries:
22 prior skeletal profiles and 67 other bestiary/monster-registry entries are
unchanged. Reversing only the native visibility block and fixture include likewise
reproduces the frontend's exact baseline hash, proving that prior transition work
survived. No source files were restored during these comparison checks.

Shared files changed: skeletal profiles, generated native table/registry/
MODELDEF/ZScript, bestiary generator/index/cards, GLDEFS, optional default-off
Blender emission and additiveFlame preview, optional generated additiveFlame
proxy defaults, native visibility helper/fixture, and engine fingerprint inputs
plus test fixture. Other profiles keep their existing material defaults.

Natural encounter remains unresolved. The existing ordinary-intent copied-state
search covered seeds 1–2000 with 1500-action/depth-15 bounds. Analysis of its
1500 runs for seeds 501–2000 found no endpoint beyond depth 9, below the wisp's
nominal ordinary range 10–17; 619 runs ended dead and 881 stalled alive.
This explains why increasing the same bounds alone is unpromising; it does not
prove encounters impossible. The unchanged search was not repeated, and no
spawn, visibility or health override is claimed as natural proof.

Natural combat/hit/death, physical input, standalone comparison, full release
launcher packaging and user art approval remain open. The unrelated launcher
NuGet NU1301 path was not rerun. No gameplay changes require parity redefinition.

## Review package archive

Coordinator independently checked final IQM, skin, bindings, GLDEFS and shader against both packages. The review PK3s are losslessly archived with verified SHA256 manifests. Captures/logs remain available. Restore a package with:

```powershell
python -m tools.monster_models.review_archive restore artifacts/creature-queue/BRG-M23/final-vulkan/ProjectBroom-review.pk3.archive.json
```

Use the corresponding final-opengl manifest for OpenGL.
