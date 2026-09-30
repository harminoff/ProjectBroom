"""Stone guardian: profile, rigid stone, clearance, key poses, rubble and exact bytes."""
import math
import unittest
from . import guardian_kit as K
from . import stone_guardian_animation as g

Base = K.creature_tests('stone_guardian_animation', 'stone_guardian_materials', 'MK_GUARDIAN',
                        {'present': ('BRGSGRD_S.png', 'BRGSGRD_N.png'), 'absent': ('glow', 'shader', 'brightmap')},
                        planted=('idle', 'recoil'))


class StoneGuardianTests(Base):
    def test_cleave_strikes_the_floor_far_forward(self):
        T = g.matrices(self.frame('cleave'))
        head = K.add(T[g.IDS['weapon']][0], K.rotate(T[g.IDS['weapon']][1], K.mul(g.HAFT, g.HEAD_AT*g.SCALE)))
        self.assertGreater(head[0], 18); self.assertLess(head[2], 12)
        self.assertLess(T[g.IDS['pelvis']][0][2], (32-7)*g.SCALE)        # deep lunge
        windup = g.matrices(self.frame('cleave', 4))
        self.assertGreater(windup[g.IDS['arm_R_end']][0][2], 50*g.SCALE)   # hauled up behind the shoulder

    def test_sweep_holds_the_axe_out_wide(self):
        T = g.matrices(self.frame('sweep'))
        head = K.add(T[g.IDS['weapon']][0], K.rotate(T[g.IDS['weapon']][1], K.mul(g.HAFT, g.HEAD_AT*g.SCALE)))
        self.assertLess(head[1], -20); self.assertGreater(head[2], 20)

    def test_hands_stay_on_the_haft(self):
        for clip in self.names[:5]:
            count = len(self.clips[self.names.index(clip)]['frames'])
            for i in range(count):
                T = g.matrices(self.frame(clip, i))
                grip, q = T[g.IDS['weapon']]
                for side in 'RL':
                    wrist = T[g.IDS[f'arm_{side}_end']][0]
                    rel = K.rotate(K.inverse(q), K.sub(wrist, grip))
                    rest = K.sub(g.REST[g.IDS[f'arm_{side}_end']], g.REST[g.IDS['weapon']])
                    off = K.sub(rel, rest)   # only a slide along the haft is allowed
                    along = sum(a*b for a, b in zip(off, g.HAFT))
                    self.assertLess(math.dist(off, K.mul(g.HAFT, along)), .6, (clip, i, side))

    def test_sandstone_value_range(self):
        import numpy
        self.test_runtime_and_material_bytes()
        lum = self.image.reshape(-1, 3).mean(1); low, high = numpy.percentile(lum, [3, 99])
        self.assertLess(low, 45); self.assertGreater(high, 170)


del Base  # keep unittest from collecting the shared base as its own case


if __name__ == '__main__': unittest.main()
