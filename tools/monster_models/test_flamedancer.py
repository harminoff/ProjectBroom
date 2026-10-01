"""Flamedancer: lattice skinning, clearance, key poses, extinction, fullbright shader and bytes."""
import collections
import math
import unittest
from . import flamedancer_animation as g, flamedancer_materials as m, iqm
from .skeletal_registry import find


def closed(part):
    edges=collections.Counter();keys=[tuple(round(c,5) for c in v) for v in part.vertices]
    for a,b,c in part.triangles():
        for i,j in ((a,b),(b,c),(c,a)):edges[tuple(sorted((keys[i],keys[j])))]+=1
    return set(edges.values())=={2}


class FlamedancerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parts,cls.v,cls.n,cls.uv,cls.t,cls.w=g.geometry()
        cls.clips,cls.bounds=g.animation_data(cls.v,cls.w)
        cls.named={c['name']:c for c in cls.clips}

    def test_anatomy_is_fire_not_a_robe(self):
        names=[p.name for p in self.parts]
        self.assertEqual(sum(n.startswith('column_tongue') for n in names),12)
        self.assertEqual(sum(n.startswith('skirt_flame') for n in names),8)
        self.assertEqual(sum(n.startswith('side_lick') for n in names),11)
        self.assertIn('fireball',names);self.assertIn('head',names);self.assertIn('arm_L',names);self.assertIn('arm_R',names)
        self.assertEqual(sum(n.startswith('finger_flame') for n in names),6)
        self.assertEqual(sum(n.startswith('spark') for n in names),8)
        for p in self.parts:self.assertTrue(closed(p),p.name)
        self.assertEqual(self.clips[0]['name'],'idle')

    def test_lattice_weights_are_exact_and_affine(self):
        for p,weights in zip(self.v,self.w):
            self.assertTrue(1<=len(weights)<=4)
            self.assertAlmostEqual(math.fsum(a for _,a in weights),1,places=9)
            self.assertTrue(all(0<=a<=1 for _,a in weights))
            rec=tuple(math.fsum(g.REST[b][a]*wt for b,wt in weights) for a in range(3))
            self.assertLess(math.dist(p,rec),1e-4)
        for frame in (f for c in self.clips for f in c['frames']):
            self.assertTrue(all(tuple(b[7:])==(1,1,1) for b in frame))

    def test_loops_and_centered_clearance(self):
        for name in ('idle','dance'):
            start=g.deform(self.v,self.w,g.pose(name,0));end=g.deform(self.v,self.w,g.pose(name,1))
            self.assertLess(max(math.dist(a,b) for a,b in zip(start,end)),1e-6)
        for i,b in enumerate(self.bounds):
            self.assertGreater(b[0],-32,i);self.assertGreater(b[1],-32,i)
            self.assertLess(b[3],32,i);self.assertLess(b[4],32,i)

    def test_key_poses_on_middle_frame_change_the_silhouette(self):
        idle=g.deform(self.v,self.w,self.named['idle']['frames'][0])
        for name in ('sear','bolt','recoil'):
            frames=self.named[name]['frames'];mid=g.deform(self.v,self.w,frames[len(frames)//2])
            first=g.deform(self.v,self.w,frames[0])
            travel=max(math.dist(a,b) for a,b in zip(idle,mid))
            self.assertGreater(travel,9,name)
            self.assertGreater(max(math.dist(a,b) for a,b in zip(first,mid)),9,name)
        sear=self.named['sear']['frames'];sv=g.deform(self.v,self.w,sear[len(sear)//2])
        self.assertLess(max(p[2] for p in sv),.75*max(p[2] for p in idle))      # the lunge drops low
        self.assertGreater(max(p[0] for p in sv),max(p[0] for p in idle)+6)     # and reaches forward (+X)

    def test_cast_fireball_forms_only_in_bolt(self):
        first=0
        for p in self.parts:
            if p.name=='fireball':break
            first+=len(p.vertices)
        count=[len(p.vertices) for p in self.parts if p.name=='fireball'][0]
        def ball(frame):return g.deform(self.v,self.w,frame)[first:first+count]
        def extent(pts):return max(max(p[a] for p in pts)-min(p[a] for p in pts) for a in range(3))
        # Only the ball's own cage weights are needed to test it; skinning the whole mesh per frame is not.
        for name in ('idle','dance','sear','recoil','gutter'):
            for frame in self.named[name]['frames'][::4]:
                self.assertLess(extent(g.RIG.deform(self.v[first:first+count],self.w[first:first+count],frame)),.01,name)
        bolt=self.named['bolt']['frames'];mid=g.RIG.deform(self.v[first:first+count],self.w[first:first+count],bolt[len(bolt)//2])
        self.assertGreater(extent(mid),11)                                          # a ball about 1.5x its rest size
        self.assertGreater(sum(p[0] for p in mid)/len(mid),15)                      # out in front of the body (+X)
        self.assertLess(max(p[0] for p in mid),32)

    def test_bolt_flares_the_column_and_reaches_forward(self):
        idle=g.deform(self.v,self.w,self.named['idle']['frames'][0])
        bolt=self.named['bolt']['frames'];mid=g.deform(self.v,self.w,bolt[len(bolt)//2])
        core=[];k=0
        for p in self.parts:
            if p.name=='hot_core':core=list(range(k,k+len(p.vertices)))
            k+=len(p.vertices)
        width=lambda pts:max(p[1] for p in pts)-min(p[1] for p in pts)
        self.assertGreater(width([mid[i] for i in core]),1.35*width([idle[i] for i in core]))

    def test_death_sags_then_is_fully_extinguished(self):
        gut=self.named['gutter']['frames'];mid=g.deform(self.v,self.w,gut[len(gut)//2])
        self.assertLess(max(p[2] for p in mid),22)
        last=g.deform(self.v,self.w,gut[-1])
        self.assertLess(max(max(p[a] for p in last)-min(p[a] for p in last) for a in range(3)),.004)

    def test_front_face_and_eyes_point_plus_x(self):
        head=[p for p in self.parts if p.name=='head'][0]
        front=[v for v,a in zip(head.vertices,head.pa) if abs(a-.5)<.04]
        self.assertGreater(sum(v[0] for v in front)/len(front),head.vertices[0][0])
        px=m.pigment('head',.5+.085,.5-.02,0,0)
        self.assertLess(sum(px),260)                                             # dark eye slit at the front

    def test_profile_durations_and_report(self):
        row=find('MK_FLAMEDANCER')
        self.assertEqual(row['clips'],[c['name'] for c in self.clips])
        for role,count,fps in ((2,24,35),(3,26,35),(4,14,35),(5,36,35)):
            self.assertGreaterEqual(row['durations'][role],math.ceil(count*35/fps))
        self.assertNotIn('visualScale',row);self.assertNotIn('emissive',row);self.assertNotIn('additiveFlame',row)
        self.assertEqual(row['report'],'docs/flamedancer-animation.md');self.assertTrue(row['traits'])

    def test_exact_runtime_texture_shader_and_inert_proxy(self):
        data=iqm.encode(self.v,self.n,self.uv,self.t,self.w,g.BONES,self.clips,self.bounds,
                        mesh_label='Project_Broom_flamedancer',material_path=g.SKIN)
        self.assertEqual(data,(g.ROOT/g.MODEL).read_bytes())
        self.assertEqual(g.texture_bytes(),(g.ROOT/'mod/BrogueDoom'/g.SKIN).read_bytes())
        shader=(g.ROOT/g.SHADER).read_text()
        for word in ('material.Bright','uCameraPos','timer'):self.assertIn(word,shader)
        pending=g.ROOT/'assets/monsters/skeletal_pending/MK_FLAMEDANCER.gldefs'
        gldefs=pending.read_text() if pending.is_file() else (g.ROOT/'mod/BrogueDoom/GLDEFS').read_text()
        self.assertIn('shaders/flamedancer-fire.fp',gldefs);self.assertNotIn('pointlight',gldefs.split('BRGFDANC')[1].split('}')[0])
        text=(g.ROOT/'mod/BrogueDoom/brogue_monsters.zs').read_text()
        proxy=text.split('class BrogueMonsterK54 :')[1].split('class ')[0]
        self.assertIn('BrogueMonsterProxyBase',proxy)
        for forbidden in ('A_Explode','A_CustomMissile','A_Chase','A_Damage','+SOLID','Random'):self.assertNotIn(forbidden,proxy)


if __name__=='__main__':unittest.main()
