"""Naga anatomy continuity, deformation and cosmetic contract regression."""
import collections,math,unittest
from . import naga_animation as rig,iqm

class NagaTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.parts,cls.v,cls.n,cls.uv,cls.tri,cls.w=rig.geometry();cls.clips,cls.bounds=rig.animation_data(cls.v,cls.w)
 def test_one_closed_connected_skin(self):
  p=self.parts[0];ids=p.skin_topology;edges=collections.Counter();graph={i:set() for i in ids}
  for face in p.faces:
   for a,b in zip(face,face[1:]+face[:1]):
    a,b=ids[a],ids[b];self.assertNotEqual(a,b);edges[tuple(sorted((a,b)))]+=1;graph[a].add(b);graph[b].add(a)
  self.assertEqual(set(edges.values()),{2});todo=[ids[0]];seen={ids[0]}
  while todo:
   for b in graph[todo.pop()]:
    if b not in seen:seen.add(b);todo.append(b)
  self.assertEqual(seen,set(ids))
 def test_coil_hole_and_separate_hands(self):
  # The center of the lower coil is genuinely open, not a remeshed disk.
  low=[v for v in self.parts[0].vertices if v[2]<8 and v[0]>-5]
  self.assertGreater(min(math.hypot(v[0]-3,v[1]) for v in low),6)
  parts=rig.build_parts()
  for side in ('L','R'):
   hand=[v for p in parts if p.name.startswith((f'skin_hand_{side}',f'skin_finger_{side}')) for v in p.vertices]
   torso=[v for p in parts if p.name=='skin_torso' for v in p.vertices]
   self.assertGreater(min(math.dist(a,b) for a in hand for b in torso),3)
 def test_normalized_weights_and_uv_seams(self):
  reps={}
  for w in self.w:self.assertAlmostEqual(sum(x for b,x in w),1);self.assertLessEqual(len(w),4)
  for i,key in enumerate(self.parts[0].skin_topology):
   if key in reps:
    j=reps[key];self.assertEqual(self.v[i],self.v[j]);self.assertEqual(self.w[i],self.w[j])
   reps[key]=i
  used={rig.BONES[b][0] for weights in self.w for b,w in weights if w>.05}
  for name in ('waist','chest','neck','head','jaw','arm_L_1','arm_R_2','tail_3','tail_7','tail_10'):self.assertIn(name,used)
 def test_all_frames_centered_grounded_unit_scale(self):
  for b in self.bounds:
   self.assertGreaterEqual(b[2],.069);self.assertGreaterEqual(b[0],-32);self.assertGreaterEqual(b[1],-32);self.assertLessEqual(b[3],32);self.assertLessEqual(b[4],32)
  for clip in self.clips:
   for j,frame in enumerate(clip['frames']):
    self.assertTrue(all(row[7:]==(1,1,1) for row in frame))
    raw=rig.pose(clip['name'],j/(len(clip['frames']) if clip['loop'] else len(clip['frames'])-1))
    self.assertEqual(frame[0],raw[0], 'Whole-root floor lift must not mask a raw pose defect')
    self.assertGreaterEqual(min(v[2] for v in rig.deform(self.v,self.w,raw)),.069)
 def test_recovery_and_loop_roles(self):
  self.assertEqual([c['loop'] for c in self.clips],[True,True,False,False,False,False])
  for name in ('idle','slither','claw','tailwhip','recoil'):
   self.assertLess(max(math.dist(a,b) for a,b in zip(rig.deform(self.v,self.w,rig.pose(name,0)),rig.deform(self.v,self.w,rig.pose(name,1)))),1e-9)
  for name in ('claw','tailwhip'):
   self.assertGreater(max(math.dist(a,b) for a,b in zip(rig.deform(self.v,self.w,rig.pose(name,0)),rig.deform(self.v,self.w,rig.pose(name,.5)))),3)
 def test_collapsed_head_and_hands(self):
  dead=rig.deform(self.v,self.w,self.clips[-1]['frames'][-1])
  self.assertLess(max(v[2] for v in dead),.60*max(v[2] for v in self.v))
  for bone,limit in [('head',max(v[2] for v in self.v)/3),('arm_L_2',9),('arm_R_2',9)]:
   points=[v for v,w in zip(dead,self.w) if any(b==rig.IDS[bone] and x>.9 for b,x in w)]
   self.assertTrue(points);self.assertLess(max(v[2] for v in points),limit)
   if bone.startswith('arm'):self.assertLess(max(abs(v[1]) for v in points),11)
 def test_ventral_coordinates_and_tail_arc(self):
  self.assertAlmostEqual(rig.pigment((0,0,35))[1],.5)
  self.assertGreater(rig.pigment((-12,0,35))[1],.9)
  self.assertGreater(rig.pigment((3,0,54))[0],.64)
  self.assertGreater(abs(rig.pigment((20,0,6))[0]-rig.pigment((-2,-18,6))[0]),.03)
 def test_runtime_and_texture_match_master(self):
  data=iqm.encode(self.v,self.n,self.uv,self.tri,self.w,rig.BONES,self.clips,self.bounds,mesh_label='Project_Broom_naga',material_path=rig.SKIN)
  self.assertEqual(data,(rig.ROOT/'mod/BrogueDoom/models/monsters/28_naga.iqm').read_bytes())
  self.assertEqual(rig.texture_bytes(),(rig.ROOT/'mod/BrogueDoom'/rig.SKIN).read_bytes())
if __name__=='__main__':unittest.main()
