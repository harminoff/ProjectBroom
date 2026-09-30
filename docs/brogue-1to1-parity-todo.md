# Brogue 1:1 Bridge Parity TODO

This backlog tracks the remaining work required for GZDoom to present and
control a complete Brogue CE game while Brogue remains authoritative. It does
not include changes that would reproduce Brogue rules in GZDoom.

## Audit status — 2026-09-10

Checked against the current ABI v23 source, implementation documents and recorded
verification. Checked implementation entries mean that the named feature is
delivered; they do not close separately listed physical-input, standalone,
exhaustive-family or endurance acceptance. Earlier documents that say all boxes
remain open refer to that broader acceptance, retained explicitly below.
This was a documentation audit; no new gameplay tests were run for this edit.

## Current authoritative baseline

- [x] Start Brogue from an authoritative seed and generated level.
- [x] Submit all eight movement directions and wait as semantic actions.
- [x] Let Brogue resolve movement, melee attacks, doors, monsters,
  environmental turns, and level transitions.
- [x] Export copied player, creature, item, cell, message, and game-result
  snapshots without exposing Brogue structure pointers.
- [x] Maintain stable bridge IDs for creatures and items.
- [x] Equip and remove weapons, armor, and rings through Brogue.
- [x] Drop and throw items through Brogue, including throw targeting previews.
- [x] Apply food, potions, scrolls, and charms through Brogue.
- [x] Forward Brogue confirmation prompts and identify/enchant selections.
- [x] Inspect cells through Brogue's own terrain, creature, and item text.
- [x] Synchronize level changes and terminal game outcomes.
- [x] Run deterministic seed/action and long-run bridge tests.

## P0: Complete the gameplay command surface

- [x] Add targeted staff use through Brogue's existing device and bolt logic.
  See [implementation and verification](targeted-staff-use.md).
- [x] Add targeted wand use through Brogue's existing device and bolt logic.
  See [implementation and verification](targeted-wand-use.md).
- [x] Add a generalized target preview containing Brogue-valid targets,
  trajectory, range, obstruction, and confirmation requirements.
  API v16 implementation and automated gates are delivered.
- [ ] Complete generalized-targeting physical-input and standalone visual
  acceptance. See [evidence and remaining gates](generalized-targeting-preview.md).
- [x] Add single-turn search.
- [x] Add repeated search until interrupted or complete.
  `SearchCommand` and SEARCH_START/CONTINUE/CANCEL use the shared native search
  path; five-seed differential tests cover completion and interruption.
- [ ] Complete search discovery-family, physical-input/focus, standalone and
  performance acceptance. See [search evidence and remaining gates](search-and-discovery.md).
- [ ] Add auto-rest.
- [ ] Add auto-explore.
- [ ] Add travel to a selected Brogue cell.
- [x] Add run-until-disturbed movement (ABI v24; Shift + move).
- [ ] Add explicit ascend and descend intents using Brogue's stair behavior.
- [x] Add rethrow-last-item (ABI v24; V).
- [x] Add swap-last-equipment (ABI v24; B).
- [x] Add item relabeling (ABI v24; inventory R).
- [x] Add calling/naming item kinds and inscriptions (ABI v24; inventory C).
- [ ] Add authoritative easy-mode activation.
- [x] Add authoritative new-game (launcher-backed, optional seed), abandon-game and quit commands (ABI v24).

## P0: General prompt and interaction contract

- [x] Replace special-case targeting flows with one bridge-owned interaction
  state machine (ABI v24: every command that asks a question, including Apply, throw,
  staff/wand and movement warnings, uses `brogue_bridge_respond`; the old apply and
  confirmation overlays are gone). See [contract](general-interaction-contract.md).
- [x] Support yes/no confirmations without mutating state before approval (migrated commands).
- [x] Support stable-ID item selections for all Brogue selection prompts (identify/enchant, Call, Relabel, ring replacement).
- [x] Support location targeting prompts (rethrow `TARGET_LOCATION`; throw/staff/wand keep their preview commands).
- [x] Support text entry for call and relabel commands.
- [ ] Support nested and sequential prompts while retaining the original
  command, expected revision, and approvals.
