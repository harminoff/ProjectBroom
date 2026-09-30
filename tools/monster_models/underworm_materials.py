"""Original deterministic underworm paint and continuous longitudinal pigment coordinates.

Brogue's wormColor (80, 60, 40) is an identity cue, not literal paint: the skin
is a wet, fleshy pink-brown worm hide with a wide painted value range for the
engine's flat light. Belly and chin are pale cream-pink, flanks salmon, the
back a dark mauve-brown. About thirty annuli each carry a dark groove, a
lit ridge, and a glistening wet highlight pool on the upper flank plus a
sheen line along the spine. A paler saddle band (clitellum) sits behind the
head. The head is darker and wrinkled with a pink lip, teeth run from a yellow
root to an ivory tip, and the throat is a dark maroon well.

Pigment is a function of the body centreline, not of source-part UVs or height:
u is arc length along the coiled centreline (continuing straight through the
head), v is the circumferential angle from the belly (0) over the flank to the
spine (1), mirrored left/right. Fused skin therefore has continuous colour
through every coil turn and junction, and annuli stay square to the body.
Nothing here emits light; there is no gameplay meaning in any colour.
"""
import math
import numpy as np
from .centaur_materials import encode_png
from . import underworm_animation as g

UB = .80                      # body zone occupies u in 0..UB; palette columns above
SIZE = 1024
PALETTE_TEETH = (.83, .88)
PALETTE_CHITIN = (.88, .92)
PALETTE_LIP = (.92, .96)
PALETTE_THROAT = (.96, 1.0)


# ------------------------------------------------------------------ centreline lookup
def _axis():
    pts = [tuple(p[:3]) for p in g.REST_DENSE]
    last = pts[-1]
    step = .5
    extra = [(last[0]+step*k, last[1], last[2]) for k in range(1, int((g.HEAD_EXT+8)/step)+1)]
    pts = pts+extra
    P = np.array(pts, dtype=np.float64)
    T = np.gradient(P, axis=0)
    T /= np.linalg.norm(T, axis=1)[:, None]
    up = np.zeros_like(T)
    up[:, 2] = 1.
    flat = np.abs(T[:, 2]) > .985
    up[flat] = (1., 0., 0.)
    left = np.cross(up, T)
    left /= np.linalg.norm(left, axis=1)[:, None]
    U = np.cross(T, left)
    arc = np.concatenate([[0.], np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))])
    return P, T, left, U, arc


_AXIS = None


def axis_data():
    global _AXIS
    if _AXIS is None:
        _AXIS = _axis()
    return _AXIS


def pigment_uv(vertices):
    """(u, v) atlas coordinates for world rest-position vertices (continuous over fused skin)."""
    P, T, left, U, arc = axis_data()
    V = np.array(vertices, dtype=np.float64)
    out = np.empty((len(V), 2))
    for start in range(0, len(V), 1500):
        chunk = V[start:start+1500]
        d2 = ((chunk[:, None, :]-P[None, :, :])**2).sum(-1)
        k = np.argmin(d2, axis=1)
        rho = chunk-P[k]
        rho -= (rho*T[k]).sum(-1)[:, None]*T[k]
        norm = np.linalg.norm(rho, axis=1)
        d = np.where(norm > 1e-9, (rho*U[k]).sum(-1)/np.maximum(norm, 1e-9), 0.)
        v = np.arccos(np.clip(-d, -1., 1.))/math.pi
        u = UB*np.clip(arc[k]/g.S_TOT, 0., 1.)
        lx = chunk[:, 0]-g.HEAD[0]
        rho = np.hypot(chunk[:, 1]-g.HEAD[1], (chunk[:, 2]-g.HEAD[2])/.7)
        funnel = (lx > g.FUNNEL_X-.5) & (rho < 10.9)
        rim = (lx > 6.6) & (rho >= 10.9) & (rho < 11.9)
        u = np.where(funnel, .98, np.where(rim, .94, u))
        v = np.where(funnel, np.clip(.04+.9*rho/10.9, .04, .95), np.where(rim, .5, v))
        out[start:start+1500, 0] = u
        out[start:start+1500, 1] = v
    return [(round(float(a), 7), round(float(b), 7)) for a, b in out]


def pigment(v):
    return pigment_uv([v])[0]


# ------------------------------------------------------------------ paint
def _hash(ix, iy, seed):
    h = (ix.astype(np.uint32)*np.uint32(374761393)+iy.astype(np.uint32)*np.uint32(668265263)+np.uint32(seed*2246822519 % 2**32))
    h = (h ^ (h >> np.uint32(13)))*np.uint32(1274126177)
    return ((h ^ (h >> np.uint32(16))) & np.uint32(1023)).astype(np.float64)/1023.


