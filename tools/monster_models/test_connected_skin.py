"""Actual anatomical connectivity and seam deformation, not just bone counts."""
import importlib, math, unittest
from collections import Counter
from .skeletal_registry import profiles, ROOT


class ConnectedSkinTests(unittest.TestCase):
    def test_closed_connected_cages_and_animation_seams(self):
        for row in profiles():
            with self.subTest(enemy=row['symbol']):
                rig=importlib.import_module('tools.monster_models.'+row['module'])
                parts,v,n,uv,tri,w=rig.geometry();body=parts[0]
                self.assertEqual(body.name,'Connected_skin')
                ids=body.skin_topology;edges=Counter();graph={i:set() for i in ids}
                for face in body.faces:
                    for axis in (0,1):
                        values=[body.uv[i][axis] for i in face]
                        self.assertLess(max(values)-min(values),.6,'UV wrap crosses the atlas interior')
                    for a,b in zip(face,face[1:]+face[:1]):
                        a,b=ids[a],ids[b];self.assertNotEqual(a,b)
                        edges[tuple(sorted((a,b)))]+=1;graph[a].add(b);graph[b].add(a)
                self.assertTrue(all(count==2 for count in edges.values()),'Open or non-manifold skin')
                todo=[ids[0]];seen={ids[0]}
                while todo:
                    for neighbor in graph[todo.pop()]:
                        if neighbor not in seen:seen.add(neighbor);todo.append(neighbor)
                self.assertEqual(seen,set(ids),'Detached body or limb')
                representatives={};pairs=[]
                for i,key in enumerate(ids):
                    if key in representatives:pairs.append((i,representatives[key]))
                    else:representatives[key]=i
                self.assertTrue(pairs,'UV seam fixture missing')
                # Equal weights at coincident UV copies guarantee equality for
                # every interpolated pose, not only the sampled keyframes below.
                for a,b in pairs:
                    self.assertEqual(body.vertices[a],body.vertices[b])
                    self.assertEqual(w[a],w[b])
                for name,count,fps,loop in rig.CLIPS:
                    for t in (0,.23,.5,.77,1):
                        pose=rig.deform(body.vertices,w[:len(ids)],rig.pose(name,t))
                        self.assertLess(max(math.dist(pose[a],pose[b]) for a,b in pairs),1e-10)
                # The cage must actually span all four limb chains.
                used={rig.BONES[b][0] for weights in w[:len(ids)] for b,weight in weights if weight>.01}
                limbs=('Fore','Hind') if row['symbol']=='MK_RAT' else ('arm','leg') if row['symbol'] in ('MK_KOBOLD','MK_MONKEY') else ('fore','hind')
                for limb in limbs:
                    for side in ('L','R'):self.assertIn(f'{limb}_{side}_upper',used)

    def test_kobold_visual_height_and_nonblocking_proxy(self):
        row=next(r for r in profiles() if r['symbol']=='MK_KOBOLD')
        from . import kobold_animation as rig
        parts,*_=rig.geometry()
        head=max(v[2] for v in parts[0].vertices)*row['visualScale']
        self.assertTrue(46<=head<=49,head)
        modeldef=(ROOT/'mod/BrogueDoom/models/monsters/MODELDEF.txt').read_text().split('Model BrogueMonsterK02\n')[1].split('}')[0]
        self.assertIn('Scale 1.28 1.28 1.28',modeldef)
        source=(ROOT/'mod/BrogueDoom/brogue_monsters.zs').read_text()
        self.assertIn('Radius 1; Height 1; Scale 1.0;',source)


if __name__=='__main__':unittest.main()
