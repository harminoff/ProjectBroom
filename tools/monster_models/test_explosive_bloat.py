"""Explosive-bloat family continuity, pressure collapse and original skin proof."""
import collections
import io
import math
import unittest
from PIL import Image
from . import explosive_bloat_animation as explosive, bloat_animation as bloat, iqm


class ExplosiveBloatTests(unittest.TestCase):
    def test_shared_closed_membrane_and_animated_seams(self):
        self.assertEqual(explosive.geometry(), bloat.geometry())
        self.assertEqual(explosive.BONES, bloat.BONES)
        parts,v,n,uv,t,w=explosive.geometry()
        self.assertEqual(len(parts),1)
        keys=[tuple(round(c,6) for c in p) for p in v]
        edges=collections.Counter()
        for a,b,c in t:
            for i,j in ((a,b),(b,c),(c,a)):
                edges[tuple(sorted((keys[i],keys[j])))] += 1
        self.assertEqual(set(edges.values()),{2})
        for name,_,_,_ in explosive.CLIPS:
            points=explosive.deform(v,w,explosive.pose(name,.5));seen={}
            for key,p in zip(keys,points):
                if key in seen:self.assertLess(math.dist(p,seen[key]),1e-8)
                seen[key]=p

    def test_every_frame_centered_clearance_and_deflation(self):
        _,v,_,_,_,w=explosive.geometry()
        clips,bounds=explosive.animation_data(v,w)
        for clip in clips:
            for frame in clip['frames']:
                points=explosive.deform(v,w,frame)
                for a in (0,1):
                    self.assertGreater(min(p[a] for p in points),-32)
                    self.assertLess(max(p[a] for p in points),32)
                self.assertGreater(min(p[2] for p in points),.06999)
        final=explosive.deform(v,w,clips[-1]['frames'][-1])
        self.assertLess(max(p[2] for p in final),13)
        self.assertLess(max(p[2] for p in final)-min(p[2] for p in final),11)
        self.assertNotEqual(explosive.pose('collapse',1),bloat.pose('collapse',1))

    def test_hover_loops_and_roles(self):
        _,v,_,_,_,w=explosive.geometry()
        self.assertEqual(len(explosive.CLIPS),6)
        self.assertEqual([c[3] for c in explosive.CLIPS],[True,True,False,False,False,False])
        for name in ('idle','drift'):
            start=explosive.deform(v,w,explosive.pose(name,0))
            end=explosive.deform(v,w,explosive.pose(name,1))
            self.assertLess(max(math.dist(a,b) for a,b in zip(start,end)),1e-8)
            for t in (0,.25,.5,.75,1):
                self.assertGreater(min(p[2] for p in explosive.deform(v,w,explosive.pose(name,t))),13)

    def test_orange_continuous_diffuse(self):
        image=Image.open(io.BytesIO(explosive.texture_bytes()))
        self.assertEqual(image.mode,'RGB');self.assertEqual(image.size,(512,512))
        self.assertTrue(all(r>g+45 and g>b+35 for r,g,b in image.getdata()))
        self.assertEqual(list(image.crop((0,0,1,512)).getdata()),list(image.crop((511,0,512,512)).getdata()))
        self.assertNotEqual(explosive.texture_bytes(),bloat.texture_bytes())

    def test_deterministic_geometry_runtime_and_all_material_bytes(self):
        first=explosive.geometry();self.assertEqual(first,explosive.geometry())
        _,v,n,uv,t,w=first;clips,bounds=explosive.animation_data(v,w)
        data=iqm.encode(v,n,uv,t,w,explosive.BONES,clips,bounds,
            mesh_label='Project_Broom_explosive_bloat',material_path=explosive.SKIN)
        self.assertEqual(data,(explosive.ROOT/'mod/BrogueDoom/models/monsters/30_explosive_bloat.iqm').read_bytes())
        self.assertEqual(explosive.texture_bytes(),(explosive.ROOT/'mod/BrogueDoom'/explosive.SKIN).read_bytes())


if __name__=='__main__':unittest.main()
