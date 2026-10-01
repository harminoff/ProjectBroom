"""Original CC0, deterministic presentation for previously unrepresented terrain.

Explicit catalog bindings, never substring-based gameplay or discovery rules.
"""
from pathlib import Path
import json
import math
import random
import sys
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.pickup_models.generate import Mesh

# Material identifier, visible catalog symbols, base color, surface treatment.
SURFACES = (
    ('BTCRPT', 'CARPET', (100, 28, 30), 'carpet'),
    ('BTBURN', 'BURNED_CARPET', (40, 29, 24), 'carpet'),
    ('BTMARB', 'MARBLE_FLOOR STONE_BRIDGE CHASM_WITH_HIDDEN_BRIDGE_ACTIVE', (135, 137, 132), 'marble'),
    ('BTOBSD', 'OBSIDIAN', (28, 23, 34), 'marble'),
    ('BTBRIM', 'ACTIVE_BRIMSTONE INERT_BRIMSTONE', (108, 87, 30), 'cracks'),
    ('BTCOOL', 'LAVA_RETRACTING', (80, 28, 16), 'cracks'),
    ('BTMUD', 'MUD_FLOOR', (69, 49, 30), 'mud'),
    ('BTLICHN', 'LICHEN', (70, 116, 31), 'lichen'),
    ('BTHAY', 'HAY', (110, 88, 41), 'straw'),
    ('BTBLOOD', 'RED_BLOOD', (100, 10, 15), 'puddle'),
    ('BTGREEN', 'GREEN_BLOOD', (31, 84, 18), 'puddle'),
    ('BTPURPL', 'PURPLE_BLOOD', (86, 24, 100), 'puddle'),
    ('BTACID', 'ACID_SPLATTER', (140, 164, 34), 'puddle'),
    ('BTVOMIT', 'VOMIT', (119, 101, 45), 'puddle'),
    ('BTURINE', 'URINE', (111, 91, 23), 'puddle'),
    ('BTENTRL', 'WORM_BLOOD', (148, 71, 57), 'puddle'),
    ('BTPUDDL', 'PUDDLE', (41, 77, 96), 'puddle'),
    ('BTECTO', 'ECTOPLASM', (74, 137, 127), 'puddle'),
    ('BTASH', 'ASH', (78, 75, 70), 'dust'),
    ('BTEMBR', 'EMBERS', (128, 43, 12), 'cracks'),
    ('BTGLYPH', 'MACHINE_GLYPH MACHINE_GLYPH_INACTIVE SACRED_GLYPH', (158, 137, 222), 'glyph'),
    ('BTSUN', 'SUNLIGHT_POOL PORTAL_LIGHT', (174, 155, 97), 'light'),
    ('BTSHADE', 'DARKNESS_PATCH', (17, 15, 24), 'light'),
    ('BTGLOW', 'GUARDIAN_GLOW', (99, 26, 21), 'light'),
    ('BTCRUMB', 'MACHINE_COLLAPSE_EDGE_SPREADING', (75, 61, 42), 'cracks'),
    ('BTFADE', 'HOLE_EDGE', (55, 54, 65), 'marble'),
    ('BTCRYST', 'CRYSTAL_WALL FORCEFIELD FORCEFIELD_MELT', (61, 132, 106), 'crystal'),
)

