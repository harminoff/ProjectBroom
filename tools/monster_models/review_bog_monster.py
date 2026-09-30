"""Synthetic bog-monster mud fixture; never a natural encounter or visibility proof."""
import argparse
import json
import os
import subprocess
import zipfile
from .rat import ROOT
from tools.mapcompiler.compile import make_wad


def main():
    p=argparse.ArgumentParser();p.add_argument('--backend', choices=('0','1'),required=True)
    p.add_argument('--package',type=__import__('pathlib').Path,required=True);p.add_argument('--output',type=__import__('pathlib').Path,required=True)
    a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
    # Match the canonical opaque, non-solid liquid 3D-floor construction.
    text='namespace="ZDoom";\n'
    for x,y in ((-256,-256),(-256,256),(256,256),(256,-256),(512,0),(512,8),(520,8),(520,0)):
        text+=f'vertex {{x={x};y={y};}}\n'
    text+='sector {id=10000;heightfloor=-4;heightceiling=160;texturefloor="BRGDIRT";textureceiling="BRGROCK";lightlevel=176;}\n'
    text+='sector {heightfloor=-1;heightceiling=0;texturefloor="BRGSLDG";textureceiling="BRGSLDG";lightlevel=176;}\n'
    for i in range(8):
        special='special=160;arg0=10000;arg1=3;arg2=2049;arg3=255;' if i==4 else ''
        text+=f'sidedef {{sector={i//4};texturemiddle="BRGROCK";}}\nlinedef {{v1={i};v2={i//4*4+(i+1)%4};sidefront={i};blocking=true;{special}}}\n'
    text+='thing {x=64;y=-64;type=1;angle=135;skill1=true;skill2=true;skill3=true;skill4=true;skill5=true;single=true;}\n'
    fixture=out/'water.pk3'
    zscript='''version "5.0"
class BogMudCamera : Actor { Default { +NOINTERACTION; +NOBLOCKMAP; +NOGRAVITY; RenderStyle "None"; CameraHeight 0; } States { Spawn: TNT1 A -1; Stop; } }
class BogMudReview : EventHandler {
 Actor subject; Actor camera; int counter;
 override void WorldTick() {
 counter++; if(counter<100) return;
 if(!camera) { camera=Actor.Spawn("BogMudCamera",(0,64,41)); }
 players[consoleplayer].camera=camera;
 if(players[consoleplayer].mo) players[consoleplayer].mo.bINVISIBLE=true;
 int stage=(counter-100)/35;int tick=(counter-100)%35;
 if(stage>5) return;
 if(tick==0) {
 if(subject) subject.Destroy();
 subject=Actor.Spawn("BrogueMonsterK19",(0,0,-4));
 subject.angle=0;
 double distance=stage==1 ? 128 : stage==2 ? 192 : 64;
 camera.SetOrigin((0,distance,41),false);camera.angle=270;camera.pitch=atan2(41,distance);
 if(stage==3) {subject.bINVISIBLE=true;subject.Alpha=0;}
 if(stage==4) {subject.A_SetRenderStyle(.38,STYLE_Translucent);}
 if(stage==5) {subject.SetOrigin((0,0,-4),false);camera.SetOrigin((64,0,41),false);camera.angle=180;camera.pitch=atan2(27,64);}
 Console.Printf("BOG_MUD stage=%d z=%.2f alpha=%.2f hidden=%d blocking=%d",stage,subject.pos.z,subject.Alpha,subject.bINVISIBLE,subject.bSOLID);
 }
 if(tick==2) subject.SetAnimation(stage==5 ? "coil" : "idle",0,8,-1,-1,0,SAF_INSTANT);
 }
}
'''
    with zipfile.ZipFile(fixture,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('maps/ART01.wad',make_wad('ART01',text));z.writestr('ZSCRIPT',zscript)
        z.writestr('MAPINFO','GameInfo { AddEventHandlers="BogMudReview" }\nmap ART01 "Synthetic bog mud review" {}\n')
    package=a.package.resolve()
    with zipfile.ZipFile(package) as z:
        for path in ('models/monsters/19_bog_monster.iqm','graphics/BRGBOG.png','models/monsters/MODELDEF.txt','brogue_monsters.zs'):
            assert z.read(path)==(ROOT/'mod/BrogueDoom'/path).read_bytes()
    names=['one-cell','two-cells','three-cells','hidden','sensed','coil']
    commands=['vid_setsize 1920 1080','screenblocks 12','con_notifytime 0','wait 112']
    for name in names:commands+=['screenshot '+name+'.png','wait 35']
    commands+=['quit'];(out/'capture.cfg').write_text('; '.join(commands)+'\n')
    cmd=[str(ROOT/'.build/uzdoom/Release/uzdoom.exe'),'-iwad',str(ROOT/'.deps/freedoom-0.13.0/freedoom2.wad'),'-file',str(package),str(fixture),'-config',str(out/'test.ini'),'-noautoload','-nosound','-window','-width','1920','-height','1080','+set','vid_fullscreen','false','+set','vid_preferbackend',a.backend,'+set','i_pauseinbackground','false','+set','screenshot_dir',str(out),'+map','ART01','+exec',str(out/'capture.cfg')]
    env={k.upper():v for k,v in os.environ.items()}
    with (out/'runtime.log').open('w') as log:
        result=subprocess.run(cmd,cwd=out,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=60)
    log=(out/'runtime.log').read_text(errors='replace')
    assert result.returncode==0 and log.count('blocking=0')==6,log[-2500:]
    assert all((out/(name+'.png')).exists() for name in names)
    (out/'verification.json').write_text(json.dumps(dict(backend=a.backend,captures=names,packagedAssetsMatch=True,scope='renderer fixture, not native Brogue state transitions'),indent=2))
    print('Synthetic bog mud review passed:',out)


if __name__=='__main__':main()