def vnoise(x, y, seed=1):
    """Smooth value noise in -0.5..0.5."""
    ix, iy = np.floor(x), np.floor(y)
    fx, fy = x-ix, y-iy
    fx, fy = fx*fx*(3-2*fx), fy*fy*(3-2*fy)
    ix, iy = ix.astype(np.int64), iy.astype(np.int64)
    a = _hash(ix, iy, seed)
    b = _hash(ix+1, iy, seed)
    c = _hash(ix, iy+1, seed)
    d = _hash(ix+1, iy+1, seed)
    return (a*(1-fx)*(1-fy)+b*fx*(1-fy)+c*(1-fx)*fy+d*fx*fy)-.5


def sstep(x, a, b):
    t = np.clip((x-a)/(b-a), 0., 1.)
    return t*t*(3-2*t)


def mix(a, b, t):
    return a+(b-a)*t[..., None]


def col(r, gr, b):
    return np.array([r, gr, b], dtype=np.float64)


BELLY = col(216, 192, 148)
FLANK = col(158, 118, 70)
DORSAL = col(82, 56, 36)
GROOVE = col(28, 18, 12)
SADDLE = col(196, 156, 100)
HEAD_BELLY = col(150, 112, 76)
HEAD_FLANK = col(98, 72, 50)
HEAD_DORSAL = col(58, 42, 32)
LIP = col(120, 52, 46)
WET = col(232, 218, 190)


def body_layer(s, vt):
    px, py = s, vt*math.pi*8.
    frac = s/g.S_HEAD
    p = (s/g.PITCH) % 1.
    d = np.minimum(p, 1-p)
    groove = np.exp(-(d/.105)**2)
    ridge = np.sin(math.pi*p)**.9
    mid = mix(np.broadcast_to(BELLY, s.shape+(3,)), np.broadcast_to(FLANK, s.shape+(3,)), sstep(vt, .16, .56))
    base = mix(mid, np.broadcast_to(DORSAL, s.shape+(3,)), sstep(vt, .58, .95))
    # thicker front is heavier and more mauve; the thin tail runs paler and pinker
    base = base*(1-.10*sstep(frac, .35, 1.)[..., None])
    base = mix(base, np.broadcast_to(col(222, 200, 160), s.shape+(3,)), .5*(1-sstep(frac, .0, .18)))
    # mottling and fine skin grain in physical units so it stays isotropic on the body
    n1 = vnoise(px/2.4, py/2.4, 3)+.5*vnoise(px/1.1, py/1.1, 7)
    n2 = vnoise(px/.55, py/.55, 11)
    base = base*(1+.22*n1[..., None])+8.*n2[..., None]
    base = base*(.78+.34*ridge)[..., None]
    # clitellum saddle: paler, warmer, with shallow grooves
    cl = sstep(frac, CL0, CL0+.012)*(1-sstep(frac, CL1-.012, CL1))
    base = mix(base, np.broadcast_to(SADDLE, s.shape+(3,)), .78*cl)
    groove = groove*(1-.55*cl)
    base = mix(base, np.broadcast_to(GROOVE, s.shape+(3,)), .82*groove)
    # belly edge occlusion
    base = base*(.72+.28*sstep(vt, .0, .16))[..., None]
    # wet glisten: a specular pool on each annulus, a fainter lower one, a spine sheen line, droplets
    hl1 = np.exp(-((p-.44)/.19)**2)*np.exp(-((vt-.75)/.07)**2)
    hl2 = np.exp(-((p-.55)/.26)**2)*np.exp(-((vt-.30)/.055)**2)
    spine = np.exp(-((vt-.94)/.045)**2)*(.35+.5*ridge)
    drops = np.clip((vnoise(px/.42, py/.42, 19)-.30)*7., 0., 1.)*sstep(vt, .35, .7)*(1-groove)
    gloss = np.clip(.5*hl1+.2*hl2+.18*spine+.3*drops, 0., .6)
    return base, gloss, groove


CL0, CL1 = g.CLITELLUM


