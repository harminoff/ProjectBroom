"""Isolated before/after GZDoom gallery, with explicit shot selection."""
import json
import shutil
from tools.pickup_models.generate import ROOT, REGISTRY_PATH
from tools.packaging.package_release import zip_tree
from tools.mapcompiler.compile import make_wad

OUT=ROOT/'artifacts/pickup-models'


def prepare():
    models=json.loads(REGISTRY_PATH.read_text())['models']
    addon=OUT/'gallery';(addon/'maps').mkdir(parents=True,exist_ok=True)
    text='namespace="ZDoom";\n'
    for x,y in ((-96,-96),(-96,96),(96,96),(96,-96)): text+=f'vertex {{ x={x}; y={y}; }}\n'
    text+='sector { heightfloor=0; heightceiling=160; texturefloor="BRGDIRT"; textureceiling="BRGROCK"; lightlevel=208; }\n'
    for n in range(4):
        text+=f'sidedef {{ sector=0; texturemiddle="BRGROCK"; }}\nlinedef {{ v1={n}; v2={(n+1)%4}; sidefront={n}; blocking=true; }}\n'
    text+='thing { x=64; y=-64; type=1; angle=135; skill1=true; skill2=true; skill3=true; skill4=true; skill5=true; single=true; }\n'
    (addon/'maps/ART01.wad').write_bytes(make_wad('ART01',text))
    (addon/'MAPINFO').write_text('GameInfo { AddEventHandlers="PickupArtReview" }\nmap ART01 "Pickup art gallery - not a Brogue level" { levelnum=99 }\n')
    (addon/'CVARINFO').write_text('server noarchive int brg_pickup_review_index = -1;\n')
    cases='\n'.join(f'if(index=={i}) type="{m["class"]}";' for i,m in enumerate(models))
    (addon/'ZSCRIPT').write_text('''version "4.14"
class PickupArtCamera : Actor {
 Default { +NOINTERACTION; +NOBLOCKMAP; +NOGRAVITY; RenderStyle "None"; CameraHeight 0; }
 States { Spawn: TNT1 A -1; Stop; }
}
class PickupArtReview : EventHandler {
 Actor subject; Actor camera; int previous;
 override void WorldLoaded(WorldEvent e) { previous=-2; }
 override void WorldTick() {
  int index=CVar.GetCVar("brg_pickup_review_index").GetInt();
  if(index<0) return;
  if(!camera) camera=Actor.Spawn("PickupArtCamera",(28,-39,35));
  camera.angle=VectorAngle(-28,39);camera.pitch=atan2(32,sqrt(28*28+39*39));
  players[consoleplayer].camera=camera;
  if(players[consoleplayer].mo) players[consoleplayer].mo.bINVISIBLE=true;
  if(index==previous) return;previous=index;
  if(subject) subject.Destroy();
  Class<Actor> type;
'''+cases+'''
  if(type) subject=Actor.Spawn(type,(0,0,0));
  if(subject) { subject.angle=0; Console.Printf("PICKUP_GALLERY index=%d class=%s",index,subject.GetClassName()); }
  else Console.Printf("PICKUP_GALLERY MISSING index=%d",index);
 }
}
''')
    for phase in ('before','after'):
        folder=OUT/phase;folder.mkdir(exist_ok=True)
        lines=['vid_renderer 1','vid_fullscreen false','vid_vsync false','vid_maxfps 60','gl_texture_filter 4',
               'gl_lightmode 4','screenblocks 12','fov 70','con_notifytime 0','i_pauseinbackground false',
               'ucm_hide true','ucm_drawmap false']
        for i in range(len(models)):
            next_command=f'pickup_show_{i+1:03d}' if i<len(models)-1 else 'quit'
            lines.append(f'alias pickup_show_{i:03d} "brg_pickup_review_index {i}; wait 8; pickup_shot_{i:03d}"')
            body=f'screenshot "{(folder/f"{i:03d}.png").as_posix()}"; wait 2; {next_command}'
            lines.append(f'alias pickup_shot_{i:03d} "'+body.replace('"','\\"')+'"')
        lines.append('wait 118; pickup_show_000')
        (OUT/f'{phase}.cfg').write_text('\n'.join(lines)+'\n')
    override=OUT/'before-override';(override/'models').mkdir(parents=True,exist_ok=True)
    shutil.copytree(OUT/'baseline/pickups',override/'models/pickups',dirs_exist_ok=True)
    (override/'graphics').mkdir(exist_ok=True)
    shutil.copyfile(OUT/'baseline/BRGITEMS.png',override/'graphics/BRGITEMS.png')
    zip_tree(ROOT/'mod/BrogueDoom',OUT/'ProjectBroom-pickups.pk3')
    normal=OUT/'normal';normal.mkdir(exist_ok=True)
    (normal/'MAPINFO').write_text('GameInfo { AddEventHandlers="PickupFloorReview" }\n')
    (normal/'ZSCRIPT').write_text('''version "4.14"
class PickupFloorCamera : Actor {
 Default { +NOINTERACTION; +NOBLOCKMAP; +NOGRAVITY; RenderStyle "None"; CameraHeight 0; }
 States { Spawn: TNT1 A -1; Stop; }
}
class PickupFloorReview : EventHandler {
 Actor camera;
 override void WorldTick() {
  let pawn=players[consoleplayer].mo;if(!pawn) return;
  let it=ThinkerIterator.Create("BroguePickupProxyBase");Actor candidate;Actor subject;double best=100000;
  while(candidate=Actor(it.Next())) {
   double distance=(candidate.pos-pawn.pos).Length();
   if(!candidate.bINVISIBLE && distance<best) { best=distance;subject=candidate; }
  }
  if(!subject) { players[consoleplayer].camera=pawn;return; }
  pawn.bINVISIBLE=true;
  vector3 eye=(pawn.pos.x,pawn.pos.y,players[consoleplayer].viewz);
  if(!camera) camera=Actor.Spawn("PickupFloorCamera",eye);
  camera.SetOrigin(eye,false);vector3 delta=subject.pos+(0,0,3)-eye;
  camera.angle=VectorAngle(delta.x,delta.y);camera.pitch=atan2(-delta.z,sqrt(delta.x*delta.x+delta.y*delta.y));
  players[consoleplayer].camera=camera;
 }
}
''')
    route=' '.join(['E']*8)
    for phase in ('normal-before','normal-after'):
        (OUT/phase).mkdir(exist_ok=True)
        lines=['vid_renderer 1','vid_fullscreen false','vid_vsync false','vid_maxfps 60',
               'gl_texture_filter 4','screenblocks 12','fov 70','con_notifytime 0','i_pauseinbackground false',
               'brg_seed 1','brg_debug true','brg_rat_walk_tics 28','brg_monster_anim_tics 5',
               'brg_monster_omniscience false','ucm_hide true','ucm_drawmap false']
        def alias(name,body): lines.append(f'alias {name} "'+body.replace('"','\\"')+'"')
        alias('pickup_floor_start',f'brg_pickups; screenshot "{(OUT/phase/"start.png").as_posix()}"; brg_actions E; wait 100; pickup_floor_end')
        alias('pickup_floor_end',f'brg_pickups; screenshot "{(OUT/phase/"end.png").as_posix()}"; wait 5; quit')
        lines.extend(['brg_actions '+route,'wait 350; pickup_floor_start'])
        (OUT/f'{phase}.cfg').write_text('\n'.join(lines)+'\n')
    print('Prepared 105-model gallery and package')


def sheets():
    from PIL import Image, ImageDraw, ImageFont
    models=json.loads(REGISTRY_PATH.read_text())['models'];font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
    for phase in ('before','after','studio'):
        entries=[(i,m,OUT/phase/(f'{m["class"]}.png' if phase=='studio' else f'{i:03d}.png')) for i,m in enumerate(models)]
        entries=[r for r in entries if r[2].exists()]
        for start in range(0,len(entries),12):
            sheet=Image.new('RGB',(1200,1020),(24,29,34));draw=ImageDraw.Draw(sheet)
            for n,(i,m,path) in enumerate(entries[start:start+12]):
                x=n%4*300;y=n//4*340
                with Image.open(path) as src:
                    side=min(src.size);left=(src.width-side)//2
                    thumb=src.crop((left,0,left+side,side));thumb.thumbnail((300,300));sheet.paste(thumb,(x,y))
                draw.text((x+5,y+306),f'{i:03d} {m["categorySymbol"]} {m["name"]}'[:38],font=font,fill=(235,227,208))
            sheet.save(OUT/f'{phase}-sheet-{start//12+1}.png')


if __name__=='__main__':
    import sys
    sheets() if '--sheets' in sys.argv else prepare()
