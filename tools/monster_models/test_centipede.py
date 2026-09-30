"""Centipede-specific anatomy, plantigrade support and cosmetic source checks."""
import math
import unittest
from collections import Counter
from . import centipede_animation as c,centipede_materials as m

class CentipedeTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.parts,cls.v,_,cls.uv,cls.tri,cls.w=c.geometry()
  cls.clips,cls.bounds=c.animation_data(cls.v,cls.w)

 def test_signature_anatomy(self):
  names={p.name for p in self.parts}
  self.assertEqual(sum(n.startswith('plate_') for n in names),15)
  self.assertEqual(sum(n.startswith('leg_') for n in names),30)
  self.assertEqual(sum(n.startswith('antenna_') for n in names),2)
  self.assertEqual(sum(n.startswith('forcipule_') for n in names),2)
  self.assertEqual(sum(n.startswith('head_ocellus_') for n in names),8)
  self.assertEqual(sum(n.startswith('spiracle_') for n in names),30)
  self.assertLess(len(self.tri),34000)
  self.assertLess(len(c.BONES),128)

 def test_body_and_leg_surfaces_closed_connected(self):
  for p in self.parts:
   if p.name!='flexible_body' and not p.name.startswith('leg_'):continue
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
   for i in range(15):
    for side in ('L','R'):
     idx=c.IDS[f'leg_{i}_{side}_end'];actual=transforms[idx][0]
     expected=c.add(c.REST[idx],c.gait(i,side,t))
     self.assertLess(math.dist(actual,expected),1e-8)
     if actual[2]<.381:grounded.append((i,side))
   self.assertGreaterEqual(len(grounded),18)
   self.assertTrue(any(i<4 for i,s in grounded) and any(i>10 for i,s in grounded))
  for name in ('idle','scuttle'):
   a=c.deform(self.v,self.w,c.pose(name,0));b=c.deform(self.v,self.w,c.pose(name,1))
   self.assertLess(max(math.dist(x,y) for x,y in zip(a,b)),1e-8)

 def test_clip_envelope_and_death_settle(self):
  for b in self.bounds:
   self.assertGreaterEqual(b[2],.06999)
   self.assertLess(b[3]-b[0],64);self.assertLess(b[4]-b[1],64)
  self.assertLess(self.bounds[-1][5],self.bounds[0][5]-2)
  for clip in self.clips:
   # Foot clearance correction must be sub-unit: never hide a broken pose
   # by lifting the entire creature over the floor.
   self.assertLess(max(f[0][2] for f in clip['frames']),.55)

 def test_material_uv_isolation_and_exported_bytes(self):
  for p in self.parts:
   x0,y0,x1,y1=m.RECTS[m.role(p.name)]
   for u,v in p.uv:
    self.assertTrue(x0-.01<=u*1024<=x1+.01)
    self.assertTrue(y0-.01<=(1-v)*1024<=y1+.01)
  self.assertEqual(m.texture_bytes(),(c.ROOT/'mod/BrogueDoom'/m.SKIN).read_bytes())
  for path,data in m.surface_maps().items():self.assertEqual(data,(c.ROOT/'mod/BrogueDoom'/path).read_bytes())
  definition=(c.ROOT/'mod/BrogueDoom/GLDEFS').read_text().split('material "graphics/BRGCENT.png"')[1].split('}')[0]
  self.assertNotIn('brightmap',definition);self.assertNotIn('shader',definition)

if __name__=='__main__':unittest.main()
