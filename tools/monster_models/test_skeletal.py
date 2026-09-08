"""Reusable skeletal pipeline and kobold attachment regression tests."""
import hashlib, importlib, json, math, unittest
from . import iqm
from .skeletal_registry import ROOT, profiles, native_text
from .rat import cross, sub

class SkeletalTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.rows=profiles();cls.assets=[]
  for row in cls.rows:
   rig=importlib.import_module('tools.monster_models.'+row['module'])
   parts,v,n,uv,t,w=rig.geometry();clips,bounds=rig.animation_data(v,w)
   cls.assets.append((row,rig,parts,v,n,uv,t,w,clips,bounds))

 def test_registry_native_and_binary_agree(self):
  self.assertEqual((ROOT/'src/gzdoom-bridge/skeletal_presentation.generated.h').read_text(),native_text())
  for row,rig,parts,v,n,uv,t,w,clips,bounds in self.assets:
   with self.subTest(enemy=row['symbol']):
    data=(ROOT/'mod/BrogueDoom/models/monsters'/row['model']).read_bytes()
    expected=iqm.encode(v,n,uv,t,w,rig.BONES,clips,bounds,mesh_label='Project_Broom_'+row['symbol'][3:].lower(),material_path=row['skin'])
    self.assertEqual(data,expected)
    parsed=iqm.inspect(data)
    extra=row.get('captivity',{})
    self.assertEqual([a['name'] for a in parsed['animations']],row['clips']+([extra['idle'],extra['release']] if extra else []))
    manifest=json.loads((ROOT/row['manifest']).read_text())
    self.assertEqual(hashlib.sha256(data).hexdigest(),manifest['sha256'])
    for role in range(2,6):
     clip=clips[role]
     self.assertGreaterEqual(row['durations'][role],math.ceil(len(clip['frames'])*35/clip['fps']))

 def test_valid_skinning_geometry_and_grounding(self):
  for row,rig,parts,v,n,uv,t,w,clips,bounds in self.assets:
   with self.subTest(enemy=row['symbol']):
    self.assertEqual(len({b[0] for b in rig.BONES}),len(rig.BONES))
    for i,(_,parent,_) in enumerate(rig.BONES):self.assertTrue(-1<=parent<i)
    for weights in w:
     self.assertTrue(1<=len(weights)<=4)
     self.assertAlmostEqual(sum(a for _,a in weights),1)
     self.assertTrue(all(0<=i<len(rig.BONES) and 0<=a<=1 for i,a in weights))
    for normal in n:self.assertAlmostEqual(sum(a*a for a in normal),1,places=5)
    for a,b,c in t:self.assertGreater(sum(x*x for x in cross(sub(v[b],v[a]),sub(v[c],v[a]))),1e-15)
    self.assertTrue(all(math.isfinite(x) for b in bounds for x in b))
    self.assertTrue(all(b[2]>=.06999 for b in bounds))
    self.assertTrue(all(b[3]-b[0]<80 and b[4]-b[1]<80 for b in bounds))

 def test_kobold_hand_club_attachment_and_stance(self):
  row,rig,parts,v,n,uv,t,w,clips,bounds=next(a for a in self.assets if a[0]['symbol']=='MK_KOBOLD')
  club=rig.IDS['club'];hand=rig.IDS['arm_R_end']
  for part in parts:
   if part.name.startswith('club'):self.assertEqual(rig.weights(part,part.vertices[0],part.uv[0]),[(club,1)])
  for clip in clips:
   for frame in clip['frames']:
    transforms=rig.matrices(frame)
    self.assertLess(math.dist(transforms[club][0],transforms[hand][0]),1e-9)
    self.assertLess(math.dist(transforms[club][1],transforms[hand][1]),1e-9)
  for frame in clips[1]['frames']:
   transforms=rig.matrices(frame)
   self.assertLess(min(transforms[rig.IDS[f'leg_{side}_end']][0][2] for side in ('L','R')),2.5)
  self.assertLess(bounds[-1][5],20) # Settled death lies on its side.

 def test_bindings_use_registry_and_no_new_input_gate(self):
  source=(ROOT/'src/gzdoom-bridge/brogue_bridge_frontend.cpp').read_text()
  helper=source.split('void PlayMonsterClip(')[1].split('void BeginMonsterEventAnimations')[0]
  self.assertIn('profile->clips[clip]',helper)
  self.assertIn('profile->durations[clip]',helper)
  for forbidden in ('PerformAction','PerformCommand','Random','P_DamageMobj'):self.assertNotIn(forbidden,helper)
  gate=source.split('bool MonsterAnimationsActive()')[1].split('void SyncItems()')[0]
  self.assertNotIn('ratPoseTics',gate);self.assertNotIn('ratDeathTics',gate)

if __name__=='__main__':unittest.main()
