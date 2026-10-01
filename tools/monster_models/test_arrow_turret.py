"""Arrow mechanism attachment, export, and knowledge-limited wall projection."""
import math,json,subprocess,tempfile,unittest
from pathlib import Path
from . import arrow_turret_animation as m,arrow_turret_materials as mat,iqm
from .rat import cross,sub

class ArrowTurretTests(unittest.TestCase):
 @classmethod
 def setUpClass(c):
  c.parts,c.v,c.n,c.uv,c.tri,c.w=m.geometry();c.clips,c.bounds=m.animation_data(c.v,c.w)
 def test_mechanical_signature(self):
  names={p.name for p in self.parts}
  for n in ('iron_mount_plate','oak_mount_plank_0','laminated_bow_L0','wound_spring_R','sliding_string_carriage','loaded_arrow_shaft','forged_arrowhead','front_iron_stirrup','trigger_sear','spare_bolt_rack'):self.assertIn(n,names)
  self.assertEqual(sum(n.startswith('ratchet_tooth') for n in names),24)
  self.assertEqual(sum(n.startswith('feather_vane') for n in names),3)
  self.assertEqual(sum(n.startswith('spare_bolt_') and not n.startswith(('spare_bolt_head','spare_bolt_rack')) for n in names),4)
 def test_mount_and_support_fixed_in_every_pose(self):
  fixed=[i for i,w in enumerate(self.w) if w==[(0,1)]]
  self.assertGreater(len(fixed),500)
  for c in self.clips:
   for f in c['frames']:
    v=m.deform(self.v,self.w,f)
    self.assertLess(max(math.dist(v[i],self.v[i]) for i in fixed),1e-10)
    self.assertEqual(f[0],m.pose('rest',0)[0])
 def test_unused_move_and_idle_are_rest(self):
  for c in self.clips[:2]:
   for f in c['frames']:self.assertEqual(f,m.pose('rest',0))
 def test_action_recovery_unit_scale_and_string_continuity(self):
  for name in ('release','rearm','recoil'):
   for a,b in zip(m.pose(name,0),m.pose(name,1)):
    self.assertLess(math.dist(a,b),1e-10)
  for c in self.clips:
   for f in c['frames']:
    for row in f:
     self.assertEqual(row[7:],(1,1,1));self.assertAlmostEqual(sum(a*a for a in row[3:7]),1)
  for p in self.parts:
   if p.name.startswith('bowstring'):
    self.assertTrue(all(abs(sum(x for _,x in w)-1)<1e-9 for w in p.skin_weights))
   else:self.assertEqual(len({tuple(w) for w in p.skin_weights}),1,p.name)
 def test_mesh_and_animated_envelope(self):
  def area(v,t):
   a,b,c=(v[i] for i in t);return math.sqrt(sum(x*x for x in cross(sub(b,a),sub(c,a))))
  self.assertGreater(min(area(self.v,t) for t in self.tri),1e-6)
  for c in self.clips:
   for f in c['frames']:
    v=m.deform(self.v,self.w,f)
    self.assertGreater(min(area(v,t) for t in self.tri),1e-6)
    self.assertGreaterEqual(min(x[2] for x in v),.11999)
    self.assertTrue(all(abs(x[0])<32 and abs(x[1])<32 for x in v))
 def test_runtime_original_texture_and_profile(self):
  self.assertEqual(iqm.encode(self.v,self.n,self.uv,self.tri,self.w,m.BONES,self.clips,self.bounds,mesh_label='Project_Broom_arrow_turret',material_path=m.SKIN),(m.ROOT/'mod/BrogueDoom/models/monsters/15_arrow_turret.iqm').read_bytes())
  self.assertEqual(mat.texture_bytes(),(m.ROOT/'mod/BrogueDoom'/m.SKIN).read_bytes())
  row=next(r for r in json.loads((m.ROOT/'assets/monsters/skeletal_profiles.json').read_text())['enemies'] if r['symbol']=='MK_ARROW_TURRET')
  self.assertAlmostEqual(row['wallMountBack'],-min(v[0] for v in self.v))
 def test_wall_mount_cardinal_knowledge_and_retention(self):
  source='''#include "wall_mount.h"
#include <cassert>
int main(){bool faces[4]={true,true,true,true};
assert(WallMount::Face(false,true,faces,0,-2,0)==-1);
assert(WallMount::Face(true,false,faces,0,-2,0)==-1);
// Approach a thin wall from both sides: previous opposite face must lose.
assert(WallMount::Face(true,true,faces,0,3,0)==1);
assert(WallMount::Face(true,true,faces,1,-3,0)==0);
assert(WallMount::Face(true,true,faces,0,0,-3)==2);
assert(WallMount::Face(true,true,faces,2,0,3)==3);
// Corner tie retains attachment; deterministic first face without history.
assert(WallMount::Face(true,true,faces,2,-3,-3)==2);
assert(WallMount::Face(true,true,faces,-1,-3,-3)==0);
for(int i=0;i<4;i++)faces[i]=false;
assert(WallMount::Face(true,true,faces,2,3,0)==-1);
for(int i=0;i<4;i++){faces[i]=true;assert(WallMount::Face(true,true,faces,-1,0,0)==i);faces[i]=false;}
faces[1]=true;assert(WallMount::Face(true,true,faces,0,3,0)==1);
}'''
  with tempfile.TemporaryDirectory() as td:
   p=Path(td);(p/'test.cpp').write_text(source)
   subprocess.run(['g++','-std=c++17','-static','-I'+str(m.ROOT/'src/gzdoom-bridge'),str(p/'test.cpp'),'-o',str(p/'test.exe')],check=True,capture_output=True)
   subprocess.run([str(p/'test.exe')],check=True)
 def test_projection_reads_copied_appearance_and_guards_attack_yaw(self):
  s=(m.ROOT/'src/gzdoom-bridge/brogue_bridge_frontend.cpp').read_text()
  block=s.split('double MonsterWallMountBack(')[1].split('AActor *SpawnMonsterProxy')[0]
  for forbidden in ('terrainFlags','->isSolid','Api.','PerformAction','Random','P_DamageMobj'):self.assertNotIn(forbidden,block)
  for needed in ('presentationKind','BROGUE_TERRAIN_UNKNOWN','BROGUE_APPEARANCE_WALL','BROGUE_APPEARANCE_OPAQUE','BROGUE_VISIBILITY_DIRECT'):self.assertIn(needed,block)
  self.assertIn('proxy.wallMountFace < 0 && (dx != 0 || dy != 0)',s)

if __name__=='__main__':unittest.main()
