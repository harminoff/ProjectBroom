"""Original acidic jelly skin: deep emerald gel under a yellow-lime acid film.

The paint is evaluated in the same latitude/longitude parameters as the
sculpt, so creases, runnels, beads and etched craters line up with geometry.
Soft occlusion and top light are baked from the analytic surface because the
gallery and most dungeon lighting are flat. There is no emission or fullbright;
the green glyph is an identity cue rather than literal whole-body paint.
"""
import math
from .toad_materials import png
from . import acid_jelly_shape as shape

SKIN='graphics/BRGACJLY.png'
NORMAL='graphics/BRGACJLY_N.png'
SPECULAR='graphics/BRGACJLY_S.png'
SIZE=1024
GW,GH=288,176
TAU=math.tau


def _hash(i,salt):
    """Integer hash in [0,1): no platform or float-library dependence."""
    h=(i*2654435761+salt*40503+0x9E3779B9)&0xffffffff
    h^=h>>16;h=(h*0x45d9f3b)&0xffffffff;h^=h>>16;h=(h*0x45d9f3b)&0xffffffff;h^=h>>16
    return h/4294967296


# Small etched pits, suspended inclusions and trapped bubbles: deterministic
# scattered sets. Inclusions are painted with depth (soft deep ones, sharper
# shallow ones, each with a faint refracted light crescent beneath it).
SMALL_PITS=[(TAU*_hash(i,1),-.05+1.30*_hash(i,2)**.75,.016+.018*_hash(i,3))
            for i in range(40)]
INCLUSIONS=[(TAU*_hash(i,7),-.22+1.25*_hash(i,8),.035+.075*_hash(i,9),_hash(i,10))
            for i in range(48)]
BUBBLES=[(TAU*_hash(i,4),-.15+1.25*_hash(i,5),.018+.02*_hash(i,6))
         for i in range(12)]


def v_of_phi(phi):
    g=phi/math.pi+.5
    return g*.6 if g<.5 else .3+(g-.5)*1.4


def _grid():
    """Surface normal Z and concavity on a periodic parameter grid."""
    pos=[[shape.surface(TAU*i/GW,j/(GH-1)) for i in range(GW)] for j in range(GH)]
    nz=[[0.]*GW for _ in range(GH)];cav=[[0.]*GW for _ in range(GH)]
    for j in range(GH):
        for i in range(GW):
            p=pos[j][i]
            a=pos[j][(i+1)%GW];b=pos[j][(i-1)%GW]
            c=pos[min(GH-1,j+1)][i];d=pos[max(0,j-1)][i]
            du=[x-y for x,y in zip(a,b)];dv=[x-y for x,y in zip(c,d)]
            n=(du[1]*dv[2]-du[2]*dv[1],du[2]*dv[0]-du[0]*dv[2],du[0]*dv[1]-du[1]*dv[0])
            length=math.sqrt(sum(x*x for x in n))
            if length<1e-9:
                nz[j][i]=1. if j>GH//2 else -1.;continue
            n=[x/length for x in n]
            # Orientation: V increases upward, U counter-clockwise -> outward.
            nz[j][i]=n[2]
            total=0.
            for reach,scale in ((2,.6),(7,.4)):
                ring=[pos[j][(i+k)%GW] for k in (-reach,reach)]
                ring+=[pos[min(GH-1,max(0,j+k))][i] for k in (-reach,reach)]
                ring+=[pos[min(GH-1,max(0,j+k))][(i+m)%GW] for k in (-reach,reach) for m in (-reach,reach)]
                mean=[sum(q[k] for q in ring)/len(ring) for k in range(3)]
                total+=scale*sum((mean[k]-p[k])*n[k] for k in range(3))
            cav[j][i]=total
    return nz,cav


def _sample(grid,u,v):
    x=(u%1)*GW;y=v*(GH-1)
    i=int(x)%GW;j=min(GH-2,int(y));fx=x-int(x);fy=y-j
    i2=(i+1)%GW
    return ((grid[j][i]*(1-fx)+grid[j][i2]*fx)*(1-fy)+(grid[j+1][i]*(1-fx)+grid[j+1][i2]*fx)*fy)


