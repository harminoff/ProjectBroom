# Brogue CE → GZDoom runtime bridge

Status: bridge API v12, native GZDoom monster presentation, authoritative weapon and consumable commands, generalized Brogue confirmation forwarding, an authoritative loss screen, fall-source/landing events, and visual-only first-person weapon models are implemented and built from the official GZDoom 4.14.2 source checkout.

## Chasms and fall shafts

The map compiler uses Brogue's `isChasm` semantic together with the
authoritative `T_AUTO_DESCENT` terrain flag. Actual falling cells are rendered
as bounded 128-unit near-black cave openings; safe chasm-edge cells remain at
the surrounding floor height. The bounded recess keeps the room across a
chasm visible instead of projecting tall black lower-wall columns into the
view. Brogue still resolves the fall and level transition, so this visual depth
does not affect gameplay. This also avoids treating Brogue's broader edge
semantic as a hole.

Ground-to-chasm portals use shared, nonblocking beveled edges recessed 10 units
into the abyss. Both sectors reference the same angled shoulders, so their
polygons remain closed while the 64-unit square silhouette is softened. A
purpose-built `BRGCLIFF` lower texture supplies a full-height rocky cliff that
remains readable across the gap, then dissolves through an irregular dark
fringe into the abyss instead of ending at a ruler-straight lower edge.
Bridge edges remain straight so the deck width and Brogue cardinal topology
stay visually unambiguous. Player and creature projections still land on the
unchanged Brogue cell centers.

Generated sidedefs use UDMF's canonical `texturetop`, `texturebottom`, and
`texturemiddle` fields. Earlier builds emitted the nonstandard names
`textureupper` and `texturelower`; GZDoom ignored those keys and its missing
lower-texture path exposed horizontal floor or liquid materials across vertical
height transitions. The verifier now rejects those legacy fields and requires
an actual bottom texture on both sides of every floor-height transition.
Ordinary height offsets for water, lava, mud, and other surfaces use the
higher cell's structural cave, wet-rock, or masonry bank. Animated
`BRGWFALL`/`BRGLFALL` sheets are not selected for these offsets, so a raised
platform cannot inherit the neighboring liquid as its vertical face.

Depth 1 retains a continuous cave ceiling at 224 units. Depths 2–40 raise the
logical ceiling to 352 units and use GZDoom's `F_SKY1` ceiling with the
dedicated near-black `BRGSKY` texture. Because sky ceilings do not draw a
horizontal plane, looking upward after a fall reads as open darkness rather
than the underside of the independently generated floor above. Their one-sided
boundary walls use tall `BRGCVUP`, `BRGWTUP`, or `BRGMSUP` textures: normal
rock or masonry reaches the original 224-unit cave line, then an irregular
128-unit attached band fades upward into the black sky. Keeping this gradient
on the wall avoids the camera-relative horizon band produced by painting it
into the sky texture. This is presentation only: Brogue's separately generated
levels are still not claimed to align vertically.

Chasm darkness on depth 1 is rendered only below floor level by the recessed
pit floor and shaft walls. Chasm sectors retain ordinary cave light so the
brown-gray cliff faces across or around an opening remain readable; their lower
fringe fades into the dedicated near-black abyss flat that provides the apparent
depth. A cell-local black ceiling was
rejected because its horizontal polygons projected as moving rectangular
occluders when viewed from a bridge or brink.

Immediately before `startLevel()` replaces the source `pmap`, the adapter
records the exact cell from which the player fell. API v12 marks the resulting
`LEVEL_CHANGE_REQUESTED` event with `BROGUE_EVENT_FLAG_LEVEL_FALL` and copies
the source and authoritative destination coordinates into `fromX/fromY` and
`toX/toY`. Once the destination map is live, GZDoom places a presentation-only
dark recessed shaft beneath the landing cell's open void. Stair transitions do
not create this marker. The destination's collision and Brogue
topology remain unchanged; independently generated depths are not falsely
treated as vertically aligned maps.

## Authority boundary

The bridge executable reuses the pinned Brogue CE core at `src/brogue-mapgen/`. It does not duplicate movement, combat, terrain, monster, or turn rules. The public header at `src/brogue-mapgen/src/brogue/BrogueBridge.h` contains only fixed-width values, enums, copied strings, arrays, and a public opaque-contract shape. Brogue internal pointers and structs never cross that header.

There is one active session. The adapter owns stable IDs for creatures and items by tracking Brogue pointers internally; those pointer values are never returned to a consumer. Empty identity slots are reused after an entity disappears.

## Source-backed lifecycle and action path

