"""Original CC0 feathered gas cards and continuous cloud alpha; no random state."""
import math
from PIL import Image


def cloud_geometry():
    """Nine crossed cards, contained within one cell even during bounded drift."""
    vertices, faces = [], []
    for layer, (cx, cy, z) in enumerate(((-3, 2, 14), (3, -2, 25), (-1, -3, 37))):
        for angle in (layer * .71, layer * .71 + math.pi / 2):
            dx, dy = 24 * math.cos(angle), 24 * math.sin(angle)
            first = len(vertices) + 1
            vertices.extend([(cx-dx, cy-dy, z-12), (cx+dx, cy+dy, z-12),
                             (cx+dx, cy+dy, z+12), (cx-dx, cy-dy, z+12)])
            faces.append(tuple(range(first, first+4)))
        first = len(vertices) + 1
        vertices.extend([(cx-17, cy-17, z), (cx+17, cy-17, z),
                         (cx+17, cy+17, z), (cx-17, cy+17, z)])
        faces.append(tuple(range(first, first+4)))
    return vertices, faces


def cloud_texture(size=128):
    """Soft irregular lobes, with zero alpha along every texture boundary."""
    im = Image.new('RGBA', (size, size))
    pixels = []
    for y in range(size):
        for x in range(size):
            u, v = 2*x/(size-1)-1, 2*y/(size-1)-1
            radius = math.hypot(u, v)
            envelope = max(0, 1-radius*radius)**2
            noise = (.66 + .16*math.sin(u*9+math.sin(v*6))
                     + .11*math.sin(v*13-u*5) + .07*math.cos(u*21+v*17))
            pixels.append((255, 255, 255, round(210*envelope*noise)))
    im.putdata(pixels)
    return im
