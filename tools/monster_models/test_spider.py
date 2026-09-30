"""Centipede-specific anatomy, plantigrade support and cosmetic source checks."""
import math
import unittest
from collections import Counter
from . import spider_animation as c,spider_materials as m

class SpiderTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.parts,cls.v,_,cls.uv,cls.tri,cls.w=c.geometry()
  cls.clips,cls.bounds=c.animation_data(cls.v,cls.w)

 def test_signature_anatomy(self):
  names={p.name for p in self.parts}
  for prefix,count in [('leg_',8),('eye_',8),('fang_',2),('palp_',2),('spinneret_',2)]:
   self.assertEqual(sum(n.startswith(prefix) for n in names),count)
  self.assertIn('body_cuticle',names)
  self.assertLess(len(self.tri),20000)
  for weights in self.w:
   self.assertLessEqual(len(weights),4);self.assertAlmostEqual(sum(v for i,v in weights),1)
   self.assertTrue(all(v>0 for i,v in weights))

 def test_body_and_leg_surfaces_closed_connected(self):
  for p in self.parts:
   if p.name!='body_cuticle' and not p.name.startswith('leg_'):continue
   ids={};vi=[]
   for v in p.vertices:
    key=tuple(round(a,7) for a in v);vi.append(ids.setdefault(key,len(ids)))
   edges=Counter();adj={i:set() for i in ids.values()}
   for face in p.triangles():
    a,b,d=[vi[i] for i in face]
    for x,y in ((a,b),(b,d),(d,a)):
     edges[tuple(sorted((x,y)))]+=1;adj[x].add(y);adj[y].add(x)
   self.assertTrue(all(n==2 for n in edges.values()),p.name)
   seen=set();pending=[0]
   while pending:
    a=pending.pop()
    if a in seen:continue
    seen.add(a);pending.extend(adj[a]-seen)
   self.assertEqual(len(seen),len(ids),p.name)

 def test_distributed_support_and_metachronal_cycle(self):
  for sample in range(57):
   t=sample/56;frame=c.pose('scuttle',t);transforms=c.matrices(frame)
   grounded=[]
   for i in range(4):
    for side in ('L','R'):
     idx=c.IDS[f'leg_{i}_{side}_end'];actual=transforms[idx][0]
     expected=c.add(c.REST[idx],c.gait(i,side,t))
     self.assertLess(math.dist(actual,expected),1e-8)
     if actual[2]<.551:grounded.append((i,side))
   self.assertGreaterEqual(len(grounded),4)
   self.assertTrue(any(i<2 for i,s in grounded) and any(i>=2 for i,s in grounded))
  for name in ('idle','scuttle'):
   a=c.deform(self.v,self.w,c.pose(name,0));b=c.deform(self.v,self.w,c.pose(name,1))
   self.assertLess(max(math.dist(x,y) for x,y in zip(a,b)),1e-8)

 def test_clip_envelope_and_grounded_rolled_death(self):
  for b in self.bounds:
   self.assertGreaterEqual(b[2],.06999)
   self.assertGreater(b[0],-32);self.assertGreater(b[1],-32)
   self.assertLess(b[3],32);self.assertLess(b[4],32)
  for clip in self.clips:
   for i,f in enumerate(clip['frames']):
    source=c.pose(clip['name'],i/(len(clip['frames']) if clip['loop'] else len(clip['frames'])-1))
    self.assertEqual(f[0],source[0], 'Unexpected automatic floor compensation')
  final=c.pose('death',1)
  # Dorsal surface faces the ground, all tarsi curl above their hips.
  from .skeletal import rotate
  self.assertLess(rotate(final[0][3:7],(0,0,1))[2],-.98)
  transforms=c.matrices(final)
  for i in range(4):
   for side in ('L','R'):
    self.assertGreater(transforms[c.IDS[f'leg_{i}_{side}_end']][0][2],transforms[c.IDS[f'leg_{i}_{side}_upper']][0][2])
  verts=c.deform(self.v,self.w,final)
  self.assertAlmostEqual(min(v[2] for v in verts),.1)

 def test_material_uv_isolation_and_exported_bytes(self):
  for p in self.parts:
   x0,y0,x1,y1=m.RECTS[m.role(p.name)]
   for u,v in p.uv:
    self.assertTrue(x0-.01<=u*1024<=x1+.01)
    self.assertTrue(y0-.01<=(1-v)*1024<=y1+.01)
  self.assertEqual(m.texture_bytes(),(c.ROOT/'mod/BrogueDoom'/m.SKIN).read_bytes())
  for path,data in m.surface_maps().items():self.assertEqual(data,(c.ROOT/'mod/BrogueDoom'/path).read_bytes())
  definition=(c.ROOT/'mod/BrogueDoom/GLDEFS').read_text().split('material "graphics/BRGSPID.png"')[1].split('}')[0]
  self.assertNotIn('brightmap',definition);self.assertNotIn('shader',definition)

if __name__=='__main__':unittest.main()
