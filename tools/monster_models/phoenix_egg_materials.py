"""Original painted atlas for the phoenix egg: pale cooling ash, charred
twigs, and a fullbright membrane (column 3) painted with the yolk's glow
showing through, dark capillary veins and bright ember cracks along the
plate seams. phoenixColor (red/orange) is an identity cue. No imported art."""
import numpy as np
from . import relic_kit as kit

ATLAS = kit.Atlas({'ash': (0, 0), 'char': (1, 0), 'shell': (3, 0), 'cap': (3, 1), 'inner': (3, 2), 'yolk': (3, 3)})
CUT_FRACTION = .72


def _membrane(U, V, h, seam_u, seam_v):
    """Dark ember-red membrane lit from within, split by a bright network of
    ember cracks; the yolk's glow shows through as a hot central band."""
    glow = np.exp(-((h-.5)/.3)**2)
    rgb = kit.mix((70, 8, 4), (214, 64, 14), glow*.85+.1)
    rgb = kit.mix(rgb, (255, 176, 60), glow**3*.55)
    vein = np.abs(kit.fbm(U*1.6, h*1.2, 6, 41)) < .04
    rgb = kit.mix(rgb, (46, 4, 2), vein*.6)
    n = np.abs(kit.fbm(U*2.2+.3, h*1.6, 4, 57))
    rim = (n < .075) & (h > .12)
    crack = (n < .032) & (h > .12)
    rgb = kit.mix(rgb, (30, 3, 1), (rim & ~crack)*.8)
    rgb = kit.mix(rgb, (255, 226, 120), crack*1.0)
    # Plate seams are darker hairline splits edged with a faint ember line.
    rgb = kit.mix(rgb, (120, 24, 6), seam_u*.55)
    rgb = kit.mix(rgb, (255, 232, 140), seam_v*1.0)
    return rgb


def pigment(role, U, V):
    if role == 'ash':
        d = 34*(V-.5)+10*kit.fbm(U, V, 30, 1)
        soot = np.clip(kit.fbm(U, V, 7, 3)*1.8-.1, 0, 1)
        rgb = [102+d, 96+d, 92+d]
        rgb = kit.mix(rgb, (42, 36, 33), soot*.8)
        streak = np.abs(np.sin(U*np.pi*22+kit.fbm(U, V, 5, 17)*4)) < .12
        rgb = kit.mix(rgb, (36, 30, 28), streak*np.clip(1-V*1.3, 0, 1)*.6)
        dust = np.clip(kit.fbm(U, V, 16, 6)*2, 0, 1)*np.clip((V-.35)*2, 0, 1)
        rgb = kit.mix(rgb, (196, 190, 182), dust*.6)
        rgb = kit.mix(rgb, (176, 118, 84), np.clip((V-.6)/.4, 0, 1)*.45)
        speck = kit.hash2(np.floor(U*300), np.floor(V*300), 5) > .86
        rgb = kit.mix(rgb, (230, 226, 218), speck*.5)
    elif role == 'char':
        d = 10*kit.fbm(U, V, 20, 2)
        rgb = [58+d, 44+d, 36+d]
        ashy = np.clip(kit.fbm(U, V*3, 5, 8)*2+.2, 0, 1)
        rgb = kit.mix(rgb, (158, 150, 142), ashy*.65)
        split = np.abs(np.sin(V*60+kit.fbm(U, V, 4, 4)*3)) < .08
        rgb = kit.mix(rgb, (14, 10, 9), split*.8)
    elif role == 'shell':
        rgb = _membrane(U, V, V*CUT_FRACTION, (U < .02) | (U > .98), V > .975)
    elif role == 'cap':
        rgb = _membrane(U, V, CUT_FRACTION+V*(1-CUT_FRACTION), np.zeros_like(U, dtype=bool), V < .04)
    elif role == 'inner':
        rgb = kit.mix((255, 170, 60), (255, 244, 196), np.clip(1-np.abs(V-.5)*1.6, 0, 1))
    elif role == 'yolk':
        rgb = kit.mix((255, 132, 30), (255, 252, 222), np.clip(1-np.abs(V-.55)*2.1, 0, 1))
    else:
        raise ValueError(role)
    return rgb


def texture_bytes():
    return ATLAS.paint(pigment)
