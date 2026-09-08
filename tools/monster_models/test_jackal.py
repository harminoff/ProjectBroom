"""Jackal anatomy, jaw attachment, grounded gait and deterministic fur checks."""
import unittest,math,hashlib
from . import jackal_animation as rig,jackal_materials as skin
from .rat import ROOT
class JackalTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.parts,cls.v,cls.n,cls.uv,cls.t,cls.w=rig.geometry();cls.clips,cls.bounds=rig.animation_data(cls.v,cls.w)
 def test_jaws_ears_and_paws_follow_owned_bones(self):
  for part in self.parts:
   if part.name.startswith('jaw'):self.assertEqual(rig.weights(part,part.vertices[0],part.uv[0]),[(rig.IDS['jaw'],1)])
   if part.name.startswith('ear_L'):self.assertEqual(rig.weights(part,part.vertices[0],part.uv[0]),[(rig.IDS['ear_L'],1)])
  frame=self.clips[2]['frames'][9];self.assertGreater(abs(frame[rig.IDS['jaw']][4]),.1)
  for f in self.clips[1]['frames']:
   transforms=rig.matrices(f);heights=[transforms[rig.IDS[f'{limb}_{side}_end']][0][2] for limb in ('fore','hind') for side in ('L','R')]
   self.assertLess(sorted(heights)[1],2.6)
 def test_canine_scale_and_grounded_death(self):
  self.assertEqual(len(rig.BONES),25);self.assertLess(len(self.t),16000)
  self.assertTrue(all(b[2]>=.06999 for b in self.bounds))
  self.assertLess(self.bounds[-1][5],18)
  self.assertTrue(all(b[3]-b[0]<64 for b in self.bounds))
 def test_texture_is_deterministic_and_brown(self):
  self.assertEqual(skin.texture_bytes(),(ROOT/'mod/BrogueDoom'/skin.SKIN).read_bytes())
if __name__=='__main__':unittest.main()
