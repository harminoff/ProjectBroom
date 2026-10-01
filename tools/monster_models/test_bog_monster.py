"""Bog monster continuity, six-arm rig and deterministic presentation checks."""
import collections,hashlib,math,unittest
from . import bog_monster_animation as rig,iqm
class BogMonsterTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.parts,cls.v,cls.n,cls.uv,cls.tri,cls.w=rig.geometry();cls.clips,cls.bounds=rig.animation_data(cls.v,cls.w)
 def test_connected_closed_tentacles(self):
  self.assertEqual(len(self.parts),1);p=self.parts[0];ids=p.skin_topology;edges=collections.Counter();graph={i:set() for i in ids}
  for face in p.faces:
   for a,b in zip(face,face[1:]+face[:1]):
    a,b=ids[a],ids[b];self.assertNotEqual(a,b);edges[tuple(sorted((a,b)))]+=1;graph[a].add(b);graph[b].add(a)
  self.assertEqual(set(edges.values()),{2});todo=[ids[0]];seen={ids[0]}
  while todo:
   for b in graph[todo.pop()]:
    if b not in seen:seen.add(b);todo.append(b)
  self.assertEqual(seen,set(ids))
  used={rig.BONES[b][0] for weights in self.w for b,w in weights if w>.01}
  for arm in range(6):
   for j in (1,3,5):self.assertIn(f'arm_{arm}_{j}',used)
 def test_seams_and_normalized_weights(self):
  reps={}
  for i,key in enumerate(self.parts[0].skin_topology):
   self.assertAlmostEqual(sum(w for b,w in self.w[i]),1);self.assertLessEqual(len(self.w[i]),4)
   if key in reps:
    j=reps[key];self.assertEqual(self.v[i],self.v[j]);self.assertEqual(self.w[i],self.w[j])
   reps[key]=i
 def test_roles_floor_and_cell_envelope(self):
  self.assertEqual([c['loop'] for c in self.clips],[True,True,False,False,False,False])
  for b in self.bounds:
   self.assertGreaterEqual(b[2],.069);self.assertGreaterEqual(b[0],-32);self.assertGreaterEqual(b[1],-32);self.assertLessEqual(b[3],32);self.assertLessEqual(b[4],32)
  for clip in self.clips:
   for frame in clip['frames']:
    self.assertTrue(all(row[7:]==(1,1,1) for row in frame))
  for name in ('idle','drift','squeeze','coil','recoil'):
   self.assertLess(max(math.dist(a,b) for a,b in zip(rig.deform(self.v,self.w,rig.pose(name,0)),rig.deform(self.v,self.w,rig.pose(name,1)))),1e-9)
  death=rig.deform(self.v,self.w,self.clips[-1]['frames'][-1]);self.assertLess(max(v[2] for v in death),max(v[2] for v in self.v))
 def test_runtime_and_texture_match_master(self):
  data=iqm.encode(self.v,self.n,self.uv,self.tri,self.w,rig.BONES,self.clips,self.bounds,mesh_label='Project_Broom_bog_monster',material_path=rig.SKIN)
  self.assertEqual(data,(rig.ROOT/'mod/BrogueDoom/models/monsters/19_bog_monster.iqm').read_bytes())
  self.assertEqual(rig.texture_bytes(),(rig.ROOT/'mod/BrogueDoom'/rig.SKIN).read_bytes())
if __name__=='__main__':unittest.main()
