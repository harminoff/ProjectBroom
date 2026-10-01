"""Contracts for deterministic, presentation-only first-floor sunlight."""
import hashlib
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from tools.sunlight_assets import ROOT, generate


class SunlightAssetTests(unittest.TestCase):
    def test_generated_assets_are_complete_and_byte_identical(self) -> None:
        expected = (
            Path("mod/BrogueDoom/models/terrain/sun_ray.obj"),
            Path("mod/BrogueDoom/graphics/BRGSUNRY.png"),
            Path("mod/BrogueDoom/graphics/BRGSUNHO.png"),
        )
        before = {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in expected}
        with tempfile.TemporaryDirectory() as folder:
            generate(Path(folder))
            after = {path: hashlib.sha256((Path(folder) / path).read_bytes()).hexdigest() for path in expected}
        self.assertEqual(before, after)
        with Image.open(ROOT / expected[1]) as image:
            self.assertEqual(image.size, (64, 256))
            self.assertEqual(image.mode, "RGBA")
            self.assertGreater(max(pixel[3] for pixel in image.getdata()), 0)
        with Image.open(ROOT / expected[2]) as image:
            self.assertEqual(image.size, (128, 128))
            self.assertEqual(image.mode, "RGB")

    def test_runtime_contract_is_first_floor_and_noninteractive(self) -> None:
        frontend = (ROOT / "src/gzdoom-bridge/brogue_terrain_frontend.inc").read_text()
        zscript = (ROOT / "mod/BrogueDoom/brogue_terrain.zs").read_text()
        modeldef = (ROOT / "mod/BrogueDoom/MODELDEF").read_text()
        self.assertIn("State.depth == 1", frontend)
        self.assertIn("TT_SUNLIGHT_POOL", frontend)
        self.assertIn('sunlightOpening ? "BRGSUNHO"', frontend)
        self.assertIn("class BrogueTerrainSunRay : BrogueTerrainStone", zscript)
        self.assertIn("+NOINTERACTION", zscript)
        self.assertIn("Model BrogueTerrainSunRay", modeldef)
        self.assertIn("without using either Brogue's gameplay RNG", frontend)
        self.assertIn("for (int dy = -1; dy <= 1; ++dy)", frontend)
        self.assertNotIn("for (int dy = -2; dy <= 2; ++dy)", frontend)


if __name__ == "__main__":
    unittest.main()
