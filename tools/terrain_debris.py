"""Original CC0 organic silhouettes for catalog props; OBJ Y is up."""
import math
import random

REBUILT = {'TrampledLeaves', 'TrampledFungus', 'WitheredFungus', 'FungalForest',
           'Vines', 'Skins', 'Junk', 'Rubble'}


def build(mesh, name, rod):
    rng=random.Random(2807)

    def vein(a,b,width,material):
        # Fine veins/gills need only a thin strip, not a many-sided tube.
        dx,dz=b[0]-a[0],b[2]-a[2]; length=math.hypot(dx,dz)
        nx,nz=-dz*width/length,dx*width/length
        points=[(a[0]+nx,a[1],a[2]+nz),(b[0]+nx,b[1],b[2]+nz),
                (b[0]-nx,b[1],b[2]-nz),(a[0]-nx,a[1],a[2]-nz)]
        mesh.face(points,material); mesh.face(list(reversed(points)),material)

    def shell(rim, center, material, underside=None, thickness=.10):
        """Closed thin fan with a shaped perimeter, not a textured rectangle."""
        lower=[(x,y-thickness,z) for x,y,z in rim]
        bottom=(center[0],center[1]-thickness,center[2])
        for i,p in enumerate(rim):
            j=(i+1)%len(rim)
            mesh.face([center,rim[j],p],material)
            mesh.face([bottom,lower[i],lower[j]],underside or material)
            mesh.face([p,rim[j],lower[j],lower[i]],material)

    def leaf(x,z,length,width,angle,y=.35,material='fruit'):
        ca,sa=math.cos(angle),math.sin(angle)
        def p(u,v,h=0): return (x+ca*u-sa*v,y+h,z+sa*u+ca*v)
        outline=[(-.5,0),(-.30,-.32),(-.06,-.49),(.22,-.36),(.5,0),(.20,.39),(-.10,.44),(-.34,.27)]
        rim=[p(u*length,v*width,.08+(i%3)*.10) for i,(u,v) in enumerate(outline)]
        shell(rim,p(0,0,.45),material,thickness=.09)
        vein(p(-.60*length,0,.25),p(.40*length,0,.45),.09,'wood')
        for u in (-.22,0,.20):
            for side in (-1,1):
                vein(p(u*length,0,.48),p((u+.13)*length,side*width*.28,.27),.045,'leather')

    def cap(x,z,r,y,height,material='leather',broken=False):
        # Broad domed canopy, pale underside and radial gills.
        angles=[i*math.tau/10 for i in range(10)]
        rim=[(x+r*math.cos(a)*(1+.09*math.sin(i*7)),y+.12*math.sin(i*3),z+r*math.sin(a)) for i,a in enumerate(angles)]
        if broken: rim[2]=(x+r*.22,y+.08,z+r*.18)
        inner=[(x+(p[0]-x)*.62,y+height*.78,z+(p[2]-z)*.62) for p in rim]
        peak=(x,y+height,z)
        underside=(x,y-.18,z)
        for i,p in enumerate(rim):
            j=(i+1)%len(rim)
            # Two-sided canopy; the underside remains below the rim, never a
            # second pale dome that can read as a white top from above.
            for face in ([p,rim[j],inner[j],inner[i]],[inner[i],inner[j],peak]):
                mesh.face(face,material); mesh.face(list(reversed(face)),material)
            mesh.face([underside,p,rim[j]],'paper')
            mesh.face([underside,rim[j],p],'paper')
        for a in angles:
            vein((x,y-.22,z),(x+r*.88*math.cos(a),y-.20,z+r*.88*math.sin(a)),.065,'wood')

    if name=='TrampledLeaves':
        for i in range(14):
            leaf(rng.uniform(-22,22),rng.uniform(-22,22),rng.uniform(6,11),rng.uniform(3,5),
                 rng.random()*math.tau,.28+(i%3)*.15,'leather' if i%5==0 else 'fruit')
        # Two flattened fern-like fronds with paired, tapered leaflets.
        for x,z,angle in ((-8,7,.7),(12,-11,2.2)):
            ca,sa=math.cos(angle),math.sin(angle)
            rod((x-8*ca,.32,z-8*sa),(x+8*ca,.48,z+8*sa),.14,'wood')
            for j in range(-2,3):
                for side in (-1,1):
                    leaf(x+j*2.4*ca-side*1.8*sa,z+j*2.4*sa+side*1.8*ca,
                         5-abs(j)*.65,1.9,angle+side*.8,.52)
    elif name=='TrampledFungus':
        for i in range(9):
            x,z=rng.uniform(-21,21),rng.uniform(-21,21)
            cap(x,z,rng.uniform(2.3,4.5),.48,rng.uniform(.35,1.0),'leather' if i%3 else 'glass',True)
            rod((x+1,.60,z-2),(x+5,.75,z+2),.45,'paper')
    elif name in ('WitheredFungus','FungalForest'):
        for i,(x,z) in enumerate(((-17,-13),(14,-7),(0,13),(17,18),(-16,17))):
            h=5+i*.65 if name=='WitheredFungus' else 20+i*3
            rod((x,.5,z),(x+1,h*.65,z+1),.85 if h<10 else 1.7,'paper')
            rod((x+1,h*.65,z+1),(x-1,h,z+2),.70 if h<10 else 1.4,'paper')
            cap(x-1,z+2,3.5 if h<10 else 6.8,h,1.1 if h<10 else 3.4,
                'leather' if h<10 else 'glass',h<10)
    elif name=='Vines':
        for i in range(4):
            x=-18+i*12
            rod((x,.7,-20),(x+7,21,18),.65,'wood')
            for j in range(5):
                leaf(x+j*1.4, -20+j*7.6,6,3.2,.7 if j%2 else 2.2,1+j*4)
    elif name=='Skins':
        rod((-27,62,0),(27,62,0),1.4,'wood')
        for i,x in enumerate((-17,0,17)):
            outline=[(-6,60),(-3,51),(-9,45),(-7,24),(-4,15),(0,20),(4,13),(8,27),(7,44),(3,51),(6,60)]
            # A hide tapers at the neck and has torn/lobed edges and folds.
            rim=[(x+u,y,math.sin(j*1.7+i)*1.1) for j,(u,y) in enumerate(outline)]
            center=(x,36,-1.5)
            for j,p in enumerate(rim):
                q=rim[(j+1)%len(rim)]
                mesh.face([center,p,q],'leather')
                mesh.face([center,q,p],'leather')
            rod((x,60,0),(x,63,0),.22,'wood')
    elif name in ('Junk','Rubble'):
        for i in range(13):
            x,z=rng.uniform(-22,22),rng.uniform(-22,22)
            if name=='Rubble':
                radius=rng.uniform(1.6,4.8)
                rim=[(x+radius*rng.uniform(.65,1.1)*math.cos(j*math.tau/5),.18,
                      z+radius*rng.uniform(.65,1.1)*math.sin(j*math.tau/5)) for j in range(5)]
                shell(rim,(x+.3,radius*.7,z-.4),'metal',thickness=.12)
            else:
                angle=rng.random()*math.tau; ca,sa=math.cos(angle),math.sin(angle)
                shape=[(-3,-.8),(.9,-1.1),(3,-.3),(1.5,.2),(2.7,.7),(-2.6,.8)]
                rim=[(x+u*ca-v*sa,.25+(j%2)*.2,z+u*sa+v*ca) for j,(u,v) in enumerate(shape)]
                shell(rim,(x,.70,z),'wood' if i%3 else 'metal',thickness=.14)
