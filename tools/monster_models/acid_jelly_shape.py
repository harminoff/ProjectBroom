"""Analytic sculpt shared by the acidic jelly mesh and its painted maps.

The body is one closed latitude/longitude surface. Skin parameter U is the
azimuth and V runs from the flat underside pole to the crown pole. A rolled
contact rim, three fused crown lobes, flank pouches, acid runnels ending in
rim beads and etched craters are all offsets of that one surface, so no detail
can separate from the mass. Every value is an art choice, not a Brogue size.
"""
import math

TAU=math.tau
RB=20.0          # skirt radius before relief
ZC=4.4           # height of the overhanging skirt
HT=16.0          # low sagging dome rise above the skirt
FLOOR=.12
Y_SCALE=.94
X_SHIFT=-1.9
Y_SHIFT=1.3      # centres the forward-heavy lobes in the cell

# Swollen fused lobes: azimuth, elevation, bulge along the surface normal,
# angular radius. Each is a rounded spherical cap on the one skin; they sit
# low and far apart so deep valleys break the outline from every side.
LOBES=((0.30,.50,7.4,.80),(2.42,.58,6.4,.74),(4.28,.46,6.9,.78))
TOP_LOBE=(1.20,1.20,2.4,.58)
# Satellite blobs budding from the skirt (cosmetic, part of the same skin).
BUDS=((1.05,-.04,5.0,.30),(3.30,.00,4.4,.27),(5.25,-.06,5.2,.32))
# Acid runnels start in lobe valleys and thicken downward into hanging drips.
RUNNELS=((1.36,.080,1.25),(3.36,.074,1.15),(5.40,.082,1.30),
         (0.72,.052,.75),(2.95,.056,.80),(4.85,.052,.75),(6.05,.050,.65))
# Sculpted acid-etched craters: azimuth, elevation, angular size, depth.
CRATERS=((0.12,.62,.10,.7),(2.30,.72,.09,.6),(4.10,.60,.095,.65),
         (0.62,.28,.06,.45),(4.62,.25,.06,.4),(2.75,.30,.055,.4))


def wrap(a):
    return (a+math.pi)%TAU-math.pi


def smooth(t):
    t=max(0.,min(1.,t));return t*t*(3-2*t)


def gauss(x):
    return math.exp(-x*x)


def elevation(v):
    """Latitude: 30% of rings form the underside and rim, 70% the body."""
    g=v/.6 if v<.3 else .5+(v-.3)/1.4
    return math.pi*(g-.5)


def base(phi):
    """Axisymmetric base profile (radius, height)."""
    c=max(0.,math.cos(phi))
    if phi<0:
        s=-math.sin(phi)
        return RB*c**.30,FLOOR+ZC*(1-s**2.0)
    return RB*c**1.15,FLOOR+ZC+HT*math.sin(phi)**.9


def base_height(v):
    return base(elevation(v))[1]


def cap(theta,phi,a,e,reach):
    """Rounded spherical-cap profile by great-circle distance; pole-safe."""
    c=math.sin(phi)*math.sin(e)+math.cos(phi)*math.cos(e)*math.cos(theta-a)
    rho=math.acos(max(-1.,min(1.,c)))/reach
    return (1-rho*rho)**1.25 if rho<1 else 0.


def fields(theta,phi):
    """Named relief fields at one surface parameter; reused by the paint."""
    theta%=TAU
    taper=smooth((math.pi/2-phi)/.32)
    lobe=0.;lobe_id=-1;best=0.
    for i,(a,e,rise,reach) in enumerate(LOBES+(TOP_LOBE,)):
        g=cap(theta,phi,a,e,reach)
        if g>best and i<len(LOBES):best,lobe_id=g,i
        lobe+=rise*g
    bud=sum(amount*cap(theta,phi,a,e,reach) for a,e,amount,reach in BUDS)
    runnel=bead=0.
    down=smooth((.70-phi)/.30)*smooth((phi+.50)/.14)
    for a,width,amount in RUNNELS:
        d=wrap(theta-a-.045*math.sin(phi*7+a*3))
        # Broad low ridges: they read as thickened drips, never as fins.
        runnel+=.70*amount*gauss(d/(width*1.9))*down*(.55+.45*smooth((.5-phi)/.6))
        # Thick drips hang from the skirt lip down towards the floor.
        bead+=1.25*amount*gauss(d/(width*3.0))*gauss((phi+.40)/.22)
    pit=rim=0.
    for a,e,size,depth in CRATERS:
        rho=math.hypot(wrap(theta-a)*math.cos(e),phi-e)/size
        if rho<3.2:
            pit+=depth*gauss(rho)
            rim+=.45*depth*gauss((rho-1.35)/.45)
    fold=.40*math.sin(theta*9+phi*3.1+.8*math.sin(theta*2))*gauss((phi-.05)/.35)
    fold+=.18*math.sin(theta*14-phi*6)*gauss((phi-.55)/.35)*taper
    scallop=.055*math.cos(theta*5+.6)+.03*math.sin(theta*3+1.1)
    return dict(lobe=lobe,lobe_id=lobe_id,lobe_weight=best,bud=bud,runnel=runnel,
                bead=bead,pit=pit,pit_rim=rim,fold=fold,scallop=scallop,taper=taper)


def surface(theta,v,info=None):
    phi=elevation(v)
    r,z=base(phi)
    f=fields(theta,phi)
    c=math.cos(phi);s=math.sin(phi)
    # The heavy gel slumps: an overhanging skirt lip and a sagging belly.
    skirt=2.4*gauss((phi+.22)/.20)*(1+.18*math.sin(theta*3+.9))
    belly=1.8*gauss((phi-.12)/.28)
    radial=r*(1+f['scallop']*gauss((phi+.1)/.6))+skirt+belly+f['runnel']+f['bead']+f['fold']
    radial+=f['bud']*max(.2,c)
    # Lobes sag outward more than upward, like heavy swollen gel.
    radial+=1.10*f['lobe']*c;z+=.80*f['lobe']*max(0.,s)-1.4*gauss((math.pi/2-phi)/.45)
    etched=f['pit_rim']-f['pit']
    radial+=etched*c;z+=etched*max(0.,s)
    radial=max(0.,radial)
    t=theta%TAU
    x=radial*math.cos(t)+X_SHIFT
    y=radial*math.sin(t)*Y_SCALE+Y_SHIFT
    z=max(FLOOR,z)
    if info is not None:info.update(f,phi=phi)
    return (x,y,z)
