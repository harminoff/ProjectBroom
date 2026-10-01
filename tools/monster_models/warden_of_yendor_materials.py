"""Painted plate for the Warden of Yendor: near-black aubergine-violet armour lit
by Brogue's Yendorian light colour (``yendorLightColor``, red 50 / green -100 /
blue 30: a deep violet-magenta that dances).

Art direction only. The armour carries a wide painted value range so it
separates from grey walls and a brown floor: black-violet iron, mid violet breast
and shoulders, pale lilac worn edges, and a magenta light spill near the light
plates. Hot magenta proper is reserved for the light plates (chest seam, visor
slit, forearm strips) (all of which sink into the armour in the death clip);
``shaders/warden-yendor-light.fp`` renders exactly that colour key fullbright,
so ``glow_key`` here and the shader must stay in step. Original Project Broom art.
"""
from . import golem_materials as GM
from . import guardian_kit as K

LIGHT = (140, 106, 184)
ARMC = (112, 82, 152)
LEGC = (60, 42, 84)
MID = (86, 60, 120)
DARK = (40, 27, 56)
CORE = (14, 9, 20)
LILAC = (206, 176, 236)
GLOW = (255, 70, 216)   # inside the shader key: r>.90, g<.46, b in .62..1.0
DARK_PREFIX = ('fauld', 'greave', 'poleyn', 'sabaton', 'cuff', 'couter', 'helm', 'faceplate',
               'brow', 'cheek', 'crest', 'lame_', 'hip_block', 'tasset', 'spine', 'backplate', 'collar')
TRIM = ('belt', 'gorget', 'lame_upper', 'lame_lower')
CLOAK = (70, 42, 104)


def glow_key(rgb):
    """Python twin of the shader's fullbright key (rgb 0..255 arrays)."""
    r, g, b = rgb[..., 0]/255.0, rgb[..., 1]/255.0, rgb[..., 2]/255.0
    return (r > .90) & (g < .46) & (b > .62)


def paint(parts, scale=.84):
    import numpy as np
    names = [p.name for p in parts]
    role = np.array([p.role for p in parts])
    light = role == 'void'; core = role == 'core'
    dark = np.array([n.startswith(DARK_PREFIX) for n in names])
    trim = np.array([n in TRIM or n.startswith(('pauldron_lame', 'cuff_', 'fauld')) for n in names])
    fist = np.array([n.startswith(('gauntlet', 'knuckle', 'thumb', 'finger', 'claw')) for n in names])
    sigil = np.array([n == 'belt_sigil' for n in names])
    seeds = np.array([p.seed for p in parts])
    armc = np.array([n.startswith(('rerebrace', 'vambrace', 'pauldron')) for n in names])
    legc = np.array([n.startswith(('cuisse', 'tasset', 'hip_block')) for n in names])
    cloakm = np.array([n.startswith('cloak') for n in names])
    spill = np.array([p.box[0] for p in parts if p.role == 'void'])

    def pigment(np, P, L, N, E, CH, AO, pi):
        n = len(P)
        base = np.where(dark[pi][:, None], np.array([DARK]), np.array([MID])).astype(np.float64)
        base = np.where(armc[pi][:, None], np.array([ARMC]), base)
        base = np.where(legc[pi][:, None], np.array([LEGC]), base)
        base = np.where(cloakm[pi][:, None], np.array([CLOAK]), base)
        base = np.where(fist[pi][:, None], np.array([LIGHT]), base)
        base = np.where(core[pi][:, None], np.array([CORE]), base)
        tint = (GM._hash(np, seeds[pi], seeds[pi]*0+3, seeds[pi]*0+5, 11)-.5)*14
        val = tint+(GM.fbm(np, P*.08, 21)-.5)*26+(GM.vnoise(np, P*.45, 22)-.5)*10
        streak = GM.vnoise(np, np.stack([P[:, 0]*.5, P[:, 1]*.5, P[:, 2]*.05], 1), 25)
        val -= np.clip(streak-.5, 0, 1)*30*(1-np.abs(N[:, 2]))
        # Painted form light: lit tops, dark undersides (engine light is flat).
        lightv = np.clip(N @ np.array([.34, -.22, .91]), -1, 1)
        form = .60+.55*lightv-.16*np.clip(-N[:, 2], 0, 1)
        col = (base+val[:, None])*form[:, None]
        # Pale lilac worn edges and fresh chips.
        wear = np.clip(E, 0, 1)**1.15*(.55+.45*GM.vnoise(np, P*1.1, 26))
        col += (wear*150+np.clip(CH*2.2, 0, 1)*40)[:, None]*np.array([LILAC])/255.0*1.0
        col += (np.clip(E, 0, 1)**.8*95*cloakm[pi])[:, None]*np.array([LILAC])/255.0
        col *= (1-.88*np.clip(AO, 0, 1))[:, None]
        # Engraved bands on trim: dark grooves with a lit lip, with dark rune lines.
        t = trim[pi]
        groove = np.clip(1-np.abs(np.abs(L[:, 2])-.6)/.07, 0, 1)*t
        col *= (1-.55*groove)[:, None]
        rune = np.clip(1-np.abs(np.abs(L[:, 2])-.15)/.07, 0, 1)*t*(L[:, 0] > .3)
        # Magenta light spill from the light plates onto nearby armour.
        d = np.min([np.linalg.norm(P-s, axis=1) for s in spill], axis=0)
        cl = cloakm[pi]
        fold = np.sin(P[:, 1]*1.1+np.sin(P[:, 2]*.25)*1.3)
        col *= np.where(cl, .8+.3*fold, 1.0)[:, None]
        col += (40*np.exp(-d/3.0))[:, None]*np.array([[1.0, .16, .62]])
        col *= (1-.6*rune)[:, None]
        s_ = sigil[pi]
        lm = light[pi]
        flick = .96+.04*GM.vnoise(np, P*1.2, 91)
        col = np.where(lm[:, None], np.array([GLOW])*flick[:, None], col)
        level = 30+52*np.clip(E, 0, 1)**1.4-14*np.clip(AO, 0, 1)
        level = np.where(lm, 0, np.where(core[pi], 20, level))
        return col, level
    return K.paint(parts, pigment, background=(34, 24, 46), spec_bg=20)
