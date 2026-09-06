"""Deterministic assets and the OBJ coordinate convention used by UZDoom."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from . import generate


class SearchAssetTests(unittest.TestCase):
    def test_repeatability_and_floor_orientation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root/'mod/BrogueDoom/models/search'
            (root/'mod/BrogueDoom/graphics').mkdir(parents=True)
            with patch.object(generate, 'ROOT', root), patch.object(generate, 'OUT', output):
                generate.generate()
                first = {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}
                generate.generate()
                second = {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}
            self.assertEqual(first, second)
            self.assertEqual(len(list(output.glob('*.obj'))), 9)
            vertices = [tuple(map(float, line.split()[1:])) for line in (output/'plate.obj').read_text().splitlines() if line.startswith('v ')]
            self.assertLess(max(v[1] for v in vertices), 3)  # Y-up in the loader.
            self.assertEqual(max(v[0] for v in vertices)-min(v[0] for v in vertices), 26)
            self.assertEqual(max(v[2] for v in vertices)-min(v[2] for v in vertices), 26)


if __name__ == '__main__':
    unittest.main()
