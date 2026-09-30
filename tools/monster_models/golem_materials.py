"""Original painted stone for the golem: per-pixel carved-stone atlas.

Every quad island is painted from its interpolated rest-space position, so
pigment, grain and cracks continue across island borders. The engine's flat
light hides sculpted form, so the paint carries it: form light, occlusion in
crevices and joints, worn highlights on bevelled edges, pale fresh chips,
cracks, weathering streaks and incised (never glowing) carved glyphs.

``paint_atlas(parts, palette)`` is reusable for other stone statues; pass a
different ``Palette``. Colours are art direction, not Brogue facts; the only
source cue used is the golem's gray glyph colour (50, 50, 50).
"""
import math
import struct
import zlib
from dataclasses import dataclass

SIZE = 2048
ROLE_IDS = {'stone': 0, 'core': 1, 'void': 2}


@dataclass(frozen=True)
class Palette:
    stone: tuple = (166, 154, 134)
    core: tuple = (40, 37, 36)
    void: tuple = (12, 11, 12)
    fleck_light: float = 30.0
    fleck_dark: float = 34.0
    wear: float = 50.0
    occlusion: float = .90
    tint: float = 10.0


GRAY = Palette()


def encode_png(pixels, width, height):
    def chunk(k, d): return struct.pack('>I', len(d))+k+d+struct.pack('>I', zlib.crc32(k+d) & 0xffffffff)
    raw = b''.join(b'\0'+pixels[y*width*3:(y+1)*width*3] for y in range(height))
    return (b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(raw, 9))+chunk(b'IEND', b''))


# ------------------------------------------------------------------ noise
def _hash(np, ix, iy, iz, seed):
    h = (ix.astype(np.uint64)*np.uint64(374761393)+iy.astype(np.uint64)*np.uint64(668265263)
         + iz.astype(np.uint64)*np.uint64(1440662683)+np.uint64(seed)*np.uint64(2654435761)) & np.uint64(0xffffffff)
    h = ((h ^ (h >> np.uint64(13)))*np.uint64(1274126177)) & np.uint64(0xffffffff)
    return ((h ^ (h >> np.uint64(16))) & np.uint64(0xffff)).astype(np.float64)/65535.0


def vnoise(np, p, seed):
    f = np.floor(p); i = f.astype(np.int64)+(1 << 20); t = p-f; s = t*t*(3-2*t)
    out = 0
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                w = (s[:, 0] if dx else 1-s[:, 0])*(s[:, 1] if dy else 1-s[:, 1])*(s[:, 2] if dz else 1-s[:, 2])
                out = out+w*_hash(np, i[:, 0]+dx, i[:, 1]+dy, i[:, 2]+dz, seed)
    return out


def fbm(np, p, seed, octaves=3):
    total = 0; amp = .5; norm = 0
    for o in range(octaves):
        total = total+amp*vnoise(np, p*(2**o), seed+o*17); norm += amp; amp *= .5
    return total/norm


def worley_edge(np, p, seed):
    """F2 - F1 cellular distance: small along the borders between cells (crack lines)."""
    f = np.floor(p).astype(np.int64)+(1 << 20); frac = p-np.floor(p)
    f1 = np.full(len(p), 9.0); f2 = np.full(len(p), 9.0)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for dz in (-1, 0, 1):
                cx, cy, cz = f[:, 0]+dx, f[:, 1]+dy, f[:, 2]+dz
                fx = _hash(np, cx, cy, cz, seed)*.8+.1+dx-frac[:, 0]
                fy = _hash(np, cx, cy, cz, seed+1)*.8+.1+dy-frac[:, 1]
                fz = _hash(np, cx, cy, cz, seed+2)*.8+.1+dz-frac[:, 2]
                d = np.sqrt(fx*fx+fy*fy+fz*fz)
                f2 = np.where(d < f1, f1, np.minimum(f2, d)); f1 = np.minimum(f1, d)
    return f2-f1


