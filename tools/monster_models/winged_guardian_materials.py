"""Painted marble for the winged guardian: pale blue-grey statuary marble with
lapis-blue veining, carved feather vanes and a polished blue-grey stone sword.
Built on the golem's stone pigment (read-only import).

Art direction only. Brogue's glyph colour for the winged guardian is blue; it
tints the whole statue (cool steel-blue stone, near-white highlights, deep lapis veins and slate feather gaps), never as glow. The marble
separates strongly from the dark blue-grey cobblestone walls.
"""
import math
from . import golem_materials as GM
from . import guardian_kit as K

PALETTE = GM.Palette(stone=(172, 190, 220), core=(44, 52, 74), void=(16, 20, 34), fleck_light=14.0, fleck_dark=18.0,
                     wear=40.0, occlusion=.9, tint=6.0)


def feature(name):
    if name in ('belt', 'gorget', 'circlet'): return 3
    if name.startswith(('cuff_', 'couter_')): return 2
    if name.startswith(('rerebrace_', 'vambrace_', 'cuisse_', 'greave_')): return 6
    if name.startswith('sabaton'): return 7
    return 0


def extras(parts):
    import numpy as np
    names = [p.name for p in parts]
    sword = np.array([n.startswith('sword_') and n != 'sword_fuller' for n in names])
    blade = np.array([n == 'sword_blade' for n in names])
    feather = np.array([n.startswith(('wing_feather', 'wing_covert')) for n in names])
    fidx = np.array([int(n.rsplit('_', 1)[1]) if n.startswith(('wing_feather', 'wing_covert')) else 0 for n in names])
    rowidx = np.array([int(n.split('_r')[1].split('_')[0]) if n.startswith('wing_covert') else 0 for n in names])
    hair = np.array([n.startswith(('hair_',)) for n in names])
    robe = np.array([n.startswith('robe_') for n in names])
    face = np.array([n.startswith('face_') and 'eye' not in n for n in names])

    def extra(np, P, L, N, E, AO, pi, col, spec):
        # Lapis-blue veining through the marble (low-frequency turbulent bands).
        turb = GM.fbm(np, P*.09, 71)
        vein = np.clip(1-np.abs(np.sin(P[:, 0]*.21+P[:, 2]*.13+turb*9.0))/.08, 0, 1)
        col += (vein*70)[:, None]*np.array([[-.95, -.55, .25]])   # deep saturated lapis veins
        sw = sword[pi]
        if sw.any():
            lum = col.mean(1, keepdims=True)
            steel = lum*.62+np.array([[4, 12, 26]])
            col[sw] = steel[sw]
            edge = np.clip((np.abs(L[:, 1])-.55)/.35, 0, 1)*blade[pi]
            col += (edge*110)[:, None]
            spec[:] = np.where(sw, 50+80*edge, spec)
        f = feather[pi]
        if f.any():
            # Carved vanes: a central shaft groove and angled barb lines.
            shaft = np.clip(1-np.abs(L[:, 1])/.09, 0, 1)*(L[:, 0] < 0)
            barb = .5+.5*np.sin((np.abs(L[:, 1])*3.2+L[:, 2]*2.6)*math.pi*2.2)
            shade = 1-.28*shaft-.14*barb*np.clip(np.abs(L[:, 1])*1.4, 0, 1)
            # Feather tips catch light; the roots sink into shadow under the coverts.
            shade *= .82+.3*np.clip(L[:, 2]*.5+.5, 0, 1)
            # Value range: dark gaps at the vane edges and roots, shaded undersides,
            # and alternate feathers a step darker so the fan reads against a wall.
            edge = np.clip((np.abs(L[:, 1])-.55)/.4, 0, 1)
            shade *= 1-.3*edge**1.5
            shade *= 1-.22*np.clip((-L[:, 2]-.1)/.7, 0, 1)
            shade *= 1-.14*np.clip((-N[:, 2]-.1)/.6, 0, 1)
            shade *= 1-.08*(fidx[pi] % 2)
            shade *= 1-.05*rowidx[pi]
            shade *= 1-.15*np.clip(AO, 0, 1)
            shade = np.clip(shade*1.12, .5, 1.15)
            # The dense overlapping vanes would otherwise be crushed by ambient occlusion; relax it.
            shade = shade*np.clip((1-.35*np.clip(AO, 0, 1))/(1-PALETTE.occlusion*np.clip(AO, 0, 1)), 1.0, 4.0)
            slate = np.array([[34.0, 50.0, 96.0]])   # deep slate-blue gaps between vanes
            col = np.where(f[:, None], col*shade[:, None]+(1-np.minimum(shade, 1.0))[:, None]*slate*.9, col)
        h = hair[pi]
        if h.any():
            wave = np.sin(L[:, 1]*7.0+L[:, 2]*3.0+np.sin(L[:, 0]*5)*1.1)
            col *= np.where(h, .74+.14*wave, 1.0)[:, None]
        r = robe[pi]
        if r.any():
            fold = np.sin((P[:, 1]+P[:, 0])*1.05+.4*np.sin(P[:, 2]*.2))
            col *= np.where(r, 1+.2*fold*np.clip(.5-L[:, 2]*.5, .3, 1), 1.0)[:, None]
        fa = face[pi]
        if fa.any(): col *= np.where(fa, 1.12, 1.0)[:, None]
    return extra


def paint(parts):
    return K.paint(parts, K.stone_pigment(parts, PALETTE, feature, extras(parts)))
