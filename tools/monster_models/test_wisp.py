"""Blue flame skinning, complete extinction and presentation boundary checks."""
import collections
import hashlib
import json
import math
import unittest
from . import wisp_animation as wisp, iqm

class WispTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parts,cls.v,cls.n,cls.uv,cls.t,cls.w=wisp.geometry()
        cls.clips,cls.bounds=wisp.animation_data(cls.v,cls.w)

    def test_continuous_closed_flame_volumes(self):
        self.assertEqual(len(self.parts),9)
        for part in self.parts:
            edges=collections.Counter();keys=[tuple(round(c,6) for c in p) for p in part.vertices]
            for a,b,c in part.triangles():
                for i,j in ((a,b),(b,c),(c,a)):edges[tuple(sorted((keys[i],keys[j])))]+=1
            self.assertEqual(set(edges.values()),{2})

    def test_weights_and_rest_reconstruction(self):
        for p,weights in zip(self.v,self.w):
            self.assertTrue(1<=len(weights)<=4)
            self.assertAlmostEqual(sum(a for _,a in weights),1)
            self.assertTrue(all(0<=a<=1 for _,a in weights))
            reconstruction=tuple(sum(wisp.REST[b][a]*w for b,w in weights) for a in range(3))
            self.assertLess(math.dist(p,reconstruction),1e-9)

    def test_loops_hover_and_centered_clearance(self):
        for name in ('idle','drift'):
            start=wisp.deform(self.v,self.w,wisp.pose(name,0));end=wisp.deform(self.v,self.w,wisp.pose(name,1))
            self.assertLess(max(math.dist(a,b) for a,b in zip(start,end)),1e-8)
        for clip in self.clips:
            for frame in clip['frames']:
                self.assertTrue(all(tuple(b[7:])==(1,1,1) for b in frame))
        for b in self.bounds:
            self.assertGreater(b[0],-32);self.assertGreater(b[1],-32)
            self.assertLess(b[3],32);self.assertLess(b[4],32)
            self.assertGreater(b[2],14)
        death=self.bounds[-1]
        self.assertLess(max(death[i+3]-death[i] for i in range(3)),.004)

    def test_exact_runtime_and_texture_bytes(self):
        actual=iqm.encode(self.v,self.n,self.uv,self.t,self.w,wisp.BONES,self.clips,self.bounds,
          mesh_label='Project_Broom_will_o_the_wisp',material_path=wisp.SKIN)
        self.assertEqual(actual,(wisp.ROOT/'mod/BrogueDoom/models/monsters/23_will_o_the_wisp.iqm').read_bytes())
        self.assertEqual(wisp.texture_bytes(),(wisp.ROOT/'mod/BrogueDoom'/wisp.SKIN).read_bytes())

    def test_scoped_emission_defaults_and_inert_proxy(self):
        profiles=json.loads((wisp.ROOT/'assets/monsters/skeletal_profiles.json').read_text())['enemies']
        self.assertEqual([p['symbol'] for p in profiles if p.get('emissive')],['MK_WILL_O_THE_WISP'])
        self.assertEqual([p['symbol'] for p in profiles if p.get('additiveFlame')],['MK_WILL_O_THE_WISP'])
        text=(wisp.ROOT/'mod/BrogueDoom/brogue_monsters.zs').read_text()
        proxy=text.split('class BrogueMonsterK23 :')[1].split('class ')[0]
        self.assertIn('BrogueMonsterProxyBase',proxy);self.assertIn('RenderStyle "Add"',proxy)
        for forbidden in ('A_Explode','A_CustomMissile','A_Chase','A_Damage','+SOLID'):self.assertNotIn(forbidden,proxy)
        shader=(wisp.ROOT/'mod/BrogueDoom/shaders/wisp-flame.fp').read_text()
        self.assertIn('material.Bright',shader)
        self.assertNotIn('pointlight',(wisp.ROOT/'mod/BrogueDoom/GLDEFS').read_text().split('// Ethereal blue flame:')[1])

    def test_native_fixture_guard_precedes_any_spawn(self):
        source=(wisp.ROOT/'src/gzdoom-bridge/brogue_monster_visibility_fixture.inc').read_text()
        guard=source.split('int failures = 0;')[0]
        self.assertIn('if (Started || !primaryLevel || primaryLevel->MapName.CompareNoCase("ART01") != 0 || brg_monster_omniscience)',guard)
        self.assertIn('return;',guard);self.assertNotIn('Spawn(',guard)
        for forbidden in ('Api.', 'performCommand', 'PerformAction', 'State.'):
            self.assertNotIn(forbidden,source)
        self.assertIn('probe.actor->Destroy()',source)

if __name__=='__main__':unittest.main()