# ------------------------------------------------------------- features
def _segments(np, u, v, cell, seed):
    """Incised glyphs: strokes between a 3x3 lattice per cell, chosen by hash."""
    ci = np.floor(u/cell).astype(np.int64)+(1 << 20); lu = (u/cell-np.floor(u/cell))*2-1
    best = np.full(len(u), 9.0)
    points = [(-.55, -.7), (0, -.7), (.55, -.7), (-.55, 0), (0, 0), (.55, 0), (-.55, .7), (0, .7), (.55, .7)]
    strokes = [(0, 2), (3, 5), (6, 8), (0, 6), (1, 7), (2, 8), (0, 4), (4, 8), (2, 4), (4, 6), (1, 3), (1, 5), (3, 7), (5, 7)]
    zero = np.zeros_like(ci)
    for k, (a, b) in enumerate(strokes):
        on = _hash(np, ci, zero+k, zero, seed) > .62
        (ax, ay), (bx, by) = points[a], points[b]
        dx, dy = bx-ax, by-ay; t = np.clip(((lu-ax)*dx+(v-ay)*dy)/(dx*dx+dy*dy), 0, 1)
        d = np.sqrt((lu-ax-t*dx)**2+(v-ay-t*dy)**2)
        best = np.where(on, np.minimum(best, d), best)
    # Always keep a vertical stem so no cell is empty.
    stem = np.abs(lu-np.where(_hash(np, ci, zero+99, zero, seed) > .5, -.55, .55))+np.maximum(0, np.abs(v)-.7)
    return np.minimum(best, stem)


def _polyline(np, y, z, pts):
    best = np.full(len(y), 99.0)
    for (ay, az), (by, bz) in zip(pts, pts[1:]):
        dy, dz = by-ay, bz-az; t = np.clip(((y-ay)*dy+(z-az)*dz)/(dy*dy+dz*dz), 0, 1)
        best = np.minimum(best, np.sqrt((y-ay-t*dy)**2+(z-az-t*dz)**2))
    return best


def feature_id(name):
    if name == 'chest_block': return 1
    if name.startswith('forearm_band'): return 2
    if name in ('waist_upper', 'chest_collar'): return 3
    if name.startswith('pauldron_') and 'cap' not in name: return 4
    if name.startswith(('toe_', 'foot_')): return 7
    if name == 'head_cranium': return 8
    if name.startswith(('upperarm_', 'thigh_', 'forearm_')) and 'band' not in name: return 6
    return 0


