import subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class EnemyMovementTests(unittest.TestCase):
 def test_view_timing_and_progress(self):
  with tempfile.TemporaryDirectory() as folder:
   exe=Path(folder)/'movement.exe'
   subprocess.run(['g++','-std=c++17','-static',str(ROOT/'tools/enemy_movement_test.cpp'),'-o',str(exe)],check=True,capture_output=True)
   subprocess.run([str(exe)],check=True)
 def test_same_timers_drive_input_and_indicator(self):
  s=(ROOT/'src/gzdoom-bridge/brogue_bridge_frontend.cpp').read_text()
  hud=s.split('void DrawEnemyMovementProgress()')[1].split('void BrogueBridge_DrawHud')[0]
  for name in ('moveTics','moveTotal','pulseTics','deathTics'):self.assertIn(name,hud)
  self.assertNotIn('ratPoseTics',hud)
  self.assertIn('proxy.moveTics = proxy.pulseTics = proxy.deathTics = 0;',s)
  movement=s.split('const bool observed =')[1].split('proxy.kind = creature.kind;')[0]
  self.assertIn('proxy.actor->SetOrigin(proxy.moveTo, false)',movement)
  self.assertIn('brg_enemy_walk_tics',movement)
  for f in ('Api.','Random','PerformCommand'):self.assertNotIn(f,movement)