The current local source establishes this startup path:

```text
brogue_bridge_initialize()
  → initializeGameVariant()          // VARIANT_BROGUE, not Rapid Brogue

brogue_bridge_start_game(seed)
  → initializeRogue(seed)            // master RNG and per-depth levelSeed values
  → startLevel(rogue.depthLevel, 1)
      → seedRandomGenerator(levels[depth - 1].levelSeed)
      → digDungeon()                 // Brogue's complete dungeon pipeline
      → placeStairs() / retry logic
      → initializeLevel()             // normal initial static level setup
      → player placement and level-entry state

brogue_bridge_perform_action(MOVE_*)
  → playerMoves(direction)           // Brogue legality, doors, attacks, terrain
      → playerTurnEnded()            // Brogue scheduler, monsters, environment

brogue_bridge_perform_action(WAIT)
  → playerTurnEnded()                // no custom wait rules
```

`initializeRogue()` is called once. Its normal sequential initialization creates the per-depth seeds and all cross-depth metered state before `startLevel()` generates depth one. The adapter does not derive a replacement level seed.

Movement direction values are translated only at the boundary to Brogue's existing `UP`, `UPRIGHT`, `RIGHT`, `DOWNRIGHT`, `DOWN`, `DOWNLEFT`, `LEFT`, and `UPLEFT` values. The adapter does not perform a destination-cell legality check. `playerMoves()` returns whether the intent was accepted; turn consumption is measured from Brogue's `absoluteTurnNumber` before and after the call.

The null platform is configured for synchronous headless execution. `serverMode` and `nonInteractivePlayback` route terminal cleanup away from Brogue's interactive UI. Server mode skips only the terminal death-acknowledgment loop; it does not set `rogue.quit`, so genuine deaths retain Brogue's death outcome and score. During a semantic bridge command, `IO.c::confirm()` first delegates to the bridge confirmation broker. With no approved response remaining, the broker copies Brogue's exact prompt and supplies a safe negative response, allowing the action to unwind without a turn or revision change. GZDoom can then retry that exact command and revision with one more approved prompt. Confirmations outside a live bridge command retain the deterministic server/noninteractive policy.

## State and events

`BrogueBridgeState` includes:

- game seed, current level seed, depth, dimensions, turn counters, and revision;
- copied player coordinates, HP, status summary, and terminal state;
- all 79×29 cells, all Brogue terrain layers, raw cell flags, resolved terrain/mechanical flags, volume, machine number, fire exposure, and derived semantic booleans;
- copied live creature state with stable IDs, authoritative visibility,
  presentation kind, ally state, HP, status, mutation, and catalog flags;
- copied floor and carried item metadata with stable IDs, authoritative
  visibility, and presentation-safe identity knowledge;
- copied current message lines;
- a copied terminal result containing Brogue's outcome, cause, exact result
  sentence, score, death depth, deepest depth, and turn;
- deterministic FNV-1a 64-bit gameplay and presentation hashes.

The revision starts at 1 for the initial snapshot and increments once for every valid action request, including a blocked request. Events are ordered by a monotonically increasing bridge sequence. Native hooks record movement, attack attempts, damage, and death at Brogue's own action points; snapshot differences supplement spawn/removal/state, terrain, player, message, and level events. The gameplay hash excludes hallucination appearance and visibility, while the presentation hash covers them. Hallucinated forms use Brogue's cosmetic RNG without advancing its substantive gameplay RNG.

`brogue_bridge_get_monster_catalog()` exports all 68 local catalog entries
(the player entry plus 67 non-player kinds) without exposing `creatureType`.
`tools/monster_models/generate.py` uses that export to generate the checked-in
catalog, registry, ZScript classes, texture atlas, MODELDEF bindings, and one
deterministic low-poly OBJ silhouette for every kind.

## Headless command and tests

Build the bridge with:

```powershell
pwsh -File scripts/build-bridge.ps1
```

Run a semantic action sequence:

```powershell
pwsh -File scripts/run-bridge-test.ps1 -Seed 1 -Actions "WAIT,N,E,SE,WAIT,W"
```

Or invoke the executable directly from `src/brogue-mapgen`:

```text
bin/brogue-bridge.exe --seed 12345 --actions "N,NE,E,WAIT"
bin/brogue-bridge.exe --seed 12345 --long-run 300 --verbose
```

The CLI emits `INITIAL`, per-action `ACTION`, per-action `STATE`, and long-run `FINAL` records. `--verbose` adds ordered event records and action boundaries. The black-box test suite is:

```powershell
python -m unittest tools.test_brogue_bridge
```

