"""Acidic jelly: connected lobed gel, floor contact, spent collapse and bytes."""
import collections
import hashlib
import math
import unittest
import zlib
from . import acid_jelly_animation as jelly, acid_jelly_materials as materials, acid_jelly_shape as shape, iqm
from .rat import cross, sub


def rows(png):
    """Decode this repository's unfiltered RGB PNG writer output."""
    data=b'';pos=8
    while pos<len(png):
        length=int.from_bytes(png[pos:pos+4],'big');kind=png[pos+4:pos+8]
        if kind==b'IHDR':width=int.from_bytes(png[pos+8:pos+12],'big')
        if kind==b'IDAT':data+=png[pos+8:pos+8+length]
        pos+=12+length
    raw=zlib.decompress(data);stride=width*3+1
    return [raw[i*stride+1:(i+1)*stride] for i in range(len(raw)//stride)],width


class AcidJellyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parts,cls.v,cls.n,cls.uv,cls.tri,cls.w=jelly.geometry()
        cls.clips,cls.bounds=jelly.animation_data(cls.v,cls.w)

    def test_one_closed_connected_surface(self):
        self.assertEqual(len(self.parts),1)
        keys=[tuple(round(c,6) for c in p) for p in self.v]
        edges=collections.Counter();adj=collections.defaultdict(set)
        for a,b,c in self.tri:
            for i,j in ((a,b),(b,c),(c,a)):
                edge=tuple(sorted((keys[i],keys[j])))
                self.assertNotEqual(*edge)
                edges[edge]+=1;adj[edge[0]].add(edge[1]);adj[edge[1]].add(edge[0])
        self.assertEqual(set(edges.values()),{2})
        seen=set();queue=[keys[0]]
        while queue:
            node=queue.pop()
            if node not in seen:seen.add(node);queue.extend(adj[node]-seen)
        self.assertEqual(len(seen),len(set(keys)))
        self.assertEqual(len(set(keys))-len(edges)+len(self.tri),2)

    def test_every_frame_keeps_triangles_oriented(self):
        rest=[cross(sub(self.v[b],self.v[a]),sub(self.v[c],self.v[a])) for a,b,c in self.tri]
        for clip in self.clips:
            for f,frame in enumerate(clip['frames']):
                posed=jelly.deform(self.v,self.w,frame)
                for triangle,normal in zip(self.tri,rest):
                    a,b,c=triangle
                    current=cross(sub(posed[b],posed[a]),sub(posed[c],posed[a]))
                    self.assertGreater(sum(x*x for x in current),1e-14,(clip['name'],f,triangle))
                    self.assertGreater(sum(p*q for p,q in zip(normal,current)),0,(clip['name'],f,triangle))

    def test_cell_floor_and_spent_puddle(self):
        for bound in self.bounds:
            self.assertGreaterEqual(bound[2],.06999)
            self.assertLess(bound[2],.15)
            self.assertTrue(all(abs(v)<31.5 for v in (bound[0],bound[1],bound[3],bound[4])))
        # Settled death is a low spread puddle, far below the living crown.
        self.assertLess(self.bounds[-1][5],9)
        self.assertLess(self.bounds[-1][5],.32*self.bounds[0][5])
        self.assertGreater(self.bounds[-1][5],3)
        spent=jelly.deform(self.v,self.w,self.clips[-1]['frames'][-1])
        heights=sorted(p[2] for p in spent)
        self.assertLess(heights[len(heights)//2],3.5)
        self.assertLess(heights[int(.9*len(heights))],7)
        # A heavy slumped gel: much wider than tall, yet still a large mass.
        width=self.bounds[0][3]-self.bounds[0][0]
        self.assertGreater(self.bounds[0][5],19)
        self.assertGreater(width,2.2*self.bounds[0][5])
        # No automatic floor compensation: exported roots equal the raw pose.
        for spec,clip in zip(jelly.CLIPS,self.clips):
            count=spec[1]
            for f,frame in enumerate(clip['frames']):
                self.assertEqual(frame[0],jelly.pose(spec[0],f/(count if spec[3] else count-1))[0])

    def test_three_fused_lobes_shape_the_outline(self):
        # Three separate swollen lobes, not the pink jelly's single dome:
        # each lobe rises strongly and the sculpted upper outline bulges at
        # every lobe relative to the valley between it and its neighbour.
        phis=[.2+i*.02 for i in range(50)]
        rise=lambda theta:max(shape.fields(theta,phi)['lobe'] for phi in phis)
        def outline(theta):
            return max(math.hypot(p[0]-shape.X_SHIFT,(p[1]-shape.Y_SHIFT)/shape.Y_SCALE) for p in
                       (shape.surface(theta,.45+k*.0075) for k in range(41)))
        lobes=sorted(a for a,*_ in shape.LOBES)
        for a,b in zip(lobes,lobes[1:]+[lobes[0]+math.tau]):
            valley=outline((a+b)/2)
            self.assertGreater(min(outline(a),outline(b))-valley,1.5)
            self.assertGreater(min(rise(a),rise(b)),5.5)

    def test_overhanging_skirt_and_budding_blobs(self):
        # The skirt lip overhangs its floor contact, and three satellite
        # blobs bud from the base in the same skin (cosmetic, in the cell).
        def radius(theta,v):
            p=shape.surface(theta,v)
            return math.hypot(p[0]-shape.X_SHIFT,(p[1]-shape.Y_SHIFT)/shape.Y_SCALE),p[2]
        for i in range(0,360,15):
            theta=math.tau*i/360
            ring=[radius(theta,k/400) for k in range(1,160)]
            contact=max(r for r,z in ring if z<.6)
            lip=max(r for r,z in ring if 1.5<z<8)
            self.assertGreater(lip-contact,.8,i)
        for a,e,amount,reach in shape.BUDS:
            beside=[radius(a+d,.3)[0] for d in (-1.3*reach,1.3*reach)]
            self.assertGreater(radius(a,.3)[0]-max(beside),1.5)

    def test_loop_recovery_and_uv_seams(self):
        keys=[tuple(round(c,6) for c in p) for p in self.v]
        rest=jelly.deform(self.v,self.w,jelly.pose('idle',0))
        for name in ('idle','creep','burn','engulf','recoil'):
            first=jelly.deform(self.v,self.w,jelly.pose(name,0))
            last=jelly.deform(self.v,self.w,jelly.pose(name,1))
            self.assertLess(max(math.dist(a,b) for a,b in zip(first,last)),1e-8)
        for name in ('burn','engulf','recoil','dissolve'):
            start=jelly.deform(self.v,self.w,jelly.pose(name,0))
            self.assertLess(max(math.dist(a,b) for a,b in zip(start,self.v)),1e-8)
        for clip in self.clips:
            seen={}
            posed=jelly.deform(self.v,self.w,clip['frames'][len(clip['frames'])//2])
            for key,p,weights in zip(keys,posed,self.w):
                if key in seen:
                    self.assertLess(math.dist(p,seen[key][0]),1e-8)
                    self.assertEqual(weights,seen[key][1])
                seen[key]=(p,weights)
        pixels,width=rows(materials.texture_bytes())
        for row in pixels:self.assertEqual(row[:3],row[-3:])

    def test_translation_only_normalized_weights(self):
        for weights in self.w:
            self.assertTrue(1<=len(weights)<=4)
            self.assertAlmostEqual(sum(w for _,w in weights),1,places=9)
        for clip in self.clips:
            for frame in clip['frames']:
                for pose in frame:self.assertEqual(pose[3:],(0,0,0,1,1,1,1))
        # Lobe anchors swell out of phase in idle: a living mass, not a bob.
        idle=self.clips[0]['frames'][6]
        lobes=[jelly.bone(3,i) for i,a in enumerate(jelly.TOP) if a in jelly.LOBE_ANGLES]
        rises=[idle[b][2]-jelly.BONES[b][2][2] for b in lobes]
        self.assertGreater(max(rises)-min(rises),.5)

    def test_paint_is_distinct_acid_green(self):
        pixels,width=rows(materials.texture_bytes())
        total=[0,0,0];count=0;bright=0
        for row in pixels[80:900:4]:
            for x in range(0,width*3,12):
                r,g,b=row[x:x+3];total[0]+=r;total[1]+=g;total[2]+=b;count+=1
                bright+=r>.55*g and g>80
        mean=[t/count for t in total]
        self.assertGreater(mean[1],mean[0]*1.4)   # green dominant, never pink
        self.assertGreater(mean[1],mean[2]*1.5)
        self.assertGreater(bright/count,.06)      # visible yellow-lime acid film

    def test_export_and_all_maps_match_source(self):
        actual=iqm.encode(self.v,self.n,self.uv,self.tri,self.w,jelly.BONES,self.clips,self.bounds,
                          mesh_label='Project_Broom_acid_jelly',material_path=jelly.SKIN)
        self.assertEqual(actual,(jelly.ROOT/'mod/BrogueDoom/models/monsters/34_acid_jelly.iqm').read_bytes())
        for path,data in {jelly.SKIN:materials.texture_bytes(),**materials.surface_maps()}.items():
            self.assertEqual(hashlib.sha256(data).digest(),hashlib.sha256((jelly.ROOT/'mod/BrogueDoom'/path).read_bytes()).digest())


if __name__=='__main__':unittest.main()
