"""Immobile construct supports, suspended tablet, broken crown and export tests."""
import collections
import math
import unittest
from . import ogre_totem_animation as model, ogre_totem_materials as materials, iqm
from .rat import cross, sub


class OgreTotemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parts,cls.v,cls.n,cls.uv,cls.tri,cls.w=model.geometry()
        cls.clips,cls.bounds=model.animation_data(cls.v,cls.w)

    def test_distinct_construct_signature_and_tablet_attachment(self):
        names={p.name for p in self.parts}
        for name in ('greenstone_tablet','tablet_hanger','tablet_bronze_staple','crown_suspension_pin','crown_keystone','rear_hewn_support',
                     'hewn_column_L','hewn_column_R','outer_bone_arch_L','rear_bone_arch_R',
                     'bone_tally_L','bronze_collar'):
            self.assertIn(name,names)
        self.assertFalse(any('mask' in n or 'eye' in n or 'jaw' in n for n in names))
        for p in self.parts:
            self.assertEqual(len(set(tuple(w) for w in p.skin_weights)),1)
            if p.name.startswith(('tablet_','greenstone_')):
                self.assertEqual(p.skin_weights[0],[(model.IDS['tablet'],1)])
        self.assertEqual(sum(n.startswith('foundation_block_') for n in names),5)
        # The ring's upper centerline meets the crown pin. Its tiny angular
        # displacement stays inside both physical radii, including live cues.
        anchor=(6,0,57.3)
        for c in self.clips:
            for f in c['frames']:
                a,b=model.deform([anchor,anchor],[[(model.IDS['crown'],1)],[(model.IDS['tablet'],1)]],f)
                self.assertLess(math.dist(a,b),.12)

    def test_fixed_stone_and_live_supports_without_floor_lift(self):
        fixed=[i for i,w in enumerate(self.w) if w==[(0,1)]]
        structural=[i for i,w in enumerate(self.w) if w[0][0] in (1,2,3)]
        root=model.pose('rest',0)[0]
        for clip in self.clips:
            for frame in clip['frames']:
                self.assertEqual(frame[0],root)
                posed=model.deform(self.v,self.w,frame)
                self.assertTrue(all(math.dist(self.v[i],posed[i])<1e-10 for i in fixed))
                if clip['name']!='collapse':
                    self.assertTrue(all(math.dist(self.v[i],posed[i])<1e-10 for i in structural))

    def test_centered_cell_clearance_and_broken_crown(self):
        for b in self.bounds:
            self.assertGreaterEqual(b[2],.06999);self.assertLess(b[2],.2)
            self.assertTrue(all(-32<v<32 for v in (b[0],b[1],b[3],b[4])))
        final=model.deform(self.v,self.w,self.clips[-1]['frames'][-1])
        crown=[v for v,w in zip(final,self.w) if w[0][0]>=model.IDS['crown']]
        self.assertLess(max(v[2] for v in crown),18)
        self.assertLess(self.bounds[-1][5],24)
        # Death is a toppled object, not the same upright shape translated down.
        q=self.clips[-1]['frames'][-1][model.IDS['crown']][3:7]
        self.assertGreater(abs(q[1]),.65)

    def test_no_locomotion_loop_recovery_and_unit_scale(self):
        rest=model.pose('rest',0)
        self.assertTrue(all(f==rest for f in self.clips[1]['frames']))
        for name in ('idle','rest','toll','tremor','recoil'):
            a=model.deform(self.v,self.w,model.pose(name,0));b=model.deform(self.v,self.w,model.pose(name,1))
            self.assertLess(max(math.dist(x,y) for x,y in zip(a,b)),1e-10)
        for clip in self.clips:
            for f in clip['frames']:
                for row in f:
                    self.assertEqual(row[7:],(1,1,1));self.assertAlmostEqual(sum(x*x for x in row[3:7]),1)

    def test_real_ring_holes_and_identical_seams(self):
        for part in self.parts:
            if not part.name.startswith(('tablet_hanger','hanging_link_')):continue
            keys=[tuple(round(x,7) for x in v) for v in part.vertices]
            edges=collections.Counter()
            for tri in part.triangles():
                for i,j in zip(tri,tri[1:]+tri[:1]):edges[tuple(sorted((keys[i],keys[j])))]+=1
            self.assertEqual(set(edges.values()),{2},part.name)
            self.assertEqual(len(set(keys))-len(edges)+len(list(part.triangles())),0)

    def test_triangles_retain_area_at_every_frame(self):
        def area(v,t):
            a,b,c=t;return math.sqrt(sum(x*x for x in cross(sub(v[b],v[a]),sub(v[c],v[a]))))
        original=[area(self.v,t) for t in self.tri];self.assertGreater(min(original),1e-7)
        for c in self.clips:
            for f in c['frames']:
                posed=model.deform(self.v,self.w,f)
                self.assertLess(max(abs(area(posed,t)-a) for t,a in zip(self.tri,original)),1e-9)

    def test_original_texture_and_iqm_match_all_source_bytes(self):
        data=iqm.encode(self.v,self.n,self.uv,self.tri,self.w,model.BONES,self.clips,self.bounds,
                        mesh_label='Project_Broom_ogre_totem',material_path=model.SKIN)
        self.assertEqual(data,(model.ROOT/'mod/BrogueDoom/models/monsters/20_ogre_totem.iqm').read_bytes())
        self.assertEqual(materials.texture_bytes(),(model.ROOT/'mod/BrogueDoom'/model.SKIN).read_bytes())
        self.assertTrue(all(0<u<1 and 0<v<1 for u,v in self.uv))


if __name__=='__main__':unittest.main()
