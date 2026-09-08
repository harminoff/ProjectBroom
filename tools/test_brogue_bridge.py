"""Deterministic black-box tests for the Brogue CE bridge executable."""

from __future__ import annotations

import hashlib
import re
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BRIDGE_DIR = ROOT / "src" / "brogue-mapgen"
BRIDGE_EXE = BRIDGE_DIR / "bin" / "brogue-bridge.exe"

INITIAL_RE = re.compile(
    r"^INITIAL revision=(?P<revision>\d+) turn=(?P<turn>\d+) "
    r"depth=(?P<depth>\d+) player=(?P<x>-?\d+),(?P<y>-?\d+) "
    r"hp=(?P<hp>-?\d+)/(?P<max_hp>-?\d+) creatures=(?P<creatures>\d+) "
    r"items=(?P<items>\d+) hash=(?P<hash>[0-9a-f]+) "
    r"presentation=(?P<presentation>[0-9a-f]+)$"
)
ACTION_RE = re.compile(
    r"^ACTION index=(?P<index>\d+) revision=(?P<revision>\d+) "
    r"type=(?P<type>\S+) accepted=(?P<accepted>true|false) "
    r"consumedTurn=(?P<consumed>true|false) turn=(?P<turn>\d+) "
    r"player=(?P<x>-?\d+),(?P<y>-?\d+) hash=(?P<hash>[0-9a-f]+)$"
)
STATE_RE = re.compile(
    r"^STATE revision=(?P<revision>\d+) turn=(?P<turn>\d+) "
    r"player=(?P<x>-?\d+),(?P<y>-?\d+) hp=(?P<hp>-?\d+)/(?P<max_hp>-?\d+) "
    r"creatures=(?P<creatures>\d+) hash=(?P<hash>[0-9a-f]+)$"
)


def run_bridge(*, seed: int, actions: str | None = None, long_run: int | None = None,
               weapon_smoke: bool = False, consumable_smoke: bool = False,
               warning_smoke: bool = False, look_smoke: bool = False,
               verbose: bool = False, staff_smoke: bool = False, wand_smoke: bool = False) -> str:
    if not BRIDGE_EXE.is_file():
        raise AssertionError(
            f"missing {BRIDGE_EXE}; run scripts/build-bridge.ps1 before these tests"
        )
    args = [str(BRIDGE_EXE), "--seed", str(seed)]
    if actions is not None:
        args += ["--actions", actions]
    if long_run is not None:
        args += ["--long-run", str(long_run)]
    if weapon_smoke:
        args += ["--weapon-smoke"]
    if consumable_smoke:
        args += ["--consumable-smoke"]
    if staff_smoke:
        args += ["--staff-smoke"]
    if wand_smoke:
        args += ["--wand-smoke"]
    if warning_smoke:
        args += ["--warning-smoke"]
    if look_smoke:
        args += ["--look-smoke"]
    if verbose:
        args += ["--verbose"]
    completed = subprocess.run(
        args,
        cwd=BRIDGE_DIR,
        check=True,
        capture_output=True,
        text=True,
        timeout=20,
    )
    return completed.stdout


def lines_matching(output: str, pattern: re.Pattern[str]) -> list[re.Match[str]]:
    matches = [pattern.match(line) for line in output.splitlines()]
    return [match for match in matches if match is not None]


