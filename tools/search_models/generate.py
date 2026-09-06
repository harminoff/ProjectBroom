"""Original deterministic Project Broom mechanism meshes. No gameplay data."""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'mod/BrogueDoom/models/search'


def box(vertices, faces, x, y, z, w, d, h):
    start = len(vertices) + 1
    vertices.extend((x + a*w, y + b*d, z + c*h)
                    for a, b, c in ((0,0,0),(1,0,0),(1,1,0),(0,1,0),
                                    (0,0,1),(1,0,1),(1,1,1),(0,1,1)))
    faces.extend(tuple(start + i for i in f) for f in
                 ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)))


def generate():
    OUT.mkdir(parents=True, exist_ok=True)
    vertices, faces = [], []
    box(vertices, faces, -13, -13, 0, 26, 26, .7)
    box(vertices, faces, -10, -10, .7, 20, 20, .4)
    for x in (-11, 10):
        for y in (-11, 10):
            box(vertices, faces, x, y, 1.1, 1, 1, .3)
    for x in range(-8, 9, 4):
        box(vertices, faces, x, 8, 1.1, 1, 3, .5)
    text = '# Original Project Broom pressure plate, deterministic source\n'
    # UZDoom's OBJ loader uses Y-up; source geometry above is Z-up.
    text += ''.join(f'v {x:.4f} {z:.4f} {-y:.4f}\n' for x,y,z in vertices)
    text += 'vt 0 0\nvt 1 0\nvt 1 1\nvt 0 1\n'
    text += ''.join('f ' + ' '.join(f'{v}/{uv+1}' for uv,v in enumerate(f)) + '\n' for f in faces)
    (OUT/'plate.obj').write_text(text, encoding='utf-8', newline='\n')
    base_vertices, base_faces = vertices[:], faces[:]
    for name in ('fire', 'flood', 'net', 'alarm', 'vent', 'lever', 'rim', 'cover'):
        vertices, faces = ([], []) if name in ('lever', 'rim', 'cover') else (base_vertices[:], base_faces[:])
        if name == 'fire':
            box(vertices, faces, -6, 8, 1, 12, 6, 5)
            for x in (-4, 0, 4): box(vertices, faces, x, 6, 2, 2, 4, 2)
        elif name in ('flood', 'vent'):
            for x in range(-10, 11, 4): box(vertices, faces, x, -10, 1.5, 1, 20, 1)
        elif name == 'alarm':
            box(vertices, faces, 7, -7, 1, 4, 15, 5)
            box(vertices, faces, -4, -1, 1, 13, 2, 2)
        elif name == 'net':
            for x in range(-20, 21, 5):
                box(vertices, faces, x, -20, 180, .6, 40, .6)
                box(vertices, faces, -20, x, 180, 40, .6, .6)
            for x in (-20,20):
                for y in (-20,20): box(vertices, faces, x, y, 180, .6, .6, 44)
        elif name == 'lever':
            box(vertices, faces, -2, -9, 32, 3, 18, 26)
            box(vertices, faces, 1, -2, 39, 8, 4, 4)
            box(vertices, faces, 7, -2, 42, 3, 4, 13)
        elif name == 'rim':
            for x in range(-28, 29, 8):
                box(vertices, faces, x-3, -32, -.4, 6, 4, 1.8)
                box(vertices, faces, x-3, 28, -.4, 6, 4, 1.8)
                box(vertices, faces, -32, x-3, -.4, 4, 6, 1.8)
                box(vertices, faces, 28, x-3, -.4, 4, 6, 1.8)
        elif name == 'cover':
            box(vertices, faces, -32, -32, -.1, 64, 64, .1)
        text = '# Original Project Broom physical mechanism\n'
        text += ''.join(f'v {x:.4f} {z:.4f} {-y:.4f}\n' for x,y,z in vertices)
        text += 'vt 0 0\nvt 1 0\nvt 1 1\nvt 0 1\n'
        text += ''.join('f ' + ' '.join(f'{v}/{uv+1}' for uv,v in enumerate(f)) + '\n' for f in faces)
        (OUT/(name+'.obj')).write_text(text, encoding='utf-8', newline='\n')
    # Muted iron/stone in the existing brown-gray palette; fixed pixel noise.
    texture = Image.new('RGB', (64,64))
    texture.putdata([(65+n, 61+n, 53+n) for y in range(64) for x in range(64)
                     for n in [((x*37 + y*71 + (x*y)*13) % 17) - 8]])
    texture.save(ROOT/'mod/BrogueDoom/graphics/BRGSEARCH.png', optimize=False)


if __name__ == '__main__':
    generate()
