"""Prepare isolated rat clip review and a normal seed-one encounter capture.

Generated harnesses live only under ignored artifacts/rat-animation.
"""
import json
import shutil
from .rat_animation import ROOT, CLIPS
from tools.packaging.package_release import zip_tree
from tools.mapcompiler.compile import make_wad

OUT=ROOT/'artifacts/rat-animation'


def cfg(phase,shots,wait,first=118,extra=()):
    folder=OUT/phase; folder.mkdir(parents=True,exist_ok=True)
    lines=['vid_renderer 1','vid_fullscreen false','vid_vsync false','vid_maxfps 60',
           'gl_texture_filter 4','gl_lightmode 4','screenblocks 12','fov 70','con_notifytime 0',
           'i_pauseinbackground false','ucm_hide true','ucm_drawmap false',*extra]
    for i in range(shots):
        next_command=f'rat_capture_{i+1:02d}' if i<shots-1 else 'quit'
        body=f'screenshot "{(folder/f"{i:02d}.png").as_posix()}"; wait {wait}; {next_command}'
        lines.append(f'alias rat_capture_{i:02d} "'+body.replace('"','\\"')+'"')
    lines.append(f'wait {first}; rat_capture_00')
    (OUT/f'{phase}.cfg').write_text('\n'.join(lines)+'\n')


