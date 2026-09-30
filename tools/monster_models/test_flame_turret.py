"""Flame turret mechanism, mesh-local fire, extinction, export and wall mount checks."""
import math,json,subprocess,tempfile,unittest
from pathlib import Path
from . import flame_turret_animation as m,flame_turret_materials as mat,iqm
from .rat import cross,sub

EMISSIVE_PREFIXES=('blast_','pilot_core','pilot_lick_','ember_eye_')


def area(v,t):
    a,b,c=(v[i] for i in t);return math.sqrt(sum(x*x for x in cross(sub(b,a),sub(c,a))))/2


class FlameTurretTests(unittest.TestCase):
 @classmethod
 def setUpClass(c):
  c.parts,c.v,c.n,c.uv,c.tri,c.w=m.geometry();c.clips,c.bounds=m.animation_data(c.v,c.w)
  c.clip={x['name']:x for x in c.clips}
  c.ranges={};start=0;tstart=0
  for p in c.parts:
   ntri=len(list(p.triangles()));c.ranges[p.name]=(range(start,start+len(p.vertices)),range(tstart,tstart+ntri));start+=len(p.vertices);tstart+=ntri
  c.emissive={p.name for p in c.parts if p.name.startswith(EMISSIVE_PREFIXES)}
 def tris(self,prefixes):
  return [self.tri[i] for p in self.parts if p.name.startswith(prefixes) for i in self.ranges[p.name][1]]
 def test_signature_construction(self):
  names={p.name for p in self.parts}
  for n in ('shield_backplate','stepped_plate_panel','support_shelf','riveted_firebox','infernal_mask_plate','snout_crest','fanged_mouth_ring',
            'curled_horn_L','curled_horn_R','angry_brow_L','ember_eye_L','ember_eye_R','iron_eyelid_L','tempered_nozzle_barrel',
            'mouth_shutter_L','mouth_shutter_R','copper_pilot_line','pilot_jet_tip','fuel_canister_L','fuel_canister_R','dial_face','dial_needle',
            'pleated_leather_bellows','bellows_top_board','pilot_core','blast_core'):self.assertIn(n,names)
  self.assertEqual(sum(n.startswith('cooling_fin_') for n in names),5)
  self.assertEqual(sum(n.startswith('anchor_hex_bolt_') for n in names),6)
  self.assertEqual(sum(n.startswith('mouth_fang_') for n in names),8)
  self.assertEqual(sum(n.startswith('blast_lick_') for n in names),7)
  self.assertGreaterEqual(sum(n.startswith('plate_rivet_') for n in names),20)
  self.assertEqual(len(m.BONES),33);self.assertEqual([c[0] for c in m.CLIPS],['idle','rest','spit','gout','jolt','extinguish'])
 def test_backplate_supports_and_canisters_fixed_in_every_frame(self):
  fixed=[i for i,w in enumerate(self.w) if w==[(0,1)]]
  self.assertGreater(len(fixed),4000)
  for name in ('shield_backplate','fuel_canister_L','gusset_bracket_L','support_shelf','valve_wheel_R'):
   self.assertTrue(all(self.w[i]==[(0,1)] for i in self.ranges[name][0]),name)
  for c in self.clips:
   for f in c['frames']:
    v=m.deform(self.v,self.w,f);self.assertEqual(f[0],m.pose('rest',0)[0])
    self.assertLess(max(math.dist(v[i],self.v[i]) for i in fixed),1e-9)
 def test_weights_quantized_normalized_and_cages_isolated(self):
  for p in self.parts:
   for i in self.ranges[p.name][0]:
    w=self.w[i];self.assertLessEqual(len(w),4);self.assertAlmostEqual(sum(x for _,x in w),1,12)
    self.assertTrue(all(abs(x*1e6-round(x*1e6))<1e-6 and x>0 for _,x in w))
    bones={m.BONES[b][0] for b,_ in w}
    if p.name in self.emissive:
     prefix='blast_' if p.name.startswith('blast') else 'pilot_' if p.name.startswith('pilot') else 'eye'+p.name[-1]+'_'
     self.assertTrue(all(b.startswith(prefix) for b in bones),(p.name,bones))
    else:self.assertFalse(any(b.startswith(('blast_','pilot_','eye')) for b in bones),p.name)
 def test_rest_idle_and_action_recovery(self):
  rest=m.pose('rest',0)
  for f in self.clip['rest']['frames']:self.assertEqual(f,rest)
  moving={m.IDS[n] for n,_,_ in m.BONES if n.startswith('pilot_')}|{m.IDS['needle']}
  for f in self.clip['idle']['frames']:
   for i,(a,b) in enumerate(zip(f,rest)):
    if i not in moving:self.assertEqual(a,b,m.BONES[i][0])
  self.assertEqual(self.clip['idle']['frames'][0],rest)
  for name in ('spit','gout','jolt'):
   for a,b in zip(m.pose(name,0),m.pose(name,1)):self.assertLess(math.dist(a,b),1e-9,name)
   for a,b in zip(m.pose(name,1),rest):self.assertLess(math.dist(a,b),1e-9,name)
  for c in self.clips:
   self.assertEqual(c['loop'],c['name'] in ('idle','rest'))
   for f in c['frames']:
    for row in f:self.assertEqual(row[7:],(1,1,1));self.assertAlmostEqual(sum(a*a for a in row[3:7]),1,12)
 def test_emissive_atlas_column_is_exactly_the_fire(self):
  for p in self.parts:
   us=[u for u,_ in p.uv]
   if p.name in self.emissive:self.assertGreaterEqual(min(us),mat.EMISSIVE_U+.005,p.name)
   else:self.assertLess(max(us),mat.EMISSIVE_U-.005,p.name)
  self.assertEqual({p.role for p in self.parts if p.name in self.emissive},{'flame','ember'})
 def test_fire_visible_in_idle_blast_only_in_attacks_and_complete_extinction(self):
  def total(frame,prefixes):
   v=m.deform(self.v,self.w,frame);return sum(area(v,t) for t in self.tris(prefixes))
  idle=self.clip['idle']['frames'][0]
  self.assertGreater(total(idle,('pilot_',)),6);self.assertGreater(total(idle,('ember_eye_L',)),6);self.assertGreater(total(idle,('ember_eye_R',)),6)
  for name in ('idle','rest','jolt','extinguish'):
   for f in self.clip[name]['frames']:self.assertLess(total(f,('blast_',)),1e-6,name)
  spit=self.clip['spit']['frames'];mid=spit[len(spit)//2]
  self.assertGreater(total(mid,('blast_',)),.9*total(m.pose('spit',.52),('blast_',)))
  vmid=m.deform(self.v,self.w,mid);blast=[i for p in self.parts if p.name.startswith('blast_') for i in self.ranges[p.name][0]]
  self.assertGreater(max(vmid[i][0] for i in blast),30)
  gout=self.clip['gout']['frames'];self.assertGreater(total(gout[len(gout)//2],('blast_',)),150)
  # Collapse is exact up to 1e-6 weight quantisation: far below one texel.
  dead=self.clip['extinguish']['frames'][-1];self.assertLess(total(dead,EMISSIVE_PREFIXES),1e-3)
  self.assertLess(total(dead,EMISSIVE_PREFIXES),1e-5*total(idle,EMISSIVE_PREFIXES))
 def test_key_poses_on_middle_frames_and_closed_death(self):
  def ang(frame,bone):
   q=frame[m.IDS[bone]][3:7];return math.degrees(2*math.acos(min(1,abs(q[3]))))
  rest=m.pose('rest',0)
  for name in ('spit','gout','jolt','extinguish'):
   frames=self.clip[name]['frames'];mid=frames[len(frames)//2]
   self.assertGreater(max(math.dist(a,b) for a,b in zip(mid,rest)),.05,name)
  self.assertGreater(ang(self.clip['jolt']['frames'][7],'body'),3)
  dead=self.clip['extinguish']['frames'][-1]
  for bone in ('lid_L','lid_R','damper_L','damper_R'):self.assertLess(ang(dead,bone),1e-6,bone)
  self.assertGreater(ang(dead,'barrel'),15);self.assertGreater(ang(dead,'body'),5)
  self.assertGreater(ang(rest,'damper_L'),100);self.assertGreater(ang(rest,'lid_L'),70)
 def test_shutters_never_pass_through_the_bell(self):
  prof=[(-2.4,3.3),(1.0,3.3),(1.6,3.35),(8.6,3.0),(15.1,2.75),(17.1,3.0),(18.6,3.8),(19.8,4.7),(20.4,4.95),(20.7,4.8)]
  def outer(s):
   for (a,r0),(b,r1) in zip(prof,prof[1:]):
    if a<=s<=b:return r0+(r1-r0)*(s-a)/(b-a)
   return 0
  ids=[i for p in self.parts if p.name.startswith(('mouth_shutter_','shutter_rib_','shutter_pull','shutter_rivet')) for i in self.ranges[p.name][0]]
  from .skeletal import rotate,inverse
  for c in self.clips:
   for f in c['frames']:
    v=m.deform(self.v,self.w,f);loc,q=m.matrices(f)[m.IDS['barrel']]
    for i in ids:
     p=rotate(inverse(q),sub(v[i],loc));s=p[0];r=math.hypot(p[1],p[2]-0)
     # p is relative to the barrel pivot; the lathe profile starts at that pivot.
     if s<=20.7:self.assertGreater(r,outer(s)-1e-6,(c['name'],i))
 def test_cell_bounds_floor_and_wall_back(self):
  self.assertEqual(round(min(v[0] for v in self.v),6),-11.0)
  for c in self.clips:
   for f in c['frames']:
    v=m.deform(self.v,self.w,f)
    self.assertGreaterEqual(min(x[0] for x in v),-11.0-1e-9)
    self.assertTrue(all(abs(x[0])<32 and abs(x[1])<32 for x in v))
    self.assertGreater(min(x[2] for x in v),2.5)
    self.assertEqual(f[0][:3],(0,0,0))
  emissive=set(self.tris(EMISSIVE_PREFIXES))
  solid=[t for t in self.tri if t not in emissive]
  for c in self.clips:
   for f in (c['frames'][0],c['frames'][len(c['frames'])//2],c['frames'][-1]):
    v=m.deform(self.v,self.w,f);self.assertGreater(min(area(v,t) for t in solid),1e-7,c['name'])
 def test_runtime_texture_shader_and_profile_match(self):
  self.assertEqual(iqm.encode(self.v,self.n,self.uv,self.tri,self.w,m.BONES,self.clips,self.bounds,mesh_label='Project_Broom_flame_turret',material_path=m.SKIN),(m.ROOT/'mod/BrogueDoom/models/monsters/44_flame_turret.iqm').read_bytes())
  self.assertEqual(mat.texture_bytes(),(m.ROOT/'mod/BrogueDoom'/m.SKIN).read_bytes())
  row=next(r for r in json.loads((m.ROOT/'assets/monsters/skeletal_profiles.json').read_text())['enemies'] if r['symbol']=='MK_FLAME_TURRET')
  self.assertAlmostEqual(row['wallMountBack'],-min(v[0] for v in self.v));self.assertFalse(row.get('additiveFlame',False))
  self.assertEqual(row['clips'],[c[0] for c in m.CLIPS])
  shader=(m.ROOT/'mod/BrogueDoom/shaders/flame-turret-fire.fp').read_text()
  self.assertIn('step(0.875, vTexCoord.s)',shader);self.assertNotIn('material.Base.a',shader)
  gldefs=(m.ROOT/'mod/BrogueDoom/GLDEFS').read_text()
  self.assertIn('material "graphics/BRGFTUR.png"\n{\n    shader "shaders/flame-turret-fire.fp"\n}',gldefs)
  self.assertNotIn('light',gldefs.split('BRGFTUR.png')[1].split('}')[0])
  zs=(m.ROOT/'mod/BrogueDoom/brogue_monsters.zs').read_text();block=zs.split('class BrogueMonsterK44 : BrogueMonsterProxyBase')[1].split('class ')[0]
  self.assertNotIn('RenderStyle',block);self.assertIn('"idle"',block)
  header=(m.ROOT/'src/gzdoom-bridge/skeletal_presentation.generated.h').read_text()
  self.assertIn('{"BrogueMonsterK44", {"idle", "rest", "spit", "gout", "jolt", "extinguish"}, {0, 0, 24, 28, 14, 36}, 20, "", "", "", 0, 11},',header)
  for legacy in ('mod/BrogueDoom/models/monsters/44_flame_turret.obj','mod/BrogueDoom/graphics/BRGM44.png','assets/monsters/sources/44_flame_turret.blend'):
   self.assertTrue((m.ROOT/legacy).is_file(),legacy)
 def test_shared_wall_mount_selector(self):
  source='''#include "wall_mount.h"
#include <cassert>
int main(){bool faces[4]={true,true,true,true};
assert(WallMount::Face(false,true,faces,0,-2,0)==-1);
assert(WallMount::Face(true,false,faces,0,-2,0)==-1);
assert(WallMount::Face(true,true,faces,0,3,0)==1);
assert(WallMount::Face(true,true,faces,1,-3,0)==0);
assert(WallMount::Face(true,true,faces,2,-3,-3)==2);
assert(WallMount::Face(true,true,faces,-1,-3,-3)==0);
for(int i=0;i<4;i++)faces[i]=false;
assert(WallMount::Face(true,true,faces,2,3,0)==-1);
}'''
  with tempfile.TemporaryDirectory() as td:
   p=Path(td);(p/'test.cpp').write_text(source)
   subprocess.run(['g++','-std=c++17','-static','-I'+str(m.ROOT/'src/gzdoom-bridge'),str(p/'test.cpp'),'-o',str(p/'test.exe')],check=True,capture_output=True)
   subprocess.run([str(p/'test.exe')],check=True)

if __name__=='__main__':unittest.main()
