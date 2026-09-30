"""Electrical mechanism attachment, export, and knowledge-limited wall projection."""
import math,json,subprocess,tempfile,unittest
from pathlib import Path
from . import spark_turret_animation as m,spark_turret_materials as mat,iqm
from .rat import cross,sub

class SparkTurretTests(unittest.TestCase):
 @classmethod
 def setUpClass(c):
  c.parts,c.v,c.n,c.uv,c.tri,c.w=m.geometry();c.clips,c.bounds=m.animation_data(c.v,c.w)
 def test_mechanical_signature(self):
  names={p.name for p in self.parts}
  for n in ('octagonal_wall_plaque','concentric_sigil_ring_0','large_focusing_crystal','curved_electrode_prong_L','upper_electrode','copper_feed_0'):self.assertIn(n,names)
  self.assertEqual(sum(n.startswith('angular_sigil_') for n in names),12)
  self.assertEqual(sum(n.startswith('embedded_capacitor_crystal_') for n in names),4)
  self.assertEqual(sum(n.startswith('copper_winding_') for n in names),4)
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
 def test_action_recovery_unit_scale_rigid_parts_and_broken_core(self):
  for name in ('discharge','recharge','impact'):
   for a,b in zip(m.pose(name,0),m.pose(name,1)):
    self.assertLess(math.dist(a,b),1e-10)
  for c in self.clips:
   for f in c['frames']:
    for row in f:
     self.assertEqual(row[7:],(1,1,1));self.assertAlmostEqual(sum(a*a for a in row[3:7]),1)
  for p in self.parts:self.assertEqual(len({tuple(w) for w in p.skin_weights}),1,p.name)
  dead=m.deform(self.v,self.w,m.pose('break',1));rest=m.deform(self.v,self.w,m.pose('idle',0))
  ids=[i for i,w in enumerate(self.w) if w==[(m.IDS['core'],1)]]
  self.assertLess(min(dead[i][2] for i in ids),min(rest[i][2] for i in ids)-10)
 def test_mesh_and_animated_envelope(self):
  def area(v,t):
   a,b,c=(v[i] for i in t);return math.sqrt(sum(x*x for x in cross(sub(b,a),sub(c,a))))
  self.assertGreater(min(area(self.v,t) for t in self.tri),1e-6)
  for c in self.clips:
   for f in c['frames']:
    v=m.deform(self.v,self.w,f)
    self.assertGreater(min(area(v,t) for t in self.tri),1e-6)
    self.assertGreaterEqual(min(x[2] for x in v),3.4)
    self.assertTrue(all(abs(x[0])<32 and abs(x[1])<32 for x in v))
 def test_runtime_original_texture_and_profile(self):
  self.assertEqual(iqm.encode(self.v,self.n,self.uv,self.tri,self.w,m.BONES,self.clips,self.bounds,mesh_label='Project_Broom_spark_turret',material_path=m.SKIN),(m.ROOT/'mod/BrogueDoom/models/monsters/22_spark_turret.iqm').read_bytes())
  self.assertEqual(mat.texture_bytes(),(m.ROOT/'mod/BrogueDoom'/m.SKIN).read_bytes())
  row=next(r for r in json.loads((m.ROOT/'assets/monsters/skeletal_profiles.json').read_text())['enemies'] if r['symbol']=='MK_SPARK_TURRET')
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
