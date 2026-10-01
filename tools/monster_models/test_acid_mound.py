"""Connected gel deformation, ground contact and deterministic export contracts."""
import collections
import hashlib
import math
import unittest
from . import acid_mound_animation as jelly, acid_mound_materials as materials, iqm
from .rat import cross, sub


class AcidMoundTests(unittest.TestCase):
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

    def test_extreme_poses_do_not_invert_or_collapse_triangles(self):
        rest=[cross(sub(self.v[b],self.v[a]),sub(self.v[c],self.v[a])) for a,b,c in self.tri]
        # Every authored frame, including high surge and settled death.
        for clip in self.clips:
            for f,frame in enumerate(clip['frames']):
                posed=jelly.deform(self.v,self.w,frame)
                for triangle,normal in zip(self.tri,rest):
                    a,b,c=triangle
                    current=cross(sub(posed[b],posed[a]),sub(posed[c],posed[a]))
                    self.assertGreater(sum(x*x for x in current),1e-14,(clip['name'],f,triangle))
                    self.assertGreater(sum(a*b for a,b in zip(normal,current)),0,(clip['name'],f,triangle))

    def test_ground_contact_corridor_and_settled_death(self):
        for bound in self.bounds:
            self.assertGreaterEqual(bound[2],.06999)
            self.assertLess(bound[2],.15)  # The skirt stays on the floor.
            self.assertLess(bound[3]-bound[0],64)
            self.assertLess(bound[4]-bound[1],64)
            self.assertTrue(all(abs(v)<32 for v in (bound[0],bound[1],bound[3],bound[4])))
        self.assertLess(self.bounds[-1][5],5)
        self.assertGreater(self.bounds[-1][5],2)

    def test_loop_recovery_and_uv_seams(self):
        keys=[tuple(round(c,6) for c in p) for p in self.v]
        for name in ('idle','squelch','slime','douse','recoil'):
            first=jelly.deform(self.v,self.w,jelly.pose(name,0))
            last=jelly.deform(self.v,self.w,jelly.pose(name,1))
            self.assertLess(max(math.dist(a,b) for a,b in zip(first,last)),1e-8)
        for clip in self.clips:
            seen={}
            posed=jelly.deform(self.v,self.w,clip['frames'][len(clip['frames'])//2])
            for key,p,weights in zip(keys,posed,self.w):
                if key in seen:
                    self.assertLess(math.dist(p,seen[key][0]),1e-8)
                    self.assertEqual(weights,seen[key][1])
                seen[key]=(p,weights)
        for i in range(101):self.assertEqual(materials.pigment(0,i/100),materials.pigment(1,i/100))

    def test_translation_only_normalized_weights(self):
        for weights in self.w:
            self.assertTrue(1<=len(weights)<=4)
            self.assertAlmostEqual(sum(w for _,w in weights),1)
        for clip in self.clips:
            for frame in clip['frames']:
                for pose in frame:self.assertEqual(pose[3:],(0,0,0,1,1,1,1))
        # Crown and skirt travel differently: a viscous shape, not rigid bobbing.
        flow=self.clips[1]['frames'][7]
        self.assertGreater(math.dist(sub(flow[1][:3],jelly.BONES[1][2]),
                                    sub(flow[17][:3],jelly.BONES[17][2])),.5)

    def test_export_and_all_materials_match_source(self):
        actual=iqm.encode(self.v,self.n,self.uv,self.tri,self.w,jelly.BONES,self.clips,self.bounds,
                          mesh_label='Project_Broom_acid_mound',material_path=jelly.SKIN)
        self.assertEqual(actual,(jelly.ROOT/'mod/BrogueDoom/models/monsters/16_acid_mound.iqm').read_bytes())
        for path,data in {jelly.SKIN:materials.texture_bytes(),**materials.surface_maps()}.items():
            self.assertEqual(hashlib.sha256(data).digest(),hashlib.sha256((jelly.ROOT/'mod/BrogueDoom'/path).read_bytes()).digest())


if __name__=='__main__':unittest.main()
