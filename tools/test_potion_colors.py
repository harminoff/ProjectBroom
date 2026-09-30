import io
import re
import unittest
import subprocess
from pathlib import Path
from PIL import Image
from tools.pickup_models import detailed

ROOT=Path(__file__).resolve().parents[1]

class PotionColors(unittest.TestCase):
    def test_export_names_identification_and_call_across_seeds(self):
        for seed in (1,2,3,17,12345):
            result=subprocess.run([str(ROOT/'src/brogue-mapgen/bin/brogue-bridge.exe'),'--seed',str(seed),'--potion-smoke'],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertIn('colors=21 namingModes=3 passed=true',result.stdout)

    def test_every_brogue_color_has_a_skin(self):
        source=(ROOT/'src/brogue-mapgen/src/brogue/Globals.c').read_text()
        block=source.split('const char itemColorsRef')[1].split('};')[0]
        names=re.findall(r'"([a-z]+)"',block)
        self.assertEqual(list(detailed.POTION_COLORS),names)

    def test_color_changes_only_glass(self):
        original=Image.open(io.BytesIO(detailed.atlas_bytes()))
        tile=detailed.MATERIALS.index('glass')
        x,y=tile%4*256,tile//4*256
        colors=[]
        for name in detailed.POTION_COLORS:
            generated=detailed.atlas_bytes(potion_color=name)
            self.assertEqual(generated,(ROOT/f'mod/BrogueDoom/graphics/BRGPOTION_{name}.png').read_bytes())
            image=Image.open(io.BytesIO(generated))
            colors.append(image.getpixel((x+128,y+128)))
            image.paste(original.crop((x,y,x+256,y+256)),(x,y))
            self.assertEqual(image.tobytes(),original.tobytes())
        self.assertEqual(len(set(colors)),21)
