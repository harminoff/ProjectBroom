"""Warden of Yendor: profile, rigid plate and strips, clearance, key poses, glow key and burial, heap and exact bytes."""
import math
import unittest
from . import guardian_kit as K
from . import warden_of_yendor_animation as g
from . import warden_of_yendor_materials as M

Base = K.creature_tests('warden_of_yendor_animation', 'warden_of_yendor_materials', 'MK_WARDEN_OF_YENDOR',
                        {'present': ('shaders/warden-yendor-light.fp',), 'absent': ('brightmap',)},
                        planted=('idle', 'recoil'))


class WardenOfYendorTests(Base):
    def painted(self):
        cls = self.__class__
        if getattr(cls, '_painted', None) is None: cls._painted = M.paint(self.parts)[0]
        return cls._painted

    def bone_z(self, clip, name, frame=None):
        return g.matrices(self.frame(clip, frame))[g.IDS[name]][0][2]

    def test_skeleton_has_two_bone_mantle_strips(self):
        self.assertEqual(len(g.STRIPS), 8)
        names = {n for n, p, v in g.BONES}
        for i in range(8): self.assertIn(f'cloak_{i}_a', names); self.assertIn(f'cloak_{i}_b', names)
        for n in ('glow_chest', 'glow_head', 'glow_L', 'glow_R'): self.assertIn(n, names)

    def test_idle_height_and_pose_bounds_use_tics_at_35hz(self):
        top = max(p[2] for p in g.deform(self.v, self.w, self.frame('idle', 0)))
        self.assertGreater(top, 66); self.assertLess(top, 72)
        for c in self.clips[2:]:
            self.assertGreaterEqual(K.tics(len(c['frames']), c['fps']), 1)

    def test_strike_is_a_wide_single_arm_hammer_fist(self):
        T = g.matrices(self.frame('strike'))
        wrist = T[g.IDS['arm_R_end']][0]
        self.assertGreater(wrist[0], 14); self.assertLess(wrist[2], 24); self.assertGreater(abs(wrist[1]), 14)
        left = T[g.IDS['arm_L_end']][0]
        self.assertLess(left[0], T[g.IDS['chest']][0][0])      # left arm flung back
        early = g.matrices(self.frame('strike', 8))
        self.assertGreater(early[g.IDS['arm_R_end']][0][2], 60)     # raised high before the blow
        self.assertLess(T[g.IDS['pelvis']][0][2], g.matrices(self.frame('strike', 0))[g.IDS['pelvis']][0][2]-5)   # lunge

    def test_strips_flare_and_trail_in_the_strike(self):
        rest = g.matrices(self.frame('idle', 0)); hit = g.matrices(self.frame('strike'))
        moved = [abs(hit[g.IDS[f'cloak_{i}_b']][0][0]-rest[g.IDS[f'cloak_{i}_b']][0][0]) for i in range(8)]
        self.assertGreater(max(moved), 6)

    def test_light_plates_burn_then_are_buried_by_the_end_of_the_collapse(self):
        first = g.matrices(self.frame('collapse', 0)); last = g.matrices(self.frame('collapse', -1))
        for bone, parent in (('glow_chest', 'chest'), ('glow_head', 'head'), ('glow_L', 'arm_L_end'), ('glow_R', 'arm_R_end')):
            def offset(T):
                pl, pq = T[g.IDS[parent]]
                return K.rotate(K.inverse(pq), K.sub(T[g.IDS[bone]][0], pl))
            moved = math.dist(offset(first), offset(last))
            self.assertGreater(moved, 2.0*g.SCALE, bone)

    def test_collapse_ends_as_a_low_heap_with_the_helm_on_the_floor(self):
        last = g.deform(self.v, self.w, self.frame('collapse', -1))
        owner = [g.BONES[row[0][0]][0] for row in self.w]
        head = [p for p, b in zip(last, owner) if b in ('head', 'glow_head')]
        self.assertLess(max(p[2] for p in head), 24); self.assertGreater(min(p[2] for p in head), .07)
        self.assertLess(max(p[2] for p in last), 24)
        # Every strip lies down: no strip vertex stands more than a few units above the floor.
        strips = [p for p, b in zip(last, owner) if b.startswith('cloak_')]
        self.assertLess(max(p[2] for p in strips), 14)

    def test_glow_key_is_only_the_light_plates(self):
        image = self.painted()
        key = M.glow_key(image)
        self.assertGreater(int(key.sum()), 500)
        self.assertLess(key.mean(), .08)
        # Every quad of the light plates is inside the key; ordinary armour quads are not.
        size = M.K.SIZE
        def inside(part):
            hits = 0
            for f in part.faces:
                u = sum(part.uv[i][0] for i in f)/4; v = sum(part.uv[i][1] for i in f)/4
                hits += bool(key[min(size-1, int((1-v)*size)), min(size-1, int(u*size))])
            return hits/len(part.faces)
        for p in self.parts:
            if p.role == 'void': self.assertGreater(inside(p), .9, p.name)
        for name in ('breast_1', 'helm', 'gauntlet_palm_R', 'cloak_3_a'):
            self.assertLess(inside(next(p for p in self.parts if p.name == name)), .05, name)

    def test_value_range_and_arm_lift(self):
        import numpy
        lum = self.painted().reshape(-1, 3).mean(1); low, high = numpy.percentile(lum, [3, 99.5])
        self.assertLess(low, 45); self.assertGreater(high, 150)
        self.assertGreater(M.ARMC[0]+M.ARMC[1], M.LEGC[0]+M.LEGC[1]+40)   # arms read a step lighter than legs


del Base  # keep unittest from collecting the shared base as its own case


if __name__ == '__main__': unittest.main()