def _stamp(buffer,features,profile,reach):
    """Accumulate small periodic features only inside their pixel footprint."""
    W=SIZE-1
    for a,e,size in features:
        v=v_of_phi(e);slope=math.pi/.6 if v<.3 else math.pi/1.4
        span_x=int(reach*size/max(.18,math.cos(e))/TAU*W)+2
        span_y=int(reach*size/slope*(SIZE-1))+2
        cx=a/TAU*W;cy=(1-v)*(SIZE-1)
        for y in range(max(0,int(cy)-span_y),min(SIZE,int(cy)+span_y+1)):
            phi=shape.elevation(1-y/(SIZE-1))
            for x in range(int(cx)-span_x,int(cx)+span_x+1):
                xx=x%W;theta=TAU*xx/W
                rho=math.hypot(shape.wrap(theta-a)*math.cos(e),phi-e)/size
                value=profile(rho)
                if value:
                    buffer[y*SIZE+xx]+=value
                    if xx==0:buffer[y*SIZE+W]+=value


def _fields():
    nz,cav=_grid()
    n=SIZE*SIZE
    pit=[0.]*n;ring=[0.]*n;incl=[0.]*n;glow=[0.]*n;bubble=[0.]*n
    _stamp(pit,[(a,e,s) for a,e,s,_ in shape.CRATERS],lambda r:math.exp(-r*r) if r<3 else 0,3)
    _stamp(ring,[(a,e,s) for a,e,s,_ in shape.CRATERS],lambda r:math.exp(-((r-1.3)/.38)**2) if r<3 else 0,3)
    _stamp(pit,SMALL_PITS,lambda r:.45*math.exp(-r*r) if r<2.6 else 0,2.6)
    _stamp(ring,SMALL_PITS,lambda r:.15*math.exp(-((r-1.25)/.4)**2) if r<2.6 else 0,2.6)
    for a,e,size,depth in INCLUSIONS:
        # Deep inclusions are larger, softer and fainter; shallow ones crisp.
        soft=.6+1.1*depth;strength=.95-.55*depth
        _stamp(incl,[(a,e,size)],lambda r,soft=soft,k=strength:k*math.exp(-(r/soft)**2) if r<3.2 else 0,3.2)
        _stamp(glow,[(a,e-.55*size,size*.8)],lambda r,k=strength:.6*k*math.exp(-((r-.9)/.35)**2) if r<2.4 else 0,2.4)
    _stamp(bubble,BUBBLES,lambda r:math.exp(-((r-1)/.22)**2)+.8*math.exp(-((r-.45)/.2)**2) if r<2 else 0,2)
    return nz,cav,pit,ring,incl,glow,bubble


_CACHE={}


def _shared():
    if not _CACHE:_CACHE['fields']=_fields()
    return _CACHE['fields']


def _columns():
    W=SIZE-1
    thetas=[TAU*(x%W)/W for x in range(SIZE)]
    return thetas,None


def _mix(a,b,t):
    return [x+(y-x)*t for x,y in zip(a,b)]


DEEP=(2,22,14)
BODY=(16,70,36)
CORE=(92,172,68)
FILM=(196,218,40)
PALE=(150,184,72)
BURNT=(30,36,12)
VEIN=(4,20,12)
SPEC=(226,248,196)


