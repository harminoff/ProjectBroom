"""Black jelly: connected melting ink heap, cell clearance, readable gloss and bytes."""
import collections
import hashlib
import json
import math
import unittest
import zlib
from . import black_jelly_animation as jelly, black_jelly_materials as materials, connected_skin, iqm
from .rat import cross, sub
from .skeletal_registry import PENDING, find


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


class BlackJellyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parts,cls.v,cls.n,cls.uv,cls.tri,cls.w=jelly.geometry()
        cls.clips,cls.bounds=jelly.animation_data(cls.v,cls.w)
        cls.ranges={};i=0
        for clip in cls.clips:
            cls.ranges[clip['name']]=(i,i+len(clip['frames']));i+=len(clip['frames'])

    def clip_bounds(self,name):
        a,b=self.ranges[name];return self.bounds[a:b]

    def test_one_closed_connected_baked_surface(self):
        self.assertEqual(len(self.parts),1)
        self.assertEqual(self.parts[0].name,'Connected_skin')
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
        # The committed bake matches the current sculpt and weights.
        self.assertEqual(connected_skin.attach('black_jelly',jelly.build_parts(),jelly.weights)[0].vertices,self.parts[0].vertices)

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

    def test_cell_clearance_floor_contact_and_raw_roots(self):
        # Every frame of every clip stays inside the centred -32..+32 cell.
        for bound in self.bounds:
            self.assertGreaterEqual(bound[2],.06999)
            self.assertLess(bound[2],.15)
            self.assertTrue(all(abs(v)<31.5 for v in (bound[0],bound[1],bound[3],bound[4])))
        for spec,clip in zip(jelly.CLIPS,self.clips):
            count=spec[1]
            for f,frame in enumerate(clip['frames']):
                self.assertEqual(frame[0],jelly.pose(spec[0],f/(count if spec[3] else count-1))[0])

    def test_sagging_heap_proportions_and_spent_puddle(self):
        rest=self.bounds[0]
        width=rest[3]-rest[0];depth=rest[4]-rest[1];height=rest[5]
        self.assertTrue(22<height<30,height)
        self.assertGreater(width,1.8*height)
        self.assertGreater(depth,1.7*height)
        spent=jelly.deform(self.v,self.w,self.clips[-1]['frames'][-1])
        heights=sorted(p[2] for p in spent)
        self.assertLess(max(heights),.4*height)
        self.assertLess(heights[len(heights)//2],3.5)
        # The puddle spreads: its footprint is at least as wide as the heap's.
        self.assertGreaterEqual(max(p[0] for p in spent)-min(p[0] for p in spent),width-.5)

    def test_melting_folds_piles_and_spill_lip(self):
        def radius(theta,v):
            p=jelly.surface(theta,v);lean=jelly.fields(theta,v)['lean']
            return math.hypot(p[0]-jelly.X_SHIFT-jelly.LEAN[0]*lean,
                              (p[1]-jelly.Y_SHIFT-jelly.LEAN[1]*lean)/jelly.Y_SCALE)
        for a,w,amount,top,end in jelly.FOLDS:
            mid=(top+end)/2
            beside=max(radius(a+d,mid) for d in (-2.6*w,2.6*w))
            self.assertGreater(radius(a,mid)-beside,.5*amount,a)
            # Each fold ends in a heavy pile hanging over the pour fillet.
            self.assertGreater(radius(a,end)-max(radius(a+d,end) for d in (-3*w,3*w)),1.5,a)
        # Between the folds the spill lip is the widest ring: the ink pools.
        # (At fold azimuths the heavy piles are meant to spill past it.)
        checked=0
        for i in range(0,360,5):
            theta=math.tau*i/360
            if any(abs(jelly.wrap(theta-a))<1.6*w for a,w,*_ in jelly.FOLDS):continue
            if any(abs(jelly.wrap(theta-a))<1.2*w for a,_,w in jelly.SPILL_RETREATS):continue
            checked+=1
            lip=max(radius(theta,k/1000) for k in range(120,200))
            body=max(radius(theta,k/1000) for k in range(300,700))
            self.assertGreater(lip-body,1.0,i)
        self.assertGreater(checked,12)

    def test_spill_pool_is_irregular_not_a_disc(self):
        # Lobes, drip tongues and retreats make the outline uneven, and the
        # pool's thickness varies: a wet ink spill, not a ceramic saucer.
        def ring(theta):
            pts=[jelly.surface(theta,k/1000) for k in range(100,230)]
            reach=max(math.hypot(p[0]-jelly.X_SHIFT,(p[1]-jelly.Y_SHIFT)/jelly.Y_SCALE) for p in pts)
            lip=max(p[2] for p in pts[:90])
            return reach,lip
        rings=[ring(math.tau*i/180) for i in range(180)]
        reach=[r for r,_ in rings];lip=[z for _,z in rings]
        self.assertGreater(max(reach)-min(reach),4)
        self.assertGreater(max(lip)/min(lip),1.8)
        # At least six separate outward drip lobes around the outline.
        peaks=sum(1 for i in range(180) if reach[i]>reach[i-1] and reach[i]>=reach[(i+1)%180] and reach[i]-min(reach[i-8:i] or reach)>.6)
        self.assertGreaterEqual(peaks,6)

    def test_key_poses_sit_on_middle_frames(self):
        rest=self.bounds[0]
        names=[c['name'] for c in self.clips]
        def mid(name):
            b=self.clip_bounds(name);return b[len(b)//2]
        def mean_x(name):
            frames=self.clips[names.index(name)]['frames']
            posed=jelly.deform(self.v,self.w,frames[len(frames)//2])
            top=[p for p,q in zip(posed,self.v) if q[2]>12]
            return sum(p[0] for p in top)/len(top)
        rest_top=[p for p in self.v if p[2]>12]
        rest_x=sum(p[0] for p in rest_top)/len(rest_top)
        # Slime: a long pseudopod lunges to near the +X cell limit while the
        # heap crouches low behind it.
        self.assertGreater(mean_x('slime')-rest_x,3.0)
        self.assertGreater(mid('slime')[3],rest[3]+2.5)
        self.assertGreater(mid('slime')[3],29)
        self.assertLess(mid('slime')[5],rest[5]-4)
        # Drench: a wave 1.6-2x the resting height whose crest overhangs its
        # own front, so downward-facing underside shows high on the body.
        self.assertGreater(mid('drench')[5],1.6*rest[5])
        self.assertLess(mid('drench')[5],2.0*rest[5])
        frames=self.clips[names.index('drench')]['frames']
        posed=jelly.deform(self.v,self.w,frames[len(frames)//2]);high=.55*mid('drench')[5]
        under=0
        for a,b,c in self.tri:
            pa,pb,pc=posed[a],posed[b],posed[c]
            if min(pa[2],pb[2],pc[2])<high or (pa[0]+pb[0]+pc[0])/3<0:continue
            nrm=cross(sub(pb,pa),sub(pc,pa));length=math.sqrt(sum(x*x for x in nrm))
            if length and nrm[2]/length<-.25:under+=1
        self.assertGreater(under,40)
        self.assertLess(mid('recoil')[5],rest[5]-3.5)          # squashed back
        self.assertLess(mean_x('recoil')-rest_x,-2)
        self.assertLess(mid('collapse')[5],.8*rest[5])         # visibly slumping

    def test_loops_rest_starts_and_weights(self):
        for name in ('idle','ooze','slime','drench','recoil'):
            first=jelly.deform(self.v,self.w,jelly.pose(name,0))
            last=jelly.deform(self.v,self.w,jelly.pose(name,1))
            self.assertLess(max(math.dist(a,b) for a,b in zip(first,last)),1e-8)
        for name in ('slime','drench','recoil','collapse'):
            start=jelly.deform(self.v,self.w,jelly.pose(name,0))
            self.assertLess(max(math.dist(a,b) for a,b in zip(start,self.v)),1e-8)
        for weights in self.w:
            self.assertTrue(1<=len(weights)<=4)
            self.assertAlmostEqual(sum(w for _,w in weights),1,places=9)
        for clip in self.clips:
            for frame in clip['frames']:
                for pose in frame:self.assertEqual(pose[3:],(0,0,0,1,1,1,1))
        # Coincident UV-seam copies share position and weights in every pose.
        keys=[tuple(round(c,6) for c in p) for p in self.v]
        for clip in self.clips:
            posed=jelly.deform(self.v,self.w,clip['frames'][len(clip['frames'])//2]);seen={}
            for key,p,weights in zip(keys,posed,self.w):
                if key in seen:
                    self.assertLess(math.dist(p,seen[key][0]),1e-8)
                    self.assertEqual(weights,seen[key][1])
                seen[key]=(p,weights)

    def test_paint_is_jet_black_yet_readable(self):
        pixels,width=rows(materials.texture_bytes())
        for row in pixels:self.assertEqual(row[:3],row[-3:])   # seamless meridian
        lum=[];violet=0;count=0
        for row in pixels[80:880:4]:
            for x in range(0,width*3,12):
                r,g,b=row[x:x+3];lum.append(.2126*r+.7152*g+.0722*b);count+=1
                violet+=b>g+12 and r>g
        lum.sort()
        self.assertLess(lum[len(lum)//2],32)                     # the body is ink
        # Crisp gloss pools and drip lines: a small, bright fraction.
        self.assertGreater(sum(l>170 for l in lum)/count,.0015)
        self.assertGreater(sum(l>120 for l in lum)/count,.015)
        self.assertGreater(sum(l<12 for l in lum)/count,.15)     # true black depth
        self.assertGreater(violet/count,.2)                      # violet depth, not grey

    def test_shader_and_pending_profile(self):
        shader=(jelly.ROOT/'mod/BrogueDoom'/jelly.SHADER).read_text()
        self.assertNotIn('Bright',shader)
        self.assertNotIn('timer',shader)
        row=find('MK_BLACK_JELLY')
        self.assertEqual(row['clips'],[c[0] for c in jelly.CLIPS])
        self.assertEqual(row['durations'][2:],[c[1] for c in jelly.CLIPS[2:]])
        self.assertEqual(row['skin'],jelly.SKIN)
        for path in row['ownedFiles']:self.assertTrue((jelly.ROOT/path).is_file(),path)
        snippet=PENDING/'MK_BLACK_JELLY.gldefs'  # integration appends it to the shared GLDEFS
        gldefs=(snippet if snippet.exists() else jelly.ROOT/'mod/BrogueDoom/GLDEFS').read_text()
        for path in (jelly.SKIN,jelly.NORMAL,jelly.SPECULAR,jelly.SHADER):self.assertIn(f'"{path}"',gldefs)

    def test_export_and_all_maps_match_source(self):
        actual=iqm.encode(self.v,self.n,self.uv,self.tri,self.w,jelly.BONES,self.clips,self.bounds,
                          mesh_label='Project_Broom_black_jelly',material_path=jelly.SKIN)
        self.assertEqual(actual,(jelly.ROOT/'mod/BrogueDoom/models/monsters/52_black_jelly.iqm').read_bytes())
        for path,data in {jelly.SKIN:materials.texture_bytes(),**materials.surface_maps()}.items():
            self.assertEqual(hashlib.sha256(data).digest(),hashlib.sha256((jelly.ROOT/'mod/BrogueDoom'/path).read_bytes()).digest())


if __name__=='__main__':unittest.main()
