# Brogue / UZDoom side-by-side comparison mode

## Purpose

Comparison mode launches two independent simulations from the same game seed:

- graphical Brogue CE built from pinned commit
  `7f52dd93b7fa553dd6e354ccd44229a3c22d8a76`;
- source-built UZDoom using the in-process bridge built from that same Brogue
  snapshot.

Brogue appears on the left and UZDoom on the right. The mode is deliberately a
test harness: neither process copies coordinates into the other. Each receives
the same semantic movement or wait intent and resolves it through its own copy
of Brogue CE. A visible difference therefore identifies simulation, snapshot,
map-projection, or presentation drift instead of being hidden by forced state
synchronization.

## Launch

From Windows PowerShell in the project root:

```powershell
.\scripts\launch-comparison.cmd -Seed 1
```

The `.cmd` wrapper works with Windows PowerShell when `pwsh` is unavailable.
The Brogue HUD defaults to its crisp native bitmap size in both normal and
comparison launches. For a larger presentation, use `-HudScale 2`; accepted
values are whole-pixel multiples from 1 through 3. Fractional input is rounded
to prevent texture filtering from blurring the glyphs.

## Synchronized controls

Use Num Lock and press one key at a time:

| Key | Brogue action |
| --- | --- |
| Numpad 8 | north |
| Numpad 9 | northeast |
| Numpad 6 | east |
| Numpad 3 | southeast |
| Numpad 2 | south |
| Numpad 1 | southwest |
| Numpad 4 | west |
| Numpad 7 | northwest |
| Numpad 5 | wait |

UZDoom samples these physical key edges globally. When UZDoom owns focus it
forwards the same keypad event to Brogue; when Brogue owns focus, Brogue receives
the physical event directly. UZDoom suppresses its ordinary keypad input path
while comparison mode is active, preventing duplicate bridge turns.

One key-down edge produces at most one action in each process. Holding a key is
not intended for parity testing.

## What this verifies

- identical initial terrain and stair coordinates for a game seed;
- legal, blocked, and diagonal movement decisions;
- turn timing and wait behavior;
- door and dynamic-terrain changes;
- monster responses and messages;
- UZDoom's Brogue-cell to world-position projection.

Inventory/menu commands, mouse actions, camera-relative WASD, ascent, and
descent are not mirrored in this first mode. They remain available in their
normal frontends but should not be used during a synchronized action trace.

## Implementation boundary

`brg_compare_pid` is a development-only UZDoom CVAR. The native frontend polls
the nine comparison keys once per tic and submits the corresponding
`BrogueBridgeAction`. It does not alter Brogue state directly. The launcher
passes the graphical Brogue process ID and arranges both native windows.

The comparison executable is hash-gated by the launcher. A missing or modified
binary fails visibly rather than silently falling back to a different Brogue
version.
