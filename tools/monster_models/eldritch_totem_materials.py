"""Original painted atlas for the eldritch totem: dark red-violet twisted
stone with pale ridge highlights and colour-keyed glyph channels, dark iron,
a fullbright red ichor core and fullbright spectral-blue blades (column 3).
glyphColor (dark red) and spectralBladeColor (blue) are identity cues only."""
import numpy as np
from . import relic_kit as kit

ATLAS = kit.Atlas({'stone': (0, 0), 'metal': (1, 0), 'spur': (2, 0), 'core': (3, 0), 'blade': (3, 1)})
GLYPH = (255, 40, 30)  # exact key colour; the shader keys r>=.9, g,b<=.3


def _glyphs(U, V):
    """Alien stroke glyphs down the centre of each of the five facets."""
    f = np.floor(np.clip(U, 0, .999)*5); fu = U*5-f
    x = (fu-.5)/.5  # -1..1 across a facet
    row = np.floor(V*5); fv = V*5-row
    h = (kit.hash2(f*7+3, row*13+5, 7)+1)/2
    y = (fv-.5)/.5
    inside = (np.abs(x) < .55) & (np.abs(y) < .75)
    bar = np.abs(y) < .12
    stem = np.abs(x) < .09
    ring = np.abs(np.hypot(x*1.4, y)-.5) < .11
    chevron = np.abs(np.abs(x)*1.1-y*.8) < .12
    tri = (np.abs(y+.55) < .1) | (np.abs(np.abs(x)*1.6+y*.9-.35) < .11)
    hook = (np.abs(np.hypot(x-.15, y-.2)-.32) < .1) & (x < .3) | (np.abs(x-.15) < .09) & (y < .2)
    dots = (np.hypot(x-.25, y+.3) < .14) | (np.hypot(x+.25, y-.3) < .14) | (np.hypot(x, y) < .1)
    mark = np.select([h < .15, h < .3, h < .45, h < .6, h < .75], [bar | stem, ring | stem, chevron | bar, tri, hook], dots)
    return inside & mark & (V > .12) & (V < .88) & ((f+row) % 2 == 0)


def pigment(role, U, V):
    if role == 'stone':
        f = np.floor(np.clip(U, 0, .999)*5); fu = U*5-f
        ridge = np.clip(1-np.minimum(fu, 1-fu)/.1, 0, 1)
        d = 40*(V-.5)+np.where(f % 2 == 0, 8.0, -8.0)+10*kit.fbm(U, V, 12, 3)
        base = np.array((64, 34, 50), float)
        rgb = [base[k]+d*m for k, m in enumerate((1, .75, .95))]
        rgb = kit.mix(rgb, (156, 136, 156), ridge*.8)
        rgb = kit.mix(rgb, (104, 84, 110), np.clip((V-.72)/.28, 0, 1)*.5)
        vein = np.abs(kit.fbm(U*2, V, 6, 9)) < .035
        rgb = kit.mix(rgb, (18, 8, 14), vein*.85)
        rgb = [np.minimum(c, 205) for c in rgb]
        g = _glyphs(U, V)
        halo = _glyphs(np.clip(U+.012, 0, 1), V) | _glyphs(np.clip(U-.012, 0, 1), V)
        rgb = kit.mix(rgb, (28, 6, 8), (halo & ~g)*.9)
        rgb = kit.mix(rgb, GLYPH, g*1.0)
    elif role == 'spur':
        d = 30*(V-.5)+8*kit.fbm(U, V, 16, 6)
        rgb = kit.mix((40, 22, 30), (196, 182, 170), np.clip((V-.55)/.45, 0, 1))
        rgb = [c+d for c in rgb]
    elif role == 'metal':
        d = 30*(V-.5)+12*kit.fbm(U, V, 20, 4)
        rgb = [52+d, 46+d*.9, 50+d]
        rust = np.clip(kit.fbm(U, V, 6, 12)-.1, 0, 1)
        rgb = kit.mix(rgb, (96, 36, 24), rust)
        rgb = kit.mix(rgb, (150, 140, 150), np.clip(1-np.abs(V-.5)/.08, 0, 1)*.6)
    elif role == 'core':
        pulse = .5+.5*np.sin(V*np.pi*6)
        rgb = kit.mix((200, 20, 16), (255, 150, 90), pulse*.6)
        rgb = kit.mix(rgb, (255, 235, 200), np.clip(1-np.abs(U-.5)/.08, 0, 1)*.5)
    elif role == 'blade':
        edge = np.clip(1-np.minimum(V, 1-V)/.22, 0, 1)
        rgb = kit.mix((42, 52, 150), (170, 196, 255), edge)
        rgb = kit.mix(rgb, (232, 240, 255), np.clip(1-np.minimum(V, 1-V)/.07, 0, 1)*.9)
        fuller = np.abs(V-.5) < .05
        rgb = kit.mix(rgb, (26, 30, 96), fuller*(U > .08)*(U < .78)*.8)
        rgb = kit.mix(rgb, (120, 140, 230), np.clip((U-.8)/.2, 0, 1)*.6)
        rgb = [c+10*kit.fbm(U, V, 14, 2) for c in rgb]
    else:
        raise ValueError(role)
    return rgb


def texture_bytes():
    return ATLAS.paint(pigment)
