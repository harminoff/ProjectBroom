"""Tentacle horror: braided connected column, seated suckers, clearance, key poses, heap death."""
import json
import math
import unittest
from . import tentacle_horror_animation as g, tentacle_horror_materials as m, kraken_animation as kraken
from .test_kraken import TentacleChecks


class TentacleHorrorTests(TentacleChecks, unittest.TestCase):
    g = g
    symbol = 'MK_TENTACLE_HORROR'
    label = 'Project_Broom_tentacle_horror'

    def test_distinct_towering_eyeless_anatomy(self):
        names = {p.name for p in self.parts}
        self.assertFalse(any(n.startswith(('eye', 'beak')) for n in names), 'no eyes or beak: not a recoloured kraken')
        self.assertIn('maw_throat', names)
        self.assertGreaterEqual(sum(n.startswith('tooth_') for n in names), 20)
        self.assertEqual(len(g.STRANDS), 4)
        self.assertGreaterEqual(len(g.LIMBS), 20)
        height = max(p[2] for p in self.v)
        self.assertGreater(height, 72, 'towering')
        self.assertLess(height, 84, 'crown stays inside the review framing')
        kraken_height = json.loads((kraken.ROOT/'assets/monsters/kraken/animation.json').read_text())['dimensions'][2]
        self.assertGreater(height, kraken_height+5)

    def test_batter_and_crush_key_poses_on_middle_frames(self):
        rest = self.tips(self.g.pose('batter', 0))
        blow = self.tips(self.middle('batter'))
        crowns = [n for n in rest if n.startswith('crown')]
        self.assertGreater(sum(blow[n][0] for n in crowns)/len(crowns), sum(rest[n][0] for n in crowns)/len(crowns)+15,
                           'the whole crown streams toward the target')
        for n in ('arm_0', 'arm_3'):
            self.assertGreater(blow[n][0], 24)
        grip = self.tips(self.middle('crush'))
        for n in ('arm_0', 'arm_3'):
            self.assertLess(abs(grip[n][1]), 6, 'front arms wrap across the target')
            self.assertGreater(grip[n][0], 18)
            self.assertLess(grip[n][2], 12, 'crush wraps a target near the floor')
        mean = lambda d, key: sum(d[n][key] for n in crowns)/len(crowns)
        self.assertGreater(mean(blow, 2), 40, 'batter hammers at head height')
        self.assertLess(mean(grip, 2), mean(blow, 2)-15, 'crush pours the crown down over the target')
        head = lambda frame: g.matrices(frame)[g.IDS['head']][0]
        self.assertGreater(head(self.middle('crush'))[0], head(self.middle('batter'))[0]+3, 'column bent over the target')
        # An irregular crown: clearly varied lengths and thickness.
        lengths = [l.length for l in g.LIMBS if l.name.startswith('crown')]
        radii = [l.rows[0]['r'] for l in g.LIMBS if l.name.startswith('crown')]
        self.assertGreater(max(lengths)/min(lengths), 1.4)
        self.assertGreater(max(radii)/min(radii), 1.8)

    def test_collapse_ends_in_a_heap(self):
        frame = self.clips[5]['frames'][-1]
        settled = g.deform(self.v, self.w, frame)
        self.assertLess(max(p[2] for p in settled), 32)
        mid = g.deform(self.v, self.w, self.middle('collapse'))
        self.assertLess(max(p[2] for p in mid), 42, 'already buckled by the middle frame')
        world = g.matrices(frame)
        for limb in g.LIMBS:
            if not limb.name.startswith('root'):
                self.assertLess(world[limb.ids[-1]][0][2], 6, limb.name+' lies slack on the floor')

    def test_painted_braid_grooves_and_value_range(self):
        bright = lambda c: sum(c)/3
        limb = g.BY_NAME['crown_1']
        row = limb.at(limb.length*.45)
        ventral = m.pigment(tuple(a+b*row['r'] for a, b in zip(row['c'], row['V'])), row['V'])
        dorsal = m.pigment(tuple(a-b*row['r'] for a, b in zip(row['c'], row['V'])), tuple(-x for x in row['V']))
        self.assertLess(row['V'][2], -.5, 'this sample is an underside, seen from below in play')
        self.assertGreater(bright(ventral)-bright(dorsal), 40)
        a, b = g.STRANDS[0].rows[12], g.STRANDS[1].rows[12]
        mid = tuple((x+y)/2 for x, y in zip(a['c'], b['c']))
        out = math.atan2(mid[1], mid[0])
        normal = (math.cos(out), math.sin(out), 0.)
        crest = tuple(x+y*a['r'] for x, y in zip(a['c'], normal))
        self.assertLess(bright(m.pigment(mid, normal)), bright(m.pigment(crest, normal)))


if __name__ == '__main__':
    unittest.main()
