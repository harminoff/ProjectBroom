"""Monkey body, bindings and authored release continuity."""
import hashlib,json,math,unittest,subprocess,tempfile,shutil
from . import monkey_animation as rig,iqm
from .skeletal_registry import ROOT,profiles

class MonkeyTests(unittest.TestCase):
 def test_natural_captive_confirmation_and_rng_continuation(self):
  compiler=shutil.which('gcc')
  if not compiler:self.skipTest('gcc required for public bridge captivity fixture')
  with tempfile.TemporaryDirectory(prefix='broom-monkey-') as directory:
   from pathlib import Path
   exe=Path(directory)/'captivity.exe'
   subprocess.run([compiler,'-I'+str(ROOT/'src/brogue-mapgen/src/platform'),str(ROOT/'tools/monkey_captivity_test.c'),'-o',str(exe)],check=True,capture_output=True)
   command=[str(exe),str(ROOT/'src/brogue-mapgen/bin/brogue-bridge.dll')]
   a=subprocess.check_output(command,cwd=directory,timeout=20)
   b=subprocess.check_output(command,cwd=directory,timeout=20)
   self.assertEqual(a,b)
   self.assertIn(b'CAPTIVITY_OK',a)
   self.assertIn(b'CONTINUATION 22 3bd39f040e715e22',a)
 @classmethod
 def setUpClass(cls):
  cls.normal=rig.geometry();cls.captive=rig.geometry(True)
 def test_bindings_are_only_on_captive_variant(self):
  a,b=self.normal,self.captive
  for i in (1,2,3,5):self.assertEqual(a[i],b[i][:len(a[i])])
  self.assertEqual(len(b[0])-len(a[0]),15)
  for part in b[0][len(a[0]):]:
   self.assertTrue(part.name.startswith('binding'))
   for v,uv in zip(part.vertices,part.uv):
    weights=rig.weights(part,v,uv)
    self.assertAlmostEqual(sum(w for _,w in weights),1)
    self.assertTrue(all(rig.BONES[i][0] in ('arm_L_end','arm_R_end') for i,_ in weights))
 def test_release_matches_bound_start_and_idle_finish(self):
  vertices=self.normal[1];weights=self.normal[5]
  for a,ta,b,tb in [('captive',0,'released',0),('released',1,'idle',0)]:
   x=rig.deform(vertices,weights,rig.pose(a,ta));y=rig.deform(vertices,weights,rig.pose(b,tb))
   self.assertLess(max(math.dist(p,q) for p,q in zip(x,y)),1e-9)
  self.assertTrue(31<max(v[2] for v in vertices)<34)
 def test_lower_arms_do_not_fuse_to_the_torso(self):
  body=self.normal[0][0]
  for point,weights in zip(body.vertices,self.normal[5]):
   if point[2]>=19:continue # Shoulder blend is intentional.
   bones={rig.BONES[i][0] for i,w in weights if w>.1}
   self.assertFalse(any(n.startswith('arm_') for n in bones) and bones.intersection(('spine','pelvis')),
                    'Arm clearance lost during the connected skin bake')
 def test_captive_binary_matches_generator(self):
  parts,v,n,uv,t,w=self.captive;clips,bounds=rig.animation_data(v,w)
  payload=iqm.encode(v,n,uv,t,w,rig.BONES,clips,bounds,mesh_label='Project_Broom_monkey',material_path=rig.monkey_materials.SKIN)
  self.assertEqual(payload,(ROOT/'mod/BrogueDoom/models/monsters/05_monkey_captive.iqm').read_bytes())
  manifest=json.loads((ROOT/'assets/monsters/monkey/animation.json').read_text())
  self.assertEqual(hashlib.sha256(payload).hexdigest(),manifest['variants']['captive']['sha256'])
  self.assertEqual(len(clips),8)
 def test_captivity_uses_copied_state_and_existing_action_path(self):
  source=(ROOT/'src/gzdoom-bridge/brogue_bridge_frontend.cpp').read_text()
  self.assertIn('CopiedCaptiveFlag = uint64_t(1) << 8',source)
  rogue=(ROOT/'src/brogue-mapgen/src/brogue/Rogue.h').read_text()
  self.assertRegex(rogue,r'MB_CAPTIVE\s*=\s*Fl\(8\)')
  sync=source.split('void SyncMonsters(')[1].split('void TickMonsterAnimations')[0]
  self.assertIn('proxy.captive && !captive',sync)
  self.assertIn('result != nullptr',sync)
  self.assertIn('proxy.visibility == BROGUE_VISIBILITY_DIRECT',sync)
  self.assertIn('creature.visibility == BROGUE_VISIBILITY_DIRECT',sync)
  for prohibited in ('freeCaptive(', 'becomeAllyWith(', 'playerTurnEnded('):self.assertNotIn(prohibited,sync)
if __name__=='__main__':unittest.main()
