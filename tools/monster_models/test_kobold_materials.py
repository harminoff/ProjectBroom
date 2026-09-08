"""Kobold material ownership, padding and reproducible texture gates."""
import unittest,hashlib
from . import kobold_materials as skin,kobold_animation as rig
from .rat import ROOT

class KoboldMaterialTests(unittest.TestCase):
 def test_original_reference_and_deterministic_diffuse(self):
  self.assertEqual(skin.texture_bytes(),(ROOT/'mod/BrogueDoom'/skin.SKIN).read_bytes())
  self.assertEqual(hashlib.sha256((ROOT/'mod/BrogueDoom/graphics/BRGM02.png').read_bytes()).hexdigest(),'49e898e9875306dd97fe861b83344764945bd2f076b7c987b136b08d8fd5cbe5')

 def test_every_part_stays_inside_its_padded_material(self):
  for part in rig.build_parts():
   x0,y0,x1,y1=skin.RECTS[skin.role(part.name)]
   for u,v in part.uv:
    self.assertTrue(x0-.01<=u*1024<=x1+.01,part.name)
    self.assertTrue(y0-.01<=(1-v)*1024<=y1+.01,part.name)
  self.assertEqual(skin.role('head_eye_1'),'eye')
  self.assertEqual(skin.role('head_pupil_1'),'dark')
  self.assertEqual(skin.role('club_binding1'),'leather')
  self.assertEqual(skin.role('club_shaft'),'wood')
  self.assertEqual(skin.role('foot_L_claw0'),'bone')

 def test_brown_scales_and_readable_material_separation(self):
  brown=skin.shade('scales',.4,.4);belly=skin.shade('ventral',.5,.4)
  self.assertGreater(brown[0],brown[1]);self.assertGreater(brown[1],brown[2])
  self.assertGreater(sum(belly),sum(brown)+100)
  self.assertGreater(sum(skin.shade('eye',.5,.5)),sum(skin.shade('dark',.5,.5))+250)
  self.assertGreater(sum(skin.shade('bone',.5,.5)),sum(skin.shade('wood',.5,.5))+200)

if __name__=='__main__':unittest.main()
