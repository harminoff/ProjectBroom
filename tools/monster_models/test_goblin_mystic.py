"""Source-led mystic signature, unarmed deformation and material boundaries."""
import math
import unittest
from . import goblin_mystic_animation as g


class MysticTests(unittest.TestCase):
    def test_unarmed_primate_and_fur(self):
        parts=g.build_parts();names={p.name for p in parts}
        self.assertEqual(len(g.BONES),18)
        self.assertFalse(any(any(w in n for w in ('spear','blade','staff','sigil')) for n in names))
        self.assertTrue({'head_cranium','wrap_ragged','hand_L_palm','hand_R_palm'}<=names)
        for side in ('L','R'):
            self.assertEqual(len([n for n in names if n.startswith('hand_'+side+'_finger')]),4)
        self.assertEqual(len([n for n in names if n.startswith('head_hair')]),5)
        self.assertEqual(len([n for n in names if n.startswith('coat_shoulder')]),4)

    def test_only_irises_use_gold_tile(self):
        for p in g.build_parts():
            uses_gold=any(.5<u<.75 and 1-682/1024<v<1-341/1024 for u,v in p.uv)
            self.assertEqual(uses_gold,p.name.startswith('head_eye_iris'),p.name)
        shader=(g.ROOT/'mod/BrogueDoom/shaders/mystic-eyes.fp').read_text()
        self.assertIn('material.Bright',shader)
        for forbidden in ('timer','random','Spawn','Damage','brogue_bridge'):
            self.assertNotIn(forbidden,shader)

    def test_six_roles_loops_clearance_and_open_palms(self):
        _,v,n,uv,t,w=g.geometry()
        self.assertEqual([c[3] for c in g.CLIPS],[True,True,False,False,False,False])
        for name,count,fps,loop in g.CLIPS:
            if loop:
                a=g.deform(v,w,g.pose(name,0));b=g.deform(v,w,g.pose(name,1))
                self.assertLess(max(math.dist(x,y) for x,y in zip(a,b)),1e-8)
            for phase in (0,.25,.5,.75,1):
                frame=g.pose(name,phase);posed=g.deform(v,w,frame)
                self.assertTrue(all(row[7:]==(1,1,1) for row in frame))
                self.assertTrue(all(math.isfinite(c) for p in posed for c in p))
                self.assertLess(max(p[1] for p in posed)-min(p[1] for p in posed),64)
        self.assertNotEqual(g.pose('palm',.5),g.pose('sweep',.5))
        self.assertNotEqual(g.pose('idle',0)[g.IDS['arm_L_end']][3:7],(0,0,0,1))

    def test_reproducible_material(self):
        self.assertEqual(g.texture_bytes(),(g.ROOT/'mod/BrogueDoom'/g.SKIN).read_bytes())


if __name__=='__main__':unittest.main()
