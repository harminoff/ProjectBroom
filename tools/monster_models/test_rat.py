"""Asset integrity and regeneration protection for the authored rat."""
import contextlib
import io
import json
import math
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch

from tools.monster_models import generate, rat


class RatAssetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parts = rat.build_parts()
        cls.model = rat.obj_bytes(cls.parts)

    def test_geometry_indices_normals_floor_and_budget(self):
        count = 0
        for part in self.parts:
            self.assertEqual(len(part.vertices),len(part.uv),part.name)
            for vertex in part.vertices:
                self.assertTrue(all(math.isfinite(x) for x in vertex),part.name)
            for u,v in part.uv:
                self.assertTrue(0 < u < 1 and 0 < v < 1,part.name)
            for normal in part.normals():
                self.assertAlmostEqual(sum(x*x for x in normal),1,places=6)
            for a,b,c in part.triangles():
                self.assertTrue(all(0 <= i < len(part.vertices) for i in (a,b,c)),part.name)
                area=rat.cross(rat.sub(part.vertices[b],part.vertices[a]),rat.sub(part.vertices[c],part.vertices[a]))
                self.assertGreater(sum(x*x for x in area),1e-14,(part.name,a,b,c))
                count+=1
        self.assertLessEqual(count,15000)
        vertices=[v for p in self.parts for v in p.vertices]
        self.assertGreaterEqual(min(v[2] for v in vertices),0)
        self.assertLess(min(v[2] for v in vertices),.1)
        self.assertLess(max(v[0] for v in vertices)-min(v[0] for v in vertices),64)
        self.assertLess(max(v[1] for v in vertices)-min(v[1] for v in vertices),24)
        self.assertLess(max(v[2] for v in vertices),20)

    def test_export_is_deterministic_and_matches_shipped_asset(self):
        self.assertEqual(self.model,rat.obj_bytes(rat.build_parts()))
        self.assertEqual(self.model,(rat.ROOT/'mod/BrogueDoom/models/monsters/01_rat.obj').read_bytes())
        self.assertNotIn(b'\nmtllib ',self.model)
        self.assertNotIn(b'\nusemtl ',self.model)
        for line in self.model.decode('ascii').splitlines():
            if line.startswith('f '):
                self.assertEqual(len(line.split()),4)
                for corner in line.split()[1:]:
                    self.assertEqual(len(corner.split('/')),3)
        # +Z in Blender becomes positive OBJ Y, so the model stands upright.
        first=self.parts[0].vertices[0]
        exported=next(line for line in self.model.decode('ascii').splitlines() if line.startswith('v '))
        for actual,expected in zip(map(float,exported.split()[1:]),(first[0],first[2],-first[1])):
            self.assertAlmostEqual(actual,expected,places=5)

    def test_texture_is_deterministic_rgb_and_shipped(self):
        first=rat.texture_bytes()
        self.assertEqual(first,rat.texture_bytes())
        self.assertEqual(first,(rat.ROOT/'mod/BrogueDoom/graphics/BRGRAT.png').read_bytes())
        self.assertEqual(struct.unpack('>IIBB',first[16:26]),(1024,1024,8,2))

    def test_regeneration_retains_custom_model_and_skin_binding(self):
        source=json.loads(rat.ROOT.joinpath('assets/monsters/brogue_monster_catalog.json').read_text())
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            catalog=root/'catalog.json'
            catalog.write_text(json.dumps(source))
            models=root/'models'
            graphics=root/'graphics'
            models.mkdir()
            graphics.mkdir()
            original=b'authored geometry must remain byte-identical'
            (models/'01_rat.obj').write_bytes(original)
            (models/'01_rat.iqm').write_bytes(original)
            (graphics/'BRGRAT.png').write_bytes(b'skin')
            # The roster now has other authored assets too. Seed their fixture
            # bytes and prove roster regeneration preserves every one.
            for kind in source['kinds']:
                custom=generate.CUSTOM_MODELS.get(kind['symbol'])
                if custom and kind['kind']!=1:
                    name=custom.get('runtimeFilename',f"{kind['kind']:02d}_{generate.slug(kind['symbol'])}.obj")
                    (models/name).write_bytes(original)
                    (graphics/Path(custom['skin']).name).write_bytes(b'skin')
            with patch.multiple(generate,ROOT=root,CATALOG=catalog,REGISTRY=root/'registry.json',
                                MODEL_DIR=models,GRAPHICS=graphics,ZSCRIPT=root/'monsters.zs'):
                with patch.object(generate.subprocess,'run'),contextlib.redirect_stdout(io.StringIO()):
                    generate.main()
            self.assertEqual((models/'01_rat.obj').read_bytes(),original)
            for kind in source['kinds']:
                if kind['symbol'] in generate.CUSTOM_MODELS:
                    name=generate.CUSTOM_MODELS[kind['symbol']].get('runtimeFilename',f"{kind['kind']:02d}_{generate.slug(kind['symbol'])}.obj")
                    self.assertEqual((models/name).read_bytes(),original)
            text=(models/'MODELDEF.txt').read_text()
            binding=text.split('Model BrogueMonsterK01\n',1)[1].split('}',1)[0]
            self.assertIn('Skin 0 "graphics/BRGRAT.png"',binding)
            registry=json.loads((root/'registry.json').read_text())
            entry=next(m for m in registry['monsters'] if m['kind']==1)
            self.assertEqual(entry['skin'],'graphics/BRGRAT.png')
            self.assertEqual(entry['authoringSource'],'assets/monsters/rat/rat-animated.blend')

    def test_bound_rat_uses_original_proxy_contract(self):
        registry=json.loads(rat.ROOT.joinpath('assets/monsters/brogue_monster_registry.json').read_text())
        entry=next(m for m in registry['monsters'] if m['kind']==1)
        self.assertEqual(entry['symbol'],'MK_RAT')
        self.assertEqual(entry['class'],'BrogueMonsterK01')
        self.assertEqual(entry['model'],'01_rat.iqm')
        self.assertEqual(entry['behaviorFlags'],'0')
        self.assertEqual(entry['abilityFlags'],'0')
        self.assertTrue(rat.ROOT.joinpath(entry['authoringSource']).is_file())
        modeldef=rat.ROOT.joinpath('mod/BrogueDoom/models/monsters/MODELDEF.txt').read_text()
        self.assertIn('Skin 0 "graphics/BRGRAT.png"',modeldef)


if __name__=='__main__':
    unittest.main()
