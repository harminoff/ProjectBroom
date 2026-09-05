# Project Broom bridge-driven GUI

## Implemented core

The source-built GZDoom frontend now projects its game-facing interface from
the live Brogue CE simulation. `BrogueBridgeState` API v15 is the only source
for player statistics, status flags, messages, visible entities, map knowledge,
inventory order, equipment, item descriptions, and legal item actions.

The permanent HUD uses a Brogue-inspired frame:

- a left rail for depth, health, nutrition, strength, armor, gold, stealth,
  turn count, active statuses, and Brogue-visible creatures/items;
- Brogue's three current message lines along the top;
- a bottom terrain/cell context line and concise control reminders;
- a 79x29 upper-right minimap drawn only from Brogue's discovered or currently
  visible cells;
- a modal two-pane inventory with Brogue's equipped-first ordering and original
  `a`-`z` inventory letters.

Ultimate Classic Minimap remains vendored for development, but the canonical
source-bridge launcher hides it and disables its full-map reveal. The GUI
minimap does not inspect Doom automap discovery or line of sight.

## Input and authority

`I` opens and closes inventory. Arrow keys, mouse wheel, or a Brogue inventory
letter change the selected row. `Enter` or `U` uses a consumable, `E`
equips/removes, `D` drops, and `T` starts the existing throw-target mode.
Potentially wasteful or known-hazardous consumption presents Brogue's
confirmation text. Identify and enchant scrolls present a mandatory picker
containing only the items Brogue considers valid for that scroll.

Movement and combat confirmations are captured directly at Brogue's normal
`confirm()` boundary. Chasms, fire, dangerous gas, pressure plates, captives,
allies, and weapon-degradation warnings therefore use Brogue's exact text and
conditions. A negative response keeps the original bridge revision and does
not consume a turn; a positive response retries the same semantic command at
that revision with one additional approved prompt.

Opening, closing, and navigating the inventory are presentation operations and
consume no Brogue turn. Item commands carry the bridge revision and stable item
ID into Brogue CE. Brogue decides whether equipment can be changed, whether an
item can be dropped, whether a throw is legal, and whether time advances. The
frontend refreshes from the resulting authoritative snapshot.

## Bridge data contract

API v13 adds copied values only; no Brogue pointers cross the DLL boundary:

- player armor, strength, nutrition, gold, stealth, and all four equipment IDs;
- per-cell `discovered`, `currentlyVisible`, and `magicMapped` flags;
- item inventory letter/order, equipment slot, action mask, and bounded plain
  text detail;
- `BROGUE_COMMAND_DROP_ITEM`, plus armor/ring support for existing equip/remove
  commands.
- `BROGUE_COMMAND_APPLY_ITEM`, a confirmation response, and stable secondary
  item IDs for identify/enchant scroll choices.
- Brogue's terminal outcome, exact game-over sentence, cause, score, depth,
  deepest depth, and turn for the loss screen.

The loss screen appears only after `player.gameHasEnded` is returned by Brogue.
It blocks further gameplay input, clears queued actions, and presents Brogue's
own summary and score. Space, Enter, Esc, or primary click opens the main menu.

The fixed-size CLI reserves an 8 MB Windows stack because the full snapshot and
turn result are intentionally value objects. Make dependencies now include both
bridge headers so an ABI edit cannot leave stale CLI/DLL objects.

## Deferred GUI work

Food, potions, scrolls, and charms now use Brogue's existing `apply`, `eat`,
`drinkPotion`, `readScroll`, and `useCharm` paths. Selecting a staff or wand and pressing
Enter/U opens its targeting cursor; Tab cycles Brogue's eligible targets,
Enter/click uses the selected device, and Esc/right-click cancels without a command.
Brogue's existing device/bolt path resolves charges, effects, and blinking
warnings. Wands retain Brogue's depletion and discharge-count behavior. See
[staff verification](targeted-staff-use.md) and [wand verification](targeted-wand-use.md).
Discovery/help, death/victory, save, and replay screens are also deferred.
Standard GZDoom video/audio/input settings may remain engine-native.

## Verification

Run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build-source-bridge.ps1
.\scripts\launch-source-bridge.cmd -Seed 1
```

The Python bridge/resource suite verifies API versioning, deterministic action
hashes, non-mutating consumable and chasm confirmations followed by their
authoritative confirmed actions, visibility-safe GUI wiring, disabled full-map
reveal, and the existing monster/weapon presentation contracts. Mapcompiler
tests remain a separate gate because GUI changes must not alter generated
topology.
