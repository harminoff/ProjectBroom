"""Original black jelly skin: glossy jet-black ink with violet depth.

Brogue gives the jelly a black glyph and purple blood (`DF_PURPLE_BLOOD`).
These are identity cues, not literal whole-body paint and not powers. A black
blob would read as a hole on a dark floor, so the paint is built for the
engine's flat light:

- value structure comes from painted gloss, never from lighter body paint:
  crisp white-lavender specular pools on every convex fold, blister and pile,
  a broad ceiling reflection on upward faces and a pale meniscus at the spill;
- inky depth comes from a deep violet fake-subsurface core in the thick belly,
  clouded by near-black density and suspended inclusions;
- thin-film teal/magenta fringes ring the highlights like an oil slick;
- painted occlusion keeps grooves, the fold roots and the pour fillet darkest.

The paint is evaluated in the same (azimuth, V) parameters as the sculpt, so
highlights and grooves sit on the actual relief. There is no emission.
"""
import math
from .toad_materials import png
from . import black_jelly_animation as shape

SKIN=shape.SKIN
NORMAL=shape.NORMAL
SPECULAR=shape.SPECULAR
SIZE=1024
GW,GH=384,240
TAU=math.tau


def _hash(i,salt):
    """Integer hash in [0,1): no platform or float-library dependence."""
    h=(i*2654435761+salt*40503+0x9E3779B9)&0xffffffff
    h^=h>>16;h=(h*0x45d9f3b)&0xffffffff;h^=h>>16;h=(h*0x45d9f3b)&0xffffffff;h^=h>>16
    return h/4294967296


# Suspended inclusions (azimuth, V, radius in V units, depth) and small
# trapped bubbles in the body.
INCLUSIONS=[(TAU*_hash(i,11),.30+.48*_hash(i,12),.018+.030*_hash(i,13),_hash(i,14)) for i in range(40)]
BUBBLES=[(TAU*_hash(i,21),.32+.46*_hash(i,22),.006+.005*_hash(i,23)) for i in range(14)]


def _unit(v):
    n=math.sqrt(sum(x*x for x in v));return tuple(x/n for x in v)


KEY=_unit((.40,.46,.88))      # painted key reflection toward the usual views
BACK=_unit((-.70,-.45,.62))   # weaker second reflection for rear views
EYE=_unit((.45,.45,.35))


def _half(light):return _unit(tuple(a+b for a,b in zip(light,EYE)))


H_KEY=_half(KEY);H_BACK=_half(BACK)


def _grid():
    """Surface normals and concavity on a periodic parameter grid."""
    pos=[[shape.surface(shape.theta_of(i/GW),j/(GH-1)) for i in range(GW)] for j in range(GH)]
    normal=[[(0.,0.,1.)]*GW for _ in range(GH)];cav=[[0.]*GW for _ in range(GH)]
    for j in range(GH):
        for i in range(GW):
            p=pos[j][i]
            a=pos[j][(i+1)%GW];b=pos[j][(i-1)%GW]
            c=pos[min(GH-1,j+1)][i];d=pos[max(0,j-1)][i]
            du=[x-y for x,y in zip(a,b)];dv=[x-y for x,y in zip(c,d)]
            n=(du[1]*dv[2]-du[2]*dv[1],du[2]*dv[0]-du[0]*dv[2],du[0]*dv[1]-du[1]*dv[0])
            length=math.sqrt(sum(x*x for x in n))
            if length<1e-6:
                normal[j][i]=(0.,0.,1.) if j>GH//2 else (0.,0.,-1.);continue
            normal[j][i]=tuple(x/length for x in n)
            n=normal[j][i];total=0.
            for reach,scale in ((2,.6),(6,.4)):
                ring=[pos[j][(i+k)%GW] for k in (-reach,reach)]
                ring+=[pos[min(GH-1,max(0,j+k))][i] for k in (-reach,reach)]
                ring+=[pos[min(GH-1,max(0,j+k))][(i+m)%GW] for k in (-reach,reach) for m in (-reach,reach)]
                mean=[sum(q[k] for q in ring)/len(ring) for k in range(3)]
                total+=scale*sum((mean[k]-p[k])*n[k] for k in range(3))
            cav[j][i]=total
    # The crest pole has no azimuth: give its last rows the pole normal.
    for j in range(GH-3,GH):
        normal[j]=[(0.,0.,1.)]*GW
    return normal,cav


