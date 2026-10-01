"""Original flame turret atlas: soot-black iron, heat-tempered nozzle, bronze mask.

Each opaque region is a small painted material: horizontal texture position
carries surface pattern (temper bands, wear, grain) and vertical position is a
painted top-light ramp chosen per vertex from its rest normal. That keeps form
readable under the engine's flat light. The rightmost atlas column (u >= 0.875)
holds the only emissive regions, the flame tongues and ember eye lenses, read by
`shaders/flame-turret-fire.fp`. Original Project Broom art; no imported artwork.
"""
import math
from .toad_materials import png

SIZE=1024
ROLES=('plate','iron','mask','nozzle','brass','copper','leather','soot',
       'horn','gauge','steel','tank','fin','bolt')
RECTS={name:(i%4*224+8,i//4*256+8,i%4*224+216,i//4*256+248) for i,name in enumerate(ROLES)}
# Emissive column. The runtime shader and Blender preview both key on u >= EMISSIVE_U.
EMISSIVE_U=0.875
RECTS['flame']=(904,8,1016,504)
RECTS['ember']=(904,520,1016,1016)
EMISSIVE=('flame','ember')


def uv(role,a,b):
    """Local (a, b) in [0,1] (b downwards in the image) to IQM/Blender UV."""
    x0,y0,x1,y1=RECTS[role]
    a=min(1,max(0,a));b=min(1,max(0,b))
    return ((x0+a*(x1-x0))/SIZE,1-(y0+b*(y1-y0))/SIZE)


def _hash(x,y,seed):
    h=(x*374761393+y*668265263+seed*1442695041)&0xffffffff
    h=((h^(h>>13))*1274126177)&0xffffffff
    return ((h^(h>>16))&0xffff)/65535.0


def _table(seed,n=128):
    # Tileable value-noise fbm, precomputed once per seed for speed.
    def value(x,y,cell):
        gx,gy=x/cell,y/cell;ix,iy=int(gx),int(gy);fx,fy=gx-ix,gy-iy
        fx=fx*fx*(3-2*fx);fy=fy*fy*(3-2*fy);m=n//cell
        c=[_hash((ix+i)%m,(iy+j)%m,seed+cell) for j in (0,1) for i in (0,1)]
        return (c[0]*(1-fx)+c[1]*fx)*(1-fy)+(c[2]*(1-fx)+c[3]*fx)*fy
    rows=[]
    for y in range(n):
        row=[]
        for x in range(n):
            row.append(value(x,y,32)*.5+value(x,y,16)*.25+value(x,y,8)*.15+value(x,y,4)*.1)
        rows.append(row)
    return rows


_TABLES={}


def noise(x,y,seed=0):
    """Smooth periodic fbm in [0,1] sampled with bilinear filtering."""
    t=_TABLES.get(seed)
    if t is None:t=_TABLES[seed]=_table(seed)
    n=len(t);ix,iy=math.floor(x),math.floor(y);fx,fy=x-ix,y-iy
    a=t[iy%n][ix%n];b=t[iy%n][(ix+1)%n];c=t[(iy+1)%n][ix%n];d=t[(iy+1)%n][(ix+1)%n]
    return (a*(1-fx)+b*fx)*(1-fy)+(c*(1-fx)+d*fx)*fy


def mix(a,b,t):
    t=min(1,max(0,t));return tuple(x+(y-x)*t for x,y in zip(a,b))


def ramp(stops,t):
    t=min(1,max(0,t))
    for (t0,c0),(t1,c1) in zip(stops,stops[1:]):
        if t<=t1:return mix(c0,c1,(t-t0)/(t1-t0) if t1>t0 else 1)
    return stops[-1][1]


def lit(color,b,spec=None,gloss=.1,ambient=.3):
    """Painted top light: b=0 faces the light, b=1 is occluded underside."""
    shade=1.22-(1.22-ambient)*b
    out=tuple(c*shade for c in color)
    if spec:out=mix(out,spec,max(0,1-b/gloss)**2*.85)
    return out


TEMPER=[(0,(64,54,46)),(.1,(74,60,48)),(.16,(144,122,84)),(.24,(160,112,66)),(.31,(120,76,70)),
        (.37,(90,66,96)),(.43,(66,78,112)),(.49,(76,80,88)),(.54,(46,42,40)),(.6,(24,21,20)),(1,(16,14,13))]


def pigment(role,a,b,px,py):
    n=noise(px*.5,py*.5,1);g=noise(px*.18,py*.18,2);f=noise(px*1.7,py*1.7,3)
    if role=='plate':
        c=mix((50,48,47),(33,31,31),g*1.2-.2)
        c=mix(c,(96,54,34),max(0,g-.6)*3.2*(n>.42))
        c=mix(c,(20,19,19),max(0,.28-f)*3)
        return lit(c,b,(118,112,106),.07)
    if role=='iron':
        c=mix((60,56,53),(36,33,32),n*1.1)
        c=mix(c,(86,50,36),max(0,g-.62)*2.5)
        c=mix(c,(24,22,22),max(0,.3-f)*2.4)
        return lit(c,b,(150,140,128),.08)
    if role=='mask':
        # Heat-blackened cast bronze: dark body, worn bright ridges via the light ramp.
        c=mix((84,58,36),(40,28,21),g*1.3-.1)
        c=mix(c,(26,20,17),max(0,.35-n)*2)
        c=mix(c,(104,44,26),max(0,g-.68)*2.2)
        return lit(c,b,(236,190,120),.2,.22)
    if role=='nozzle':
        c=ramp(TEMPER,a+(n-.5)*.035)
        c=mix(c,(20,18,17),max(0,.3-f)*1.4)
        return lit(c,b,(210,196,176) if a<.55 else None,.1,.28)
    if role=='brass':
        c=mix((176,132,62),(118,84,40),g*1.2-.1)
        c=mix(c,(70,52,32),max(0,.3-f)*2.2)
        return lit(c,b,(255,232,170),.2,.26)
    if role=='copper':
        c=mix((158,84,50),(104,56,36),g)
        c=mix(c,(66,118,98),max(0,n-.66)*3)
        return lit(c,b,(250,190,150),.15)
    if role=='leather':
        c=mix((98,42,32),(62,26,22),n*1.2)
        c=mix(c,(46,22,20),max(0,.35-f)*2)
        c=mix(c,(130,70,48),max(0,f-.7)*1.6)
        return lit(c,b,(150,96,80),.05,.34)
    if role=='soot':
        return lit(mix((24,21,20),(12,11,11),n),b*.5)
    if role=='horn':
        rib=.5+.5*math.cos(a*math.tau*9)
        c=mix((44,40,39),(28,26,26),rib*.8+(n-.5)*.4)
        c=mix(c,(168,156,142),max(0,a-.78)*4.5)
        c=mix(c,(92,48,34),max(0,.22-a)*3*(g>.45))
        return lit(c,b,(190,180,170),.1)
    if role=='gauge':
        x,y=a*2-1,b*2-1;r=math.hypot(x,y);ang=math.atan2(x,-y)
        c=mix((214,200,166),(176,160,126),n)
        if r>.93:c=(62,52,40)
        elif .72<r<.9:
            frac=(ang+2.36)/4.71
            if 0<=frac<=1:
                if frac>.78:c=mix(c,(170,40,26),.9)
                if abs(frac*20-round(frac*20))<.12 or (r>.82 and abs(frac*4-round(frac*4))<.03):c=(30,26,24)
        if r<.1:c=(40,34,28)
        return lit(c,b*.25,None,.1,.8)
    if role=='steel':
        c=mix((60,62,68),(34,36,42),n*1.2)
        c=mix(c,(90,62,44),max(0,g-.66)*2)
        return lit(c,b,(200,206,214),.12)
    if role=='tank':
        c=mix((72,58,50),(44,36,32),g*1.2)
        drip=max(0,noise(px*.9,py*.08,4)-.62)*3
        c=mix(c,(104,56,34),drip)
        c=mix(c,(28,25,24),max(0,.3-f)*2)
        return lit(c,b,(150,134,120),.08)
    if role=='fin':
        c=mix((50,56,72),(30,32,40),n*1.2)
        c=mix(c,(110,78,54),max(0,g-.6)*2)
        return lit(c,b,(170,186,210),.12)
    if role=='bolt':
        c=mix((78,76,76),(50,48,48),n)
        return lit(c,b,(210,206,198),.14)
    if role=='flame':
        # a across (0.5 = core, 1 = outer lick), b along (0 base, 1 tip).
        d=abs(a-.5)*2;flick=(noise(px*.7,py*.2,5)-.5)*.22
        heat=(1-b)*.78+(1-d)*.34+flick-.08
        return ramp([(0,(120,26,10)),(.25,(196,52,14)),(.45,(238,104,26)),(.65,(255,168,52)),
                     (.82,(255,222,122)),(1,(255,248,214))],heat)
    if role=='ember':
        x,y=a*2-1,b*2-1;r=math.hypot(x,y)
        c=ramp([(0,(255,244,190)),(.3,(255,190,70)),(.62,(236,98,24)),(.85,(150,32,10)),(1,(70,14,6))],r+(n-.5)*.12)
        # Vertical slit pupil gives the furnace mask its infernal stare.
        if abs(x)<.13*(1-abs(y)*.6) and r<.78:c=mix(c,(92,14,6),.82)
        return c
    raise KeyError(role)


def texture_bytes():
    pixels=bytearray(SIZE*SIZE*3)
    for name,(x0,y0,x1,y1) in RECTS.items():
        for y in range(y0-8,y1+8):
            for x in range(x0-8,x1+8):
                rgb=pigment(name,max(0,min(1,(x-x0)/(x1-x0))),max(0,min(1,(y-y0)/(y1-y0))),x,y)
                pixels[(y*SIZE+x)*3:(y*SIZE+x)*3+3]=bytes(max(0,min(255,round(c))) for c in rgb)
    return png(pixels,SIZE,SIZE)
