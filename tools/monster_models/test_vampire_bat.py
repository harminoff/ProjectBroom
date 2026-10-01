"""Bat-specific connected anatomy, flight and source/runtime checks."""
import unittest,math,json,hashlib
from collections import Counter
from . import vampire_bat_animation as bat
class VampireBatTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.parts,cls.v,_,_,cls.tri,cls.w=bat.geometry();cls.clips,cls.bounds=bat.animation_data(cls.v,cls.w)
 def test_signature(self):
  names={p.name for p in bat.build_parts()}
  for side in ('L','R'):
   self.assertEqual(sum(n.startswith('digit_'+side) for n in names),4)
   self.assertEqual(sum(n.startswith('toe_'+side) for n in names),5)
   for prefix in ('wing','ear_inner','ear_tragus','thumb','fang'):self.assertIn(prefix+'_'+side,names)
  self.assertLess(len(self.tri),12000)
 def test_closed_single_component_and_seams(self):
  body=self.parts[0];ids=body.skin_topology;edges=Counter();graph={i:set() for i in ids};same={}
  for f in body.faces:
   for a,b in zip(f,f[1:]+f[:1]):
    a,b=ids[a],ids[b];edges[tuple(sorted((a,b)))]+=1;graph[a].add(b);graph[b].add(a)
  self.assertTrue(all(n==2 for n in edges.values()))
  seen={ids[0]};todo=[ids[0]]
  while todo:
   for n in graph[todo.pop()]:
    if n not in seen:seen.add(n);todo.append(n)
  self.assertEqual(seen,set(ids))
  for i,key in enumerate(ids):
   if key in same:self.assertEqual((body.vertices[i],self.w[i]),(body.vertices[same[key]],self.w[same[key]]))
   same[key]=i
  used={bat.BONES[b][0] for ws in self.w[:len(ids)] for b,w in ws if w>.01}
  for side in ('L','R'):
   for role in ('arm','hand','fingers','leg','ear'):self.assertIn(role+'_'+side,used)
 def test_flight_loop_and_pose_envelope(self):
  for name in ('idle','fly'):
   a=bat.deform(self.v,self.w,bat.pose(name,0));b=bat.deform(self.v,self.w,bat.pose(name,1))
   self.assertLess(max(math.dist(x,y) for x,y in zip(a,b)),1e-8)
  for b in self.bounds:
   self.assertLess(b[4]-b[1],64);self.assertGreaterEqual(b[2],.06999)
  self.assertLess(self.bounds[-1][5],22)
  self.assertGreater(min(b[2] for b in self.bounds[:56]),4)
 def test_weights_and_unit_scale(self):
  for ws in self.w:
   self.assertLessEqual(len(ws),4);self.assertAlmostEqual(sum(w for _,w in ws),1,places=6)
  for c in self.clips:
   for f in c['frames']:
    for row in f:self.assertEqual(row[7:],(1,1,1))
  self.assertEqual([c['loop'] for c in self.clips],[True,True,False,False,False,False])
 def test_actions_recover(self):
  for name in ('nip','feed','recoil'):
   a=bat.deform(self.v,self.w,bat.pose(name,0));b=bat.deform(self.v,self.w,bat.pose(name,1))
   self.assertLess(max(math.dist(x,y) for x,y in zip(a,b)),1e-8)
 def test_triangle_area_every_frame(self):
  for c in self.clips:
   for f in c['frames']:
    v=bat.deform(self.v,self.w,f)
    for a,b,d in self.tri:
     x=tuple(v[b][k]-v[a][k] for k in range(3));y=tuple(v[d][k]-v[a][k] for k in range(3))
     area=sum((x[(k+1)%3]*y[(k+2)%3]-x[(k+2)%3]*y[(k+1)%3])**2 for k in range(3))
     self.assertGreater(area,1e-14)
 def test_export(self):
  m=json.loads((bat.ROOT/'assets/monsters/vampire_bat/animation.json').read_text())
  for path,digest in [(m['runtimeModel'],m['sha256']),('mod/BrogueDoom/'+bat.SKIN,m['skinSha256'])]:
   self.assertEqual(hashlib.sha256((bat.ROOT/path).read_bytes()).hexdigest(),digest)
  self.assertEqual(bat.materials.texture_bytes(),(bat.ROOT/'mod/BrogueDoom'/bat.SKIN).read_bytes())
if __name__=='__main__':unittest.main()
