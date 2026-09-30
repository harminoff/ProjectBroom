"""Dart turret spring mechanism, attached dart feed, broken death, export and wall mount checks."""
import math,json,subprocess,tempfile,unittest
from pathlib import Path
from . import dart_turret_animation as m,dart_turret_materials as mat,iqm
from .rat import cross,sub
from .skeletal import rotate,inverse

CAGED=('chamber_dart','poison_bead')


def area(v,t):
 a,b,c=(v[i] for i in t);return math.sqrt(sum(x*x for x in cross(sub(b,a),sub(c,a))))/2


class DartTurretTests(unittest.TestCase):
 @classmethod
 def setUpClass(c):
  c.parts,c.v,c.n,c.uv,c.tri,c.w=m.geometry();c.clips,c.bounds=m.animation_data(c.v,c.w)
  c.clip={x['name']:x for x in c.clips}
  c.ranges={};start=0;tstart=0
  for p in c.parts:
   ntri=len(list(p.triangles()));c.ranges[p.name]=(range(start,start+len(p.vertices)),range(tstart,tstart+ntri));start+=len(p.vertices);tstart+=ntri
 def ids(self,prefixes):return [i for p in self.parts if p.name.startswith(prefixes) for i in self.ranges[p.name][0]]
 def tris(self,prefixes):return [self.tri[i] for p in self.parts if p.name.startswith(prefixes) for i in self.ranges[p.name][1]]
 def head_space(self,frame,ids):
  """Deformed vertices mapped back into the launcher's rest frame."""
  v=m.deform(self.v,self.w,frame);loc,q=m.matrices(frame)[m.IDS['head']];pivot=m.REST[m.IDS['head']]
  return [tuple(a+b for a,b in zip(rotate(inverse(q),sub(v[i],loc)),pivot)) for i in ids]
 def test_signature_construction(self):
  names={p.name for p in self.parts}
  for n in ('diamond_backplate','enamel_plate_panel','yoke_bracket_L','yoke_bracket_R','cradle_strut','breech_block','sliding_crosshead','striker_rod',
            'tension_spring_L','tension_spring_R','channel_floor','muzzle_collar','hopper_throat','hopper_lid','poison_vial','poison_bead',
            'drip_feed_line','ratchet_wheel','ratchet_pawl','lever_arm','lever_grip','chamber_dart_shaft'):self.assertIn(n,names)
  self.assertEqual(sum(n.startswith('muzzle_spur_') for n in names),6)
  self.assertEqual(sum(n.startswith('anchor_hex_bolt_') for n in names),4)
  self.assertEqual(sum(n.startswith('stack_dart_') and n.endswith('_shaft') for n in names),3)
  self.assertEqual(sum(n.startswith('chamber_dart_flight_') for n in names),4)
  self.assertGreaterEqual(sum(n.startswith('plate_rivet_') for n in names),24)
  self.assertEqual(len(m.BONES),24);self.assertEqual([c[0] for c in m.CLIPS],['idle','rest','loose','snap','jar','jam'])
 def test_plate_brackets_and_trunnion_bosses_fixed_in_every_frame(self):
  fixed=[i for i,w in enumerate(self.w) if w==[(0,1)]]
  self.assertGreater(len(fixed),2000)
  for name in ('diamond_backplate','enamel_plate_panel','yoke_bracket_L','yoke_bracket_R','trunnion_boss_L','cradle_strut','cradle_pad','pawl_stud'):
   self.assertTrue(all(self.w[i]==[(0,1)] for i in self.ranges[name][0]),name)
  for c in self.clips:
   for f in c['frames']:
    v=m.deform(self.v,self.w,f);self.assertEqual(f[0],m.pose('rest',0)[0])
    self.assertLess(max(math.dist(v[i],self.v[i]) for i in fixed),1e-9)
    # The head only pivots on the trunnion axis; its origin never leaves the pins.
    self.assertLess(math.dist(m.matrices(f)[m.IDS['head']][0],m.PIVOT),1e-9)
 def test_weights_quantized_normalized_and_cages_isolated(self):
  for p in self.parts:
   for i in self.ranges[p.name][0]:
    w=self.w[i];self.assertLessEqual(len(w),4);self.assertAlmostEqual(sum(x for _,x in w),1,12)
    self.assertTrue(all(abs(x*1e6-round(x*1e6))<1e-6 and x>0 for _,x in w))
    bones={m.BONES[b][0] for b,_ in w}
    if p.name.startswith('chamber_dart'):self.assertTrue(all(b.startswith('dart_') for b in bones),p.name)
    elif p.name=='poison_bead':self.assertTrue(all(b.startswith('bead_') for b in bones),p.name)
    else:self.assertFalse(any(b.startswith(('dart_','bead_')) for b in bones),p.name)
 def test_rest_idle_and_action_recovery(self):
  rest=m.pose('rest',0)
  for f in self.clip['rest']['frames']:self.assertEqual(f,rest)
  moving={m.IDS[n] for n,_,_ in m.BONES if n.startswith('bead_')}|{m.IDS['pawl']}
  for f in self.clip['idle']['frames']:
   for i,(a,b) in enumerate(zip(f,rest)):
    if i not in moving:self.assertEqual(a,b,m.BONES[i][0])
  self.assertEqual(self.clip['idle']['frames'][0],rest)
  for name in ('loose','snap','jar'):
   for a,b in zip(m.pose(name,0),rest):self.assertLess(math.dist(a,b),1e-9,name)
   for a,b in zip(m.pose(name,1),rest):self.assertLess(math.dist(a,b),1e-9,name)
  for c in self.clips:
   self.assertEqual(c['loop'],c['name'] in ('idle','rest'))
   for f in c['frames']:
    for row in f:self.assertEqual(row[7:],(1,1,1));self.assertAlmostEqual(sum(a*a for a in row[3:7]),1,12)
 def test_springs_stretch_with_the_crosshead_and_stay_attached(self):
  mid=self.clip['loose']['frames'][12]
  for side in ('L','R'):
   ids=self.ids((f'tension_spring_{side}',));hs=self.head_space(mid,ids)
   shot=mid[m.IDS['crosshead']][0]-m.BONES[m.IDS['crosshead']][2][0]
   self.assertAlmostEqual(shot,m.SHOT,6)
   for i,p in zip(ids,hs):
    x=self.v[i][0];f=min(1,max(0,(x-m.SPRING_REAR)/(m.SPRING_FRONT-m.SPRING_REAR)))
    # Exact linear stretch between the hook and the fixed front post.
    self.assertLess(abs(p[0]-(x+(1-f)*shot)),.02,(side,x))
   front=[p for i,p in zip(ids,hs) if self.v[i][0]>=m.SPRING_FRONT];self.assertTrue(front)
   self.assertTrue(all(math.dist(p,self.v[i])<.03 for i,p in zip(ids,hs) if self.v[i][0]>=m.SPRING_FRONT))
  rest_len=m.SPRING_FRONT-m.SPRING_REAR;self.assertLess((rest_len-m.SHOT)/rest_len,.7)
 def test_chamber_dart_attached_fires_and_never_streaks(self):
  ids=self.ids(('chamber_dart',));dart_tris=self.tris(('chamber_dart',))
  rest=[self.v[i] for i in ids]
  self.assertTrue(all(m.DART_X0-1e-6<=p[0]<=22.3 and abs(p[1])<1.3 and 20.8<p[2]<23.8 for p in rest))
  throat=lambda p:7.0<p[0]<22.0 and abs(p[1])<2.9 and 23.8<p[2]<26.4
  for name in ('loose','snap'):
   frames=self.clip[name]['frames'];mid=self.head_space(frames[len(frames)//2],ids)
   self.assertGreater(max(p[0] for p in mid),26 if name=='loose' else 24.5,name)
   prev=None
   for k,f in enumerate(frames):
    hs=self.head_space(f,ids);v=m.deform(self.v,self.w,f);a=sum(area(v,t) for t in dart_tris)
    if prev:
     jump=max(math.dist(p,q) for p,q in zip(hs,prev[0]))
     hidden=lambda s,ar:ar<1e-6 or all(throat(p) for p in s)
     # A large per-frame change is only allowed as the striker's forward stroke along the
     # launch axis, or while the dart is collapsed or inside the closed throat (no reload streak).
     stroke=all(abs(p[1]-q[1])<1e-6 and abs(p[2]-q[2])<1e-6 and p[0]>=q[0] for p,q in zip(hs,prev[0])) and a>1
     # Or the dart contracting uniformly onto its own fixed needle tip at the muzzle.
     tip=max(prev[0],key=lambda q:q[0]);far=max(prev[0],key=lambda q:math.dist(q,tip))
     kk=math.dist(hs[prev[0].index(far)],tip)/max(1e-9,math.dist(far,tip))
     shrink=kk<=1 and all(math.dist(p,tuple(t+kk*(q-t) for q,t in zip(q,tip)))<2e-3 for p,q in zip(hs,prev[0]))
     stroke=stroke or shrink
     if jump>3.2:self.assertTrue(stroke or (hidden(hs,a) and hidden(*prev)),(name,k,jump))
     if not stroke:self.assertTrue(jump<3.2 or (hidden(hs,a) and hidden(*prev)),(name,k,jump))
    prev=(hs,a)
 def test_key_poses_on_middle_frames_and_broken_death(self):
  def ang(frame,bone):
   q=frame[m.IDS[bone]][3:7];return math.degrees(2*math.acos(min(1,abs(q[3]))))
  rest=m.pose('rest',0)
  for name in ('loose','snap','jar','jam'):
   frames=self.clip[name]['frames'];mid=frames[len(frames)//2]
   self.assertGreater(max(math.dist(a,b) for a,b in zip(mid,rest)),.05,name)
  self.assertGreater(ang(self.clip['jar']['frames'][7],'head'),3)
  self.assertGreater(ang(self.clip['snap']['frames'][14],'head'),5)
  dead=self.clip['jam']['frames'][-1]
  self.assertGreater(ang(dead,'head'),20);self.assertGreater(ang(dead,'lid'),25);self.assertGreater(ang(dead,'lever'),60)
  self.assertGreater(math.dist(dead[m.IDS['hook_L']][:3],m.BONES[m.IDS['hook_L']][2]),5)
  self.assertLess(math.dist(dead[m.IDS['hook_R']][:3],m.BONES[m.IDS['hook_R']][2]),1e-9)
  hs=self.head_space(dead,self.ids(('chamber_dart',)))
  self.assertGreater(max(p[0] for p in hs),25.5);self.assertGreater(max(abs(p[1]) for p in hs),.8)
  v=m.deform(self.v,self.w,dead);self.assertLess(sum(area(v,t) for t in self.tris(('poison_bead',))),1e-6)
 def test_cell_bounds_floor_and_wall_back(self):
  self.assertEqual(round(min(v[0] for v in self.v),6),m.BACK)
  for c in self.clips:
   for f in c['frames']:
    v=m.deform(self.v,self.w,f)
    self.assertGreaterEqual(min(x[0] for x in v),m.BACK-1e-9)
    self.assertTrue(all(abs(x[0])<32 and abs(x[1])<32 for x in v))
    self.assertGreater(min(x[2] for x in v),2.5)
    self.assertEqual(f[0][:3],(0,0,0))
  caged=set(self.tris(CAGED));solid=[t for t in self.tri if t not in caged]
  for c in self.clips:
   for f in (c['frames'][0],c['frames'][len(c['frames'])//2],c['frames'][-1]):
    v=m.deform(self.v,self.w,f);self.assertGreater(min(area(v,t) for t in solid),1e-7,c['name'])
  v=self.v;self.assertGreater(min(area(v,t) for t in self.tri),1e-7)
 def test_runtime_texture_and_profile_match(self):
  self.assertEqual(iqm.encode(self.v,self.n,self.uv,self.tri,self.w,m.BONES,self.clips,self.bounds,mesh_label='Project_Broom_dart_turret',material_path=m.SKIN),(m.ROOT/'mod/BrogueDoom/models/monsters/38_dart_turret.iqm').read_bytes())
  self.assertEqual(mat.texture_bytes(),(m.ROOT/'mod/BrogueDoom'/m.SKIN).read_bytes())
  row=next(r for r in json.loads((m.ROOT/'assets/monsters/skeletal_profiles.json').read_text())['enemies'] if r['symbol']=='MK_DART_TURRET')
  self.assertAlmostEqual(row['wallMountBack'],-min(v[0] for v in self.v));self.assertFalse(row.get('additiveFlame',False))
  self.assertEqual(row['clips'],[c[0] for c in m.CLIPS])
  # Nothing is emissive: no material shader, light or render style for this skin.
  self.assertNotIn('BRGDTUR',(m.ROOT/'mod/BrogueDoom/GLDEFS').read_text())
  zs=(m.ROOT/'mod/BrogueDoom/brogue_monsters.zs').read_text();block=zs.split('class BrogueMonsterK38 : BrogueMonsterProxyBase')[1].split('class ')[0]
  self.assertNotIn('RenderStyle',block);self.assertIn('"idle"',block)
  header=(m.ROOT/'src/gzdoom-bridge/skeletal_presentation.generated.h').read_text()
  self.assertIn('{"BrogueMonsterK38", {"idle", "rest", "loose", "snap", "jar", "jam"}, {0, 0, 24, 28, 14, 36}, 20, "", "", "", 0, 10},',header)
  for legacy in ('mod/BrogueDoom/models/monsters/38_dart_turret.obj','mod/BrogueDoom/graphics/BRGM38.png','assets/monsters/sources/38_dart_turret.blend'):
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
