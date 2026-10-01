"""Guardian spirit: profile, hover, clearance, key poses, collapse, glow material and exact bytes."""
import unittest
from . import guardian_kit as K
from . import guardian_spirit_animation as g

Base = K.creature_tests('guardian_spirit_animation', 'guardian_spirit_materials', 'MK_CHARM_GUARDIAN',
                        {'present': ('shaders/guardian-spirit-glow.fp',), 'absent': ('brightmap', 'glow "')},
                        emissive=True, unused_bones=('leg_L_end', 'leg_R_end'))


class GuardianSpiritTests(Base):
    def test_profile_is_additive(self):
        from .skeletal_registry import find
        row = find('MK_CHARM_GUARDIAN'); self.assertTrue(row['additiveFlame'])
        shader = (K.ROOT/g.SHADER).read_text()
        for word in ('Bright', 'timer'): self.assertIn(word, shader)
        for word in ('uLightLevel', 'random', 'dynlight'): self.assertNotIn(word, shader)

    def test_hovers_until_it_fades(self):
        for clip in self.names[:5]:
            for i in range(len(self.clips[self.names.index(clip)]['frames'])):
                pts = g.deform(self.v, self.w, self.frame(clip, i))
                self.assertGreater(min(p[2] for p in pts), 4.5, (clip, i))

    def test_reap_and_jab_key_poses(self):
        T = g.matrices(self.frame('reap'))
        head = K.add(T[g.IDS['weapon']][0], K.rotate(T[g.IDS['weapon']][1], K.mul(g.HAFT, g.HEAD_AT*g.SCALE)))
        self.assertGreater(head[1], 10); self.assertLess(head[2], 22)
        T = g.matrices(self.frame('jab'))
        spike = K.add(T[g.IDS['weapon']][0], K.rotate(T[g.IDS['weapon']][1], K.mul(g.HAFT, (g.HEAD_AT+7)*g.SCALE)))
        self.assertGreater(spike[0], 26); self.assertGreater(spike[2], 30)

    def test_painted_light_fades_below(self):
        import numpy
        self.test_runtime_and_material_bytes()
        lum = self.image.reshape(-1, 3).mean(1)
        self.assertGreater(numpy.percentile(lum, 99), 200)
        self.assertGreater((lum < 8).mean(), .02)   # black = empty in additive rendering


del Base  # keep unittest from collecting the shared base as its own case


if __name__ == '__main__': unittest.main()
