# Brogue 1:1 Bridge Parity TODO

This backlog tracks the remaining work required for GZDoom to present and
control a complete Brogue CE game while Brogue remains authoritative. It does
not include changes that would reproduce Brogue rules in GZDoom.

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

- [ ] Add targeted staff use through Brogue's existing device and bolt logic.
- [ ] Add targeted wand use through Brogue's existing device and bolt logic.
- [ ] Add a generalized target preview containing Brogue-valid targets,
  trajectory, range, obstruction, and confirmation requirements.
- [ ] Add single-turn search.
- [ ] Add repeated search until interrupted or complete.
- [ ] Add auto-rest.
- [ ] Add auto-explore.
- [ ] Add travel to a selected Brogue cell.
- [ ] Add run-until-disturbed movement.
- [ ] Add explicit ascend and descend intents using Brogue's stair behavior.
- [ ] Add rethrow-last-item.
- [ ] Add swap-last-equipment.
- [ ] Add item relabeling.
- [ ] Add calling/naming unidentified item kinds.
- [ ] Add authoritative easy-mode activation.
- [ ] Add authoritative new-game, abandon-game, and quit commands.

## P0: General prompt and interaction contract

- [ ] Replace special-case targeting flows with one bridge-owned interaction
  state machine.
- [ ] Support yes/no confirmations without mutating state before approval.
- [ ] Support stable-ID item selections for all Brogue selection prompts.
- [ ] Support location and creature targeting prompts.
- [ ] Support text entry for call and relabel commands.
- [ ] Support nested and sequential prompts while retaining the original
  command, expected revision, and approvals.
- [ ] Make cancel behavior match Brogue and consume no turn when Brogue does
  not consume one.
- [ ] Ensure one frontend confirmation executes exactly one Brogue command.

## P1: Expand the copied state contract

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

- [ ] Replace terrain-change logging with a coordinate-addressed frontend
  update path for every changed Brogue cell.
- [ ] Synchronize secret-door discovery and door promotion.
- [ ] Synchronize appearing, collapsing, and falling bridges.
- [ ] Synchronize flooding, retracting liquids, and changing liquid depth.
- [ ] Synchronize freezing and melting ice.
- [ ] Synchronize spreading and extinguished fire.
- [ ] Synchronize gas type and volume changes.
- [ ] Synchronize trap discovery and activation.
- [ ] Synchronize machine and vault terrain promotions.
- [ ] Synchronize collapsing floors, holes, and chasms.
- [ ] Update GZDoom collision and visual proxies only from the resulting
  Brogue cell state.
- [ ] Verify terrain updates cannot leave stale blockers, missing walls, or
  presentation actors in previously changed cells.

## P1: Save, load, and replay

- [ ] Expose Brogue's authoritative save operation through the bridge.
- [ ] Restore Brogue simulation state and RNG through an authoritative load.
- [ ] Rebuild or select the matching generated GZDoom depth after loading.
- [ ] Rebind frontend creature, item, terrain, and player proxies after load.
- [ ] Add saved-game selection to the player-facing executable and menu.
- [ ] Expose Brogue recordings/replays through the bridge.
- [ ] Add replay selection and playback controls.
- [ ] Validate replay state hashes at deterministic checkpoints.
- [ ] Add save/load round-trip tests across multiple depths and active status
  effects.

## P2: Visibility and 3D presentation fidelity

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
- [ ] Add staff and wand targeting tests for valid, blocked, reflected, and
  cancelled trajectories.
- [ ] Add regression scenarios for every terrain-promotion family.
- [ ] Add special-monster ability regression scenarios.
- [ ] Compare bridge-driven and standalone Brogue recordings turn by turn.
- [ ] Expand the normalized state hash to cover all gameplay-relevant status,
  item, terrain, and RNG/checkpoint state without pointer values.
- [ ] Run multi-depth simulations for several thousand accepted actions.
- [ ] Test save/load continuation against an uninterrupted run.
- [ ] Test event truncation followed by complete snapshot resynchronization.
- [ ] Extend side-by-side comparison beyond movement to items, devices,
  searching, terrain changes, statuses, and level transitions.
- [ ] Correct stale runtime-bridge documentation after each completed group.

## Completion criterion

The bridge can be called 1:1 when every normal Brogue player command can be
submitted semantically, Brogue alone resolves its result, every gameplay-
relevant state can be restored and verified, and GZDoom consistently presents
the resulting state without introducing independent gameplay decisions.
