"""Phoenix: signature, hidden ash, clearance, key poses, floor death, bytes."""
import hashlib
import json
import math
import unittest
from . import phoenix_animation as m, iqm
from .rat import ROOT, sub
from .relic_kit import GLOW_U
from .skeletal_registry import find, PENDING


class PhoenixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parts, cls.v, cls.n, cls.uv, cls.tri, cls.w = m.geometry()
        cls.clips, cls.bounds = m.animation_data(cls.v, cls.w)
        cls.clip = {c['name']: c for c in cls.clips}
        cls.ash_bones = {m.IDS['ash_%d' % k] for k in range(m.ASH_COUNT)}

    def posed(self, name, i):
        return m.deform(self.v, self.w, self.clip[name]['frames'][i])

    def part_pts(self, pts, *prefixes):
        out = []; i = 0
        for p in self.parts:
            if p.name.startswith(prefixes):
                out += pts[i:i+len(p.vertices)]
            i += len(p.vertices)
        return out

    def test_profile(self):
        row = find('MK_PHOENIX')
        self.assertEqual(row['clips'], [c[0] for c in m.CLIPS])
        self.assertEqual(row['walkFrames'], m.CLIPS[1][1])
        self.assertEqual(row['durations'], m.DURATIONS)
        for c, d in zip(m.CLIPS[2:], row['durations'][2:]):
            self.assertGreaterEqual(d, math.ceil(c[1]*35/c[2]))
        self.assertEqual(m.CLIPS[0][0], 'idle')
        self.assertNotIn('visualScale', row)
        self.assertEqual(row['skin'], m.SKIN)
        self.assertEqual('mod/BrogueDoom/models/monsters/'+row['model'], m.MODEL)
        self.assertTrue((ROOT/row['report']).is_file())
        self.assertTrue(row['traits'])
        self.assertEqual(row['ownedFiles'], ['mod/BrogueDoom/'+m.SHADER])

    def test_gldefs_and_shader(self):
        snip = PENDING/'MK_PHOENIX.gldefs'
        text = snip.read_text() if snip.is_file() else (ROOT/'mod/BrogueDoom/GLDEFS').read_text()
        block = text[text.index('material "%s"' % m.SKIN):]
        self.assertIn('shader "%s"' % m.SHADER, block[:block.index('}')])
        src = (ROOT/'mod/BrogueDoom'/m.SHADER).read_text()
        self.assertIn('material.Bright', src)
        for bad in ('uLightLevel', 'random', 'AddLight', 'timer'):
            self.assertNotIn(bad, src)

    def test_signature_parts_and_glow_columns(self):
        names = {p.name for p in self.parts}
        for n in ('beak_upper', 'beak_lower', 'eye_L', 'eye_R', 'primary_6_L', 'primary_6_R', 'tail_plume_6', 'crest_4'):
            self.assertIn(n, names)
        self.assertGreaterEqual(sum(n.startswith('primary_') for n in names), 14)
        self.assertGreaterEqual(sum(n.startswith('tail_plume_') for n in names), 7)
        for p in self.parts:
            us = [u for u, v in p.uv]
            if m.ATLAS.glow(p.role):
                self.assertGreaterEqual(min(us), GLOW_U, p.name)
            else:
                self.assertLess(max(us), GLOW_U, p.name)
        roles = {p.name: p.role for p in self.parts}
        self.assertEqual(roles['primary_0_L'], 'flame')
        self.assertEqual(roles['tail_plume_3'], 'plume')
        self.assertEqual(roles['plumage_03_02'], 'feather')
        for row in self.w:
            self.assertAlmostEqual(math.fsum(x for _, x in row), 1, places=6)
            self.assertLessEqual(len(row), 4)

    def test_eyes_and_beak_face_plus_x(self):
        beak = self.part_pts(self.v, 'beak_upper'); head = self.part_pts(self.v, 'head')
        self.assertGreater(max(p[0] for p in beak), max(p[0] for p in head)+3)
        for s in 'LR':
            e = self.part_pts(self.v, 'eye_'+s)
            self.assertGreater(sum(p[0] for p in e)/len(e), 11)

    def test_ash_hidden_in_torso_at_rest(self):
        for p in self.parts:
            if p.name.startswith(('ash_', 'ember_')):
                for x in p.vertices:
                    d = sub(x, m.TORSO_C)
                    a = sum(d[i]*m.TORSO_A0[i] for i in range(3))
                    b = sum(d[i]*m.TORSO_A1[i] for i in range(3))
                    c = sum(d[i]*m.TORSO_A2[i] for i in range(3))
                    self.assertLess((a/m.TORSO_R[0])**2+(b/m.TORSO_R[1])**2+(c/m.TORSO_R[2])**2, 1.0, p.name)

    def test_clearance_and_floor(self):
        root = m.pose('idle', 0)[0]
        for c in self.clips:
            for f in c['frames']:
                self.assertEqual(f[0][:2], root[:2])
        for i, b in enumerate(self.bounds):
            self.assertTrue(-31.9 < b[0] and b[3] < 31.9 and -31.9 < b[1] and b[4] < 31.9, (i, b))
            self.assertGreaterEqual(b[2], .07)
            self.assertLess(b[5], 72)

    def test_loops_close_and_unit_scales(self):
        for name in ('idle', 'fly'):
            a = m.deform(self.v, self.w, m.pose(name, 0)); b = m.deform(self.v, self.w, m.pose(name, 1))
            self.assertLess(max(math.dist(x, y) for x, y in zip(a, b)), 1e-6)
        for c in self.clips:
            for f in c['frames']:
                for r in f:
                    self.assertEqual(tuple(r[7:]), (1, 1, 1))
                    self.assertAlmostEqual(sum(x*x for x in r[3:7]), 1)

    def test_action_key_pose_on_middle_frame(self):
        rest = self.posed('idle', 0)
        for name, count, *_ in m.CLIPS[2:5]:
            frames = self.clip[name]['frames']
            mv = [max(math.dist(a, b) for a, b in zip(m.deform(self.v, self.w, f), rest)) for f in frames]
            self.assertGreaterEqual(mv[count//2], .9*max(mv), name)

    def test_claw_is_low_wide_with_talons_forward(self):
        rest = self.posed('idle', 0); key = self.posed('claw', 9)
        self.assertLess(max(p[2] for p in self.part_pts(key, 'primary_')),
                        max(p[2] for p in self.part_pts(rest, 'primary_'))-12)
        self.assertGreater(max(p[0] for p in self.part_pts(key, 'talon_')),
                           max(p[0] for p in self.part_pts(rest, 'talon_'))+6)
        self.assertGreater(max(p[2] for p in self.part_pts(key, 'beak_upper'))-min(p[2] for p in self.part_pts(key, 'beak_lower')), 5)

    def test_death_ends_on_floor_with_ash_heap(self):
        final = self.posed('death', 29)
        bird = [p for p, row in zip(final, self.w) if row[0][0] not in self.ash_bones]
        self.assertLess(max(p[2] for p in bird), 20)
        self.assertLess(min(p[2] for p in bird), .5)
        ash = self.part_pts(final, 'ash_', 'ember_')
        self.assertLess(max(p[2] for p in ash), 18)
        rc = self.part_pts(self.posed('idle', 0), 'ash_', 'ember_')
        spread = lambda pts: max(p[0] for p in pts)-min(p[0] for p in pts)
        self.assertGreater(spread(ash), spread(rc)+8)
        self.assertGreater(spread(ash), 40)
        self.assertGreater(max(p[1] for p in ash)-min(p[1] for p in ash), 24)

    def test_full_wingspan_and_scowl(self):
        rest = self.posed('idle', 0)
        tips = self.part_pts(rest, 'primary_')
        self.assertGreater(max(p[1] for p in tips), 24)
        self.assertLess(max(p[1] for p in tips), 31.9)
        self.assertGreaterEqual(sum(n.startswith('marginal_') for n in {p.name for p in self.parts}), 24)
        for s, sg in (('L', 1), ('R', -1)):
            brow = self.part_pts(self.v, 'brow_'+s); eye = self.part_pts(self.v, 'eye_'+s)
            # brow plate sits behind the eye front so the slit stays visible, and slopes down toward the beak
            self.assertLess(max(p[0] for p in brow), max(p[0] for p in eye))
            mid = sorted(abs(p[1]) for p in brow)[len(brow)//2]
            outer = [p[2] for p in brow if abs(p[1]) > mid]; inner = [p[2] for p in brow if abs(p[1]) <= mid]
            self.assertGreater(sum(outer)/len(outer), sum(inner)/len(inner)+.4)

    def test_runtime_bytes_match_source(self):
        data = iqm.encode(self.v, self.n, self.uv, self.tri, self.w, m.BONES, self.clips, self.bounds,
                          mesh_label='Project_Broom_phoenix', material_path=m.SKIN)
        self.assertEqual(data, (ROOT/m.MODEL).read_bytes())
        skin = m.texture_bytes()
        self.assertEqual(skin, (ROOT/'mod/BrogueDoom'/m.SKIN).read_bytes())
        man = json.loads((ROOT/'assets/monsters/phoenix/animation.json').read_text())
        self.assertEqual(man['sha256'], hashlib.sha256(data).hexdigest())


if __name__ == '__main__':
    unittest.main()