def _sample(grid,u,v,vector=False):
    x=(u%1)*GW;y=v*(GH-1)
    i=int(x)%GW;j=min(GH-2,int(y));fx=x-int(x);fy=y-j;i2=(i+1)%GW
    if not vector:
        return ((grid[j][i]*(1-fx)+grid[j][i2]*fx)*(1-fy)+(grid[j+1][i]*(1-fx)+grid[j+1][i2]*fx)*fy)
    out=[]
    for k in range(3):
        out.append((grid[j][i][k]*(1-fx)+grid[j][i2][k]*fx)*(1-fy)+(grid[j+1][i][k]*(1-fx)+grid[j+1][i2][k]*fx)*fy)
    return _unit(out) if any(out) else (0.,0.,1.)


def _stamp(buffer,features,profile,reach):
    """Accumulate small periodic features inside their pixel footprint."""
    W=SIZE-1
    for a,e,size in features:
        r=max(3.,shape.profile(e)[0])
        span_x=int(reach*size*17/r/.6/TAU*W)+2
        span_y=int(reach*size*(SIZE-1))+2
        u=((a-math.pi)%TAU)/TAU
        cx=u*W;cy=(1-e)*(SIZE-1)
        for y in range(max(0,int(cy)-span_y),min(SIZE,int(cy)+span_y+1)):
            v=1-y/(SIZE-1)
            for x in range(int(cx)-span_x,int(cx)+span_x+1):
                xx=x%W;theta=shape.theta_of(xx/W)
                rho=math.hypot(shape.wrap(theta-a)*r/17*.6,v-e)/size
                value=profile(rho)
                if value:
                    buffer[y*SIZE+xx]+=value
                    if xx==0:buffer[y*SIZE+W]+=value


_CACHE={}


def _shared():
    if 'fields' not in _CACHE:
        normal,cav=_grid()
        n=SIZE*SIZE
        incl=[0.]*n;halo=[0.]*n;bubble=[0.]*n
        for a,e,size,depth in INCLUSIONS:
            soft=.7+1.0*depth;k=1-.5*depth
            _stamp(incl,[(a,e,size)],lambda r,soft=soft,k=k:k*math.exp(-(r/soft)**2) if r<3 else 0,3)
            _stamp(halo,[(a,e,size)],lambda r,soft=soft,k=k:.8*k*math.exp(-((r-1.4*soft)/.5)**2) if r<3.5 else 0,3.5)
        _stamp(bubble,[(a,e,s) for a,e,s in BUBBLES],
               lambda r:.8*math.exp(-(r/.6)**2) if r<2 else 0,2)
        _CACHE['fields']=(normal,cav,incl,halo,bubble)
    return _CACHE['fields']


def _mix(a,b,t):
    return [x+(y-x)*t for x,y in zip(a,b)]


INK=(5,4,8)
BODY=(12,9,18)
DEEP=(24,13,38)
VIOLET=(62,26,94)
SKY=(104,102,132)
SPEC=(236,232,255)
TEAL=(46,128,138)
MAGENTA=(138,52,128)
MENISCUS=(132,124,164)


