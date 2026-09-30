"""Painted stone for the stone guardian: warm weathered sandstone knight with a
dark basalt battleaxe. Built on the golem's stone pigment (read-only import).

Art direction only. Brogue's glyph colour for the guardian is white; the warm
pale sandstone keeps the statue far lighter and warmer than the blue-grey
cobblestone walls, and the dark axe gives the weapon its own silhouette.
"""
from . import golem_materials as GM
from . import guardian_kit as K

PALETTE = GM.Palette(stone=(204, 178, 132), core=(52, 44, 38), void=(14, 11, 10), fleck_light=26.0, fleck_dark=30.0,
                     wear=56.0, occlusion=.9, tint=9.0)


def feature(name):
    if name in ('belt', 'gorget', 'lame_upper'): return 3          # incised glyph bands
    if name.startswith(('cuff_', 'couter_')): return 2
    if name.startswith(('rerebrace_', 'vambrace_', 'cuisse_', 'greave_')): return 6
    if name.startswith('sabaton'): return 7
    if name.startswith('pauldron_') and 'lame' not in name: return 4
    return 0


def extras(parts):
    import numpy as np
    names = [p.name for p in parts]
    is_axe = np.array([n.startswith('axe_') for n in names]); is_bit = np.array([n.startswith('axe_bit') for n in names])
    bit_sign = np.array([1.0 if n == 'axe_bit_1' else -1.0 for n in names])
    beard = np.array([n in ('face_beard', 'face_moustache') for n in names])
    cape = np.array([n == 'cape' for n in names]); tabard = np.array([n == 'tabard' for n in names])
    face = np.array([n.startswith('face_') and 'eye' not in n for n in names])

    def extra(np, P, L, N, E, AO, pi, col, spec):
        ax = is_axe[pi]
        if ax.any():
            # Dark basalt axe: cool, darker, with pale honed cutting edges.
            lum = col.mean(1, keepdims=True)
            dark = lum*.46+np.array([[6, 8, 12]])
            col[ax] = dark[ax]
            edge = np.clip((L[:, 1]*bit_sign[pi]-.62)/.3, 0, 1)*is_bit[pi]
            col += (edge*96)[:, None]*np.array([[1.0, 1.0, 1.04]])
            spec[:] = np.where(ax, 40+60*edge, spec)
        b = beard[pi]
        if b.any():
            # Carved beard locks: vertical grooves with a lit ridge.
            wave = np.sin(L[:, 1]*9.5+np.sin(L[:, 2]*3)*1.2)
            col *= np.where(b, .88+.14*wave, 1.0)[:, None]
        c = cape[pi] | tabard[pi]
        if c.any():
            # Heavy carved drapery folds: vertical grooves that deepen toward the hem.
            depth = np.clip(-L[:, 2]*.6+.5, .25, 1)
            fold = np.sin(P[:, 1]*.95+.4*np.sin(P[:, 2]*.2))
            col *= np.where(c, 1+.24*fold*depth, 1.0)[:, None]
        f = face[pi]
        if f.any():
            # The carved face catches light: lift it above the helm shadow.
            col *= np.where(f, 1.12, 1.0)[:, None]
    return extra


def paint(parts):
    return K.paint(parts, K.stone_pigment(parts, PALETTE, feature, extras(parts)))
