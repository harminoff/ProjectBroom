"""Original painted atlas for the phoenix. No imported art, no gameplay.

Brogue colours the phoenix `phoenixColor` (red with a large random green
component), so the bird's identity is a flame gradient: crimson roots through
scarlet and orange to gold-yellow tips. Column 3 (u >= 0.75) is fullbright
(flame plumes, tongues, embers, eyes, see phoenix-fire.fp); columns 0-2 are lit
body plumage, horn and ash, painted with a deliberately wide warm value range
so the form still reads under the engine's flat light. The palette matches the
phoenix egg's (dark ember red, orange, gold-white cracks).
"""
import numpy as np
from . import relic_kit as kit

ATLAS = kit.Atlas({
    'body': (0, 0), 'feather': (0, 1), 'beak': (0, 2), 'talon': (0, 3),
    'leg': (1, 0), 'ash': (1, 1), 'brow': (1, 2),
    'flame': (3, 0), 'plume': (3, 1), 'ember': (3, 2), 'eye': (3, 3)})

CRIMSON = (78, 8, 10)
BLOOD = (128, 14, 14)
SCARLET = (205, 30, 16)
ORANGE = (240, 108, 20)
GOLD = (255, 190, 58)
PALE = (255, 232, 130)


def ramp(t, stops):
    """Piecewise-linear colour ramp over (position, colour) stops."""
    t = np.asarray(t, dtype=np.float64)
    rgb = [np.zeros_like(t) for _ in range(3)]
    for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
        m = np.clip((t-p0)/(p1-p0), 0, 1)
        inside = (t >= p0) & (t < p1) if p1 < stops[-1][0] else (t >= p0)
        for k in range(3):
            rgb[k] = np.where(inside, c0[k]*(1-m)+c1[k]*m, rgb[k])
    for k in range(3):
        rgb[k] = np.where(t < stops[0][0], stops[0][1][k], rgb[k])
    return rgb


def _feather(U, V):
    """Lit flight feather, root U=0 to tip U=1, shaft along V=.5."""
    across = np.abs(V-.5)*2
    rgb = ramp(U, ((0, CRIMSON), (.3, BLOOD), (.55, SCARLET), (.8, ORANGE), (.95, GOLD), (1, PALE)))
    barb = np.sin((V-.5)*62+U*26+kit.fbm(U, V, 9, 4)*2.4)
    rgb = kit.mix(rgb, (60, 4, 8), np.clip(-barb, 0, 1)*.34*(1-U*.5))
    rgb = kit.mix(rgb, (255, 210, 110), np.clip(barb, 0, 1)*.16*U)
    shaft = across < .075
    rgb = kit.mix(rgb, (255, 226, 132), shaft*(.35+.5*U))
    # darker, crisper vane edge keeps the silhouette readable against flame
    rgb = kit.mix(rgb, (52, 4, 6), np.clip((across-.82)/.18, 0, 1)*.3*(1-U*.7))
    rgb = kit.mix(rgb, (255, 236, 150), np.clip((U-.93)/.07, 0, 1)*.55)
    return rgb


def _body(U, V):
    """Blob UV: U around (0 = back, .5 = belly), V along (0 tail, 1 head)."""
    belly = (1-np.cos(U*(2*np.pi)))/2
    rgb = kit.mix((150, 16, 12), (226, 70, 18), belly**.8)
    rgb = kit.mix(rgb, GOLD, np.clip((belly-.55)/.45, 0, 1)*np.clip((V-.35)*1.6, 0, 1)*.85)
    rgb = kit.mix(rgb, CRIMSON, np.clip((.35-belly)/.35, 0, 1)*.55)
    rows = 15
    s = (V*rows) % 1
    x = (U*22+np.floor(V*rows)*.5) % 1
    edge = np.hypot(x-.5, (s-.28)*1.15)
    scallop = np.clip((edge-.42)/.18, 0, 1)
    rgb = kit.mix(rgb, (255, 172, 54), scallop*(.45+.3*belly))
    rgb = kit.mix(rgb, CRIMSON, np.clip((.3-edge)/.3, 0, 1)*(s < .5)*.28)
    rgb = kit.mix(rgb, (52, 6, 8), np.clip(kit.fbm(U, V, 12, 5)*1.6, 0, 1)*.1)
    return rgb


def _beak(U, V):
    """Beak: gold at the cere darkening to a near-black bronze hooked tip."""
    rgb = ramp(U, ((0, (232, 152, 42)), (.3, (176, 92, 24)), (.62, (92, 44, 18)), (1, (22, 10, 8))))
    ridge = np.exp(-((V-.25)/.08)**2)
    rgb = kit.mix(rgb, (255, 200, 100), ridge*.35*(1-U))
    rgb = kit.mix(rgb, (30, 8, 6), np.clip((np.abs(V-.75)-.18)/.1, 0, 1)*.3)
    return rgb