def _texel(u,v,index,cache):
    normal,cav,incl,halo,bubble=cache
    theta=shape.theta_of(u)
    f=shape.fields(theta,v)
    n=_sample(normal,u,v,True)
    concave=_sample(cav,u,v)
    pole=shape.smooth((.985-v)/.05)
    body=shape.smooth((v-.24)/.08)
    color=list(BODY)
    # Fake subsurface: the thick lower belly and the fold piles hold a deep
    # violet core, clouded by near-black density; thin edges stay ink.
    cloud=(math.sin(theta*2+v*7+1.1*math.sin(theta*3-v*5))*math.sin(theta*3-v*4+.6)*.5+.5)*pole
    thick=math.exp(-((v-.42)/.15)**2)*body
    core=min(1.,thick*(.35+.85*cloud)+.30*min(1.,f['pile']/3)+.25*min(1.,f['slump']/4)+.2*min(1.,f['fold']/3)*body)
    color=_mix(color,DEEP,.8*core)
    color=_mix(color,VIOLET,.45*core*core*cloud*cloud)
    # Inclusions: black nuclei in violet halos; faint trapped bubbles.
    color=_mix(color,VIOLET,.35*min(1.,halo[index])*body)
    color=_mix(color,INK,.32*min(1.,incl[index]))
    # Painted occlusion: grooves beside the folds, fold roots, the crease and
    # the pour fillet are the darkest ink.
    occlusion=shape.smooth((concave+.02)/.22)
    groove=min(1.,f['groove'])*.5+min(1.,f['crease'])*.8
    fillet=math.exp(-((v-.285)/.03)**2)*.6
    dark=min(1.,occlusion+.6*groove+fillet)
    color=_mix(color,INK,.85*dark)
    # Broad ceiling reflection on upward faces, broken into soft bands like
    # a reflected dungeon vault; the spill pool mirrors it most strongly.
    up=shape.smooth((n[2]-.25)/.6)
    bands=shape.smooth((math.sin(theta*2.0+v*11+.8*math.sin(theta*3))+.1)/.7)*pole
    pool=math.exp(-((v-.215)/.035)**2)
    color=_mix(color,SKY,(.20*up*bands+.10*pool*up*bands)*(1-.7*dark))
    # Crisp specular pools where the surface turns toward the painted key,
    # and a weaker counter reflection for rear views.
    key=sum(a*b for a,b in zip(n,H_KEY));back=sum(a*b for a,b in zip(n,H_BACK))
    # Highlights break into curved bands, like the reflected ribs of a vault,
    # so a broad lobe never carries one flat painted blob.
    ribs=shape.smooth((math.sin((n[0]-n[1])*11+n[2]*5+.6)+.15)/.45)
    hl=(shape.smooth((key-.975)/.015)+.55*shape.smooth((back-.975)/.015))*ribs
    hl*=1-.5*min(1.,f['slump']/shape.SLUMP[2])   # calm the broad slump bulge
    fringe=shape.smooth((key-.955)/.02)*(1-shape.smooth((key-.982)/.012))
    film=_mix(TEAL,MAGENTA,.5+.5*math.sin(theta*3+v*14))
    color=_mix(color,film,.30*fringe*(1-dark))
    # Glossy lines run down every fold ridge and bead on its pile.
    line=0.
    for a,w,amount,top,end in shape.FOLDS:
        d=shape.wrap(theta-a-.05*math.sin(v*23+a*2)+.35*w)
        along=shape.smooth((top-v)/.14)*shape.smooth((v-end-.03)/.04)
        line+=math.exp(-(d/(.22*w))**2)*along*(.55+.45*math.sin(v*40+a*5))
        line+=1.3*math.exp(-(shape.wrap(theta-a+.3*w)/(.45*w))**2)*math.exp(-((v-end-.012)/.012)**2)
    # A pale meniscus along the spill lip separates the ink from the floor.
    # The meniscus only catches light in scattered places along the edge.
    glints=shape.smooth((math.sin(theta*11+1.3*math.sin(theta*3))+.6*math.sin(theta*5+.7)-.35)/.7)
    meniscus=math.exp(-((v-.166)/.010)**2)*glints
    spill=math.exp(-((v-.215)/.04)**2)
    color=_mix(color,INK,.7*spill*(1-hl))
    color=_mix(color,MENISCUS,.42*meniscus)
    sheen=min(1.,hl+.7*min(1.,line))
    color=_mix(color,SPEC,.9*sheen)
    color=_mix(color,SPEC,.55*min(1.,bubble[index]))
    return tuple(max(0,min(255,round(c))) for c in color),sheen,dark,up,meniscus


def _maps():
    if 'maps' in _CACHE:return _CACHE['maps']
    cache=_shared()
    diffuse=bytearray();spec=bytearray()
    for y in range(SIZE):
        v=1-y/(SIZE-1)
        for x in range(SIZE):
            u=x/(SIZE-1)
            rgb,sheen,dark,up,glint=_texel(u,v,y*SIZE+x,cache)
            diffuse.extend(rgb)
            # Wet everywhere; brightest on highlights, dullest in the grooves.
            apron=1-shape.smooth((v-.17)/.08)
            level=round(max(40,min(250,190+50*sheen+20*up-120*dark-115*apron+150*glint)))
            spec.extend((level,)*3)
    _CACHE['maps']=(png(diffuse,SIZE,SIZE),png(spec,SIZE,SIZE))
    return _CACHE['maps']


def texture_bytes():
    return _maps()[0]


def surface_maps():
    return {NORMAL:png(bytes((128,128,255))*16,4,4),SPECULAR:_maps()[1]}