def pigment(np, P, L, N, E, CH, AO, role, seed, feat, half, pal=GRAY):
    n = len(P)
    base = np.array([pal.stone, pal.core, pal.void], dtype=np.float64)[role]
    # Per-segment tint: carved from slightly different blocks of stone.
    tint = (_hash(np, seed, seed*0+3, seed*0+5, 11)-.5)*2*pal.tint
    warm = (_hash(np, seed, seed*0+7, seed*0+1, 12)-.5)*4
    col = base+tint[:, None]+np.stack([warm, warm*.2, -warm], 1)
    value = np.zeros(n)
    value += (fbm(np, P*.07, 21)-.5)*30
    value += (vnoise(np, P*.38, 22)-.5)*16
    value += (vnoise(np, P*2.2, 23)-.5)*18
    fl = vnoise(np, P*3.7+17.3, 24)
    value += np.where(fl > .80, pal.fleck_light*(fl-.80)/.2, 0)-np.where(fl < .16, pal.fleck_dark*(.16-fl)/.16, 0)
    vertical = 1-np.abs(N[:, 2])
    streak = vnoise(np, np.stack([P[:, 0]*.55, P[:, 1]*.55, P[:, 2]*.035], 1), 25)
    value -= np.clip(streak-.45, 0, 1)*38*vertical
    # Painted form light for flat engine lighting: lit tops, darker undersides.
    light = np.clip(N @ np.array([.34, -.22, .91]), -1, 1)
    form = .72+.46*light-.20*np.clip(-N[:, 2], 0, 1)
    # Grime settles toward each block's lower end; upper faces stay dusted pale.
    value += 10*np.clip(L[:, 2], 0, 1)-18*np.clip(-L[:, 2], 0, 1)**2
    # Worn bevel highlights and pale fresh fracture in chips.
    wear = pal.wear*np.clip(E, 0, 1)**1.6*(.45+.55*vnoise(np, P*1.1, 26))
    value += wear+34*np.clip(CH*2.2, 0, 1)
    # Cracks: cellular borders, only in some regions, darker where deeper.
    cracked = np.clip((vnoise(np, P*.075, 27)-.58)*5, 0, 1)
    edge = worley_edge(np, P*.12, 28)
    crack = np.clip(1-edge/.04, 0, 1)*cracked
    rim = np.clip(1-np.abs(edge-.06)/.025, 0, 1)*cracked
    # Hero cracks and carved detail per feature.
    y, z, x = P[:, 1], P[:, 2], P[:, 0]
    groove = np.zeros(n); lip = np.zeros(n)
    f1 = feat == 1
    if f1.any():
        jag = (vnoise(np, P*.9, 29)-.5)*1.4
        d = _polyline(np, y+jag, z, [(13.5, 70), (9, 64.5), (10.5, 59), (4.5, 53.5), (6, 49), (1.5, 45.5)])
        d2 = _polyline(np, y+jag, z, [(-15, 66), (-11, 61), (-13, 55.5)])
        hero = np.clip(1-np.minimum(d, d2)/.42, 0, 1)*f1*(x > -2)
        crack = np.maximum(crack, hero)
        # Horizontal masonry course across the chest back and sides.
        course = np.clip(1-np.abs(z-52.2)/.38, 0, 1)*f1*(x < 6)
        groove = np.maximum(groove, course); lip = np.maximum(lip, np.clip(1-np.abs(z-51.6)/.35, 0, 1)*f1*(x < 6))
    ang_u = np.arctan2(L[:, 1], L[:, 0])
    f2 = feat == 2
    if f2.any():
        u = ang_u*6.4; v = L[:, 2]*1.25
        g = _segments(np, u, v, 2.6, 31)
        mask = f2*(np.abs(L[:, 2]) < .78)
        groove = np.maximum(groove, np.clip(1-g/.16, 0, 1)*mask)
        lip = np.maximum(lip, np.clip(1-np.abs(g-.22)/.07, 0, 1)*mask*.6)
    f3 = feat == 3
    if f3.any():
        u = L[:, 1]*half[:, 1]; v = L[:, 2]*1.3
        g = _segments(np, u, v, 2.9, 32)
        mask = f3*(L[:, 0] > .55)*(np.abs(L[:, 2]) < .8)
        groove = np.maximum(groove, np.clip(1-g/.15, 0, 1)*mask)
        lip = np.maximum(lip, np.clip(1-np.abs(g-.21)/.07, 0, 1)*mask*.6)
    f4 = feat == 4
    if f4.any():
        jag = (vnoise(np, P*1.1, 33)-.5)*1.2
        d = _polyline(np, x+jag, z, [(-9, 71), (-4, 67.5), (-5.5, 63.5), (1, 61)])
        crack = np.maximum(crack, np.clip(1-d/.4, 0, 1)*f4*(np.abs(y) > 24))
    f6 = feat == 6
    if f6.any():
        # Chisel bands where limb segments were dressed; subtle carved rings.
        ring = np.clip(1-np.abs(np.abs(L[:, 2])-.62)/.05, 0, 1)*f6
        groove = np.maximum(groove, ring*.7); lip = np.maximum(lip, np.clip(1-np.abs(np.abs(L[:, 2])-.7)/.04, 0, 1)*f6*.5)
    f8 = feat == 8
    if f8.any():
        # Deep shadowed eye sockets carved under the brow (paint only, no glow).
        socket = np.exp(-((np.abs(L[:, 1])-.5)/.24)**2-((L[:, 2]-.02)/.2)**2)*np.clip((L[:, 0]-.3)*3, 0, 1)*f8
        groove = np.maximum(groove, np.clip(socket*1.25, 0, 1))
    f7 = feat == 7
    # Toes and feet sit in floor grime: less edge wear, darker stone.
    value -= f7*(wear*.7+16)
    value += 14*rim-10*crack
    col = (col+value[:, None])*form[:, None]
    col *= (1-pal.occlusion*np.clip(AO, 0, 1))[:, None]
    col *= (1-.72*crack)[:, None]
    col *= (1-.7*groove)[:, None]
    col += (26*lip)[:, None]
    # Voids and cores keep their own, darker values.
    col = np.where((role == 2)[:, None], base*(.7+.3*vnoise(np, P*1.3, 34))[:, None], col)
    return np.clip(np.rint(col), 0, 255).astype(np.uint8), crack, groove


def _corner_data(np, parts):
    boxes_c = np.array([p.box[0] for p in parts]); boxes_r = np.array([p.box[1] for p in parts])
    boxes_h = np.array([p.box[2] for p in parts])
    rows = []
    for pi, p in enumerate(parts):
        normals = p.normals()
        for f in p.faces:
            rows.append((pi, [p.vertices[i] for i in f], [p.local[i] for i in f], [normals[i] for i in f],
                         [p.edge[i] for i in f], [p.chip[i] for i in f], [p.uv[i] for i in f]))
    part = np.array([r[0] for r in rows]); V = np.array([r[1] for r in rows]); Lc = np.array([r[2] for r in rows])
    Nc = np.array([r[3] for r in rows]); Ec = np.array([r[4] for r in rows]); Cc = np.array([r[5] for r in rows])
    UV = np.array([r[6] for r in rows])
    # Ambient occlusion from neighbouring segments, measured at the corners.
    flat = V.reshape(-1, 3); own = np.repeat(part, 4); occ = np.zeros(len(flat))
    head = np.array([getattr(p, 'bone', '') == 'head' for p in parts])
    for bi in range(len(parts)):
        rel = flat-boxes_c[bi]; local = np.einsum('nk,jk->nj', rel, boxes_r[bi])
        d = np.linalg.norm(np.maximum(np.abs(local)-boxes_h[bi], 0), axis=1)
        weight = 1.0 if parts[bi].role == 'void' else min(1.0, min(parts[bi].box[2])/3.5)
        # Head segments take occlusion only from the eye sockets, never from the
        # collar, pauldrons or their own overlapping blocks: the carved face stays lit.
        skip = (own == bi) | (head[own] & (parts[bi].role != 'void'))
        occ += np.where(skip, 0, np.exp(-d/(1.3 if parts[bi].role == 'void' else 1.9)))*weight
    # Contact shadow near the floor and under the top-heavy chest.
    occ += np.exp(-np.maximum(flat[:, 2], 0)/1.6)*.8
    AOc = (1-np.exp(-occ*.9)).reshape(-1, 4)
    return part, V, Lc, Nc, Ec, Cc, AOc, UV


