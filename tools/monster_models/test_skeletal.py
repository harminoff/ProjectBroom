"""Reusable skeletal pipeline and kobold attachment regression tests.

Rebuilding every creature's geometry and animation costs minutes per creature,
and the registry grows every batch. A creature whose generator sources (found
statically, see creature_pipeline.module_deps), profile row and exported bytes
are identical to a previous fully verified run is checked cheaply instead: file
hash against its manifest, clip names, and durations against the recorded frame
counts. Anything changed gets the full rebuild. Set BROOM_SKELETAL_FULL=1 to
force the full rebuild for every creature.
"""
import hashlib, importlib, json, math, os, unittest
from . import iqm
from .skeletal_registry import ROOT, profiles, native_text
from .rat import cross, sub

CACHE=ROOT/'.build/skeletal-verified.json'


def input_key(row):
 from .creature_pipeline import module_deps, fingerprint
 return fingerprint(module_deps(row['module'])+['tools/monster_models/iqm.py','tools/monster_models/skeletal.py',
                    'mod/BrogueDoom/models/monsters/'+row['model'],row['manifest']],extra=row)


class SkeletalTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.rows=profiles();cls._assets={};cls.failed=set()
  full=os.environ.get('BROOM_SKELETAL_FULL')=='1'
  cls.cache=json.loads(CACHE.read_text()) if CACHE.is_file() and not full else {}
  cls.keys={row['symbol']:input_key(row) for row in cls.rows}
  cls.fresh={s for s,k in cls.keys.items() if cls.cache.get(s,{}).get('key')!=k}

 @classmethod
 def tearDownClass(cls):
  data=json.loads(CACHE.read_text()) if CACHE.is_file() else {}
  for row in cls.rows:
   s=row['symbol']
   if s in cls._assets and s not in cls.failed:
    clips=cls._assets[s][8]
    data[s]=dict(key=cls.keys[s],clipFrames=[[len(c['frames']),c['fps']] for c in clips])
  CACHE.parent.mkdir(parents=True,exist_ok=True);CACHE.write_text(json.dumps(data,indent=1,sort_keys=True))

 @classmethod
 def asset(cls,row):
  s=row['symbol']
  if s not in cls._assets:
   rig=importlib.import_module('tools.monster_models.'+row['module'])
   parts,v,n,uv,t,w=rig.geometry();clips,bounds=rig.animation_data(v,w)
   cls._assets[s]=(row,rig,parts,v,n,uv,t,w,clips,bounds)
  return cls._assets[s]

 @property
 def assets(self):
  """Full assets for creatures whose inputs changed (tests needing geometry use this)."""
  return [self.asset(row) for row in self.rows if row['symbol'] in self.fresh]

 def check(self,symbol,body):
  try:body()
  except Exception:
   type(self).failed.add(symbol);raise

 def test_registry_native_and_binary_agree(self):
  self.assertEqual((ROOT/'src/gzdoom-bridge/skeletal_presentation.generated.h').read_text(),native_text())
  for row in self.rows:
   with self.subTest(enemy=row['symbol']):
    self.check(row['symbol'],lambda:self._binary(row))

 def _binary(self,row):
  data=(ROOT/'mod/BrogueDoom/models/monsters'/row['model']).read_bytes()
  manifest=json.loads((ROOT/row['manifest']).read_text())
  self.assertEqual(hashlib.sha256(data).hexdigest(),manifest['sha256'])
  parsed=iqm.inspect(data)
  extra=row.get('captivity',{})
  self.assertEqual([a['name'] for a in parsed['animations']],row['clips']+([extra['idle'],extra['release']] if extra else []))
  if row['symbol'] in self.fresh:
   _,rig,parts,v,n,uv,t,w,clips,bounds=self.asset(row)
   expected=iqm.encode(v,n,uv,t,w,rig.BONES,clips,bounds,mesh_label='Project_Broom_'+row['symbol'][3:].lower(),material_path=row['skin'])
   self.assertEqual(data,expected)
   frames=[(len(c['frames']),c['fps']) for c in clips]
  else:
   frames=[tuple(f) for f in self.cache[row['symbol']]['clipFrames']]
  for role in range(2,6):
   count,fps=frames[role]
   self.assertGreaterEqual(row['durations'][role],math.ceil(count*35/fps))

 def test_valid_skinning_geometry_and_grounding(self):
  for row,rig,parts,v,n,uv,t,w,clips,bounds in self.assets:
   with self.subTest(enemy=row['symbol']):
    self.check(row['symbol'],lambda:self._geometry(rig,v,n,t,w,bounds))

 def _geometry(self,rig,v,n,t,w,bounds):
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
  row,rig,parts,v,n,uv,t,w,clips,bounds=self.asset(next(r for r in self.rows if r['symbol']=='MK_KOBOLD'))
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
