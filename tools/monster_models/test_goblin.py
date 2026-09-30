"""Connected primate, held spear, clip bounds and deterministic output."""
import collections
import math
import unittest
from . import goblin_animation as g, iqm


class GoblinTests(unittest.TestCase):
    def test_connected_body_and_seams(self):
        parts,v,n,uv,t,w=g.geometry();body=parts[0];ids=body.skin_topology
        graph={i:set() for i in ids};edges=collections.Counter()
        for face in body.faces:
            for a,b in zip(face,face[1:]+face[:1]):
                a,b=ids[a],ids[b];edges[tuple(sorted((a,b)))]+=1
                graph[a].add(b);graph[b].add(a)
        self.assertEqual(set(edges.values()),{2})
        seen={ids[0]};todo=[ids[0]]
        while todo:
            for n in graph[todo.pop()]:
                if n not in seen:seen.add(n);todo.append(n)
        self.assertEqual(seen,set(ids))
        pairs={}
        for i,key in enumerate(ids):
            if key in pairs:
                self.assertEqual(body.vertices[i],body.vertices[pairs[key]])
                self.assertEqual(w[i],w[pairs[key]])
            pairs[key]=i
        used={g.BONES[b][0] for row in w[:len(ids)] for b,weight in row if weight>.01}
        for limb in ('arm','leg'):
            for side in ('L','R'):self.assertIn(f'{limb}_{side}_upper',used)

    def test_spear_follows_grip_and_clip_bounds(self):
        parts,v,n,uv,t,w=g.geometry()
        self.assertTrue(any(p.name=='spear_stone' for p in parts))
        for clip,count,fps,loop in g.CLIPS:
            for phase in (0,.25,.5,.75,1):
                transforms=g.matrices(g.pose(clip,phase))
                self.assertLess(math.dist(transforms[g.IDS['spear']][0],transforms[g.IDS['arm_R_end']][0]),1e-8)
                points=g.deform(v,w,g.pose(clip,phase))
                self.assertTrue(all(math.isfinite(c) for p in points for c in p))
                self.assertLess(max(p[1] for p in points)-min(p[1] for p in points),64)
            if loop:
                a=g.deform(v,w,g.pose(clip,0));b=g.deform(v,w,g.pose(clip,1))
                self.assertLess(max(math.dist(x,y) for x,y in zip(a,b)),1e-8)
        self.assertFalse(any('tail' in name for name,_,_ in g.BONES))
        settled=g.deform(v,w,g.pose('death',1))
        self.assertGreater(min(p[2] for p in settled),-.5)

    def test_refined_material_regions_and_readable_spear(self):
        from . import goblin_materials as materials
        parts=g.build_parts()
        self.assertEqual({materials.role(p.name) for p in parts},set(materials.ROLES))
        for p in parts:
            x0,y0,x1,y1=materials.RECTS[materials.role(p.name)]
            for u,v in p.uv:
                self.assertTrue(x0-.01<=u*1024<=x1+.01)
                self.assertTrue(y0-.01<=(1-v)*1024<=y1+.01)
        tip=next(p for p in parts if p.name=='spear_stone')
        self.assertLess(min(p[1] for p in tip.vertices),-17)
        self.assertEqual(len([p for p in parts if p.name.startswith('spear_lashing')]),7)

    def test_deterministic_export(self):
        _,v,n,uv,t,w=g.geometry();clips,bounds=g.animation_data(v,w)
        data=iqm.encode(v,n,uv,t,w,g.BONES,clips,bounds,mesh_label='Project_Broom_goblin',material_path=g.SKIN)
        self.assertEqual(data,(g.ROOT/'mod/BrogueDoom/models/monsters/08_goblin.iqm').read_bytes())
        self.assertEqual(g.texture_bytes(),(g.ROOT/'mod/BrogueDoom'/g.SKIN).read_bytes())

    def test_distinct_goblin_landmarks_and_closed_accessories(self):
        parts={p.name:p for p in g.build_parts()}
        self.assertNotIn('head_muzzle',parts)
        self.assertIn('wrap_ragged',parts)
        for name in ('head_cranium','head_ear_1','head_ear_-1','spear_stone','wrap_ragged'):
            p=parts[name];edges=collections.Counter()
            for face in p.faces:
                for a,b in zip(face,face[1:]+face[:1]):edges[tuple(sorted((a,b)))]+=1
            self.assertEqual(set(edges.values()),{2},name)
        self.assertGreater(max(v[1] for v in parts['head_ear_1'].vertices),6)
        self.assertLess(min(v[1] for v in parts['head_ear_-1'].vertices),-6)
        for sign in (-1,1):
            eye=parts[f'head_eye_socket_{sign}']
            # Shallow slanted sockets replace protruding round monkey eyes.
            self.assertLess(max(v[0] for v in eye.vertices)-min(v[0] for v in eye.vertices),.4)
        for p in (parts['wrap_ragged'],parts['spear_stone']):
            bone='pelvis' if p.name.startswith('wrap') else 'spear'
            self.assertTrue(all(g.weights(p,v,u)==[(g.IDS[bone],1)] for v,u in zip(p.vertices,p.uv)))


if __name__=='__main__':unittest.main()
