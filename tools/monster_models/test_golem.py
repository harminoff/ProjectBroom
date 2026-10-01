"""Golem: rigid carved segments, clearance, key poses, rubble collapse and exact bytes."""
import math
import unittest
from . import golem_animation as g, golem_materials as m, iqm
from .skeletal_registry import ROOT, find, PENDING


class GolemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parts, cls.v, cls.n, cls.uv, cls.tri, cls.w = g.geometry()
        cls.clips, cls.bounds = g.animation_data(cls.v, cls.w)
        cls.owner = [p.name for p in cls.parts for _ in p.vertices]
        cls.names = [c['name'] for c in cls.clips]

    def world(self, clip, frame):
        return g.matrices(self.clips[self.names.index(clip)]['frames'][frame])

    def test_profile_matches_clips(self):
        profile = find('MK_GOLEM')
        self.assertEqual(profile['clips'], self.names)
        self.assertEqual(profile['durations'][2:], [math.ceil(len(c['frames'])*35/c['fps']) for c in self.clips][2:])  # engine tics at 35 Hz
        self.assertEqual(profile['walkFrames'], len(self.clips[1]['frames']))
        self.assertEqual([c['loop'] for c in self.clips], [True, True, False, False, False, False])
        self.assertEqual(profile['model'], '49_golem.iqm'); self.assertEqual(profile['skin'], g.SKIN)

    def test_rigid_segments_and_every_bone_used(self):
        for row in self.w:
            self.assertEqual(len(row), 1); self.assertEqual(row[0][1], 1)
        used = {g.BONES[row[0][0]][0] for row in self.w}
        self.assertEqual(used, {n for n, p, v in g.BONES} - {'root'})
        for p in self.parts:
            self.assertEqual(len(p.vertices), 4*len(p.faces))
            # Outward winding: each closed segment encloses a positive signed volume.
            volume = 0.0
            for a, b, c in p.triangles():
                (ax, ay, az), (bx, by, bz), (cx, cy, cz) = p.vertices[a], p.vertices[b], p.vertices[c]
                volume += (ax*(by*cz-bz*cy)-ay*(bx*cz-bz*cx)+az*(bx*cy-by*cx))/6
            hx, hy, hz = p.box[2]
            self.assertGreater(volume, .3*8*hx*hy*hz if p.role != 'core' else .3*4.18*hx**3, p.name)

    def test_kit_is_deterministic(self):
        a = g.carved_block('probe', 'chest', (1, 2, 3), (4, 5, 6), seed=3)
        b = g.carved_block('probe', 'chest', (1, 2, 3), (4, 5, 6), seed=3)
        self.assertEqual((a.vertices, a.faces, a.edge, a.chip), (b.vertices, b.faces, b.edge, b.chip))

    def test_centred_cell_clearance_without_floor_compensation(self):
        for b in self.bounds:
            self.assertGreaterEqual(b[0], -32); self.assertGreaterEqual(b[1], -32)
            self.assertLessEqual(b[3], 32); self.assertLessEqual(b[4], 32); self.assertGreater(b[2], .07)
        for c in self.clips:
            count = len(c['frames'])
            for i, frame in enumerate(c['frames']):
                self.assertEqual(frame, g.pose(c['name'], i/(count if c['loop'] else count-1)))
            if c['loop']:
                a = g.deform(self.v, self.w, g.pose(c['name'], 0)); b = g.deform(self.v, self.w, g.pose(c['name'], 1))
                self.assertLess(max(math.dist(x, y) for x, y in zip(a, b)), 1e-8)
            for scale in (b[3]-b[0] for b in self.bounds): self.assertLess(scale, 64)

    def test_planted_feet(self):
        for name, count, fps, loop in g.CLIPS:
            if name == 'crumble': continue
            for i in range(count):
                T = g.matrices(g.pose(name, i/(count if loop else count-1)))
                for side in 'LR':
                    foot = T[g.IDS[f'leg_{side}_end']][0]
                    if name == 'stomp': self.assertGreaterEqual(foot[2], g.FEET[side][2]-1e-6)
                    elif name == 'backhand': self.assertAlmostEqual(foot[2], g.FEET[side][2], places=6)  # widened stance
                    else: self.assertLess(math.dist(foot, g.FEET[side]), 1e-6, (name, i, side))

    def test_middle_frame_key_poses(self):
        rest = g.matrices(g.pose('idle', 0)); head = rest[g.IDS['head']][0][2]
        raised = self.world('smash', 9)
        for side in 'LR': self.assertGreater(raised[g.IDS[f'arm_{side}_end']][0][2], head+4*g.SCALE)
        slam = self.world('smash', len(self.clips[2]['frames'])//2)
        for side in 'LR':
            wrist = slam[g.IDS[f'arm_{side}_end']][0]
            self.assertLess(wrist[2], 20*g.SCALE); self.assertGreater(wrist[0], 20*g.SCALE)
        # Deep forward lunge: head driven far forward and down, knees bent.
        self.assertGreater(slam[g.IDS['head']][0][0], 18*g.SCALE); self.assertLess(slam[g.IDS['pelvis']][0][2], 24*g.SCALE)
        hit = self.world('backhand', len(self.clips[3]['frames'])//2)
        wrist = hit[g.IDS['arm_R_end']][0]
        self.assertLess(wrist[1], -22*g.SCALE); self.assertGreater(wrist[2], 45*g.SCALE)
        from .skeletal import rotate
        facing = rotate(hit[g.IDS['chest']][1], (1, 0, 0))
        self.assertGreater(abs(math.degrees(math.atan2(facing[1], facing[0]))), 35)
        feet = [hit[g.IDS[f'leg_{s}_end']][0][1] for s in 'LR']
        self.assertGreater(feet[0]-feet[1], (g.A_FEET['L'][1]-g.A_FEET['R'][1]+4)*g.SCALE)
        recoil = self.world('recoil', len(self.clips[4]['frames'])//2)
        self.assertLess(recoil[g.IDS['head']][0][0], rest[g.IDS['head']][0][0]-3*g.SCALE)

    def test_crumble_ends_as_floor_rubble(self):
        frames = self.clips[5]['frames']
        settled = g.deform(self.v, self.w, frames[-1])
        self.assertLess(max(p[2] for p in settled), 32)
        self.assertGreater(min(p[2] for p in settled), .07)
        T = g.matrices(frames[-1])
        # The head broke away from the chest and every piece touches down.
        self.assertGreater(math.dist(T[g.IDS['head']][0], T[g.IDS['chest']][0]), 20*g.SCALE)
        for bone in g.RUBBLE:
            low = min(p[2] for p, row in zip(settled, self.w) if g.BONES[row[0][0]][0] == bone)
            self.assertLess(low, (.4 + g.STACK.get(bone, 0))*g.SCALE + 1e-6, bone)
        middle = g.deform(self.v, self.w, frames[len(frames)//2])
        self.assertLess(max(p[2] for p in middle), 70*g.SCALE)

    def test_islands_do_not_overlap(self):
        rects = set()
        for p in self.parts:
            for f in p.faces:
                us = [p.uv[i] for i in f]
                for u, v in us: self.assertTrue(0 < u < 1 and 0 < v < 1)
                key = (round(us[0][0]*m.SIZE), round(us[0][1]*m.SIZE)); self.assertNotIn(key, rects); rects.add(key)

    def test_material_is_matte_and_not_emissive(self):
        snippet = PENDING/'MK_GOLEM.gldefs'
        text = snippet.read_text() if snippet.is_file() else (ROOT/'mod/BrogueDoom/GLDEFS').read_text()
        block = text[text.index('material "graphics/BRGGOLEM.png"'):]; block = block[:block.index('}')]
        for word in ('glow', 'shader', 'brightmap', 'emissive'): self.assertNotIn(word, block.lower())
        self.assertIn('BRGGOLEM_S.png', block)

    def test_runtime_and_material_bytes(self):
        data = iqm.encode(self.v, self.n, self.uv, self.tri, self.w, g.BONES, self.clips, self.bounds,
                          mesh_label='Project_Broom_golem', material_path=g.SKIN)
        self.assertEqual(data, (ROOT/g.MODEL).read_bytes())
        image, spec = m.paint(self.parts)
        self.assertEqual(m.encode_png(image.tobytes(), m.SIZE, m.SIZE), (ROOT/'mod/BrogueDoom'/g.SKIN).read_bytes())
        for name, blob in m.surface_maps(self.parts, spec=spec).items():
            self.assertEqual(blob, (ROOT/'mod/BrogueDoom'/name).read_bytes(), name)
        # Painted value range: dark crevices and pale worn edges for flat engine light.
        import numpy
        lum = image.reshape(-1, 3).mean(1)
        low, high = numpy.percentile(lum, [3, 99])
        self.assertLess(low, 30); self.assertGreater(high, 100); self.assertGreater(high-low, 80)


if __name__ == '__main__': unittest.main()
