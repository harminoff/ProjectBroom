"""Painted indigo stone and glowing warding crystal for the sentinel.

Stone uses the golem's pigment (read-only import) with a weathered indigo
slate palette. Crystal islands live only in the atlas region
``sentinel_animation.GLOW_REGION``; ``shaders/sentinel-crystal.fp`` renders
exactly that region fullbright. Colours follow Brogue's sentinel glyph
(3, 3, 30) and sentinel light (20, 20, 120) as cues, not literal materials.
"""
from . import golem_materials as GM
from . import guardian_kit as K

PALETTE = GM.Palette(stone=(92, 96, 146), core=(26, 26, 42), void=(10, 10, 18), fleck_light=22.0, fleck_dark=24.0,
                     wear=46.0, occlusion=.85, tint=8.0)


def feature(name):
    if name in ('robe_band', 'mantle', 'collar'): return 3
    if name.startswith('sleeve_'): return 6
    if name.startswith('plinth'): return 7
    return 0


def paint(parts):
    import numpy as np
    glow = np.array([p.role == 'glow' for p in parts])
    stone = K.stone_pigment(parts, PALETTE, feature)

    def pigment(np, P, L, N, E, CH, AO, pi):
        col, level = stone(np, P, L, N, E, CH, AO, pi)
        g = glow[pi]
        if g.any():
            # Faceted crystal: each facet a different blue, bright pale core and edges.
            facet = .5+.5*np.sin(N[:, 0]*5.1+N[:, 1]*3.7+N[:, 2]*4.3)
            core = np.clip(1-np.sqrt(L[:, 0]**2+L[:, 1]**2), 0, 1)
            tip = np.clip(np.abs(L[:, 2]), 0, 1)
            deep = np.array([34, 70, 210]); mid = np.array([80, 150, 255]); pale = np.array([200, 235, 255])
            c = deep[None, :]*(1-facet[:, None])+mid[None, :]*facet[:, None]
            c = c+(pale-c)*np.clip(.55*core+.55*E+.35*tip**3, 0, 1)[:, None]
            col = np.where(g[:, None], c, col)
            level = np.where(g, 160, level)
        return col, level
    return K.paint(parts, pigment)