def paint(parts, pal=GRAY):
    """Diffuse RGB and specular level arrays for the laid-out parts."""
    import numpy as np
    part, V, Lc, Nc, Ec, Cc, AOc, UV = _corner_data(np, parts)
    roles = np.array([ROLE_IDS[p.role] for p in parts]); seeds = np.array([p.seed for p in parts])
    feats = np.array([feature_id(p.name) for p in parts]); halves = np.array([p.box[2] for p in parts])
    image = np.zeros((SIZE, SIZE, 3), dtype=np.uint8); image[:] = (96, 94, 90)
    spec = np.zeros((SIZE, SIZE), dtype=np.uint8); spec[:] = 20
    x0 = np.rint(UV[:, 0, 0]*SIZE-.5).astype(int); y0 = np.rint((1-UV[:, 0, 1])*SIZE-.5).astype(int)
    x1 = np.rint(UV[:, 2, 0]*SIZE-.5).astype(int); y1 = np.rint((1-UV[:, 2, 1])*SIZE-.5).astype(int)
    pad = 2; order = np.arange(len(part)); start = 0
    while start < len(order):
        chunk = order[start:start+1500]; start += len(chunk)
        idx = []; px = []; py = []
        for k in chunk:
            xs = np.arange(x0[k]-pad, x1[k]+pad+1); ys = np.arange(y0[k]-pad, y1[k]+pad+1)
            gx, gy = np.meshgrid(xs, ys); px.append(gx.ravel()); py.append(gy.ravel()); idx.append(np.full(gx.size, k))
        idx = np.concatenate(idx); px = np.concatenate(px); py = np.concatenate(py)
        s = np.clip((px-x0[idx])/np.maximum(x1[idx]-x0[idx], 1), -.3, 1.3)
        t = np.clip((py-y0[idx])/np.maximum(y1[idx]-y0[idx], 1), -.3, 1.3)
        upper = s >= t
        w = np.stack([np.where(upper, 1-s, 1-t), np.where(upper, s-t, 0), np.where(upper, t, s), np.where(upper, 0, t-s)], 1)
        def interp(a): return np.einsum('nc,nc...->n...', w, a[idx])
        P = interp(V); L = interp(Lc); N = interp(Nc)
        N = N/np.maximum(np.linalg.norm(N, axis=1), 1e-9)[:, None]
        pi = part[idx]
        col, crack, groove = pigment(np, P, L, N, interp(Ec), interp(Cc), interp(AOc), roles[pi], seeds[pi], feats[pi], halves[pi], pal)
        image[py, px] = col
        level = 24+34*np.clip(interp(Ec), 0, 1)**1.5+22*np.clip(interp(Cc)*2, 0, 1)-18*np.maximum(crack, groove)
        level = np.where(roles[pi] == 2, 4, np.where(roles[pi] == 1, 30, level))
        spec[py, px] = np.clip(np.rint(level), 0, 255).astype(np.uint8)
    return image, spec


def paint_atlas(parts, pal=GRAY):
    return encode_png(paint(parts, pal)[0].tobytes(), SIZE, SIZE)


def surface_maps(parts, skin='graphics/BRGGOLEM', spec=None, pal=GRAY):
    """Specular: matte weathered stone, slightly polished worn edges. Flat normal map."""
    if spec is None: spec = paint(parts, pal)[1]
    rgb = spec.repeat(3).tobytes()
    return {skin+'_N.png': encode_png(bytes((128, 128, 255))*16, 4, 4), skin+'_S.png': encode_png(rgb, SIZE, SIZE)}
