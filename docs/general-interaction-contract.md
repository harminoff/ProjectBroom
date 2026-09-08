# General interaction migration

Contribution category: Brogue parity and bridge work. Brogue CE owns every
choice, mutation, recording event and turn. This migration is in progress;
none of the eight interaction acceptance entries is complete.

## Independent baseline

`tools/capture_native_interactions.py` runs finite input tapes through native
`executeKeystroke()` without starting a bridge session. The console callback
captures the actual terminal at input boundaries and fails on unexpected or
unused input. It does not automatically answer acknowledgments or confirmations.

The pre-refactor evidence is under
`artifacts/interactions/native-baseline-full/`. Its manifest contains source
hashes, the dirty status, executable hash and repeated transcript/recording
hashes. `native-source.zip` and `native-oracle.exe` preserve that exact core.
The baseline covers the five requested seeds. Synthetic inventory/terrain/monster
setup is harness-only; recordings from those cases require the same fixture
setup and must not be advertised as naturally replayable saves. Starting-pack
inscription and relabel cases need no synthetic setup.

Snapshots record player status, inventory knowledge/text, terrain, basic creature
state, messages and native recording bytes before/after the command and after
a subsequent native WAIT, followed by an RNG continuation sample. This is a
bounded comparison surface, not a claim of exhaustive simulation serialization.

## Expected native behavior before extraction

`executeKeystroke(CALL_KEY)` calls `call(NULL)`, which selects an item and may
ask whether to inscribe one item. No and Escape at that confirmation both
continue into naming the kind. Escape during text entry cancels that command.
Empty accepted text clears the inscription or kind name. Text entry admits
ASCII space through tilde. The actual accepted length accounts for Brogue's
closing quote; it is not simply the size of the 30-byte local array.

`executeKeystroke(RELABEL_KEY)` calls `relabel(NULL)`. Uppercase letters become
lowercase; occupied letters swap; unchanged letters report the native message
without recording a change. Neither command consumes a turn. Relabel preserves
the existing item allocations, so the bridge identity mapping can remain stable.

An identify/enchant scroll records and identifies itself before acknowledgment
and its required selection. Escape at a mandatory choice does not abort the
scroll. A third ring asks which equipped ring to replace and can be cancelled.
Sequential acid/discord warnings must retain the first answer and execution
position. A confirmed chasm entry pauses for the native plunge acknowledgment.

The extraction must preserve these results and match the frozen oracle's
messages, recording bytes, turns and subsequent WAIT/RNG. Pending frames must
retain native execution state; no stage may be replayed to reconstruct it.

## Delivery order and gates

1. Capture standalone fixtures and native input recordings.
2. Extract shared native begin/step/finish continuations.
3. Migrate all ABI v19 consumers and validate tokens and copied descriptors.
4. Connect one presenter, existing targeting controls and engine text input.
5. Integrate command-boundary persistence and stream-complete reconstruction.
6. Complete deterministic, build, renderer, physical-input and package gates.

`ItemCommandFrame.h/.c` currently provides native begin/step continuations for
Call/Inscribe, Relabel, Equip, Remove and Drop. `Items.c` uses the same frames
through its terminal driver. Frames retain the selected item, ring replacement,
recording prefix and execution position. A pending optional prompt cannot
execute its guarded action, and a completed frame rejects another response.
These are internal native types; they are not a public ABI or a completed
general interaction system. Informational-message overflow is still native
synchronous execution and has not been generalized into resumable acknowledgments.

All 255 frozen terminal/state/RNG transcripts and command recordings match after
this extraction. Direct frame tests cover pending text, invalid response type,
invalid/overlong/unterminated text, duplicate completion, turnless mutation,
pointer-preserving relabel swaps, Escape-to-kind-name and ring replacement
cancellation. `tools.test_native_interactions` is included in `scripts/test.ps1`.

Movement/attack warning continuations, Apply and its mandatory selections,
targeting and acknowledgments still need conversion. The existing confirmation
broker and identify/enchant preselection remain in place for those unmigrated
commands. ABI remains v18. Call/Inscribe and Relabel are not yet available in
UZDoom inventory actions. ABI migration, frontend/text input, command-boundary
persistence, and the requested full acceptance matrix remain unfinished.
Existing save/load and UI acceptance entries remain unchanged.

## Verification evidence

- `powershell -ExecutionPolicy Bypass -File scripts/build-bridge.ps1`: DLL and
  harness compiled; see `artifacts/interactions/native-frame-build.log`.
- `powershell -ExecutionPolicy Bypass -File scripts/build-search-standalone.ps1`:
  standalone SDL build passed; see `artifacts/interactions/standalone-build.log`.
- `powershell -ExecutionPolicy Bypass -File scripts/build-source-bridge.ps1`:
  UZDoom compiled and its 125-test gate passed. The final launcher restore failed
  under restricted network access. Retrying only
  `scripts/build-launcher.ps1 -SelfContained` with network access succeeded.
  See `source-build.log` and `launcher-build.log` in the evidence directory.
- `python tools/capture_native_interactions.py artifacts/interactions/native-baseline-full --verify`:
  all 255 native transcript/recording comparisons passed.
- `powershell -ExecutionPolicy Bypass -File scripts/test.ps1`: passed all 125
  tests and its seed-1 long run; see `artifacts/interactions/canonical-tests.log`.
  After clearing confirmation-only cancellation metadata at the next text
  prompt, standalone and bridge were rebuilt and the native frame/oracle tests
  passed again. Final logs are `standalone-build-final.log`,
  `bridge-build-final.log` and `native-frame-tests-final.log`.
- `brogue-bridge.exe --seed SEED --long-run 300 --verbose`: repeated for
  1, 2, 42, 12345 and 99999. Each pair is byte-identical; the normal pattern
  reaches Brogue death before 300 actions in all five cases. Final turns are
  195, 43, 72, 145 and 109 respectively. Full hashes and logs are in
  `artifacts/interactions/long-runs/manifest.json`. This is not a 300-turn
  survival test.

`scripts/test-staff-ui.ps1` now accepts `-EvidenceDirectory` and contains its
native recordings below that directory. Reproduce the existing throw regression
with `-Throw -Renderer Vulkan -HudScale 1 -EvidenceDirectory PATH`; substitute
OpenGL and scales 2–3 for the other entries. Evidence belongs under
`artifacts/interactions/runtime-canonical/`. The first attempt using the prior
default save directory could not start recording under the filesystem sandbox;
the contained-recording runs successfully attached Brogue.
The existing throw smoke passed under Vulkan and OpenGL at HUD scales 1, 2
and 3, preserving state on cancellation and advancing exactly one revision on
the confirmed throw. Sample captures at Vulkan scale 1 and OpenGL scale 3 were
visually inspected. The dark, gold-edged confirmation panel remained readable.

These are automated checks of the existing target and confirmation UI. They do
not establish physical keyboard/mouse behavior, all new prompt families,
menu/focus behavior for a unified presenter, or an extracted-package save
continuation. Those gates remain open, as does the native save reconstruction
fix for commands recorded after the final turn.
