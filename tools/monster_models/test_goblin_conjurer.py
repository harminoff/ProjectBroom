"""Conjurer anatomy, conforming emissive markings and authority regressions."""
import math
import unittest
from . import goblin_conjurer_animation as g
from .rat import add, mul


class ConjurerTests(unittest.TestCase):
    def test_unarmed_family_anatomy(self):
        parts=g.build_parts();names={p.name for p in parts}
        self.assertEqual(len(g.BONES),18)
        self.assertFalse(any('spear' in n or 'blade' in n for n in names))
        self.assertTrue({'hand_L_palm','hand_R_palm','head_cranium','wrap_ragged'}<=names)
        self.assertEqual(len([n for n in names if n.startswith('hand_R_finger')]),4)

    def test_sigils_follow_actual_skin_not_an_approximate_bone(self):
        parts,*_=g.geometry();body=parts[0];normals=body.normals()
        lookup={add(v,mul(n,.035)):w for v,n,w in zip(body.vertices,normals,body.skin_weights)}
        sigils=[p for p in parts if p.name.startswith('sigil_')]
        self.assertEqual(len(sigils),6)
        for p in sigils:
            self.assertGreater(len(p.faces),4)
            for v,w,(u,t) in zip(p.vertices,p.skin_weights,p.uv):
                self.assertEqual(w,lookup[v])
                self.assertTrue(.25<u<.5 and 0<t<1-682/1024)
        # Equal influences bound deformation separation by the original offset
        # because the clip hierarchy only rotates/translates, never scales.
        for name,count,fps,loop in g.CLIPS:
            for phase in (0,.5,1):
                frame=g.pose(name,phase)
                self.assertEqual(len(frame),18)
                self.assertTrue(all(row[7:]==(1,1,1) for row in frame))

    def test_loops_bounds_and_texture(self):
        _,v,n,uv,t,w=g.geometry()
        for name,count,fps,loop in g.CLIPS:
            if loop:
                a=g.deform(v,w,g.pose(name,0));b=g.deform(v,w,g.pose(name,1))
                self.assertLess(max(math.dist(x,y) for x,y in zip(a,b)),1e-8)
            for phase in (0,.25,.5,.75,1):
                posed=g.deform(v,w,g.pose(name,phase))
                self.assertLess(max(p[1] for p in posed)-min(p[1] for p in posed),64)
        self.assertEqual(g.texture_bytes(),(g.ROOT/'mod/BrogueDoom'/g.SKIN).read_bytes())
        self.assertGreater(g.glyph_distance(0,0),.1)
        self.assertLess(g.glyph_distance(.5,.5),.001)

    def test_pulse_is_material_only(self):
        shader=(g.ROOT/'mod/BrogueDoom/shaders/conjurer-sigils.fp').read_text()
        self.assertIn('sin(timer * 2.4)',shader)
        self.assertIn('material.Bright',shader)
        for forbidden in ('random','brogue_bridge','Spawn','Damage','ConsoleCommand'):
            self.assertNotIn(forbidden,shader)


if __name__=='__main__':unittest.main()
