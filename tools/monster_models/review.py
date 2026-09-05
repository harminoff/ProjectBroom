"""Prepare an isolated GZDoom art gallery, never a generated Brogue campaign.

python -m tools.monster_models.review prepare
python -m tools.monster_models.review sheets
The optional contact-sheet step requires Pillow; runtime generators do not.
"""
from pathlib import Path
import argparse
import json
import zipfile

from .bestiary import ROOT, source_records
from tools.mapcompiler.compile import make_wad
from tools.packaging.package_release import zip_tree

EVIDENCE=ROOT/'artifacts/creature-models'


def prepare():
    addon=EVIDENCE/'gallery'
    addon.mkdir(parents=True,exist_ok=True)
    textmap='namespace = "ZDoom";\n'
    for x,y in ((-256,-256),(-256,256),(256,256),(256,-256)):
        textmap+=f'vertex {{ x={x}; y={y}; }}\n'
    textmap+='sector { heightfloor=0; heightceiling=224; texturefloor="BRGDIRT"; textureceiling="BRGROCK"; lightlevel=208; }\n'
    for n in range(4):
        textmap+=f'sidedef {{ sector=0; texturemiddle="BRGROCK"; }}\n'
        textmap+=f'linedef {{ v1={n}; v2={(n+1)%4}; sidefront={n}; blocking=true; }}\n'
    textmap+='thing { x=128; y=-160; height=0; type=1; angle=130; skill1=true; skill2=true; skill3=true; skill4=true; skill5=true; single=true; }\n'
    maps=addon/'maps'; maps.mkdir(exist_ok=True)
    (maps/'ART01.wad').write_bytes(make_wad('ART01',textmap))
    (addon/'MAPINFO').write_text('GameInfo { AddEventHandlers = "CreatureArtGallery" }\nmap ART01 "Creature model review (NOT a Brogue level)" { levelnum = 99 }\n')
    (addon/'ZSCRIPT').write_text('''version "4.14"
// Private presentation gallery: no Brogue level, actions, creatures or RNG.
class CreatureArtCamera : Actor {
    Default { +NOINTERACTION; +NOBLOCKMAP; +NOGRAVITY; RenderStyle "None"; CameraHeight 0; }
    States { Spawn: TNT1 A -1; Stop; }
}
class CreatureArtGallery : EventHandler {
    Actor subject;
    Actor camera;
    int counter;
    override void WorldTick() {
        counter++;
        if (counter < 100) return;
        if (!camera) camera=Actor.Spawn("CreatureArtCamera",(128,-160,78));
        camera.angle=VectorAngle(-128,160);
        camera.pitch=atan2(78-34,sqrt(128*128+160*160));
        players[consoleplayer].camera=camera;
        int kind=1+(counter-100)/35;
        if(kind>67) return;
        if((counter-100)%35==0) {
            if(subject) subject.Destroy();
            Class<Actor> type=String.Format("BrogueMonsterK%02d",kind);
            subject=Actor.Spawn(type,(0,0,0));
            if(subject) { subject.angle=0; subject.alpha=1; }
            if(subject) Console.Printf("CREATURE_GALLERY kind=%d actor=%s",kind,subject.GetClassName());
            else Console.Printf("CREATURE_GALLERY kind=%d MISSING",kind);
        }
    }
}
''')
    # A fixed 64-unit ground grid provides a model-size reference in the engine.
    from .creatures import Sculpt, obj_bytes
    grid=Sculpt()
    for n in (-32,32):
        grid.strand(f'grid_x_{n}',[(-96,n,.15,.15),(96,n,.15,.15)],'bone',6,1)
        grid.strand(f'grid_y_{n}',[(n,-96,.15,.15),(n,96,.15,.15)],'bone',6,1)
    grid.strand('height_reference_58',[(-36,36,0,.35),(-36,36,58,.35)],'bone',8,1)
    (addon/'grid.obj').write_bytes(obj_bytes(grid.parts,'REVIEW_GRID'))
    with (addon/'ZSCRIPT').open('a') as f:
        f.write('''
class CreatureScaleGrid : Actor {
 Default { +NOINTERACTION; +NOBLOCKMAP; +NOGRAVITY; }
 States { Spawn: BRM0 A -1; Stop; }
}
class CreatureGridEvent : EventHandler {
 override void WorldLoaded(WorldEvent e) { Actor.Spawn("CreatureScaleGrid",(0,0,0)); }
}
''')
    with (addon/'MAPINFO').open('a') as f: f.write('GameInfo { AddEventHandlers = "CreatureGridEvent" }\n')
    (addon/'MODELDEF').write_text('Model CreatureScaleGrid { Model 0 "grid.obj" Skin 0 "graphics/BRGRAT.png" Scale 1 1 1 FrameIndex BRM0 A 0 0 }\n')
    for phase in ('runtime-before','runtime-after'):
        (EVIDENCE/phase).mkdir(exist_ok=True)
        commands=['vid_renderer 1','vid_fullscreen false','vid_vsync false','vid_maxfps 60',
                  'gl_texture_filter 4','screenblocks 12','fov 70','con_notifytime 0','i_pauseinbackground false']
        for kind in range(1,68):
            target=(EVIDENCE/phase/f'{kind:02d}.png').as_posix()
            next_command=f'creature_capture_{kind+1:02d}' if kind<67 else 'quit'
            body=f'screenshot "{target}"; wait 35; {next_command}'
            commands.append(f'alias creature_capture_{kind:02d} "'+body.replace('"','\\"')+'"')
        # Keep each cfg line below the engine line buffer limit, while wait
        # delays the next alias rather than independent cfg lines.
        commands.append('wait 118; creature_capture_01')
        (EVIDENCE/f'{phase}.cfg').write_text('\n'.join(commands)+'\n')
    # Old resources only: must be loaded after the new static package for before shots.
    before=EVIDENCE/'before-override'; (before/'models').mkdir(parents=True,exist_ok=True)
    import shutil
    shutil.copytree(EVIDENCE/'baseline/monsters',before/'models/monsters',dirs_exist_ok=True)
    (before/'graphics').mkdir(exist_ok=True)
    for name in ('BRGMON.png','BRGRAT.png'): shutil.copyfile(EVIDENCE/'baseline'/name,before/'graphics'/name)
    zip_tree(ROOT/'mod/BrogueDoom',EVIDENCE/'ProjectBroom-creatures.pk3')
    print('Prepared isolated art map and static package:',EVIDENCE)