def _texel(theta,phi,v,u,col,index,cache):
    nz,cav,pit,ring,incl,glow,bubble=cache
    cap=max(0.,math.cos(phi))**.6
    height=shape.smooth((phi+.25)/1.25)
    concave=_sample(cav,u,v)
    n=_sample(nz,u,v)
    color=_mix(DEEP,BODY,height)
    # Fake subsurface: the thick swollen lobes, buds and belly glow lighter
    # and warmer; thin skirt edges and deep valleys stay dark and dense.
    lobe=max(shape.cap(theta,phi,a,e,reach) for a,e,rise,reach in shape.LOBES+(shape.TOP_LOBE,)+shape.BUDS)
    belly=math.exp(-((phi-.18)/.32)**2)
    core=min(1,.85*lobe**.8+.35*belly)*(1-shape.smooth((concave+.02)/.25))
    color=_mix(color,DEEP,.6*(1-lobe)*height)
    color=_mix(color,CORE,.78*core)
    # Dancing-colour variance: broad blue-green and yellow-green mottles.
    m=math.sin(theta*3+phi*2.1+1.3*math.sin(theta*2-phi))*math.sin(theta*5-phi*3+.7)*cap
    color=[color[0]+9*m,color[1]+6*m,color[2]-10*m]
    m2=math.sin(theta*4-phi*5+.8*math.sin(theta*3+phi*2))*cap
    color=[color[0]-4*m2,color[1]-3*m2,color[2]+8*m2]
    # Suspended inclusions with depth, and a few trapped bubbles.
    dark=min(1,incl[index])
    color=_mix(color,VEIN,.62*dark)
    color=_mix(color,CORE,.35*min(1,glow[index]))
    cloud=max(0,math.sin(theta*2+phi*3+1.7)*math.sin(theta*3-phi*1.5+.4))*cap
    color=_mix(color,VEIN,.35*cloud*(1-.5*height))
    # Acid film pools in concavities, runs down the runnels and beads at
    # the skirt; marbled rivulets cross the upper gel.
    down=shape.smooth((.72-phi)/.30)*shape.smooth((phi+.62)/.12)
    streaks=[(shape.wrap(theta-a-.045*math.sin(phi*7+a*3)),w,amount) for a,w,amount in shape.RUNNELS]
    runnel_col=sum(amount*math.exp(-(d/(w*1.5))**2) for d,w,amount in streaks)
    core_line=sum(math.exp(-(d/(w*.32))**2) for d,w,amount in streaks)
    streak=min(1,runnel_col*down*1.05)
    patch=max(0,math.sin(theta*2+phi*4+.4)*math.sin(theta*3-phi*2.5+1.1))**2*height*cap
    pool=shape.smooth((concave+.02)/.18)*height
    bead=runnel_col*1.2*math.exp(-((phi+.42)/.16)**2)
    warp=theta*3+phi*4+.9*math.sin(theta*2-phi*5)+.5*math.sin(theta*5+phi*3)
    marble=math.exp(-(abs(math.sin(warp))/.24)**2)*shape.smooth((phi-.05)/.35)*cap
    marble*=.55+.45*math.sin(theta*2+phi*6+.3)
    film=min(1,streak+pool+.35*patch+min(.9,bead)+.8*max(0,marble))
    color=_mix(color,FILM,.88*film)
    # Etched craters hold pooled acid inside a faint corroded lip.
    pits=min(1,pit[index]);lip=min(1,ring[index])
    color=_mix(color,BURNT,.30*pits)
    color=_mix(color,FILM,.50*pits*pits)
    color=_mix(color,PALE,.22*lip)
    # Baked form light and occlusion.
    occlusion=shape.smooth((concave+.03)/.26)
    shade=.66+.34*max(-.5,min(1,n*.9+.15))-.52*occlusion
    color=[c*shade for c in color]
    # Painted wet highlights: specular pools on lobes and buds, a broken
    # rim sheen along the skirt lip, and glossy lines down every drip.
    sheen=0.
    for a,e,rise,reach in shape.LOBES+shape.BUDS:
        d=math.hypot(shape.wrap(theta-a+.10)*math.cos(e+.25*reach),phi-e-.25*reach)/(.24*reach)
        sheen=max(sheen,math.exp(-d*d))
    sheen+=.35*math.exp(-((phi-.03)/.06)**2)*max(0,math.sin(theta*7+1.3))**2
    sheen+=.75*min(1,core_line)*down*(.6+.4*math.sin(phi*9+theta*2))
    sheen=min(1,sheen)
    color=_mix(color,SPEC,.72*sheen)
    color=_mix(color,SPEC,.30*min(1,bubble[index]))
    return tuple(max(0,min(255,round(c))) for c in color),film,pits,n,sheen,dark


def _maps():
    if 'maps' in _CACHE:return _CACHE['maps']
    cache=_shared();thetas,runnel=_columns()
    diffuse=bytearray();spec=bytearray()
    for y in range(SIZE):
        v=1-y/(SIZE-1);phi=shape.elevation(v)
        for x in range(SIZE):
            u=x/(SIZE-1)
            rgb,film,pits,n,sheen,dark=_texel(thetas[x],phi,v,u,None,y*SIZE+x,cache)
            diffuse.extend(rgb)
            level=round(max(20,min(250,96+70*film+34*max(0,n)+80*sheen-70*pits-30*dark)))
            spec.extend((level,)*3)
    _CACHE['maps']=(png(diffuse,SIZE,SIZE),png(spec,SIZE,SIZE))
    return _CACHE['maps']


def texture_bytes():
    return _maps()[0]


def surface_maps():
    return {NORMAL:png(bytes((128,128,255))*16,4,4),SPECULAR:_maps()[1]}
