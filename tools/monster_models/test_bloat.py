"""Bloat membrane continuity, hover clearance and collapse/export checks."""
import collections
import math
import unittest
from . import bloat_animation as bloat,iqm


class BloatTests(unittest.TestCase):
    def test_closed_skin_and_identical_animated_seams(self):
        parts,v,n,uv,t,w=bloat.geometry()
        self.assertEqual(len(parts),1)
        keys=[tuple(round(c,6) for c in p) for p in v]
        edges=collections.Counter()
        for a,b,c in t:
            for i,j in ((a,b),(b,c),(c,a)):edges[tuple(sorted((keys[i],keys[j])))] += 1
        self.assertEqual(set(edges.values()),{2})
        for name in ('idle','drift','collapse'):
            points=bloat.deform(v,w,bloat.pose(name,.5))
            seen={}
            for key,p in zip(keys,points):
                if key in seen:self.assertLess(math.dist(p,seen[key]),1e-8)
                seen[key]=p

    def test_hover_loop_and_collapse(self):
        _,v,_,_,_,w=bloat.geometry()
        clips,bounds=bloat.animation_data(v,w)
        for c in clips[:2]:
            for f in c['frames']:
                posed=bloat.deform(v,w,f)
                self.assertGreater(min(p[2] for p in posed),13)
                self.assertLess(max(p[2] for p in posed),51)
            start=bloat.deform(v,w,bloat.pose(c['name'],0))
            end=bloat.deform(v,w,bloat.pose(c['name'],1))
            self.assertLess(max(math.dist(a,b) for a,b in zip(start,end)),1e-8)
        self.assertLess(bounds[-1][5],19)
        self.assertLess(bounds[-1][5]-bounds[-1][2],12)

    def test_deterministic_model_and_skin(self):
        _,v,n,uv,t,w=bloat.geometry();clips,bounds=bloat.animation_data(v,w)
        actual=iqm.encode(v,n,uv,t,w,bloat.BONES,clips,bounds,mesh_label='Project_Broom_bloat',material_path=bloat.SKIN)
        self.assertEqual(actual,(bloat.ROOT/'mod/BrogueDoom/models/monsters/06_bloat.iqm').read_bytes())
        self.assertEqual(bloat.texture_bytes(),(bloat.ROOT/'mod/BrogueDoom'/bloat.SKIN).read_bytes())


if __name__=='__main__':unittest.main()