- [x] Make cancel behavior match Brogue and consume no turn when Brogue does
  not consume one.
- [x] Ensure one frontend confirmation executes exactly one Brogue command.

## P1: Expand the copied state contract

- [x] Export knowledge-safe dungeon/liquid/surface appearance layers independently
  of effect overlays (ABI v21). See [terrain overlays](terrain-overlay-implementation.md).
- [x] Export assigned potion colors and wood/metal/gemstone/scroll-title
  appearances independently of identification and Call text (ABI v22/v23).
  See [item appearances](item-appearance-implementation.md).
- [ ] Export status effect duration and magnitude, not only active flags.
- [ ] Export complete item device state, including charges and recharge state.
- [ ] Export secondary enchantment, quiver identity, runic target, origin
  depth, and other UI-relevant item metadata.
- [ ] Export Brogue's complete message archive with copied color spans.
- [ ] Export discoveries and identified-item knowledge tables.
- [ ] Export feats and complete run statistics.
- [ ] Export seed and mode information required by Brogue's information
  screens.
- [ ] Define versioned, bounded contracts for new arrays and report truncation
  explicitly.
- [ ] Ensure rejected commands advance the state revision only if
  authoritative state actually changes.
- [ ] Add an explicit full-resynchronization signal when an event stream is
  truncated.

## P1: Generalize dynamic terrain synchronization

The [geometry foundation and evidence](dynamic-terrain-foundation.md) now includes
ABI v20 copied appearance and a settled snapshot reconciler. The
[animation implementation and evidence](terrain-animation-research.md) adds
retargetable transitions and original physical assets. The settled update path
is delivered; full family-by-family runtime/parity acceptance remains open.

- [x] Replace terrain-change logging with a coordinate-addressed frontend
  update path for every changed Brogue cell.
  `ReconcileTerrain` applies complete snapshots through 2,291 cell bindings;
  changed cells and neighboring boundaries are reconciled in place.
- [ ] Synchronize secret-door discovery and door promotion.
- [ ] Synchronize appearing, collapsing, and falling bridges.
- [ ] Synchronize flooding, retracting liquids, and changing liquid depth.
- [ ] Synchronize freezing and melting ice.
- [ ] Synchronize spreading and extinguished fire.
- [ ] Synchronize gas type and volume changes.
- [ ] Synchronize trap discovery and activation.
- [ ] Synchronize machine and vault terrain promotions.
- [ ] Synchronize collapsing floors, holes, and chasms.
- [x] Update GZDoom collision and visual proxies only from the resulting
  Brogue cell state.
  The settled reconciler and retargetable animations derive support and owned
  actors from copied appearances. This does not close every promotion scenario.
- [ ] Verify terrain updates cannot leave stale blockers, missing walls, or
  presentation actors in previously changed cells.
- [x] Correct terrain-description/material bindings, floor-preserving overlays
  and malformed debris models. See [catalog verification](terrain-audit-verification.md),
  [overlays](terrain-overlay-implementation.md) and [debris](terrain-debris-repair.md).
  These are catalog/renderer checks, not exhaustive natural promotion coverage.

## P1: Save, load, and replay

Native save/load implementation and current evidence are in [save-and-load.md](save-and-load.md).
Native operations, reconstructed maps and proxy rebinding are delivered and
have command-driven/runtime/package evidence. Full interaction and exhaustive
continuation acceptance remain separate below. Replay UI is not implemented.

- [x] Expose Brogue's authoritative save operation through the bridge.
- [x] Restore Brogue simulation state and RNG through an authoritative load.
- [x] Rebuild or select the matching generated GZDoom depth after loading.
- [x] Rebind frontend creature, item, terrain, and player proxies after load.
  Native multi-depth round trips and extracted-package restore/WAIT checks are
  recorded in [save/load](save-and-load.md) and
  [restored terrain integration](terrain-animation-research.md).
- [x] Add saved-game selection to the player-facing executable and menu.
  Continue, Load/Import and Save and Exit exist in the launcher/native frontend.
