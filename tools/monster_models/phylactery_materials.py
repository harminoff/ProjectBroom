"""Original painted atlas for the phylactery: gilt metal, serpentine, bone and
a fullbright lich-green soul gem (column 3). Painted for flat engine light:
facet-by-facet values, lit tops, dark undersides. No imported artwork."""
import numpy as np
from . import relic_kit as kit

ATLAS = kit.Atlas({'onyx': (0, 0), 'gold': (1, 0), 'bone': (2, 0), 'dark': (0, 1), 'gem': (3, 0)})


def _facets(U, n):
    return np.floor(np.clip(U, 0, .999)*n)


def pigment(role, U, V):
    if role == 'gold':
        f = _facets(U, 8); fu = U*8-f
        # Polished antique gilt: hard facet contrast and a bright specular
        # stripe per facet read as metal under flat light; dark tarnish
        # collects only in the engraved rings, never as wood-like grain.
        d = np.where(f % 2 == 0, 18.0, -30.0)+48*(V-.5)
        spec = np.exp(-(fu-.3)**2/.004)
        ring = np.abs(np.sin(V*np.pi*7)) < .09
        base = (170, 124, 46)
        rgb = [base[0]+d, base[1]+d*.85, base[2]+d*.45]
        rgb = kit.mix(rgb, (255, 236, 168), spec*.8)
        rgb = kit.mix(rgb, (48, 30, 14), ring*.85)
        rgb = kit.mix(rgb, (92, 60, 26), np.clip((.12-V)/.12, 0, 1)*.6)
    elif role == 'onyx':
        f = _facets(U, 8)
        vein = np.abs(kit.fbm(U, V, 4, 11)+.4*kit.fbm(U, V, 13, 5))
        d = np.where(f % 2 == 0, 10.0, -8.0)+34*(V-.5)+8*kit.fbm(U, V, 30, 7)
        base = np.array((52, 64, 58), dtype=float)
        rgb = [base[k]+d for k in range(3)]
        rgb = kit.mix(rgb, (150, 170, 150), (vein < .05)*.75+(vein < .1)*.2)
    elif role == 'bone':
        d = 12*kit.fbm(U, V, 9, 2)-44*(1-V)**2+10*V
        d -= 55*(np.abs(kit.fbm(U, V, 5, 21)) < .025)
        rgb = [218+d, 204+d, 168+d*.9]
    elif role == 'dark':
        d = 6*kit.fbm(U, V, 10, 4)
        rgb = [12+d, 18+d, 13+d]
    elif role == 'gem':
        # Same soul gem as the lich carries (lich_materials GLOW/GLOW_DARK,
        # both from Brogue's lichLightColor): lit facets burn mint-teal,
        # alternate facets stay deep green.
        f = _facets(U, 2); fu = U*2-f
        lit = kit.mix((120, 255, 182), (160, 255, 214), np.clip(.25+.6*np.exp(-(V-.36)**2/.01), 0, 1))
        dark = kit.mix((18, 128, 80), (40, 170, 110), np.clip(V*1.2, 0, 1))
        rgb = [np.where(f == 0, a, b) for a, b in zip(lit, dark)]
        glint = np.exp(-((fu-.28)**2)/.004-((V-.62)**2)/.02)*(f == 0)
        rgb = kit.mix(rgb, (200, 255, 230), glint*.8)
        smoke = np.clip(1-np.abs(kit.fbm(U*1.3+V*.8, V, 3, 31))*9, 0, 1)*np.clip((V-.1)*3, 0, 1)*np.clip((.9-V)*4, 0, 1)
        rgb = kit.mix(rgb, (12, 96, 62), smoke*.45)
        rgb = kit.mix(rgb, (190, 255, 225), np.clip((V-.94)/.06, 0, 1))
    else:
        raise ValueError(role)
    return rgb


def texture_bytes():
    return ATLAS.paint(pigment)