class BrogueBridgeTests(unittest.TestCase):
    def test_general_target_preview_is_read_only(self) -> None:
        for seed in (1, 2, 42, 12345, 99999):
            with self.subTest(seed=seed):
                args = [str(BRIDGE_EXE), "--seed", str(seed), "--target-smoke"]
                first = subprocess.check_output(args, cwd=BRIDGE_DIR, text=True, timeout=60)
                self.assertEqual(first, subprocess.check_output(args, cwd=BRIDGE_DIR, text=True, timeout=60))
                self.assertEqual(first.count("TARGET case="), 21)
                self.assertEqual(first.count("TARGET_ACTION "), 8)

    def test_wands_match_standalone_apply_and_targeting(self) -> None:
        for seed in (1, 2, 42, 12345, 99999):
            with self.subTest(seed=seed):
                first = run_bridge(seed=seed, wand_smoke=True)
                self.assertEqual(first, run_bridge(seed=seed, wand_smoke=True))
                self.assertEqual(first.count("parity=true"), 14)
                self.assertIn("WAND case=known-empty parity=true consumedTurn=false charges=0", first)
                self.assertIn("WAND case=unknown-empty parity=true consumedTurn=true charges=0", first)

    def test_targeted_staff_use_preserves_brogue_rules(self) -> None:
        for seed in (1, 2, 42, 12345, 99999):
            with self.subTest(seed=seed):
                first = run_bridge(seed=seed, staff_smoke=True)
                self.assertEqual(first, run_bridge(seed=seed, staff_smoke=True))
                for case in ("fire", "blocked", "reflected", "unknown-empty", "blink-warning"):
                    self.assertIn(f"STAFF case={case} accepted=true consumedTurn=true", first)
                self.assertIn("STAFF case=known-empty accepted=false consumedTurn=false charges=0", first)

    def test_monster_catalog_is_exported_from_brogue(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "catalog.json"
            subprocess.run(
                [str(BRIDGE_EXE), "--dump-monster-catalog", str(output)],
                cwd=BRIDGE_DIR, check=True, capture_output=True, text=True,
            )
            catalog = __import__("json").loads(output.read_text(encoding="utf-8"))
        self.assertEqual(catalog["bridgeApiVersion"], 20)
        self.assertEqual(catalog["count"], 68)
        self.assertEqual(catalog["kinds"][0]["symbol"], "MK_YOU")
        self.assertEqual(catalog["kinds"][1]["symbol"], "MK_RAT")
        self.assertEqual(catalog["kinds"][-1]["symbol"], "MK_ANCIENT_SPIRIT")

    def test_initial_state_comes_from_normal_brogue_start(self) -> None:
        output = run_bridge(seed=1)
        matches = lines_matching(output, INITIAL_RE)
        self.assertEqual(len(matches), 1)
        initial = matches[0].groupdict()
        self.assertEqual(initial["depth"], "1")
        self.assertEqual(initial["turn"], "0")
        self.assertEqual(initial["creatures"], "8")
        # Brogue's floorItems and packItems list heads are sentinels; only
        # their linked gameplay entries belong in the public item state.
        self.assertEqual(initial["items"], "18")

    def test_look_inspection_is_authoritative_and_non_turn_consuming(self) -> None:
        output = run_bridge(seed=1, look_smoke=True)
        self.assertRegex(
            output,
            r"LOOK revision=1 turn=0 cell=38,26 kind=2 known=true title=You .* hash=[0-9a-f]+",
        )

    def test_action_sequence_is_deterministic(self) -> None:
        actions = "WAIT,N,E,SE,WAIT,W"
        first = run_bridge(seed=1, actions=actions)
        second = run_bridge(seed=1, actions=actions)
        self.assertEqual(first, second)
        self.assertEqual(
            hashlib.sha256(first.encode("utf-8")).hexdigest(),
            # ABI v20 adds copied terrain appearance to the presentation hash.
            # Gameplay/RNG parity is checked independently by terrain-smoke.
            "27cca20f6d65346e2915a26b4480ac7152311674c46d02bf610da5eb2f694fc2",
        )
        action_matches = lines_matching(first, ACTION_RE)
        self.assertEqual(len(action_matches), 6)
        self.assertEqual([match["turn"] for match in action_matches], ["1", "2", "3", "4", "5", "6"])
        self.assertTrue(all(match["hash"] for match in action_matches))

    def test_search_matches_standalone(self) -> None:
        for seed in (1, 2, 42, 12345, 99999):
            with self.subTest(seed=seed):
                command = [str(BRIDGE_EXE), '--seed', str(seed), '--search-smoke']
                first = subprocess.run(command, cwd=BRIDGE_DIR, capture_output=True, text=True, check=True).stdout
                second = subprocess.run(command, cwd=BRIDGE_DIR, capture_output=True, text=True, check=True).stdout
                self.assertEqual(first, second)
                self.assertEqual(first.count('parity=true'), 21)
                self.assertIn('contract=truncation-memory-reset cancelTurn=false cancelRng=false', first)

    def test_multiple_game_seeds_keep_the_same_contract(self) -> None:
        actions = "WAIT,N,E,SE,WAIT,W"
        for seed in (1, 2, 3, 4, 5):
            with self.subTest(seed=seed):
                first = run_bridge(seed=seed, actions=actions)
                second = run_bridge(seed=seed, actions=actions)
                self.assertEqual(first, second)
                self.assertEqual(len(lines_matching(first, INITIAL_RE)), 1)
                self.assertEqual(len(lines_matching(first, ACTION_RE)), 6)
                self.assertTrue(all(match["hash"] for match in lines_matching(first, ACTION_RE)))

    def test_blocked_movement_is_reported_without_a_turn(self) -> None:
        output = run_bridge(seed=1, actions="S,S,S")
        actions = lines_matching(output, ACTION_RE)
        self.assertEqual(len(actions), 3)
        self.assertTrue(all(match["accepted"] == "false" for match in actions))
        self.assertTrue(all(match["consumed"] == "false" for match in actions))
        self.assertEqual({match["turn"] for match in actions}, {"0"})
        self.assertEqual({(match["x"], match["y"]) for match in actions}, {("38", "26")})

    def test_all_semantic_movement_actions_are_accepted_by_the_contract(self) -> None:
        output = run_bridge(seed=1, actions="N,NE,E,SE,S,SW,W,NW,WAIT")
        actions = lines_matching(output, ACTION_RE)
        self.assertEqual([match["type"] for match in actions], [
            "MOVE_N", "MOVE_NE", "MOVE_E", "MOVE_SE", "MOVE_S",
            "MOVE_SW", "MOVE_W", "MOVE_NW", "WAIT",
        ])
        self.assertEqual([match["index"] for match in actions], [str(index) for index in range(9)])

    def test_entering_a_closed_door_promotes_it_to_open_door(self) -> None:
        route = "N,N,N," + ",".join(["W"] * 20) + ",S"
        output = run_bridge(seed=1, actions=route, verbose=True)
        self.assertIn("ACTION index=23", output)
        self.assertRegex(
            output,
            r"type=CELL_TERRAIN_CHANGED x=18 y=24 .*beforeDungeon=7 afterDungeon=8 ",
        )

    def test_seed_one_down_ladder_is_an_accepted_brogue_transition(self) -> None:
        # Cardinal-only deterministic route from Brogue's seed-1 start to its
        # authoritative down-stair cell. playerMoves() commits the transition
        # without ordinary tile displacement or turn consumption.
        route = (
            "N,N,N,N,E,E,E,E,E,E,E,N,N,N,E,E,E,E,E,E,E,N,N,N,N,N,E,"
            "N,N,N,N,N,N,N,N,E,E,E,E,E,E,E,E,N,E,N,E,E,N,E,E,N"
        )
        actions = lines_matching(run_bridge(seed=1, actions=route), ACTION_RE)
        self.assertEqual(len(actions), 52)
        self.assertEqual(actions[-1]["accepted"], "true")
        self.assertEqual(actions[-1]["consumed"], "false")

    def test_long_run_uses_authoritative_turn_processing_until_game_end(self) -> None:
        output = run_bridge(seed=1, long_run=300)
        final = lines_matching(output, re.compile(
            r"^FINAL revision=(?P<revision>\d+) turn=(?P<turn>\d+) "
            r"depth=(?P<depth>\d+) player=(?P<x>-?\d+),(?P<y>-?\d+) "
            r"hp=(?P<hp>-?\d+)/(?P<max_hp>-?\d+) creatures=(?P<creatures>\d+) "
            r"items=(?P<items>\d+) hash=(?P<hash>[0-9a-f]+) "
            r"presentation=(?P<presentation>[0-9a-f]+)$"
        ))
        self.assertEqual(len(final), 1)
        self.assertGreaterEqual(int(final[0]["turn"]), 190)
        self.assertEqual(final[0]["hp"], "0")
        self.assertIn(
            'RESULT outcome=1 score=0 depth=1 deepest=1 turn=195 cause="rat" '
            'summary="Killed by a rat on depth 1."',
            output,
        )

    def test_weapon_commands_and_throw_path_are_deterministic(self) -> None:
        first = run_bridge(seed=1, weapon_smoke=True)
        second = run_bridge(seed=1, weapon_smoke=True)
        self.assertEqual(first, second)
        self.assertIn("WEAPON phase=initial equipped=2 kind=0 name=dagger", first)
        self.assertIn("WEAPON phase=unequip revision=2 accepted=true consumedTurn=true equipped=0", first)
        self.assertIn("WEAPON phase=equip revision=3 accepted=true consumedTurn=true equipped=2", first)
        self.assertRegex(first, r"WEAPON phase=preview item=\d+ target=38,23 range=16 path=3 confirm=false")
        self.assertIn("WEAPON phase=throw revision=4 accepted=true consumedTurn=true dartQuantity=14", first)

    def test_consumable_confirmation_and_apply_are_authoritative(self) -> None:
        first = run_bridge(seed=1, consumable_smoke=True)
        second = run_bridge(seed=1, consumable_smoke=True)
        self.assertEqual(first, second)
        self.assertRegex(
            first,
            r"CONSUMABLE phase=confirm revision=1 result=CONFIRMATION_REQUIRED prompt=You're not hungry enough to fully enjoy the food\. Eat it anyway\?",
        )
        self.assertRegex(
            first,
            r"CONSUMABLE phase=apply revision=2 accepted=true consumedTurn=true quantity=0 hash=[0-9a-f]+",
        )
        self.assertRegex(
            first,
            r"CONSUMABLE phase=selection revision=3 result=SELECTION_REQUIRED type=1 choices=1 prompt=Identify what\?",
        )
        self.assertRegex(
            first,
            r"CONSUMABLE phase=identify revision=4 accepted=true consumedTurn=true target=\d+ identifiable=false hash=[0-9a-f]+",
        )

    def test_brogue_movement_warning_pauses_and_resumes_without_drift(self) -> None:
        first = run_bridge(seed=1, warning_smoke=True)
        second = run_bridge(seed=1, warning_smoke=True)
        self.assertEqual(first, second)
        self.assertRegex(
            first,
            r"WARNING phase=prompt revision=1 result=CONFIRMATION_REQUIRED prompt=Dive into the depths\? player=38,26 hash=[0-9a-f]+",
        )
        self.assertRegex(
            first,
            r"WARNING phase=confirmed revision=2 accepted=true consumedTurn=false depth=2 player=37,24 hash=[0-9a-f]+ transition=fall source=38,25 landing=37,24",
        )


if __name__ == "__main__":
    unittest.main()