# Separate silhouettes for described objects; never reuse a pickup class.
OBJECTS = {
    'Algae': 'DEEP_WATER_ALGAE_1', 'DenseAlgae': 'DEEP_WATER_ALGAE_2',
    'WitheredFungus': 'GRAY_FUNGUS', 'FungalForest': 'FUNGUS_FOREST',
    'IronDoor': 'LOCKED_DOOR', 'OpenIronDoor': 'OPEN_IRON_DOOR_INERT',
    'Altar': 'ALTAR_INERT ALTAR_KEYHOLE ALTAR_CAGE_OPEN ALTAR_SWITCH ALTAR_SWITCH_RETRACTING',
    'CommuteAltar': 'COMMUTATION_ALTAR',
    'ResurrectAltar': 'RESURRECTION_ALTAR',
    'SacrificeAltar': 'SACRIFICE_ALTAR_DORMANT SACRIFICE_ALTAR',
    'ScorchedAltar': 'COMMUTATION_ALTAR_INERT RESURRECTION_ALTAR_INERT',
    'Pedestal': 'PEDESTAL',
    'OpenCage': 'MONSTER_CAGE_OPEN',
    'Coffin': 'COFFIN_CLOSED', 'OpenCoffin': 'COFFIN_OPEN',
    'DewarCaustic': 'DEWAR_CAUSTIC_GAS', 'DewarConfusion': 'DEWAR_CONFUSION_GAS',
    'DewarParalysis': 'DEWAR_PARALYSIS_GAS', 'DewarMethane': 'DEWAR_METHANE_GAS',
    'Bedroll': 'HAVEN_BEDROLL', 'Bones': 'BONES', 'Rubble': 'RUBBLE',
    'Junk': 'JUNK', 'Glass': 'BROKEN_GLASS', 'Droppings': 'UNICORN_POOP',
    'Web': 'SPIDERWEB', 'Net': 'NETTING', 'Vines': 'ANCIENT_SPIRIT_VINES',
    'Arch': 'PORTAL', 'CrystalPortal': 'DUNGEON_PORTAL',
    'CrystalOff': 'ELECTRIC_CRYSTAL_OFF', 'CrystalOn': 'ELECTRIC_CRYSTAL_ON',
    'Pipes': 'PIPE_GLOWING', 'BurntPipes': 'PIPE_INERT', 'Brazier': 'BRAZIER',
    'Skins': 'MUD_DOORWAY', 'FallenTorch': 'PILOT_LIGHT',
    'TrampledLeaves': 'TRAMPLED_FOLIAGE', 'TrampledFungus': 'TRAMPLED_FUNGUS_FOREST',
    'RopeBridge': 'BRIDGE BRIDGE_EDGE BRIDGE_FALLING',
}

# Dedicated inert dressing classes reuse original catalog meshes without
# pretending to be authoritative Brogue terrain records.
EXPLORER_DRESSING = {
    'ExplorerBedroll': ('Bedroll', 1.0),
    'ExplorerBones': ('Bones', .8),
    'ExplorerJunk': ('Junk', .65),
    'ExplorerFallenTorch': ('FallenTorch', .85),
    'ExplorerSkins': ('Skins', .7),
    'ExplorerRubble': ('Rubble', .55),
}


