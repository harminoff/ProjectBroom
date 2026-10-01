import json
import subprocess
import unittest
from pathlib import Path
from tools.pickup_models.flavors import catalog
from tools.pickup_models.scroll_letters import PATTERNS
from PIL import Image, ImageStat

ROOT=Path(__file__).resolve().parents[1]

class ItemFlavors(unittest.TestCase):
    def test_complete_catalog_and_runtime_bindings(self):
        colors=catalog(ROOT)
        self.assertEqual([len(colors[c]) for c in ('Staff','Wand','Ring')],[21,12,18])
        definitions=(ROOT/'mod/BrogueDoom/models/pickups/FLAVORS.txt').read_text()
        for category,entries in colors.items():
            for name in entries:
                self.assertIn(f'Model BrogueFlavor{category}{name}\n',definitions)
                self.assertTrue((ROOT/f'mod/BrogueDoom/graphics/BRGFL_{category}_{name}.png').is_file())
                if category!='Ring': self.assertIn(f'Model BrogueFlavorView{category}{name}\n',definitions)

    def test_all_title_letters_and_blank_parchment(self):
        self.assertEqual(''.join(PATTERNS),'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        model=(ROOT/'mod/BrogueDoom/models/pickups/scroll_titled.obj').read_text()
        self.assertNotIn('Faded_ink_stroke',model)
        self.assertNotIn('Wax_seal',model)
        for letter in PATTERNS:
            self.assertTrue((ROOT/f'mod/BrogueDoom/models/pickups/letter_{letter}.obj').is_file())

    def test_held_skin_covers_entire_material_tile(self):
        for kind,entries in catalog(ROOT).items():
            if kind=='Ring': continue
            for flavor,color in entries.items():
                image=Image.open(ROOT/f'mod/BrogueDoom/graphics/VIEW_BRGFL_{kind}_{flavor}.png')
                x=(3 if kind=='Staff' else 2)*128
                for top in (0,128):
                    mean=ImageStat.Stat(image.crop((x,top,x+128,top+128))).mean
                    for actual,expected in zip(mean,color): self.assertLess(abs(actual-expected),20,(kind,flavor,top,mean,color))

    def test_export_across_seeds_and_naming_modes(self):
        for seed in (1,2,3,17,12345):
            command=[str(ROOT/'src/brogue-mapgen/bin/brogue-bridge.exe'),'--seed',str(seed),'--flavor-smoke']
            first=subprocess.run(command,capture_output=True,text=True)
            second=subprocess.run(command,capture_output=True,text=True)
            self.assertEqual(first.returncode,0,first.stdout+first.stderr)
            self.assertEqual(first.stdout,second.stdout)
            self.assertIn('materials=51 titles=3 namingModes=3 passed=true',first.stdout)
