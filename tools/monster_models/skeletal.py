"""Shared deterministic skeleton math, skinning and clip sampling. No gameplay.

Enemy modules provide anatomy, weights and local poses; this layer handles the
format-independent hierarchy and the common IQM export preparation.
"""
import math
from dataclasses import dataclass
from .rat import add, sub, mul, unit, cross


def qmul(a,b):
    x,y,z,w=a; X,Y,Z,W=b
    return (w*X+x*W+y*Z-z*Y,w*Y-x*Z+y*W+z*X,w*Z+x*Y-y*X+z*W,w*W-x*X-y*Y-z*Z)


def inverse(q): return (-q[0],-q[1],-q[2],q[3])


def rotate(q,v):
    t=mul(cross(q[:3],v),2)
    return add(v,add(mul(t,q[3]),cross(q[:3],t)))


def axis(direction,angle): return (*mul(unit(direction),math.sin(angle/2)),math.cos(angle/2))


def between(a,b):
    a,b=unit(a),unit(b)
    xyz=cross(a,b); w=1+sum(x*y for x,y in zip(a,b))
    if w<1e-8: return axis(cross(a,(0,1,0)),math.pi)
    n=math.sqrt(sum(x*x for x in xyz)+w*w)
    return (*mul(xyz,1/n),w/n)


@dataclass
class Rig:
    bones: list
    rest: list

    @classmethod
    def from_world(cls, specs):
        ids={name:i for i,(name,parent,point) in enumerate(specs)}
        bones=[]
        for i,(name,parent,point) in enumerate(specs):
            p=ids[parent] if parent else -1
            if p>=i: raise ValueError('Parents must precede children: '+name)
            bones.append((name,p,sub(point,specs[p][2]) if p>=0 else point))
        return cls(bones,[s[2] for s in specs])

    def matrices(self,frame):
        out=[]
        for i,(name,parent,rest) in enumerate(self.bones):
            loc,q=frame[i][:3],frame[i][3:7]
            if parent>=0:
                pl,pq=out[parent]; loc=add(pl,rotate(pq,loc)); q=qmul(pq,q)
            out.append((loc,q))
        return out

    def deform(self,vertices,influences,frame):
        transforms=self.matrices(frame)
        shifted=[sub(loc,rotate(q,self.rest[i])) for i,(loc,q) in enumerate(transforms)]
        # Rotate once per influence, not once per coordinate. The connected cage
        # has more UV splits; avoid tripling authoring/export work for each one.
        output=[]
        for v,weights in zip(vertices,influences):
            x=y=z=0.0
            for b,w in weights:
                r=rotate(transforms[b][1],v);s=shifted[b]
                x+=w*(r[0]+s[0]);y+=w*(r[1]+s[1]);z+=w*(r[2]+s[2])
            output.append((x,y,z))
        return output

    def chain_weights(self,point,indices):
        best=None
        for a,b in zip(indices,indices[1:]):
            start,end=self.rest[a],self.rest[b];d=sub(end,start)
            t=max(0,min(1,sum(x*y for x,y in zip(sub(point,start),d))/sum(x*x for x in d)))
            distance=math.dist(point,add(start,mul(d,t)))
            if best is None or distance<best[0]: best=(distance,a,b,t)
        _,a,b,t=best
        return [(a,1-t),(b,t)] if 0<t<1 else [(b if t else a,1)]


def assemble(parts,weights):
    vertices=[]; normals=[]; uv=[]; triangles=[]; influences=[]
    for part in parts:
        base=len(vertices)
        vertices.extend(part.vertices); normals.extend(part.normals()); uv.extend(part.uv)
        triangles.extend(tuple(base+i for i in tri) for tri in part.triangles())
        influences.extend(part.skin_weights if hasattr(part,'skin_weights') else
                          [weights(part,v,u) for v,u in zip(part.vertices,part.uv)])
    return parts,vertices,normals,uv,triangles,influences


def sample_clips(rig,clip_specs,pose,vertices,influences):
    clips=[]; bounds=[]
    for name,count,fps,loop in clip_specs:
        frames=[]
        for f in range(count):
            frame=pose(name,f/(count if loop else count-1))
            deformed=rig.deform(vertices,influences,frame)
            lift=max(0,.07-min(v[2] for v in deformed))
            row=list(frame[0]); row[2]+=lift; frame[0]=tuple(row)
            low=[min(v[i] for v in deformed)+(lift if i==2 else 0) for i in range(3)]
            high=[max(v[i] for v in deformed)+(lift if i==2 else 0) for i in range(3)]
            radius=math.sqrt(sum(max(abs(a),abs(b))**2 for a,b in zip(low,high)))
            bounds.append((*low,*high,math.hypot(max(abs(low[0]),abs(high[0])),max(abs(low[1]),abs(high[1]))),radius))
            frames.append(frame)
        clips.append({'name':name,'fps':fps,'loop':loop,'frames':frames})
    return clips,bounds