The test suite proves seed-one initial state, exact repeatability including output hash, repeatability across five game seeds, blocked movement without a turn, all semantic movement action names, and a deterministic long run through the authoritative monster/turn path until the Brogue state reaches its normal terminal result.

When Brogue ends a run, `gameOver()` remains the source of the outcome. After it
has constructed the same sentence used by the original death screen, the bridge
copies that sentence and its score into `BrogueBridgeGameResult`. GZDoom stops
all queued actions and draws a crisp Brogue-style loss panel. Space, Enter, Esc,
or primary click returns to the main menu; none of those presentation inputs
advance the ended Brogue simulation.

## GZDoom integration

`scripts/bootstrap-dev.ps1` checks out official GZDoom 4.14.2 under the ignored
`.deps/gzdoom-source/` directory, pinned to commit
`99aa489d09015a95bb78df2b30ede29f328cc874`, and applies the checked-in Project
Broom integration patch.

The source build adds `src/gzdoom-bridge/brogue_bridge_frontend.cpp` to the engine and uses
`src/brogue-mapgen/bin/brogue-bridge.dll` as a same-process C ABI adapter. The
DLL boundary isolates Brogue's global C state without using networking or a
second simulation. The engine loads it from beside the source-built `gzdoom.exe`, starts
Brogue on the first `BRGxx` level tick, and invokes the public bridge API
synchronously on the GZDoom game thread.

`G_Responder` intercepts arrow, movement, and Space keys before normal Doom
bindings. Key-up events are consumed, key-down events become semantic
`MOVE_*` or `WAIT` actions, and Brogue's returned state projects the player to
the existing `x * 64 + 32`, `(28 - y) * 64 + 32` cell center. Arrow directions
remain absolute. WASD is camera-relative: `W` moves forward, `S` backward, `A`
left, `D` right, and `E` forward-right; the camera yaw is quantized to Brogue's
eight directions. Space submits `WAIT`. The numpad is reserved for the explicit
side-by-side parity mode, where one key edge is delivered to both applications.
At the end of command construction, all Doom translational/action buttons are
cleared, so Doom physics cannot advance the authoritative player.

