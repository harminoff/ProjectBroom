"""Compare shared native commands against immutable pre-extraction evidence."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from tools.capture_native_interactions import EXE, sha

FIXTURES = Path(__file__).with_name("fixtures") / "native_interactions_v18.json"


class NativeInteractionTests(unittest.TestCase):
    def test_frozen_terminal_oracle(self):
        baseline = json.loads(FIXTURES.read_text(encoding="utf-8"))
        for case in baseline["cases"]:
            with self.subTest(seed=case["seed"], scenario=case["scenario"]):
                with tempfile.TemporaryDirectory(prefix="broom-native-") as directory:
                    result = subprocess.run([str(EXE), "--seed", str(case["seed"]),
                                             "--native-interaction-fixture", case["scenario"]],
                                            cwd=directory, capture_output=True, timeout=30)
                    self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
                    self.assertEqual(sha(result.stdout), case["terminal"], "Native terminal/state/RNG transcript changed")
                    recording = Path(directory, "native-command.broguesave").read_bytes()
                    self.assertEqual(sha(recording), case["recording"], "Native recording changed")

    def test_native_frames_retain_execution_and_reject_invalid_responses(self):
        for seed in (1, 2, 42, 12345, 99999):
            with self.subTest(seed=seed), tempfile.TemporaryDirectory(prefix="broom-frame-") as directory:
                result = subprocess.run([str(EXE), "--seed", str(seed), "--native-interaction-fixture", "frame-check"],
                                        cwd=directory, capture_output=True, timeout=30)
                self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
                self.assertIn(b"pending=retained invalid=unchanged duplicate=no-effect", result.stdout)


if __name__ == "__main__":
    unittest.main()
