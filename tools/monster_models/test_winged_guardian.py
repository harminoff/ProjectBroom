"""Winged guardian: profile, rigid marble, clearance, wing key poses, rubble and exact bytes."""
import math
import unittest
from . import guardian_kit as K
from . import winged_guardian_animation as g

Base = K.creature_tests('winged_guardian_animation', 'winged_guardian_materials', 'MK_WINGED_GUARDIAN',
                        {'present': ('BRGWGRD_S.png', 'BRGWGRD_N.png'), 'absent': ('glow', 'shader', 'brightmap')},
                        planted=('idle', 'recoil'))


def indices(test, *prefixes):
    """Vertex indices of every part whose name starts with one of ``prefixes`` (cached)."""
    cache = test.__dict__.setdefault('_idx', {})
    if prefixes not in cache:
        idx, offset = [], 0
        for part in test.parts:
            if part.name.startswith(prefixes): idx.extend(range(offset, offset+len(part.vertices)))
            offset += len(part.vertices)
        cache[prefixes] = idx
    return cache[prefixes]


def verts(test, frame, *prefixes):
    pts = g.deform(test.v, test.w, frame)
    return [pts[i] for i in indices(test, *prefixes)]


def centroid(pts): return [sum(p[k] for p in pts)/len(pts) for k in range(3)]


class WingedGuardianTests(Base):
    def test_wings_are_carried_raised_and_flared(self):
        # Measured idle: wing bar/knuckle top ~70 vs head ~63; feather |y| ~28 vs pauldron ~17.
        for clip in ('idle', 'stride'):
            frame = self.frame(clip, 0)
            head = max(p[2] for p in verts(self, frame, 'helm', 'hair', 'face', 'circlet'))
            arch = max(p[2] for p in verts(self, frame, 'wing_covert', 'wing_feather'))
            self.assertGreater(arch, head+4, clip)
            self.assertLess(arch, 72, clip)
            shoulder = max(abs(p[1]) for p in verts(self, frame, 'pauldron_'))
            flare = max(abs(p[1]) for p in verts(self, frame, 'wing_feather'))
            self.assertGreater(flare, shoulder+7, clip); self.assertLess(flare, 32, clip)

    def test_thrust_lunges_low_and_fans_the_primaries(self):
        T = g.matrices(self.frame('thrust'))
        tip = K.add(T[g.IDS['weapon']][0], K.rotate(T[g.IDS['weapon']][1], K.mul(g.BLADE_DIR, 34*g.SCALE)))
        self.assertGreater(tip[0], 25); self.assertLess(tip[2], 25)
        rest, thrust = self.frame('idle', 0), self.frame('thrust')
        def tilt(frame, i):
            pts = sorted(verts(self, frame, f'wing_feather_L_{i}'), key=lambda q: q[2]); k = len(pts)//4
            lo = [sum(q[c] for q in pts[:k])/k for c in range(3)]; hi = [sum(q[c] for q in pts[-k:])/k for c in range(3)]
            return math.degrees(math.atan2(lo[1]-hi[1], hi[2]-lo[2]))
        def fan(frame): return tilt(frame, 0)-tilt(frame, 7)
        # Angle between the outermost and innermost feather axes: measured 13.9 degrees at rest, 30.8 mid-thrust.
        self.assertGreater(fan(thrust), fan(rest)+10)
        pts = g.deform(self.v, self.w, thrust)
        self.assertGreater(max(abs(p[1]) for p in verts(self, thrust, 'wing_feather')), 27)
        self.assertLess(max(p[2] for p in pts), 72)

    def test_slash_ends_low_and_wide_with_wings_swept_back(self):
        T = g.matrices(self.frame('slash'))
        tip = K.add(T[g.IDS['weapon']][0], K.rotate(T[g.IDS['weapon']][1], K.mul(g.BLADE_DIR, 34*g.SCALE)))
        self.assertLess(tip[1], -20); self.assertLess(tip[2], 30)
        # Measured feather min x: ~-14 at rest, ~-31.5 mid-slash (swept back).
        rest_x = min(p[0] for p in verts(self, self.frame('idle', 0), 'wing_feather'))
        slash_x = min(p[0] for p in verts(self, self.frame('slash'), 'wing_feather'))
        self.assertLess(slash_x, rest_x-10); self.assertLess(slash_x, -25)

    def test_face_and_hair_are_legible(self):
        names = {p.name for p in self.parts}
        for n in ('face_brow', 'face_nose', 'face_lip_upper', 'face_lip_lower', 'face_lid_1', 'face_eye_1', 'face_eye_-1', 'circlet'):
            self.assertIn(n, names)
        # Carved locks, not a cap: at least ten separate hair pieces.
        self.assertGreaterEqual(len([n for n in names if n.startswith('hair_')]), 10)
        face = verts(self, self.frame('idle', 0), 'face_mass', 'face_brow', 'face_nose', 'face_chin')
        self.assertGreater(max(p[2] for p in face)-min(p[2] for p in face), 8)

    def test_primaries_fan_on_their_own_bones(self):
        owners = {p.name: p.bone for p in self.parts if p.name.startswith('wing_feather_L_')}
        self.assertEqual({owners[f'wing_feather_L_{i}'] for i in range(3)}, {'wing_L_tip'})
        self.assertEqual({owners[f'wing_feather_L_{i}'] for i in (3, 4)}, {'wing_L_mid'})
        self.assertEqual({owners[f'wing_feather_L_{i}'] for i in (5, 6, 7)}, {'wing_L_hand'})

    def test_marble_is_the_blue_guardian(self):
        # Brogue colours the winged guardian blue and the stone guardian white: the lit stone hue must differ.
        import colorsys
        import numpy
        from PIL import Image
        self.test_runtime_and_material_bytes()
        def lit(a):
            a = numpy.asarray(a).reshape(-1, 3).astype(float); lum = a.mean(1)
            bg = (abs(a[:, 0]-96) < 1) & (abs(a[:, 1]-94) < 1) & (abs(a[:, 2]-90) < 1)
            return a[(lum > 90) & ~bg]
        mine = lit(self.image)
        theirs = lit(Image.open(K.ROOT/'mod/BrogueDoom/graphics/BRGSGRD.png').convert('RGB'))
        hue = numpy.mean([colorsys.rgb_to_hsv(*(x/255))[0]*360 for x in mine[::50]])
        self.assertTrue(190 < hue < 250, hue)                      # measured 216
        self.assertGreater((mine[:, 2]-mine[:, 0]).mean(), 15)     # measured +29.7
        self.assertLess((theirs[:, 2]-theirs[:, 0]).mean(), 0)     # stone guardian is warm (-43)

    def test_marble_value_range(self):
        import numpy
        self.test_runtime_and_material_bytes()
        lum = self.image.reshape(-1, 3).mean(1); low, high = numpy.percentile(lum, [3, 99])
        self.assertLess(low, 60); self.assertGreater(high, 200)


del Base  # keep unittest from collecting the shared base as its own case


if __name__ == '__main__': unittest.main()