def _brow(U, V):
    """Deep crimson-brown brow plate with a dark edge."""
    across = np.abs(V-.5)*2
    rgb = kit.mix((96, 22, 16), (58, 12, 10), np.clip(U, 0, 1))
    rgb = kit.mix(rgb, (130, 34, 20), np.clip(kit.fbm(U, V, 8, 4)*1.4, 0, 1)*.35)
    return kit.mix(rgb, (30, 6, 6), np.clip((across-.6)/.4, 0, 1)*.6)


def _talon(U, V):
    rgb = ramp(U, ((0, (108, 34, 14)), (.35, (76, 22, 10)), (1, (30, 8, 6))))
    return kit.mix(rgb, (190, 96, 34), np.exp(-((V-.25)/.12)**2)*.6)


def _leg(U, V):
    """Scaled tarsus: gold-orange plates outlined in crimson."""
    x = (V*6) % 1
    y = (U*11+np.floor(V*6)*.5) % 1
    edge = np.hypot(x-.5, y-.5)
    rgb = kit.mix((226, 122, 28), (255, 188, 60), np.clip(1-edge*2, 0, 1))
    rgb = kit.mix(rgb, (92, 14, 10), np.clip((edge-.4)/.1, 0, 1)*.85)
    return kit.mix(rgb, (110, 22, 12), np.clip(U*.4, 0, 1)*.35)


def _ash(U, V):
    """Soft warm-grey ash: smooth, light, with thin ember veins and a few bright specks (no dark pits)."""
    n = kit.fbm(U, V, 5, 3)
    rgb = kit.mix((146, 136, 124), (108, 100, 90), np.clip(n*1.4, 0, 1))
    rgb = kit.mix(rgb, (176, 166, 152), np.clip(kit.fbm(U, V, 11, 6)*1.6, 0, 1)*.3)
    vein = np.abs(kit.fbm(U*1.3, V*1.3, 5, 21)) < .014
    rgb = kit.mix(rgb, (236, 110, 30), vein*.75)
    speck = kit.fbm(U, V, 30, 9) > .40
    rgb = kit.mix(rgb, (255, 190, 70), speck*.85)
    return rgb


def _flame(U, V, hot):
    """Fullbright flame tongue: U root->tip, V across. Crimson root to gold tip,
    a hot core line and licking streaks."""
    across = np.abs(V-.5)*2
    streak = kit.fbm(V*3.0+U*.6, U*1.1, 5, 33+hot)
    shifted = np.clip(U*1.05+streak*.16, 0, 1)
    stops = ((0, (150, 14, 8)), (.25, SCARLET), (.6, ORANGE), (.86, GOLD), (1, PALE))
    if hot:
        stops = ((0, (214, 52, 14)), (.22, (246, 96, 20)), (.55, GOLD), (.85, (255, 228, 120)), (1, (255, 250, 200)))
    rgb = ramp(shifted, stops)
    core = np.exp(-(across/.42)**2)
    rgb = kit.mix(rgb, GOLD, core*.28*np.clip(U*2.2, 0, 1))
    rgb = kit.mix(rgb, PALE, np.exp(-(across/.16)**2)*.55*np.clip(U*1.6, 0, 1))
    rgb = kit.mix(rgb, (150, 14, 8), np.clip((across-.72)/.28, 0, 1)*.55*(1-U))
    lick = np.sin((V-.5)*23+U*15+streak*3.5) > .55
    rgb = kit.mix(rgb, PALE, lick*.16*U)
    return rgb


def _ember(U, V):
    return kit.mix((222, 62, 12), (255, 176, 52), np.clip(1-np.abs(V-.5)*1.7+kit.fbm(U, V, 6, 8)*.3, 0, 1))


def _eye(U, V):
    """Blob UV, pole facing forward at V=1: a hot white-gold slit fading to orange."""
    r = 1-V
    return ramp(np.clip(r*1.1, 0, 1), ((0, (255, 250, 200)), (.35, (255, 232, 120)), (.7, (255, 150, 30)),
                                       (1, (200, 60, 12))))


def pigment(role, U, V):
    if role == 'feather':
        return _feather(U, V)
    if role == 'body':
        return _body(U, V)
    if role == 'beak':
        return _beak(U, V)
    if role == 'brow':
        return _brow(U, V)
    if role == 'talon':
        return _talon(U, V)
    if role == 'leg':
        return _leg(U, V)
    if role == 'ash':
        return _ash(U, V)
    if role == 'flame':
        return _flame(U, V, 0)
    if role == 'plume':
        return _flame(U, V, 1)
    if role == 'ember':
        return _ember(U, V)
    if role == 'eye':
        return _eye(U, V)
    raise ValueError(role)


def texture_bytes():
    return ATLAS.paint(pigment)
