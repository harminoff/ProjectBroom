"""Planted inanimate construction, rigid hinges and deterministic runtime proof."""
import math
import unittest
from . import goblin_totem_animation as model, goblin_totem_materials as materials, iqm
from .rat import cross, sub


class GoblinTotemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parts,cls.v,cls.n,cls.uv,cls.tri,cls.w=model.geometry()
        cls.clips,cls.bounds=model.animation_data(cls.v,cls.w)

    def test_signature_construction_and_rigid_parts(self):
        names={p.name for p in self.parts}
        for name in ('carved_mask_board','stump_timber','crown_timber','crooked_crosspiece',
                     'bone_crown_L','bone_crown_R','drilled_bone_L','ragged_ochre_strip_R'):
            self.assertIn(name,names)
        self.assertEqual(sum(n.startswith('footing_stone') for n in names),9)
        for part in self.parts:
            self.assertEqual(len(set(tuple(w) for w in part.skin_weights)),1,part.name)
            self.assertEqual(part.skin_weights[0][0][1],1)
        self.assertFalse(any(any(s in name for s in ('leg','eye_iris','arm_upper')) for name in names))

    def test_unused_move_role_is_exact_rest(self):
        rest=model.pose('rest',0)
        for frame in self.clips[1]['frames']:
            self.assertEqual(frame,rest)
        self.assertLess(max(math.dist(a,b) for a,b in zip(self.v,model.deform(self.v,self.w,rest))),1e-10)

    def test_fixed_footing_and_live_timber_contact(self):
        fixed=[i for i,w in enumerate(self.w) if w==[(0,1)]]
        stump=[i for i,w in enumerate(self.w) if w==[(model.IDS['stump'],1)]]
        for clip in self.clips:
            for frame in clip['frames']:
                posed=model.deform(self.v,self.w,frame)
                self.assertEqual(frame[0],model.pose('rest',0)[0])
                self.assertTrue(all(math.dist(posed[i],self.v[i])<1e-10 for i in fixed))
                if clip['name']!='collapse':self.assertTrue(all(math.dist(posed[i],self.v[i])<1e-10 for i in stump))

    def test_clearance_and_settled_breakage(self):
        for bound in self.bounds:
            self.assertGreaterEqual(bound[2],.06999)
            self.assertLess(bound[2],.2)
            self.assertTrue(all(abs(v)<32 for v in (bound[0],bound[1],bound[3],bound[4])))
            self.assertLess(bound[3]-bound[0],64);self.assertLess(bound[4]-bound[1],64)
        self.assertLess(self.bounds[-1][5],17)
        self.assertGreater(self.bounds[-1][5],8)

    def test_loops_recovery_and_unit_scale(self):
        for clip in self.clips:
            for frame in clip['frames']:
                for row in frame:
                    self.assertEqual(row[7:],(1,1,1))
                    self.assertAlmostEqual(sum(x*x for x in row[3:7]),1)
        for name in ('idle','rest','rattle','shudder','recoil'):
            a=model.deform(self.v,self.w,model.pose(name,0));b=model.deform(self.v,self.w,model.pose(name,1))
            self.assertLess(max(math.dist(x,y) for x,y in zip(a,b)),1e-10)

    def test_triangles_retain_rigid_area_in_every_pose(self):
        def area(v,t):
            a,b,c=t;return math.sqrt(sum(x*x for x in cross(sub(v[b],v[a]),sub(v[c],v[a]))))
        original=[area(self.v,t) for t in self.tri]
        self.assertGreater(min(original),1e-6)
        for clip in self.clips:
            for frame in clip['frames']:
                posed=model.deform(self.v,self.w,frame)
                self.assertLess(max(abs(area(posed,t)-a) for t,a in zip(self.tri,original)),1e-9)
        # Front-facing carved board surfaces must point outward, not vanish.
        for p in self.parts:
            if p.name in ('carved_mask_board','carved_nose','ragged_ochre_strip_L'):
                front=max(v[0] for v in p.vertices)
                for tri in p.triangles():
                    a,b,c=(p.vertices[i] for i in tri)
                    if all(v[0]==front for v in (a,b,c)):
                        self.assertGreater(cross(sub(b,a),sub(c,a))[0],0,p.name)

    def test_source_runtime_and_original_atlas_bytes(self):
        data=iqm.encode(self.v,self.n,self.uv,self.tri,self.w,model.BONES,self.clips,self.bounds,
                        mesh_label='Project_Broom_goblin_totem',material_path=model.SKIN)
        self.assertEqual(data,(model.ROOT/'mod/BrogueDoom/models/monsters/11_goblin_totem.iqm').read_bytes())
        self.assertEqual(materials.texture_bytes(),(model.ROOT/'mod/BrogueDoom'/model.SKIN).read_bytes())
        for u,v in self.uv:self.assertTrue(0<u<1 and 0<v<1)


if __name__=='__main__':unittest.main()
