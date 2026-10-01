"""Held forward input pacing; Brogue remains the step validator."""
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class HeldMovementTests(unittest.TestCase):
    def test_repeat_delay_release_and_no_catchup(self):
        with tempfile.TemporaryDirectory() as folder:
            exe = Path(folder) / 'held.exe'
            subprocess.run(['g++', '-std=c++17', '-static',
                            str(ROOT / 'tools/held_movement_test.cpp'), '-o', str(exe)],
                           check=True, capture_output=True)
            subprocess.run([str(exe)], check=True)

    def test_repeat_uses_existing_revision_checked_action(self):
        source = (ROOT / 'src/gzdoom-bridge/brogue_bridge_frontend.cpp').read_text()
        repeat = source.split('void TickForwardHold()')[1].split('bool BrogueBridge_HandleInput')[0]
        self.assertIn('MapFacingRelativeKeyToAction(0x11, action)', repeat)
        self.assertIn('PerformAction(action, "held-forward")', repeat)
        self.assertNotIn('while (', repeat)
        self.assertNotIn('BufferedAction =', repeat)
        action = source.split('bool PerformAction(')[1].split('bool PerformItemCommand')[0]
        self.assertIn('command.expectedRevision = State.revision;', action)

    def test_full_map_keeps_movement_on_authoritative_input_path(self):
        source = (ROOT / 'src/gzdoom-bridge/brogue_bridge_frontend.cpp').read_text()
        allowed = source.split('bool ForwardInputAllowed()')[1].split('void TickForwardHold()')[0]
        self.assertNotIn('!FullMapOpen', allowed)
        handler = source.split('bool BrogueBridge_HandleInput(')[1].split('void BrogueBridge_PrepareTiccmd')[0]
        modal = handler.split('if (FullMapOpen) {', 1)[1].split('\n\t}', 1)[0]
        self.assertIn('if (!MapKeyToAction(event->data1, mapAction)) return true;', modal)
        self.assertIn('FullMapOpen = false;', modal)
        self.assertIn('PerformAction(action, "input")', handler)