def texture_bytes():
    n = SIZE
    xs = np.arange(n)/(n-1)
    ys = np.arange(n)/(n-1)
    u = np.broadcast_to(xs[None, :], (n, n))
    vt = np.broadcast_to((1-ys)[:, None], (n, n))
    s = np.clip(u/UB, 0., 1.)*g.S_TOT
    base, gloss, groove = body_layer(s, vt)
    # head zone: darker wrinkled hide, no annulus grooves, pink lip
    hz = sstep(s, g.S_HEAD-3.0, g.S_HEAD+.5)
    hmid = mix(np.broadcast_to(HEAD_BELLY, s.shape+(3,)), np.broadcast_to(HEAD_FLANK, s.shape+(3,)), sstep(vt, .16, .56))
    head = mix(hmid, np.broadcast_to(HEAD_DORSAL, s.shape+(3,)), sstep(vt, .58, .95))
    wr = vnoise(s/1.6, vt*math.pi*8./1.6, 23)+.6*vnoise(s/.7, vt*math.pi*8./.7, 29)
    ridge = .5+.5*np.sin(s*2.1+3.*vnoise(s/3., vt*4., 31)+vt*3.)
    crease = np.exp(-((((s*.6+2.2*vnoise(s/2.5, vt*5., 37)) % 1.)-.5)/.07)**2)
    head = head*(.72+.34*ridge[..., None])*(1+.3*wr[..., None])*(1-.55*crease[..., None])
    hgloss = np.clip(np.exp(-((s-(g.S_HEAD+2.5))/2.8)**2)*np.exp(-((vt-.78)/.10)**2)*.2
                     +.45*np.clip((vnoise(s/.5, vt*20., 41)-.28)*6., 0., 1.)*sstep(vt, .4, .8), 0., .9)
    base = mix(base, head, hz)
    gloss = gloss*(1-hz)+hgloss*hz
    img = mix(base, np.broadcast_to(WET, s.shape+(3,)), gloss*.7)
    img = np.clip(img, 0, 255)
    # palette columns: teeth (yellow root -> ivory tip) and throat well (dark centre -> red rim)
    tx0, tx1 = PALETTE_TEETH
    xx = xs[None, :]
    tv = np.broadcast_to(1-ys[:, None], (n, n))
    tooth = mix(mix(np.broadcast_to(col(46, 32, 24), (n, n, 3)), np.broadcast_to(col(178, 148, 106), (n, n, 3)),
                    sstep(tv, .04, .4)), np.broadcast_to(col(246, 238, 214), (n, n, 3)), sstep(tv, .3, .95))
    throat = mix(mix(np.broadcast_to(col(22, 4, 6), (n, n, 3)), np.broadcast_to(col(78, 18, 26), (n, n, 3)), sstep(tv, .05, .55)),
                 np.broadcast_to(col(132, 46, 44), (n, n, 3)), sstep(tv, .5, .98))
    crest = 1-np.abs(2*tv-1)                        # 0 at the lip's rims, 1 along its crest
    lip = mix(mix(np.broadcast_to(col(58, 24, 22), (n, n, 3)), np.broadcast_to(LIP, (n, n, 3)), sstep(crest, .0, .6)),
              np.broadcast_to(col(150, 78, 62), (n, n, 3)), sstep(crest, .72, 1.))
    ct = np.clip((xx-PALETTE_CHITIN[0])/(PALETTE_CHITIN[1]-PALETTE_CHITIN[0]), 0., 1.)*np.ones((n, 1))
    keel = np.exp(-((np.sin(math.tau*ct*1.)**2)/.05)) + 0*ct       # dark seams along the plate's edges
    chitin = mix(mix(np.broadcast_to(col(40, 28, 20), (n, n, 3)), np.broadcast_to(col(150, 112, 66), (n, n, 3)), sstep(tv, .0, .85)),
                 np.broadcast_to(col(196, 164, 110), (n, n, 3)), .5*np.exp(-((np.cos(math.tau*ct)+1)/.5)**2)*sstep(tv, .2, .9))
    chitin = mix(chitin, np.broadcast_to(col(26, 18, 12), (n, n, 3)), .75*keel)
    img = np.where(((xx >= PALETTE_CHITIN[0]) & (xx < PALETTE_CHITIN[1]))[..., None], chitin, img)
    img = np.where(((xx >= tx0) & (xx < tx1))[..., None], tooth, img)
    img = np.where(((xx >= PALETTE_LIP[0]) & (xx < PALETTE_LIP[1]))[..., None], lip, img)
    img = np.where((xx >= PALETTE_THROAT[0])[..., None], throat, img)
    # gutter between the body zone and the palette repeats the body's last column
    gut = (xx > UB) & (xx < tx0)
    edge = img[:, int(UB*(n-1)):int(UB*(n-1))+1, :]
    img = np.where(gut[..., None], np.broadcast_to(edge, img.shape), img)
    raw = np.rint(img).astype(np.uint8).tobytes()
    return encode_png(raw, n, n)
