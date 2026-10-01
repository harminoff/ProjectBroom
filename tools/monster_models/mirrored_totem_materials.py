"""Original painted atlas for the mirrored totem: blue-black carved lacquer,
engraved pewter, bright polished silver bosses, opaque silver-mirror glass
(column 2, one cell per face plus one for the crown shards; the shader adds
a view-dependent term) and a fullbright white flash crystal (column 3).
beckonColor is near-black; the painted mirror reads cool silver so the prism
separates from grey walls and dark floors. No imported artwork."""
import numpy as np
from . import relic_kit as kit

ATLAS = kit.Atlas({'lacquer': (0, 0), 'pewter': (1, 0), 'silver': (1, 1),
                   'mirror_0': (2, 0), 'mirror_1': (2, 1), 'mirror_2': (2, 2), 'mirror_3': (2, 3),
                   'flash': (3, 0)})
# Per face: horizon height, streak angle, streak offsets, upper-band tint.
FACE_STYLE = {
    'mirror_0': (.42, .55, (.05, .31), (112, 122, 142)),
    'mirror_1': (.48, -.45, (.18, .52), (96, 104, 124)),
    'mirror_2': (.38, .8, (.12, .44, .7), (120, 128, 146)),
    'mirror_3': (.45, .35, (.2,), (132, 140, 160)),
}


def mirror(role, U, V):
    """Opaque polished mirror: a dark cave/floor reflection below, a bright
    horizon streak, darker cool upper reflections with angled highlight
    streaks, and a thin dark bevel; each face has its own banding."""
    horizon, slope, offsets, upper = FACE_STYLE[role]
    seed = int(role[-1])
    floor_band = kit.mix((24, 22, 24), (58, 54, 56), np.clip(V/horizon, 0, 1)**2)
    rgb = kit.mix(floor_band, upper, np.clip((V-horizon)/.04, 0, 1))
    # upper reflections fall off quickly into a dark vault
    rgb = kit.mix(rgb, (52, 58, 76), np.clip((V-horizon-.03)/.2, 0, 1))
    rgb = kit.mix(rgb, (24, 26, 36), np.clip((V-horizon-.25)/(.75-horizon), 0, 1))
    # soft reflected pillars and wall blocks
    pillars = np.clip(np.sin((U*2.3+seed*.37)*np.pi*2)*2-1.2, 0, 1)
    rgb = kit.mix(rgb, (16, 16, 22), pillars*.5*(V > horizon))
    blocks = kit.fbm(U*1.4, V, 5, 60+seed)
    rgb = [c+12*blocks*(V > horizon) for c in rgb]
    band = np.exp(-((V-horizon-.012)/.022)**2)
    rgb = kit.mix(rgb, (236, 242, 255), band*.95)
    rgb = kit.mix(rgb, (150, 158, 176), np.exp(-((V-horizon-.07)/.03)**2)*.5)
    for o in offsets:
        d = ((U+V*slope-o) % 1.4)
        streak = np.exp(-((d-.0)/.025)**2)+np.exp(-((d-.06)/.012)**2)*.6
        rgb = kit.mix(rgb, (226, 234, 250), np.clip(streak, 0, 1)*.7*(V > horizon*.6))
    edge = np.clip(1-np.minimum(np.minimum(U, 1-U), np.minimum(V, 1-V))/.035, 0, 1)
    rgb = kit.mix(rgb, (20, 20, 28), edge*.8)
    return rgb


def pigment(role, U, V):
    if role == 'lacquer':
        f = np.floor(np.clip(U, 0, .999)*6); fu = U*6-f
        d = 40*(V-.5)+np.where(f % 2 == 0, 9.0, -7.0)+6*kit.fbm(U, V, 18, 2)
        rgb = [28+d, 30+d, 44+d*1.1]
        # carved recessed panels with pale engraved borders on every facet
        inset = (np.abs(fu-.5) < .36) & (((V > .12) & (V < .28)) | ((V > .42) & (V < .56)) | ((V > .7) & (V < .86)))
        border = (np.abs(np.abs(fu-.5)-.36) < .03) & (V > .1) & (V < .88)
        rgb = kit.mix(rgb, (14, 14, 22), inset*.55)
        rgb = kit.mix(rgb, (150, 158, 176), border*.75)
    elif role == 'pewter':
        fu = (U*8) % 1
        d = 44*(V-.5)+34*np.exp(-(fu-.3)**2/.01)-20*np.exp(-(fu-.75)**2/.02)+8*kit.fbm(U, V, 24, 5)
        rgb = [112+d, 116+d, 128+d]
        engraved = np.abs(np.sin(V*np.pi*4)) < .06
        rgb = kit.mix(rgb, (38, 38, 46), engraved*.65)
    elif role == 'silver':
        fu = (U*4) % 1
        d = 50*(V-.5)+50*np.exp(-(fu-.3)**2/.01)
        rgb = [190+d, 196+d, 210+d]
    elif role.startswith('mirror'):
        rgb = mirror(role, U, V)
    elif role == 'flash':
        rgb = kit.mix((255, 230, 170), (255, 255, 250), np.clip(1-np.abs(V-.5)*2.2, 0, 1))
    else:
        raise ValueError(role)
    return rgb


def texture_bytes():
    return ATLAS.paint(pigment)