def surface(color, treatment):
    rng = random.Random(319)
    image = Image.new('RGB', (128, 128))
    image.putdata([tuple(max(0, min(255, c + rng.randrange(-14, 15))) for c in color)
                   for _ in range(128 * 128)])
    draw = ImageDraw.Draw(image)
    if treatment == 'carpet':
        for x in range(0, 128, 4): draw.line((x, 0, x, 127), fill=tuple(c//2 for c in color))
        for y in range(0, 128, 32):
            draw.line((0, y, 127, y), fill=(144, 112, 49), width=3)
        for x in range(16, 128, 32):
            for y in range(16, 128, 32): draw.polygon([(x,y-9),(x+9,y),(x,y+9),(x-9,y)], outline=(153,114,53))
    elif treatment in ('marble', 'crystal'):
        for i in range(9):
            points = [(x, int(i*17+9*math.sin(x*.045+i))%128) for x in range(128)]
            draw.line(points, fill=tuple(min(255,c+40) for c in color), width=2)
        if treatment == 'marble':
            for p in (0,64): draw.line((p,0,p,127), fill=(22,22,23),width=2); draw.line((0,p,127,p),fill=(22,22,23),width=2)
    elif treatment in ('cracks', 'mud'):
        for i in range(28):
            x,y=rng.randrange(128),rng.randrange(128)
            draw.line([(x,y),(x+7,y+9),(x+3,y+18)], fill=(215,100,18) if treatment=='cracks' and color[0]>100 else (27,22,19),width=2)
    elif treatment in ('puddle', 'lichen', 'dust', 'light'):
        # Irregular islands leave a neutral soil surround, not a solid colored tile.
        ground=Image.new('RGB',(128,128)); ground.putdata([(43+n,35+n,25+n) for _ in range(128*128) for n in [rng.randrange(12)]])
        mask=Image.new('L',(128,128)); d=ImageDraw.Draw(mask)
        for i in range(30):
            x,y=rng.randrange(15,105),rng.randrange(15,105); radius=rng.randrange(5,24)
            d.ellipse((x-radius,y-radius,x+radius,y+radius),fill=255)
        ground.paste(image,(0,0),mask); image=ground
    elif treatment=='straw':
        for i in range(420):
            x,y=rng.randrange(128),rng.randrange(128)
            draw.line((x,y,x+rng.randrange(-18,19),y+rng.randrange(-18,19)),fill=(159+rng.randrange(40),137,68))
    elif treatment=='glyph':
        draw.rectangle((0,0,127,127),fill=(32,28,27))
        draw.ellipse((18,18,110,110),outline=color,width=3)
        points=[(64+40*math.cos(i*2*math.pi/5),64+40*math.sin(i*2*math.pi/5)) for i in range(5)]
        draw.line(points+[points[0]],fill=color,width=3)
        draw.line((64,18,64,110),fill=color,width=2)
    return image


def model(name):
    m=Mesh(name)
    def box(x,y,z,w,h,d,mat='metal'): m.box(x,y,z,w,h,d,mat)
    def rod(a,b,r,mat):
        # Eight-sided tube connecting arbitrary endpoints, with closed caps.
        import math
        axis=[b[i]-a[i] for i in range(3)]; length=math.sqrt(sum(v*v for v in axis)); axis=[v/length for v in axis]
        ref=(0,1,0) if abs(axis[1])<.9 else (1,0,0)
        u=(axis[1]*ref[2]-axis[2]*ref[1],axis[2]*ref[0]-axis[0]*ref[2],axis[0]*ref[1]-axis[1]*ref[0]); norm=math.sqrt(sum(v*v for v in u)); u=[v/norm for v in u]
        v=(axis[1]*u[2]-axis[2]*u[1],axis[2]*u[0]-axis[0]*u[2],axis[0]*u[1]-axis[1]*u[0])
        rings=[[tuple(p[j]+r*(u[j]*math.cos(i*math.pi/4)+v[j]*math.sin(i*math.pi/4)) for j in range(3)) for i in range(8)] for p in (a,b)]
        for i in range(8): m.face([rings[0][i],rings[0][(i+1)%8],rings[1][(i+1)%8],rings[1][i]],mat)
        for ring in rings:
            for i in range(1,7): m.face([ring[0],ring[i],ring[i+1]],mat)
    from tools.terrain_debris import REBUILT, build as build_debris
    if name in REBUILT:
        build_debris(m, name, rod)
        return m
    if name in ('Algae','DenseAlgae'):
        rng=random.Random(45)
        for i in range(18 if name=='Algae' else 36):
            m.cylinder(rng.randrange(-28,29),.2,rng.randrange(-28,29),rng.uniform(.5,2),.15,'crystal',6)
    elif 'Altar' in name or name=='Pedestal':
        mat='metal' if name=='ScorchedAltar' else 'paper'
        box(0,0,0,32,5,26,mat); box(0,5,0,21,23,16,mat); box(0,28,0,38,5,28,mat)
        if name!='Pedestal':
            for x in (-13,13):
                m.cylinder(x,33,0,2,9,'paper'); m.sphere(x,42,0,1.8,'gold')
            if name=='CommuteAltar':
                for x in (-7,7): m.torus(x,34,0,4,.8,'gold')
            elif name=='ResurrectAltar': box(0,33,0,3,12,3,'gold'); box(0,39,0,10,2,3,'gold')
            elif name=='SacrificeAltar': box(0,33,0,16,1,14,'leather')
    elif name=='ExitDoors':
        for x in (-15,15):
            box(x,0,0,29,86,5,'wood'); box(x,5,-3,24,76,1,'gold')
            m.torus(x*.3,38,-5,3,.8,'gold')
    elif name in ('IronDoor','OpenIronDoor'):
        for x in (-28,28): box(x,0,0,4,88,8)
        box(0,86,0,60,4,8)
        if name=='IronDoor':
            box(0,0,0,52,86,4)
            for y in (14,40,68): box(0,y,-3,52,3,2,'wood')
            m.torus(17,40,-4,3,.8,'gold')
        else: box(28,0,24,4,86,48)
    elif name in ('Coffin','OpenCoffin'):
        box(0,0,0,24,4,46,'wood')
        for x in (-12,12): box(x,4,0,3,12,46,'wood')
        for z in (-23,23): box(0,4,z,25,12,3,'wood')
        if name=='Coffin': box(0,16,0,27,3,49,'wood'); box(0,19,0,2,1,24,'metal')
        else: box(22,0,0,8,3,49,'wood')
    elif name=='OpenCage':
        for z in (-24,24):
            for x in range(-24,25,8): box(x,0,z,2,58,2)
        for z in range(-24,25,8): box(-24,0,z,2,58,2)
        for y in (0,56):
            for z in (-24,24): box(0,y,z,50,2,2)
            box(-24,y,0,2,2,50)
        for z in range(24,57,8): box(24,0,z,2,58,2)
    elif name.startswith('Dewar'):
        m.cylinder(0,0,0,10,3,'metal'); m.cylinder(0,3,0,9,27,'glass'); m.cylinder(0,30,0,4,8,'glass'); m.cylinder(0,38,0,5,3,'wood')
        # Bands identify the known terrain description, not unidentified potions.
        mat={'DewarCaustic':'fruit','DewarConfusion':'crystal','DewarParalysis':'gold','DewarMethane':'paper'}[name]
        m.cylinder(0,14,0,9.3,7,mat)
    elif name in ('Arch','CrystalPortal'):
        mat='crystal' if name=='CrystalPortal' else 'paper'
        for x in (-23,23): box(x,0,0,10,65,16,mat)
        for i in range(8):
            a=i*math.pi/7; box(23*math.cos(a),61+23*math.sin(a),0,11,10,16,mat)
    elif name in ('CrystalOn','CrystalOff'):
        m.cylinder(0,0,0,10,7,'metal'); m.cylinder(0,7,0,4,19,'metal'); m.sphere(0,26,0,11,'crystal' if name=='CrystalOn' else 'glass')
    elif name in ('Pipes','BurntPipes'):
        for x in (-13,0,13): rod((x,3,-28),(x,3,28),2,'glass' if name=='Pipes' else 'metal')
        for z in (-20,20): box(0,0,z,36,3,5,'metal')
    elif name=='Brazier':
        for x in (-9,9):
            for z in (-9,9): rod((x,0,z),(x*.6,22,z*.6),1.5,'metal')
        m.cylinder(0,20,0,12,5,'metal'); m.torus(0,25,0,12,2,'metal')
        for x in (-5,0,5): m.sphere(x,26,0,3,'gold')
    elif name=='Bedroll':
        box(0,0,0,22,3,45,'leather'); box(0,3,-16,21,5,9,'paper')
        for z in (-8,8): box(0,3,z,22,1,2,'wood')
    elif name=='FallenTorch': rod((-15,3,0),(15,3,0),2,'wood'); m.sphere(15,2,0,4,'gold')
    elif name=='RopeBridge':
        for x in (-29,29):
            for z in (-30,30): rod((x,0,z),(x,27,z),1.5,'wood')
            for y in (12,25):
                for z in range(-32,32,8): rod((x,y-3*math.cos(z*math.pi/64),z),(x,y-3*math.cos((z+8)*math.pi/64),z+8),.65,'leather')
    elif name in ('Web','Net'):
        if name=='Net':
            for p in range(-25,26,8): rod((p,2,-25),(p,2,25),.35,'leather'); rod((-25,2,p),(25,2,p),.35,'leather')
        else:
            for i in range(12):
                a=i*math.pi/6; rod((0,3,0),(28*math.cos(a),3,28*math.sin(a)),.22,'paper')
            for r in (8,16,24): m.torus(0,3,0,r,.22,'paper',12)
    else:
        rng=random.Random(28)
        for i in range(15):
            x,z=rng.randrange(-23,24),rng.randrange(-23,24)
            if name=='Bones': rod((x,2,z),(x+7,2,z+3),.8,'paper'); m.sphere(x,1,z,1.5,'paper')
            elif name=='Glass': m.face([(x,1,z),(x+6,1,z+2),(x+2,2,z+8)],'glass')
            elif name=='Droppings': m.sphere(x,0,z,2,'leather')
            else: m.sphere(x,0,z,2+i%4,'metal',3,5)
    return m


def generate():
    graphics=ROOT/'mod/BrogueDoom/graphics'; out=ROOT/'mod/BrogueDoom/models/terrain/catalog'
    out.mkdir(parents=True,exist_ok=True)
    # Muted original material palette using the Mesh writer's 4x2 UV contract.
    # Avoid the pickup atlas's deliberately saturated unidentified-item colors.
    colors=((86,87,84),(83,58,34),(171,165,146),(77,53,34),
            (81,128,137),(166,128,53),(55,129,106),(80,110,44))
    atlas=Image.new('RGB',(256,128))
    atlas.putdata([tuple(max(0,min(255,c+((x*17+y*31)%13)-6)) for c in colors[(y//64)*4+x//64])
                   for y in range(128) for x in range(256)])
    atlas.save(graphics/'BTATLAS.png')
    textures=[]
    for identifier, symbols, color, treatment in SURFACES:
        surface(color,treatment).save(graphics/(identifier+'.png'))
        textures.append(f'Texture "{identifier}", 128, 128\n{{\n XScale 2\n YScale 2\n Patch "graphics/{identifier}.png", 0, 0\n}}\n')
    zs=['// Original CC0 terrain catalog models. Presentation only.']
    definitions=[]
    for name in OBJECTS:
        model(name).write(out/(name+'.obj'))
        cls='BrogueCatalog'+name
        body='Default { RenderStyle "Add"; Alpha 0.7; } States { Spawn: BRGD A -1 Bright; Stop; }' if name in ('Algae','DenseAlgae') else ''
        zs.append(f'class {cls} : BrogueTerrainStone {{ {body} }}')
        definitions.append(f'Model {cls}\n{{\n Path "models/terrain/catalog"\n Model 0 "{name}.obj"\n Skin 0 "graphics/BTATLAS.png"\n Scale 1 1 1\n FrameIndex BRGD A 0 0\n}}\n')
    zs.append('// Cosmetic explorer traces: inert, non-loot, and never synchronized as terrain.')
    for class_suffix, (mesh, scale) in EXPLORER_DRESSING.items():
        cls = 'Brogue' + class_suffix
        zs.append(f'class {cls} : BrogueTerrainStone {{ Default {{ Scale {scale:g}; }} }}')
        definitions.append(f'Model {cls}\n{{\n Path "models/terrain/catalog"\n Model 0 "{mesh}.obj"\n Skin 0 "graphics/BTATLAS.png"\n Scale 1 1 1\n FrameIndex BRGD A 0 0\n}}\n')
    (out/'MODELDEF.txt').write_text('\n'.join(definitions))
    (ROOT/'mod/BrogueDoom/brogue_terrain_catalog.zs').write_text('\n'.join(zs)+'\n')
    path=ROOT/'mod/BrogueDoom/TEXTURES.txt'; text=path.read_text()
    begin,end='// BEGIN TERRAIN CATALOG MATERIALS','// END TERRAIN CATALOG MATERIALS'
    block=begin+'\n'+''.join(textures)+end
    text=text[:text.index(begin)]+block+text[text.index(end)+len(end):] if begin in text else text.rstrip()+'\n\n'+block+'\n'
    path.write_text(text)
    from tools.terrain_overlays import generate as generate_overlays
    generate_overlays()


if __name__=='__main__': generate()
