"""Skeletal binary, geometry, grounding, and presentation-only regression gates."""
import hashlib
import json
import math
import unittest

from . import iqm, rat_animation as rat


class RatAnimationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parts,cls.vertices,cls.normals,cls.uv,cls.triangles,cls.weights=rat.geometry()
        cls.clips,cls.bounds=rat.animation_data(cls.vertices,cls.weights)
        cls.data=(rat.ROOT/'mod/BrogueDoom/models/monsters/01_rat.iqm').read_bytes()
        cls.parsed=iqm.inspect(cls.data)

    def test_deterministic_binary_and_manifest(self):
        self.assertEqual(self.data,iqm.encode(self.vertices,self.normals,self.uv,self.triangles,self.weights,rat.BONES,self.clips,self.bounds))
        manifest=json.loads((rat.ROOT/'assets/monsters/rat/animation.json').read_text())
        self.assertEqual(manifest['sha256'],hashlib.sha256(self.data).hexdigest())
        self.assertEqual(manifest['boneCount'],28)

    def test_skeleton_weights_and_rest_pose(self):
        self.assertEqual(self.parsed['triangles'],[(c,b,a) for a,b,c in self.triangles])
        self.assertEqual(len(self.parsed['bones']),28)
        for i,(name,parent,trs) in enumerate(self.parsed['bones']):
            self.assertLess(parent,i)
            self.assertEqual(name,rat.BONES[i][0])
        for ids,weights in zip(self.parsed['indices'],self.parsed['weights']):
            self.assertAlmostEqual(sum(weights),1,places=6)
            self.assertTrue(all(0<=b<28 for b in ids))
            self.assertTrue(all(0<=w<=1 for w in weights))
        rest=[(*local,0,0,0,1,1,1,1) for n,p,local in rat.BONES]
        for a,b in zip(self.vertices,rat.deform(self.vertices,self.weights,rest)):
            self.assertLess(math.dist(a,b),1e-10)

    def test_clip_coverage_and_quantized_samples(self):
        self.assertEqual([a['name'] for a in self.parsed['animations']],['idle','scurry','bite','scratch','recoil','death'])
        first=0
        for clip in self.clips:
            for f in (0,len(clip['frames'])//2,len(clip['frames'])-1):
                decoded=self.parsed['frames'][first+f]
                expected=clip['frames'][f]
                self.assertLess(max(abs(x-y) for a,b in zip(decoded,expected) for x,y in zip(a,b)),.0002)
                for row in decoded:
                    self.assertAlmostEqual(sum(q*q for q in row[3:7]),1,places=4)
            self.assertNotEqual(clip['frames'][0],clip['frames'][len(clip['frames'])//2])
            first+=len(clip['frames'])

    def test_animation_ground_and_silhouette_budget(self):
        for b in self.bounds:
            self.assertGreaterEqual(b[2],.06999)
            self.assertLessEqual(b[3]-b[0],64)
            self.assertLessEqual(b[4]-b[1],64)
            self.assertLessEqual(b[5],23)
        self.assertLess(len(self.triangles),16500)
        for normal in self.normals: self.assertAlmostEqual(sum(v*v for v in normal),1,places=5)
        for a,b,c in self.triangles:
            self.assertGreater(sum(v*v for v in rat.cross(rat.sub(self.vertices[b],self.vertices[a]),rat.sub(self.vertices[c],self.vertices[a]))),1e-15)

    def test_attached_face_and_planted_paw_controls(self):
        for part in self.parts:
            if part.name.startswith(('Nostril','Eye','Whisker','Nose')):
                self.assertEqual(rat.weights(part,part.vertices[0],part.uv[0]),[(rat.IDS['head'],1)])
        # Bone-space IK keeps a stance foot at ground while the opposite pair lifts.
        clip=next(c for c in self.clips if c['name']=='scurry')
        for frame in clip['frames']:
            positions=rat.matrices(frame)
            paws=[positions[rat.IDS[f'{limb}_{side}_paw']][0][2] for limb in ('Fore','Hind') for side in ('L','R')]
            self.assertLess(min(paws),1.0)

    def test_bindings_and_no_new_gameplay_gate(self):
        zs=(rat.ROOT/'mod/BrogueDoom/brogue_monsters.zs').read_text()
        binding=(rat.ROOT/'mod/BrogueDoom/models/monsters/MODELDEF.txt').read_text().split('Model BrogueMonsterK01\n')[1].split('}')[0]
        self.assertIn('01_rat.iqm',binding); self.assertIn('BaseFrame',binding)
        self.assertIn('+DECOUPLEDANIMATIONS',zs)
        source=(rat.ROOT/'src/gzdoom-bridge/brogue_bridge_frontend.cpp').read_text()
        gating=source.split('bool MonsterAnimationsActive()')[1].split('void SyncItems()')[0]
        self.assertNotIn('ratDeathTics',gating); self.assertNotIn('ratPoseTics',gating)
        helper=source.split('void PlayRatClip(')[1].split('void BeginMonsterEventAnimations')[0]
        for forbidden in ('PerformAction','PerformCommand','Random','P_DamageMobj'):
            self.assertNotIn(forbidden,helper)
        self.assertIn('proxy.actor->GetClass()->TypeName == FName("BrogueMonsterK01")',source)
        self.assertIn('event.eventFlags & BROGUE_EVENT_FLAG_ADMINISTRATIVE',source)

    def test_visible_rat_walk_pacing_contract(self):
        source=(rat.ROOT/'src/gzdoom-bridge/brogue_bridge_frontend.cpp').read_text()
        self.assertIn('CVAR(Int, brg_rat_walk_tics, 28,',source)
        movement=source.split('const bool ratWalk =')[1].split('proxy.kind = creature.kind;')[0]
        self.assertIn('IsSkeletalRat(proxy)',movement)
        self.assertIn('creature.visibility != BROGUE_VISIBILITY_HIDDEN',movement)
        self.assertIn('distance <= 64.0 * std::sqrt(2.0) + .01',movement)
        self.assertIn('std::ceil(tileTics * distance / 64.0)',movement)
        self.assertIn('2.0 * distance / 64.0',movement)
        self.assertIn('proxy.moveTotal = proxy.moveTics',movement)
        for forbidden in ('PerformAction','PerformCommand','Random','P_DamageMobj'):
            self.assertNotIn(forbidden,movement)
        ticking=source.split('bool TickMonsterAnimations()')[1].split('bool MonsterAnimationsActive()')[0]
        self.assertIn('PlayRatClip(proxy, RatScurry, proxy.moveTics, proxy.ratScurryRate)',ticking)


if __name__=='__main__': unittest.main()