def prepare():
    OUT.mkdir(parents=True,exist_ok=True)
    gallery=OUT/'gallery'; (gallery/'maps').mkdir(parents=True,exist_ok=True)
    text='namespace="ZDoom";\n'
    for x,y in ((-128,-128),(-128,128),(128,128),(128,-128)): text+=f'vertex {{ x={x}; y={y}; }}\n'
    text+='sector { heightfloor=0; heightceiling=160; texturefloor="BRGDIRT"; textureceiling="BRGROCK"; lightlevel=208; }\n'
    for n in range(4):
        text+=f'sidedef {{ sector=0; texturemiddle="BRGROCK"; }}\nlinedef {{ v1={n}; v2={(n+1)%4}; sidefront={n}; blocking=true; }}\n'
    text+='thing { x=64; y=-64; type=1; angle=135; skill1=true; skill2=true; skill3=true; skill4=true; skill5=true; single=true; }\n'
    (gallery/'maps/ART01.wad').write_bytes(make_wad('ART01',text))
    camera='''class RatReviewCamera : Actor {
 Default { +NOINTERACTION; +NOBLOCKMAP; +NOGRAVITY; RenderStyle "None"; CameraHeight 0; }
 States { Spawn: TNT1 A -1; Stop; }
}
'''
    shots=[]
    for name,count,fps,loop in CLIPS:
        for f in (0,count//2,count-1): shots.append({'clip':name,'frame':f,'camera':(48,-64,32)})
    for loc in ((64,0,22),(0,64,24),(-64,0,24),(0,-64,24)):
        shots.append({'clip':'idle','frame':0,'camera':loc})
    body=''
    for i,shot in enumerate(shots):
        x,y,z=shot['camera']
        body+=f'''if(index=={i}) {{
 subject.SetAnimation("{shot['clip']}",0,{shot['frame']},-1,-1,1,SAF_INSTANT);
 camera.SetOrigin(({x},{y},{z}),false);
 camera.angle=VectorAngle({-x},{-y}); camera.pitch=atan2({z}-7,{(x*x+y*y)**.5});
 Console.Printf("RAT_GALLERY shot={i:02d} clip={shot['clip']} frame={shot['frame']}");
 }}\n'''
    script='version "4.14"\n'+camera+'''class RatClipReview : EventHandler {
 Actor subject; Actor camera; int counter;
 override void WorldTick() {
  counter++;
  if(counter<100) return;
  if(!subject) { subject=Actor.Spawn("BrogueMonsterK01",(0,0,0)); subject.angle=0; }
  if(!camera) camera=Actor.Spawn("RatReviewCamera",(48,-64,32));
  players[consoleplayer].camera=camera;
  if(players[consoleplayer].mo) players[consoleplayer].mo.bINVISIBLE=true;
  if((counter-100)%20) return;
  int index=(counter-100)/20;
'''+body+'}\n}\n'
    (gallery/'ZSCRIPT').write_text(script)
    (gallery/'MAPINFO').write_text('GameInfo { AddEventHandlers="RatClipReview" }\nmap ART01 "Rat animation review - not a Brogue level" {}\n')
    before=OUT/'before'; before.mkdir(exist_ok=True)
    shutil.copytree(gallery/'maps',before/'maps',dirs_exist_ok=True)
    (before/'ZSCRIPT').write_text('\n'.join(line for line in script.splitlines() if 'subject.SetAnimation(' not in line)+'\n')
    shutil.copyfile(gallery/'MAPINFO',before/'MAPINFO')
    cfg('gallery',len(shots),20)
    cfg('before',len(shots),20)
    (OUT/'gallery-shots.json').write_text(json.dumps(shots,indent=2)+'\n')
    normal=OUT/'normal'; normal.mkdir(exist_ok=True)
    (normal/'ZSCRIPT').write_text('version "4.14"\n'+camera+'''class RatEncounterReview : EventHandler {
 Actor camera;
 override void WorldTick() {
  if(level.time<250) return;
  let pawn=players[consoleplayer].mo;
  if(!pawn) return;
  let it=ThinkerIterator.Create("BrogueMonsterK01"); Actor candidate; Actor subject; double best=100000;
  while(candidate=Actor(it.Next())) {
   double d=(candidate.pos-pawn.pos).Length();
   if(candidate.alpha>0 && d<best) { best=d; subject=candidate; }
  }
  if(!subject) return;
  pawn.bINVISIBLE=true;
  vector3 eye=(pawn.pos.x,pawn.pos.y,players[consoleplayer].viewz);
  if(!camera) camera=Actor.Spawn("RatReviewCamera",eye);
  camera.SetOrigin(eye,false);
  vector3 delta=subject.pos+(0,0,7)-eye;
  camera.angle=VectorAngle(delta.x,delta.y);
  camera.pitch=atan2(-delta.z,sqrt(delta.x*delta.x+delta.y*delta.y));
  players[consoleplayer].camera=camera;
 }
}
''')
    (normal/'MAPINFO').write_text('GameInfo { AddEventHandlers="RatEncounterReview" }\n')
    route=' '.join(['N']*3+['W']*25+['N'])
    cfg('normal',55,2,1000,['brg_seed 1','brg_debug true','brg_monster_omniscience false',
                          'brg_monster_anim_tics 5','brg_rat_walk_tics 28','brg_actions '+route])
    # Include the final approach step, so captures show translation and gait
    # together before the unchanged real wait/attack sequence.
    path=OUT/'normal.cfg'; text=path.read_text()
    text=text.replace('wait 1000; rat_capture_00','wait 1000; brg_monsters; brg_actions W WAIT WAIT W W W W; rat_capture_00')
    path.write_text(text)
    zip_tree(ROOT/'mod/BrogueDoom',OUT/'ProjectBroom-rat-animated.pk3')
    print('Prepared rat review harnesses and package:',OUT)


def sheets():
    from PIL import Image, ImageDraw, ImageFont
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
    for phase in ('gallery','before','normal'):
        paths=sorted((OUT/phase).glob('*.png'))
        for start in range(0,len(paths),12):
            sheet=Image.new('RGB',(1200,1020),(24,29,34)); draw=ImageDraw.Draw(sheet)
            for i,path in enumerate(paths[start:start+12]):
                x=(i%4)*300; y=(i//4)*340
                with Image.open(path) as src:
                    side=min(src.size); left=(src.width-side)//2
                    src=src.crop((left,0,left+side,side)); src.thumbnail((300,300))
                    sheet.paste(src,(x,y))
                label=path.stem
                if phase in ('gallery','before'):
                    entry=json.loads((OUT/'gallery-shots.json').read_text())[int(path.stem)]
                    label+=f" {entry['clip']} f{entry['frame']}"
                draw.text((x+6,y+309),label,fill=(235,226,206),font=font)
            sheet.save(OUT/f'{phase}-sheet-{start//12+1}.png')


if __name__=='__main__':
    import sys
    sheets() if '--sheets' in sys.argv else prepare()
