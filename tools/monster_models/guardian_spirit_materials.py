"""Crimson spectral paint for the guardian spirit, drawn for additive fullbright
rendering (``shaders/guardian-spirit-glow.fp``): black is empty, so bright plate
edges form a glowing outline around a dim crimson core. The palette is the
spectral sword's (Brogue's ``spectralImageColor``, a dark red with a dancing
red component): deep crimson, rose, pink-white, with a brighter pink-white axe.

Art direction only. Original Project Broom art; no imported artwork.
"""
from . import golem_materials as GM
from . import guardian_kit as K

DEEP = (92, 8, 28)
MID = (226, 52, 76)
PINK = (244, 104, 118)
HOT = (255, 232, 228)


def paint(parts):
    import numpy as np
    names = [p.name for p in parts]
    axe = np.array([n.startswith('axe_') for n in names]); bit = np.array([n == 'axe_bit' for n in names])
    eye = np.array([p.role == 'void' for p in parts]); core = np.array([p.role == 'core' for p in parts])
    trim = np.array([n in ('belt', 'gorget', 'lame_upper', 'helm_band', 'helm_crest', 'cape_clasp') or n.startswith(('cuff_', 'pauldron_lame', 'fauld_'))
                     for n in names])
    cape = np.array([n == 'cape' for n in names])

    def ramp(v):
        """Deep crimson -> rose -> pink -> pink-white by value (like the sword's blade ramp)."""
        stops = [(0.0, (0, 0, 0)), (.12, DEEP), (.5, MID), (.8, PINK), (1.0, HOT)]
        xs = [x for x, c in stops]
        return np.stack([np.interp(v, xs, [c[i] for x, c in stops]) for i in range(3)], 1)

    def pigment(np, P, L, N, E, CH, AO, pi):
        n = len(P)
        edge = np.clip(E, 0, 1)**.9
        shimmer = GM.fbm(np, P*.18, 91)
        streak = GM.vnoise(np, np.stack([P[:, 0]*.4, P[:, 1]*.4, P[:, 2]*.06], 1), 92)
        inner = .1+.14*shimmer+.06*streak
        value = np.clip(inner+.8*edge, 0, 1.15)*(1-.5*np.clip(AO, 0, 1))
        value *= .85+.25*np.clip(N[:, 2], -1, 1)
        col = ramp(np.clip(value, 0, 1))
        # Trim bands, crest and clasp: brighter lines.
        col = np.where(trim[pi][:, None], col*1.25+24, col)
        # The weightless legs and cloak hem fade to black, which is empty in additive rendering.
        fade = np.clip((P[:, 2]-8.5)/10.0, 0, 1)
        fade = np.where(cape[pi], np.clip((P[:, 2]-11.0)/16.0, 0, 1)*.9, fade)
        col *= fade[:, None]
        # Axe: a brighter crimson pink-white with a white-hot cutting edge.
        a = axe[pi]
        if a.any():
            edge_bit = np.clip((L[:, 0]-.55)/.35, 0, 1)*bit[pi]
            ac = ramp(np.clip(.62+.28*edge+.1*shimmer, 0, 1))+255*edge_bit[:, None]*.35
            col = np.where(a[:, None], ac, col)
        # Visor slits are the brightest light of all; the core joints stay dim crimson.
        col = np.where(eye[pi][:, None], np.array([[255, 236, 232]]), col)
        col = np.where(core[pi][:, None], col*.35, col)
        return col, np.full(n, 0.0)
    return K.paint(parts, pigment, background=(0, 0, 0), spec_bg=0)