Build and launch the source-integrated executable with:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/bootstrap-dev.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/build-dev.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/run-dev.ps1 -Seed 1
```

The source engine is configured with CMake and built as `gzdoom.exe` under
`.build/gzdoom/`. The native integration files are
`src/gzdoom-bridge/brogue_bridge_frontend.h` and
`src/gzdoom-bridge/brogue_bridge_frontend.cpp`; the small upstream hooks are
recorded in `patches/gzdoom-project-broom.patch`.

For a deterministic in-engine smoke without synthetic keyboard injection, the
source build also registers the development command `brg_wait`. Because startup
commands are processed before `+map`, it queues until `BRG01` is active:

```text
gzdoom.exe ... +map BRG01 +brg_wait
```

The resulting log should contain an attachment line followed by
`Brogue command=WAIT accepted=true` with an incremented turn and bridge
revision. Physical direct-input controls remain available through the normal
GZDoom window.

### Dynamic doors and stair presentation

Closed Brogue doors are generated as zero-height sectors with the stable tag
`10000 + y * 79 + x`. They have two-sided portals toward connected cells and
use the Project Broom door panel as their upper texture. They do not carry a Doom
line-use special.

Brogue's closed `DOOR` terrain deliberately does not obstruct passability: a
move into it promotes the terrain as part of Brogue's action processing. It
does still obstruct vision. The compiler therefore derives initial closure
from the raw closed-door terrain symbol, and the runtime bridge derives it from
`isDoor && blocksVision`; neither uses `isSolid`. `OPEN_DOOR` retains the same
addressable door sector but starts, or is moved, to the surrounding ceiling.

When Brogue promotes or otherwise changes a door cell, the bridge consumes the
ordered `BROGUE_EVENT_CELL_TERRAIN_CHANGED` event, reads the authoritative
post-turn cell state, and raises or closes that tagged sector with GZDoom's
native sector-door mover. Consequently, the normal interaction is Brogue's:
bump/move toward a closed door, let Brogue decide whether it opens and whether
time is consumed, and only then animate the GZDoom sector. The Use key does not
bypass Brogue.

The logical stair actors remain invisible at the exact Brogue stair cell
centers. Separate presentation actors use deterministic static OBJ models from
`mod/BrogueDoom/models/stairs/`, bound through `MODELDEF`; this avoids billboard
rotation while retaining the existing level-travel contract. Upstairs are
shown as wall-height ladders. Downstairs are shown as stone-rimmed dark pits
with short ladders entering the opening. Entering an armed stair cell triggers
travel; the cell is initially disarmed while occupied so starting a game or
arriving on a destination ladder cannot immediately send the player away
again. Stepping off arms it for the next entry in the stock-engine visual
fallback. In the source-integrated frontend, Brogue's existing `playerMoves()`
stair branch invokes `useStairs()` and emits `LEVEL_CHANGE_REQUESTED`; only
that authoritative event asks GZDoom to load the matching `BRGxx` map.
The up-ladder marker carries a generated UDMF `scaley` derived from its exact
sector floor and ceiling. Its rails therefore terminate at the ceiling in
corridors, rooms, and tall liquid caverns alike. A separately skinned near-black
model surface sits just below that ceiling as the hatch/opening above the
ladder.
Depth-change events are emitted before bounded cell/entity deltas because a
new floor changes nearly every snapshot cell; cross-floor deltas are omitted
and the new full snapshot supplies the destination state. This prevents the
level event from being lost when the event buffer reaches capacity.

For deterministic in-engine regression tests, `brg_actions` queues semantic
directions and executes one through the bridge per tic after the map loads:

```text
+brg_actions W W NW WAIT E
```

This is a development harness, not an alternate movement implementation.

## Pickup presentation

The live source bridge now mirrors every floor item as a non-interactive
GZDoom presentation actor. `assets/items/brogue_pickup_registry.json` enumerates
all 100 item kinds from the local Brogue CE catalogs: food, weapons, armor,
potions, scrolls, staves, wands, rings, charms, gold, the Amulet of Yendor,
luminescent gemstones, and all key types. The deterministic generator at
`tools/pickup_models/generate.py` produces 100 individual low-poly OBJ models,
plus generic potion, scroll, staff, wand, and ring models for unknown
identities. Models and classes are bound through the static mod's `MODELDEF`
and ZScript includes.

Brogue remains authoritative for placement and pickup. The frontend addresses
an item by its bridge-stable ID, projects its Brogue cell through the same
64-unit coordinate transform as the player, and keeps the existing actor while
that item remains on the floor. When normal Brogue movement picks the item up,
the next state snapshot marks it carried and the frontend removes its floor
proxy. These actors have no Doom collision or inventory behavior.

Visibility comes from `playerCanSeeOrSense()` in Brogue. Unseen item proxies
remain allocated but invisible, avoiding actor churn as FOV changes. Brogue's
identification state also controls presentation: randomized categories use a
category-generic model until the kind is actually known, preventing the 3D
frontend from revealing potion colors, scroll titles, ring types, or other
hidden information. `brg_pickups` prints this presentation-safe view for
development diagnostics; unknown kinds are reported as `-1`.

## Monster presentation

Every live non-player Brogue creature is mirrored by one non-interactive
`BrogueMonsterProxyBase` actor keyed by its bridge-stable ID. These actors have
no Doom AI, collision, damage, or rules. The native frontend updates the same
actor across movement, faces it toward the authoritative destination, and uses
short transform animations for movement, attacks, damage, and death. Input is
gated while those animations run and buffers at most one next action, so frame
rate and held input cannot create extra Brogue turns.

Visibility is entirely Brogue-owned. Hidden actors stay allocated but use zero
alpha; sensed creatures use a translucent proxy; directly visible creatures
use their catalog presentation. Allies carry GZDoom's friendly display flag
for the minimap only. `brg_monster_omniscience` is an explicit development
override and does not alter Brogue state. During hallucination, a proxy may
change its model class while retaining the same bridge ID. Ultimate Classic
Minimap recognizes these presentation-only actors without requiring the Doom
monster flag and skips hidden zero-alpha proxies.

Useful diagnostics are:

```text
brg_monsters
brg_monster_anim_tics 5
brg_monster_omniscience false
```

## Lighting and particle presentation

The bridge API v12 cell snapshot exposes copied `isFire` and `isGas` semantic
flags alongside liquid and lava state. The native frontend uses those flags to
maintain non-interactive `BrogueLavaFx`, `BrogueFireFx`, and `BrogueGasFx`
actors at the same Brogue cell centers used by the map compiler. Movement into
water and authoritative projectile-impact, entity-damage, and entity-death
events create short-lived cosmetic bursts. No effect actor blocks, damages,
pushes, rolls gameplay RNG, or submits an action to Brogue.

`brg_fx_quality` is an archived native setting with three levels: `0` disables
bridge particles and ambient effect actors, `1` is the sampled and
distance-culled default, and `2` increases particle density and samples lava
cells more densely. Fire and gas cells are never sampled away. The options menu also
exposes GZDoom's bloom, SSAO, dynamic-light shadow-map, and actor-shadow
settings without forcing expensive defaults. Ambient lava and fire lights are
explicitly excluded from shadow maps to keep large liquid caverns tractable.

`mod/BrogueDoom/GLDEFS` binds warm flickering lights to authoritative lava and
fire proxies, an impact flash to projectile events, an emissive brightmap to
the molten fissures in `BRGMOLT`/`BRGLFALL`, and a restrained floor glow to
lava. `BRGLAVA_BM.png` is a deterministic mask derived from the original lava
texture rather than a gameplay asset. Presentation particles use isolated
named cosmetic RNG streams and cannot perturb Brogue's RNG.

## Executable and title menu

`ProjectBroom.exe` is the player-facing entry point. On a normal double-click it
chooses a cryptographically random positive seed, runs the pinned Brogue
exporter for all 40 depths in canonical order, compiles or reuses the matching
GZDoom campaign, and then opens the Brogue-styled title menu. Selecting **New
Game** starts `BRG01` and initializes the live bridge with that same prepared
seed, so generated geometry and authoritative simulation cannot disagree.

For deterministic menu smoke tests only, `ProjectBroom.exe --seed 1` prepares a
specific seed. The underlying development launcher also accepts `-Menu` or can
continue to launch directly into `BRG01` when `-Menu` is omitted. The most
recent hidden preparation transcript is written to
`artifacts/launcher-last.log`.

The title loop uses `mod/BrogueDoom/graphics/TITLEPIC.png` as a fixed dungeon
backdrop and the small glyphs extracted from Brogue's own font sheet for the
menu text. Its title-page interval is deliberately pinned because this frontend
does not ship Doom demo or credit pages to rotate into.

Load/save is intentionally absent from the title menu until Brogue bridge state
serialization is implemented. Loading only GZDoom's presentation state would
not restore the authoritative Brogue simulation.

## Known limitations

- The native source build currently uses a Windows DLL loaded beside `gzdoom.exe`; it is in-process but not yet a statically linked GZDoom target.
- The API v12 GUI snapshot exposes copied Brogue-owned player statistics,
  equipment slots, inventory order and letters, item descriptions and action
  masks, three message lines, and each cell's final `getCellAppearance()`
  Unicode glyph and foreground/background RGB colors in addition to discovery
  state. The native frontend renders a permanent Brogue-style left rail,
  message strip, context footer, visibility-safe 79x29 ASCII minimap, and modal
  two-pane inventory and a dedicated two-pane weapon/equip/throw selector. Both
  runtime fonts are extracted from the pinned Brogue CE tile sheet and rendered
  only at whole-pixel scales. Inventory and weapon descriptions wrap against
  their actual pane width rather than a fixed character count.
- `L` opens a non-turn-consuming look cursor. Cursor movement and Tab/wheel
  target cycling happen only in the frontend, while `brogue_bridge_inspect_cell`
  returns visibility-safe descriptions from Brogue's own `describeLocation`,
  `monsterDetails`, and `itemDetails` paths. GZDoom renders the selected cell
  marker and a compact Diablo-style inspection card; it does not infer hidden
  creature or item identities.
- Item and monster inspection details preserve Brogue's explicit paragraph
  breaks and embedded RGB color changes in copied bridge-owned spans. The Look
  card renders that authoritative detail once, without prepending the shorter
  location summary or rebuilding item prose in GZDoom.
- Inventory navigation is frontend-only and consumes no turn. Equip/remove,
  drop, throw, and apply are semantic bridge commands; Brogue validates and
  executes them. Food, potions, scrolls, and charms route through Brogue's
  existing item action functions. The bridge returns confirmation prompts
  before mutation and returns stable-ID choices for identify/enchant scrolls.
  Targeted staff/wand use, discovery/help screens, death/victory screens, and
  save/replay frontends remain deferred.
- Brogue prompts reached by movement, combat, and item commands are forwarded
  through the generalized confirmation broker. Prompts reached outside a live
  semantic command still use the deterministic noninteractive policy.
- Level transitions are reported through state/event changes but are not yet swapped by a live GZDoom frontend.
- Pickup and monster models are an initial procedural low-poly presentation
  set. Item-use interactions, final combat effects, 3D FOV treatment,
  save/replay frontend, and complete multi-level runtime
  synchronization remain future work.
- The long-run smoke pattern deliberately walks a small region and can reach Brogue's normal death state before the requested action count. That is evidence that the real monster/turn path is running, not a substitute for a long-lived survival scenario.