- [ ] Complete physical-input chooser, close/failure-dialog, focus and
  standalone import/export UI acceptance; cover the outstanding active-status,
  device and pending-confirmation continuation families.
- [ ] Expose Brogue recordings/replays through the bridge.
- [ ] Add replay selection and playback controls.
- [ ] Validate replay state hashes at deterministic checkpoints.
- [ ] Add save/load round-trip tests across multiple depths and active status
  effects.

## P2: Visibility and 3D presentation fidelity

- [x] Match potion colors, staff woods, wand metals and ring gemstones to
  Brogue's assigned appearances, including held-device materials.
- [x] Put Brogue's assigned scroll titles on parchment and preserve selected
  appearances during projectile presentation without selecting hidden effects.
  [Appearance verification](item-appearance-implementation.md) includes five-seed
  naming checks, save/load flavor preservation and packaged Vulkan/OpenGL
  galleries. The moving-scroll fixture is not an interactive gameplay throw test.
- [ ] Apply Brogue visibility to the 3D presentation so GZDoom cannot reveal
  hidden creatures, items, or unexplored spaces.
- [ ] Present telepathy, invisibility, hallucination, magical detection, and
  memory exactly from Brogue's state.
- [ ] Show status duration and magnitude in the Brogue HUD.
- [ ] Render staff, wand, and monster bolts from authoritative bridge events.
- [ ] Add presentation events for summoning, teleportation, seizing, breath
  attacks, discord, entrancement, and other special abilities.
- [ ] Keep every effect cosmetic: no Doom damage, AI, collision, or gameplay
  RNG may affect Brogue.
- [ ] Audit creature and item removal so hidden, dead, consumed, or moved
  entities cannot leave stale actors.

## P2: Remaining Brogue screens

- [ ] Add the complete message archive screen.
- [ ] Add Brogue help and command reference screens.
- [ ] Add discoveries and item-knowledge screens.
- [ ] Add the feats screen.
- [ ] Add seed and run-information views.
- [ ] Add complete victory, mastery, and post-game run details.
- [ ] Add high-score or run-history presentation if it is retained from
  standalone Brogue.
- [ ] Keep GZDoom-specific video, audio, and input settings in the native
  GZDoom options menus.

## Verification required for 1:1 status

- [ ] Add deterministic tests for every semantic command.
- [x] Add staff and wand targeting tests for valid, blocked, reflected, and
  cancelled trajectories.
  See [staff](targeted-staff-use.md), [wand](targeted-wand-use.md), and the repeated
  five-seed suites in `tools.test_brogue_bridge`.
- [ ] Add regression scenarios for every terrain-promotion family.
- [ ] Add special-monster ability regression scenarios.
- [ ] Compare bridge-driven and standalone Brogue recordings turn by turn.
- [ ] Expand the normalized state hash to cover all gameplay-relevant status,
  item, terrain, and RNG/checkpoint state without pointer values.
- [ ] Run multi-depth simulations for several thousand accepted actions.
- [x] Test save/load continuation against an uninterrupted run.
  Native recording round trips check restored player state and subsequent
  WAIT/RNG continuation. Complete status/prompt coverage remains open above;
  raw pre-save versus reconstructed presentation-hash normalization is not
  claimed solved (see [restore evidence](terrain-animation-research.md)).
- [ ] Test event truncation followed by complete snapshot resynchronization.
- [ ] Extend side-by-side comparison beyond movement to items, devices,
  searching, terrain changes, statuses, and level transitions.
- [ ] Correct stale runtime-bridge documentation after each completed group.

## Completion criterion

The bridge can be called 1:1 when every normal Brogue player command can be
submitted semantically, Brogue alone resolves its result, every gameplay-
relevant state can be restored and verified, and GZDoom consistently presents
the resulting state without introducing independent gameplay decisions.

Bloodwort now has original models, snapshot ownership, growth/burst/spore
presentation and dedicated native/renderer/package checks. See
[bloodwort evidence and remaining acceptance](bloodwort-presentation.md).
This does not close unrelated dynamic-terrain backlog items.
