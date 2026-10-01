"""Wraith connected anatomy, attached claws, planted supports and exact exports."""
import collections
import math
import unittest
from . import wraith_animation as g, wraith_materials as m, iqm
class WraithTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.parts,cls.v,cls.n,cls.uv,cls.tri,cls.w=g.geometry();cls.clips,cls.bounds=g.animation_data(cls.v,cls.w)
 def test_connected_closed_skin_and_seams(self):
  p=self.parts[0];ids=p.skin_topology;edges=collections.Counter();graph={i:set() for i in ids};reps={}
  for face in p.faces:
   for a,b in zip(face,face[1:]+face[:1]):
    a,b=ids[a],ids[b];self.assertNotEqual(a,b);edges[tuple(sorted((a,b)))]+=1;graph[a].add(b);graph[b].add(a)
  self.assertEqual(set(edges.values()),{2});seen={ids[0]};todo=[ids[0]]
  while todo:
   for i in graph[todo.pop()]:
    if i not in seen:seen.add(i);todo.append(i)
  self.assertEqual(seen,set(ids))
  for i,key in enumerate(ids):
   if key in reps:
    j=reps[key];self.assertEqual(self.v[i],self.v[j]);self.assertEqual(self.w[i],self.w[j]);self.assertLess(math.dist(self.n[i],self.n[j]),1e-8)
   reps[key]=i
  used={g.BONES[b][0] for row in self.w for b,weight in row if weight>.01}
  for limb in ('arm','leg'):
   for side in ('L','R'):
    for joint in ('upper','lower','end'):self.assertIn(f'{limb}_{side}_{joint}',used)
  for row in self.w:self.assertAlmostEqual(sum(weight for b,weight in row),1);self.assertLessEqual(len(row),4)
 def test_six_roles_centered_clearance_and_no_floor_compensation(self):
  self.assertEqual([c['loop'] for c in self.clips],[True,True,False,False,False,False])
  for b in self.bounds:
   self.assertGreaterEqual(b[0],-32);self.assertGreaterEqual(b[1],-32);self.assertLessEqual(b[3],32);self.assertLessEqual(b[4],32);self.assertGreater(b[2],.07)
  for c in self.clips:
   for i,f in enumerate(c['frames']):
    raw=g.pose(c['name'],i/(len(c['frames']) if c['loop'] else len(c['frames'])-1))
    self.assertEqual(f,raw,'Automatic floor compensation masks an anatomy/IK defect')
    self.assertTrue(all(row[7:]==(1,1,1) for row in f))
   if c['loop']:
    self.assertLess(max(math.dist(a,b) for a,b in zip(g.deform(self.v,self.w,g.pose(c['name'],0)),g.deform(self.v,self.w,g.pose(c['name'],1)))),1e-8)
  settled=g.deform(self.v,self.w,g.pose('fall',1));self.assertLess(max(p[2] for p in settled),35)
 def test_grounded_support_and_signature_anatomy(self):
  for name,count,fps,loop in g.CLIPS:
   for i in range(count):
    transforms=g.matrices(g.pose(name,i/(count if loop else count-1)))
    if name in ('advance','fall'):
     supports=sum(abs(transforms[g.IDS[f'leg_{side}_end']][0][2]-2.4)<1e-7 for side in ('L','R'))
     self.assertGreaterEqual(supports,1)
     if name=='fall':self.assertEqual(supports,2)
  parts={p.name:p for p in g.build_parts()}
  self.assertEqual(len([n for n in parts if n.startswith('nail_')]),10)
  self.assertEqual(len([n for n in parts if n.startswith('detail_socket_')]),2)
  self.assertFalse(any('iris' in n or 'hood' in n or 'sword' in n for n in parts))
  for n,p in parts.items():
   if n.startswith('nail_'):
    self.assertGreater(max(v[0] for v in p.vertices)-min(v[0] for v in p.vertices),2)
    self.assertTrue(all(g.weights(p,v,u)==[(g.IDS[f"arm_{n.split('_')[1]}_end"],1)] for v,u in zip(p.vertices,p.uv)))
 def test_continuous_skin_atlas_and_accessory_isolation(self):
  self.assertTrue(set(m.role(p.name) for p in g.build_parts()) <= set(m.ROLES))
  for p in self.parts:
   for u,v in p.uv:
    self.assertTrue(0<=u<=1 and 0<=v<=1)
    self.assertLess(u,.5) if p.name=='Connected_skin' else self.assertGreater(u,.5)
  # One unique padded triangle island replaces the discontinuous source-part
  # atlas. Geometry/normals/weights still agree at every shared skin vertex.
  p=self.parts[0];self.assertEqual(len(p.vertices),len(p.faces)*3)
  self.assertEqual(len({tuple(p.uv[i] for i in f) for f in p.faces}),len(p.faces))
 def test_runtime_and_material_bytes(self):
  data=iqm.encode(self.v,self.n,self.uv,self.tri,self.w,g.BONES,self.clips,self.bounds,mesh_label='Project_Broom_wraith',material_path=g.SKIN)
  self.assertEqual(data,(g.ROOT/'mod/BrogueDoom/models/monsters/24_wraith.iqm').read_bytes())
  self.assertEqual(g.texture_bytes(),(g.ROOT/'mod/BrogueDoom'/g.SKIN).read_bytes())
if __name__=='__main__':unittest.main()
