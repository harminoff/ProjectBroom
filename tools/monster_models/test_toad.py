"""Toad anatomy, grounded locomotion and deterministic cosmetic materials."""
import math
import unittest
from . import toad_animation as toad, toad_materials as materials


class ToadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parts,cls.v,_,cls.uv,cls.tri,cls.w=toad.geometry()
        cls.clips,cls.bounds=toad.animation_data(cls.v,cls.w)

    def test_anatomy_and_budget(self):
        names={p.name for p in toad.build_parts()}
        for side in ('L','R'):
            for limb,count in (('fore',4),('hind',5)):
                self.assertEqual(sum(n.startswith(f'toe_{limb}_{side}_') for n in names),count)
            self.assertIn('gland_'+side,names)
        for p in toad.build_parts():
            if p.name.startswith('eye_pupil'):
                extents=[max(v[a] for v in p.vertices)-min(v[a] for v in p.vertices) for a in range(3)]
                self.assertGreater(extents[1],extents[2]*3)
        self.assertFalse(any('tongue' in n or 'tooth' in n for n in names))
        self.assertLess(len(self.tri),15000)
        self.assertGreater(len([p for p in self.parts if p.name.startswith('wart')]),40)

    def test_crawl_support_and_cycle_seam(self):
        for t in (0,.07,.23,.39,.58,.73,.9,1):
            transforms=toad.matrices(toad.pose('crawl',t))
            feet=[transforms[toad.IDS[f'{limb}_{side}_end']][0][2]
                  for limb in ('fore','hind') for side in ('L','R')]
            self.assertGreaterEqual(sum(z<=2.01 for z in feet),2,'Crawl must keep a diagonal support pair')
        for clip in ('idle','crawl'):
            a=toad.deform(self.v,self.w,toad.pose(clip,0))
            b=toad.deform(self.v,self.w,toad.pose(clip,1))
            self.assertLess(max(math.dist(x,y) for x,y in zip(a,b)),1e-8)
        for b in self.bounds:
            self.assertGreaterEqual(b[2],.06999)
            self.assertLess(b[3]-b[0],64)
            self.assertLess(b[4]-b[1],64)
        self.assertLess(self.bounds[-1][5],20,
                        'Death must settle lower, not lift the body above its feet')

    def test_warts_remain_seated_on_animated_skin(self):
        body=self.parts[0]
        for p in self.parts[1:]:
            if not p.name.startswith('wart'): continue
            # Every attachment begins within its own radius of the connected
            # surface and stays near it after each actual action pose.
            for clip in ('crawl','slime','slam','recoil','death'):
                frame=toad.pose(clip,.6)
                center=tuple(sum(v[a] for v in p.vertices)/len(p.vertices) for a in range(3))
                anchor=toad.deform([center],[p.skin_weights[0]],frame)[0]
                nearest=min(range(len(body.vertices)),key=lambda i:math.dist(body.vertices[i],center))
                skin=toad.deform([body.vertices[nearest]],[body.skin_weights[nearest]],frame)[0]
                self.assertLess(math.dist(anchor,skin),2.2)

    def test_material_bytes_and_no_emission(self):
        self.assertEqual(materials.texture_bytes(),(toad.ROOT/'mod/BrogueDoom'/toad.SKIN).read_bytes())
        for path,data in materials.surface_maps().items():
            self.assertEqual(data,(toad.ROOT/'mod/BrogueDoom'/path).read_bytes())
        definition=(toad.ROOT/'mod/BrogueDoom/GLDEFS').read_text().split('material "graphics/BRGTOAD.png"')[1].split('}')[0]
        self.assertIn('specularlevel 0.35',definition)
        self.assertNotIn('brightmap',definition)
        self.assertNotIn('shader',definition)


if __name__=='__main__': unittest.main()