def sheets():
    from PIL import Image, ImageDraw, ImageFont
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
    records=source_records()[1:]
    for phase in ('after','before','runtime-after','runtime-before'):
        folder=EVIDENCE/phase
        if not folder.exists(): continue
        images=[]
        for r in records:
            candidates=list(folder.glob(f"{r['kind']:02d}*.png"))
            if candidates: images.append((r,candidates[0]))
        for page in range((len(images)+11)//12):
            sheet=Image.new('RGB',(1200,1020),(24,29,34)); draw=ImageDraw.Draw(sheet)
            for i,(r,path) in enumerate(images[page*12:(page+1)*12]):
                x=(i%4)*300; y=(i//4)*340
                with Image.open(path) as src:
                    if phase.startswith('runtime-'):
                        # Consistent central crop; retain the original full-frame
                        # captures separately for framing/scale verification.
                        side=min(src.size)
                        left=(src.width-side)//2
                        src=src.crop((left,0,left+side,side))
                    src.thumbnail((300,305))
                    sheet.paste(src,(x+(300-src.width)//2,y))
                draw.text((x+7,y+308),f"M{r['kind']:02d} {r['name']}",fill=(232,224,204),font=font)
            sheet.save(EVIDENCE/f'{phase}-sheet-{page+1}.png')


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('action',choices=['prepare','sheets'])
    {'prepare':prepare,'sheets':sheets}[parser.parse_args().action]()
