"""Isolated pillar fixture: native selector on opposite sides/corners, no Brogue session."""
import argparse,json,os,subprocess,time
from pathlib import Path
from .rat import ROOT
from tools.mapcompiler.compile import make_wad

def main():
 p=argparse.ArgumentParser();p.add_argument('--backend',choices=('0','1'),required=True);p.add_argument('--package',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 out=a.output.resolve();out.mkdir(parents=True,exist_ok=True);fixture=out/'fixture';(fixture/'maps').mkdir(parents=True,exist_ok=True)
 # The exact same C++ selection helper supplies test transforms; no Python clone.
 cpp=out/'selector.cpp';cpp.write_text('''#include "wall_mount.h"
#include <cstdio>
int main(){bool faces[4]={true,true,true,true};int previous=-1;
int xy[6][2]={{-3,0},{3,0},{0,-3},{0,3},{3,-3},{-3,3}};
for(auto &p:xy){int f=WallMount::Face(true,true,faces,previous,p[0],p[1]);
std::printf("%d %d %d %.1f\\n",p[0],p[1],f,WallMount::YAW[f]);previous=f;}}''')
 exe=out/'selector.exe';subprocess.run(['g++','-std=c++17','-static','-I'+str(ROOT/'src/gzdoom-bridge'),str(cpp),'-o',str(exe)],check=True,capture_output=True)
 rows=[line.split() for line in subprocess.check_output([str(exe)],text=True).splitlines()];stages=[];dx=(-1,1,0,0);dy=(0,0,-1,1)
 for px,py,face,yaw in rows:
  face=int(face)
  for clip,frame in [('idle',0),('discharge',11),('break',31)]:stages.append(dict(player=[int(px),int(py)],face=face,yaw=float(yaw),position=[dx[face]*44.3,-dy[face]*44.3,0],clip=clip,frame=frame))
 (out/'selector-transforms.json').write_text(json.dumps(stages,indent=2))
 text='namespace="ZDoom";\n'
 for x,y in ((-256,-256),(-256,256),(256,256),(256,-256),(-32,-32),(32,-32),(32,32),(-32,32)):text+=f'vertex {{ x={x}; y={y}; }}\n'
 text+='sector { heightfloor=0; heightceiling=160; texturefloor="BRGDIRT"; textureceiling="BRGROCK"; lightlevel=208; }\n'
 for i in range(8):text+=f'sidedef {{ sector=0; texturemiddle="BRGROCK"; }}\nlinedef {{ v1={i}; v2={((i+1)%4 if i<4 else 4+(i-3)%4)}; sidefront={i}; blocking=true; }}\n'
 text+='thing { x=120; y=120; type=1; angle=225; skill1=true; skill2=true; skill3=true; skill4=true; skill5=true; single=true; }\n'
 (fixture/'maps/ART02.wad').write_bytes(make_wad('ART02',text));(fixture/'MAPINFO').write_text('GameInfo { AddEventHandlers="WallMountReview" }\nmap ART02 "Isolated wall mount presentation" {}\n')
 switches=[]
 for i,r in enumerate(stages):
  x,y,z=r['position'];cx=r['player'][0]*48;cy=-r['player'][1]*48
  switches.append(f'case {i}: subject.SetOrigin(({x},{y},0),false);subject.angle={r["yaw"]};camera.SetOrigin(({cx},{cy},41),false); subject.SetAnimation("{r["clip"]}",0,{r["frame"]},-1,-1,0,SAF_INSTANT); break;')
 (fixture/'ZSCRIPT').write_text('''version "5.0"
class WallMountCamera:Actor {Default{+NOINTERACTION;+NOBLOCKMAP;+NOGRAVITY;RenderStyle "None";CameraHeight 0;} States{Spawn:TNT1 A -1;Stop;}}
class WallMountReview:EventHandler {
Actor subject;Actor camera;int counter;
override void WorldTick(){counter++;if(counter<100)return;
if(!camera)camera=Actor.Spawn("WallMountCamera",(140,0,41));
players[consoleplayer].camera=camera;players[consoleplayer].mo.bINVISIBLE=true;
int stage=(counter-100)/20;if(stage>=18)return;
if((counter-100)%20==0){if(subject)subject.Destroy();subject=Actor.Spawn("BrogueMonsterK22",(0,0,0));
switch(stage){SWITCHES}
vector3 d=subject.pos+(0,0,25)-camera.pos;camera.angle=VectorAngle(d.x,d.y);camera.pitch=atan2(-d.z,sqrt(d.x*d.x+d.y*d.y));
Console.Printf("WALL_MOUNT_FIXTURE stage=%d angle=%.1f blocking=%d",stage,subject.angle,subject.bSOLID);
}
// Apply the sampled clip after the actor initial Spawn action has run.
if((counter-100)%20==2){switch(stage){SWITCHES}}
}
}'''.replace('SWITCHES','\n'.join(switches)))
 cfg=['vid_setsize 1920 1080','wait 112']
 for i,r in enumerate(stages):cfg+=['screenshot %02d-%s.png'%(i,r['clip']),'wait 20']
 cfg+=['quit'];(out/'capture.cfg').write_text('; '.join(cfg)+'\n')
 cmd=[str(ROOT/'.build/uzdoom/Release/uzdoom.exe'),'-iwad',str(ROOT/'.deps/freedoom-0.13.0/freedoom2.wad'),'-file',str(a.package.resolve()),str(fixture),'-config',str(out/'test.ini'),'-noautoload','-nosound','-window','-width','1920','-height','1080','+set','vid_fullscreen','false','+set','vid_preferbackend',a.backend,'+set','i_pauseinbackground','false','+set','screenshot_dir',str(out),'+set','con_notifytime','0','+set','screenblocks','12','+map','ART02','+exec',str(out/'capture.cfg')]
 with (out/'runtime.log').open('w') as log:
  proc=subprocess.Popen(cmd,cwd=out,stdout=log,stderr=subprocess.STDOUT)
  try:proc.wait(timeout=60)
  except subprocess.TimeoutExpired:proc.kill();proc.wait();raise
 text=(out/'runtime.log').read_text(errors='replace');assert proc.returncode==0 and text.count('blocking=0')==18,text[-3000:]
 assert len(list(out.glob('*.png')))==18
 print('Wall mount opposite-side/corner fixture passed:',out)
if __name__=='__main__':main()
