"""Shoreline topology/privacy contracts and deterministic material resources."""
import hashlib
from pathlib import Path
import subprocess
import tempfile
import unittest
from PIL import Image
from tools.shoreline_assets import generate, MASKS, FAMILIES, ROOT

class ShorelineTests(unittest.TestCase):
    def test_mask_distances_and_knowledge_height_contract(self):
        with tempfile.TemporaryDirectory() as folder:
            exe=Path(folder)/'shoreline.exe'
            build=subprocess.run(['g++','-std=c++17','-static',str(ROOT/'tools/shoreline_test.cpp'),'-o',str(exe)],capture_output=True,text=True)
            self.assertEqual(build.returncode,0,build.stdout+build.stderr)
            subprocess.run([str(exe)],check=True)

    def test_generated_data_is_complete_and_byte_identical(self):
        directory=ROOT/'mod/BrogueDoom/shaders/shoreline'
        before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in directory.iterdir()}
        with tempfile.TemporaryDirectory() as folder:
            generate(Path(folder))
            generated=Path(folder)/'mod/BrogueDoom/shaders/shoreline'
            self.assertEqual(before,{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in generated.iterdir()})
        self.assertEqual(len(MASKS),47)
        for mask in MASKS:
            with Image.open(directory/f'mask-{mask:02x}.png') as image:
                self.assertEqual(image.size,(8,1))
                self.assertEqual([pixel[0]>127 for pixel in image.getdata()], [bool(mask&(1<<i)) for i in range(8)])
        definitions=(directory/'gldefs.txt').read_text()
        textures=(directory/'textures.txt').read_text()
        for family in FAMILIES:
            for mask in MASKS:
                name=f'BS{family}{mask:02X}'
                self.assertIn(f'material flat {name}\n',definitions)
                self.assertIn(f'Flat "{name}"',textures)
        self.assertEqual(definitions.count('define SHORE_WATER'),47*len(FAMILIES))

if __name__=='__main__': unittest.main()
