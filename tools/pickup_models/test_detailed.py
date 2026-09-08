"""Coverage, deterministic export, valid mesh and identity boundary checks."""
import hashlib
import json
import math
import unittest
from . import generate as catalog, detailed


class PickupModelTests(unittest.TestCase):
    def test_thrown_weapon_tips_use_positive_x_forward(self):
        # Native projectile yaw assumes +X after the pickup's authoring rotation.
        # Check the actual dart/javelin geometry, including every compass heading.
        weapon = next(c for c in catalog.CATEGORIES if c.symbol == 'WEAPON')
        for kind, tip_name, tail_name in ((12, 'Dart point', 'Flight vane'),
                                           (13, 'Dart point', 'Flight vane'),
                                           (14, 'Leaf spear point', 'Continuous ash pole')):
            parts = detailed.build_parts(weapon, kind)
            tip = max(v[0] for p in parts if p.name == tip_name for v in p.vertices)
            tail = min(v[0] for p in parts if p.name == tail_name for v in p.vertices)
            self.assertGreater(tip, tail)
            for dx, dy in ((1,0), (1,1), (0,1), (-1,1), (-1,0), (-1,-1), (0,-1), (1,-1)):
                yaw = math.atan2(dy, dx)
                self.assertGreater((tip-tail)*(math.cos(yaw)*dx + math.sin(yaw)*dy), 0)

    def test_all_105_assets_are_deterministic_grounded_and_valid(self):
        registry=json.loads(catalog.REGISTRY_PATH.read_text())
        self.assertEqual(len(registry['models']),105)
        for category in catalog.CATEGORIES:
            for kind in ([None] if category.hidden_identity else [])+list(range(len(category.names))):
                with self.subTest(category=category.symbol,kind=kind):
                    model=detailed.Model(category,kind)
                    text=detailed.obj_text(model.parts)
                    self.assertEqual(text,(catalog.MODEL_DIR/catalog.model_name(category,kind)).read_text())
                    self.assertEqual(model.metadata()['sha256'],hashlib.sha256(
                        (catalog.MODEL_DIR/catalog.model_name(category,kind)).read_bytes()).hexdigest())
                    vertices=[v for p in model.parts for v in p.vertices]
                    self.assertAlmostEqual(min(v[2] for v in vertices),.12,places=6)
                    self.assertTrue(all(math.isfinite(x) for v in vertices for x in v))
                    self.assertLessEqual(max(v[0] for v in vertices)-min(v[0] for v in vertices),56.001)
                    self.assertLessEqual(max(v[1] for v in vertices)-min(v[1] for v in vertices),56.001)
                    self.assertLess(max(v[2] for v in vertices),24)
                    self.assertLess(sum(len(p.faces) for p in model.parts),16000)
                    for p in model.parts:
                        self.assertEqual(len(p.vertices),len(p.uv))
                        self.assertTrue(all(0<=u<=1 and 0<=v<=1 for u,v in p.uv))
                        for f in p.faces:
                            self.assertEqual(len(set(f)),3)
                            self.assertTrue(all(0<=i<len(p.vertices) for i in f))
                        for n in p.normals(): self.assertAlmostEqual(sum(v*v for v in n),1,places=5)

    def test_atlas_and_bindings(self):
        data=detailed.atlas_bytes()
        self.assertEqual(data,(catalog.ROOT/'mod/BrogueDoom/graphics/BRGPICKS.png').read_bytes())
        self.assertIn('BRGPICKS.png',catalog.MODELDEF_PATH.read_text())
        self.assertIn('BRGITEMS.png',(catalog.ROOT/'mod/BrogueDoom/models/weapons/MODELDEF.txt').read_text())

    def test_identity_and_noninteraction_contract(self):
        registry=json.loads(catalog.REGISTRY_PATH.read_text())
        self.assertEqual({m['category'] for m in registry['models'] if m['kind'] is None},{8,16,32,64,128})
        source=(catalog.ROOT/'src/gzdoom-bridge/brogue_bridge_frontend.cpp').read_text()
        self.assertIn('item.kindKnown',source)
        zs=catalog.ZSCRIPT_PATH.read_text()
        for flag in ('+NOINTERACTION','+NOBLOCKMAP','+NOGRAVITY'): self.assertIn(flag,zs)
        for forbidden in ('A_Chase','A_Explode','A_GiveInventory','Inventory.PickupMessage'):
            self.assertNotIn(forbidden,zs)

    def test_registry_labels_match_pinned_brogue(self):
        from .index import source_facts
        facts=source_facts()
        self.assertEqual(len(facts),97)
        for category in catalog.CATEGORIES:
            for kind,name in enumerate(category.names):
                if (category.symbol,kind) in facts:
                    self.assertEqual(name,facts[category.symbol,kind]['name'])


if __name__=='__main__': unittest.main()
