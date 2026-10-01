"""Mangrove dryad: fused bark skin, arching roots, clearance, key poses, floor death, exact bytes."""
import collections
import math
import unittest
from . import mangrove_dryad_animation as g, mangrove_dryad_materials as m, iqm
from .skeletal_registry import find


class MangroveDryadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parts,cls.v,cls.n,cls.uv,cls.t,cls.w=g.geometry()
        cls.clips,cls.bounds=g.animation_data(cls.v,cls.w)
        cls.named={c['name']:c for c in cls.clips}
        cls.owner=[p.name for p in cls.parts for _ in p.vertices]

    def deformed(self,clip,fraction):
        frames=self.named[clip]['frames'];return g.deform(self.v,self.w,frames[min(len(frames)-1,int(len(frames)*fraction))])

    def points(self,pts,prefix):
        return [pts[i] for i,o in enumerate(self.owner) if o.startswith(prefix)]

    def test_anatomy_and_single_fused_skin(self):
        names={p.name for p in self.parts}
        for want in ('Connected_skin','head_skull','head_brow_1','eye_1','eye_-1','head_tooth_up_2','crown_0','crown_5','moss_trail',
                     'stub_R','vine_L','vine_R','hollow','shard_0','shard_8'):
            self.assertIn(want,names)
        self.assertEqual([p.name for p in self.parts].count('Connected_skin'),1)
        self.assertFalse([n for n in names if n.startswith('skin_') or n.startswith('hang_') or n=='stub_L'])
        self.assertEqual(self.clips[0]['name'],'idle')
        skin=[p for p in self.parts if p.name=='Connected_skin'][0]
        ids=skin.skin_topology;edges=collections.Counter()
        for a,b,c in skin.triangles():
            for x,y in ((ids[a],ids[b]),(ids[b],ids[c]),(ids[c],ids[a])):edges[tuple(sorted((x,y)))]+=1
        self.assertEqual(set(edges.values()),{2})                                          # one closed surface

    def test_roots_arch_with_gaps_and_stay_in_cell(self):
        skin=[i for i,o in enumerate(self.owner) if o=='Connected_skin']
        idle=self.deformed('idle',0)
        lows=[idle[i] for i in skin if idle[i][2]<3]
        self.assertGreater(len(lows),100)                                                   # planted feet
        self.assertLess(max(max(abs(p[0]),abs(p[1])) for p in lows),31.5)
        under=[idle[i] for i in skin if 3<idle[i][2]<17.5 and math.hypot(idle[i][0],idle[i][1])<8]
        self.assertEqual(len(under),0)                                                      # open gap beneath the trunk
        self.assertEqual(len(g.ROOTS),8);self.assertGreater(len({z for _,_,z in g.ROOTS}),6)   # irregular heights

    def test_weights(self):
        for weights in self.w:
            self.assertTrue(1<=len(weights)<=4)
            self.assertAlmostEqual(math.fsum(a for _,a in weights),1,places=9)
        for frame in (f for c in self.clips for f in c['frames']):
            self.assertTrue(all(tuple(b[7:])==(1,1,1) for b in frame))

    def test_rest_pose_is_authored_shape_and_loops(self):
        rest=g.deform(self.v,self.w,[(*l,0,0,0,1,1,1,1) for _,_,l in g.BONES])
        self.assertLess(max(math.dist(a,b) for a,b in zip(rest,self.v)),1e-6)
        for name in ('idle','stride'):
            a=g.deform(self.v,self.w,g.pose(name,0));b=g.deform(self.v,self.w,g.pose(name,1))
            self.assertLess(max(math.dist(x,y) for x,y in zip(a,b)),1e-6,name)

    def test_every_frame_stays_inside_the_cell(self):
        for c in self.clips:
            for fi,frame in enumerate(c['frames']):
                d=g.deform(self.v,self.w,frame);lift=max(0,.07-min(p[2] for p in d))
                for p in d:
                    self.assertLessEqual(abs(p[0]),32,(c['name'],fi));self.assertLessEqual(abs(p[1]),32,(c['name'],fi))
                self.assertGreaterEqual(min(p[2] for p in d)+lift,-.001)
        for i,b in enumerate(self.bounds):
            self.assertGreater(b[0],-32,i);self.assertGreater(b[1],-32,i);self.assertLess(b[3],32,i);self.assertLess(b[4],32,i)

    def test_lash_is_a_wide_asymmetric_lateral_sweep_on_the_middle_frame(self):
        idle=self.deformed('idle',0);mid=self.deformed('lash',.5);first=self.deformed('lash',0)
        self.assertGreater(max(math.dist(a,b) for a,b in zip(idle,mid)),20)
        self.assertGreater(max(math.dist(a,b) for a,b in zip(first,mid)),20)
        right=[p for p in self.points(mid,'vine_R')];left=[p for p in self.points(mid,'vine_L')]
        self.assertGreater(max(p[1] for p in right),22)                                      # right vine reaches its side
        self.assertGreater(max(p[2] for p in left),55)                                       # left arm flung up
        self.assertGreater(min(p[1] for p in right)-max(p[1] for p in left),-40)
        eyes=self.points(mid,'eye_');self.assertTrue(all(p[2]>50 for p in eyes))              # face clear of the vine

    def test_vines_and_recoil_change_the_silhouette(self):
        idle=self.deformed('idle',0)
        for clip in ('vines','recoil'):
            self.assertGreater(max(math.dist(a,b) for a,b in zip(idle,self.deformed(clip,.5))),8,clip)

    def test_collapse_ends_low_on_the_floor_with_shards_out(self):
        last=self.deformed('collapse',1.0);lift=max(0,.07-min(p[2] for p in last))
        self.assertLess(max(p[2] for p in last)+lift,45)
        self.assertAlmostEqual(min(p[2] for p in last)+lift,.07,places=2)
        head=self.points(last,'head_skull');self.assertLess(max(p[2] for p in head)+lift,22)
        shards=[self.points(last,f'shard_{k}') for k in range(9)]
        for s in shards:
            self.assertLess(max(p[2] for p in s)+lift,6)                                     # lying flat on the floor
            self.assertGreater(max(math.hypot(p[0],p[1]) for p in s),8)                      # thrown out of the trunk
        idle=self.deformed('idle',0)
        for s in (self.points(idle,f'shard_{k}') for k in range(9)):
            self.assertLess(max(math.hypot(p[0],p[1]) for p in s),5)                         # hidden inside the trunk at rest
        early=self.deformed('collapse',.1)
        self.assertGreater(max(p[2] for p in early),60)

    def test_skin_paint_is_tan_with_wide_value_range(self):
        skin=[p for p in self.parts if p.name=='Connected_skin'][0]
        self.assertLess(min(skin.pv) if hasattr(skin,'pv') else 0,.1)
        lo=m.pigment('skin',.4,.05,10,10);mid=m.pigment('skin',.4,.5,10,10);hi=m.pigment('skin',.4,.95,10,10)
        self.assertLess(sum(lo),160);self.assertGreater(sum(hi),420)
        r,gg,b=mid;self.assertTrue(r>gg>b and r-b>40)                                      # khaki: warm and tan
        for role in ('glow',):
            self.assertGreater(sum(m.pigment(role,.5,.5,50,50)),500)

    def test_profile_durations_and_report(self):
        row=find('MK_ANCIENT_SPIRIT')
        self.assertEqual(row['clips'],[c['name'] for c in self.clips])
        for role,(count,fps) in zip(range(2,6),((26,35),(28,35),(14,35),(40,35))):
            self.assertGreaterEqual(row['durations'][role],math.ceil(count*35/fps))
        for bad in ('visualScale',):self.assertNotIn(bad,row)
        self.assertEqual(row['report'],'docs/mangrove-dryad-animation.md');self.assertTrue(row['traits'])
        self.assertEqual(row['class'],'BrogueMonsterK67')

    def test_exact_runtime_texture_and_inert_proxy(self):
        data=iqm.encode(self.v,self.n,self.uv,self.t,self.w,g.BONES,self.clips,self.bounds,
                        mesh_label='Project_Broom_ancient_spirit',material_path=g.SKIN)
        self.assertEqual(data,(g.ROOT/g.MODEL).read_bytes())
        self.assertEqual(g.texture_bytes(),(g.ROOT/'mod/BrogueDoom'/g.SKIN).read_bytes())
        text=(g.ROOT/'mod/BrogueDoom/brogue_monsters.zs').read_text()
        proxy=text.split('class BrogueMonsterK67 :')[1].split('class ')[0]
        self.assertIn('BrogueMonsterProxyBase',proxy)
        for forbidden in ('A_Explode','A_CustomMissile','A_Chase','A_Damage','+SOLID','Random'):
            self.assertNotIn(forbidden,proxy)


if __name__=='__main__':unittest.main()
