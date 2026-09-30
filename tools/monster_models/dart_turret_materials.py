"""Original dart turret atlas: blackened iron, violet enamel, polished spring steel.

Each opaque region is a small painted material: horizontal texture position
carries a surface pattern (along-axis coating, grain, wear) and vertical
position is a painted top-light ramp chosen per vertex from its rest normal, so
form stays readable under the engine's flat light. The violet enamel and the
violet poison coating are an art reading of Brogue's violet glyph and bolt
colour (`centipedeColor`); nothing is emissive. Original Project Broom art; no
imported artwork.
"""
import math
from .toad_materials import png
from .flame_turret_materials import noise,mix,ramp,lit

SIZE=1024
ROLES=('plate','panel','enamel','brass','steel','spring','bolt','dart',
       'flight','vial','poison','wood','soot','channel')
RECTS={name:(i%4*256+8,i//4*256+8,i%4*256+248,i//4*256+248) for i,name in enumerate(ROLES)}
POISON=(132,40,156)      # violet poison coating (art reading of centipedeColor 75/25/85)


def uv(role,a,b):
    """Local (a, b) in [0,1] (b downwards in the image) to IQM/Blender UV."""
    x0,y0,x1,y1=RECTS[role]
    a=min(1,max(0,a));b=min(1,max(0,b))
    return ((x0+a*(x1-x0))/SIZE,1-(y0+b*(y1-y0))/SIZE)


def pigment(role,a,b,px,py):
    n=noise(px*.5,py*.5,11);g=noise(px*.18,py*.18,12);f=noise(px*1.7,py*1.7,13)
    if role=='plate':
        # Blackened wrought iron with plum-brown oxide blooms.
        c=mix((58,54,60),(34,32,37),g*1.2-.15)
        c=mix(c,(92,56,62),max(0,g-.62)*2.6*(n>.45))
        c=mix(c,(22,21,24),max(0,.3-f)*2.6)
        return lit(c,b,(150,142,160),.08)
    if role=='panel':
        # Deep aubergine enamel on the stepped panel; worn edges bare the iron.
        c=mix((54,28,62),(36,18,42),n*1.1)
        c=mix(c,(58,54,60),max(0,f-.72)*2.4)
        c=mix(c,(26,14,30),max(0,.32-g)*2)
        return lit(c,b,(176,150,196),.1,.24)
    if role=='enamel':
        # Glossy violet stove enamel with chipped corners.
        # Aged plum stove enamel: darker in the grain, chipped to bare iron.
        c=mix((96,46,108),(62,28,72),g*1.2-.1)
        c=mix(c,(118,66,128),max(0,n-.66)*1.6)
        c=mix(c,(40,30,40),max(0,.3-f)*1.4)
        c=mix(c,(52,50,56),max(0,f-.8)*3.2)
        return lit(c,b,(226,200,236),.16,.22)
    if role=='brass':
        c=mix((176,132,62),(118,84,40),g*1.2-.1)
        c=mix(c,(76,56,34),max(0,.3-f)*2.2)
        return lit(c,b,(255,238,176),.22,.3)
    if role=='steel':
        c=mix((78,80,88),(46,48,56),n*1.2)
        c=mix(c,(96,70,60),max(0,g-.7)*1.8)
        return lit(c,b,(210,216,226),.14)
    if role=='channel':
        # Oiled dark gun-steel with bright wear along the running edges.
        c=mix((62,64,72),(38,40,46),n)
        c=mix(c,(126,128,136),max(0,f-.74)*2.4)
        return lit(c,b,(220,224,232),.16)
    if role=='spring':
        # Polished spring steel: bright, cool and high contrast against the violet.
        c=mix((132,136,148),(92,96,108),n*1.1)
        c=mix(c,(104,88,78),max(0,g-.74)*2)
        return lit(c,b,(255,255,255),.26,.18)
    if role=='bolt':
        c=mix((88,86,90),(58,56,60),n)
        return lit(c,b,(214,210,218),.16)
    if role=='dart':
        # a runs from nock (0) to needle tip (1): steel shaft, brass ferrule, poison-dipped head.
        edge=.735+(noise(px*.9,py*.3,14)-.5)*.05
        if a<.69:
            c=mix((170,172,182),(120,122,132),n);c=mix(c,(70,72,80),max(0,.26-f)*2)
            return lit(c,b,(255,255,255),.2,.3)
        if a<edge:
            return lit(mix((196,150,70),(140,102,48),g),b,(255,236,170),.2,.3)
        c=mix(POISON,(196,104,222),(a-edge)/(1-edge)*.8+(n-.5)*.3)
        c=mix(c,(70,20,86),max(0,.3-f)*1.6)
        return lit(c,b,(248,222,255),.24,.3)
    if role=='flight':
        c=mix((64,28,74),(38,18,44),g*1.2)
        c=mix(c,(118,60,132),max(0,n-.62)*2)
        return lit(c,b,(190,160,200),.08,.34)
    if role=='vial':
        # a runs up the lathe profile: violet liquid, bright meniscus, then clear glass.
        level=.6+(n-.5)*.02
        if a<level:
            core=mix((132,48,160),(70,18,92),abs(a/level-.55)*1.6)
            return lit(core,b,(246,220,255),.22,.34)
        if a<level+.035:return lit((214,150,236),b*.5,None,.1,.6)
        c=mix((96,92,110),(62,58,72),n)
        return lit(c,b,(255,255,255),.3,.36)
    if role=='poison':
        c=mix((150,56,180),(100,28,124),n)
        return lit(c,b,(255,232,255),.34,.4)
    if role=='wood':
        grain=.5+.5*math.sin(a*60+noise(px*.2,py*2.2,15)*6)
        c=mix((96,58,36),(62,36,24),grain*.8+(g-.5)*.4)
        return lit(c,b,(200,160,120),.08)
    if role=='soot':
        return lit(mix((28,24,30),(14,12,16),n),b*.5)
    raise KeyError(role)


def texture_bytes():
    pixels=bytearray(SIZE*SIZE*3)
    for name,(x0,y0,x1,y1) in RECTS.items():
        for y in range(y0-8,y1+8):
            for x in range(x0-8,x1+8):
                rgb=pigment(name,max(0,min(1,(x-x0)/(x1-x0))),max(0,min(1,(y-y0)/(y1-y0))),x,y)
                pixels[(y*SIZE+x)*3:(y*SIZE+x)*3+3]=bytes(max(0,min(255,round(c))) for c in rgb)
    return png(pixels,SIZE,SIZE)
