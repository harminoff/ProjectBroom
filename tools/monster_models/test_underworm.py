"""Underworm: coiled annulated worm, toothed maw, connected skin, cell clearance, key poses, limp death, bytes."""
import collections
import json
import math
import unittest
from . import underworm_animation as g, underworm_materials as m, iqm
from .skeletal import rotate
from .skeletal_registry import find


class UnderwormTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parts, cls.v, cls.n, cls.uv, cls.tri, cls.w = g.geometry()
        cls.clips, cls.bounds = g.animation_data(cls.v, cls.w)

    def clip(self, name):
        return next(c for c in self.clips if c['name'] == name)

    def middle(self, name):
        clip = self.clip(name)
        return clip['frames'][int(len(clip['frames'])*.5)]

    def head(self, frame):
        world = g.matrices(frame)
        return world[g.HEAD_ID][0], rotate(world[g.HEAD_ID][1], (1., 0., 0.))

    def test_profile_matches_manifest(self):
        row = find('MK_UNDERWORM')
        manifest = json.loads((g.ROOT/row['manifest']).read_text())
        self.assertEqual(row['module'], g.__name__.rsplit('.', 1)[1])
        self.assertEqual('graphics/'+row['skin'].split('/')[-1], g.SKIN)
        self.assertEqual('models/monsters/'+row['model'], g.MODEL)
        self.assertEqual(row['clips'], [c[0] for c in g.CLIPS])
        self.assertEqual(g.CLIPS[0][0], 'idle', 'the shared exporter needs idle first')
        counts = {c['name']: c['frameCount'] for c in manifest['clips']}
        self.assertEqual(row['walkFrames'], counts[row['clips'][1]])
        self.assertEqual([c[3] for c in g.CLIPS], [True, True, False, False, False, False])
        for role, (name, frames, fps, loop) in enumerate(g.CLIPS):
            if role < 2:
                continue
            self.assertGreaterEqual(row['durations'][role], math.ceil(frames*35/fps), name+' would be cut off in-engine')
            self.assertEqual(frames % 2, 1, 'odd action length puts the key pose exactly on the middle frame')
        self.assertNotIn('visualScale', row)
        self.assertTrue(row['report'].startswith('docs/') and (g.ROOT/row['report']).is_file())

    def test_connected_closed_skin(self):
        p = self.parts[0]
        ids = p.skin_topology
        edges = collections.Counter()
        graph = collections.defaultdict(set)
        for face in p.faces:
            for a, b in zip(face, face[1:]+face[:1]):
                a, b = ids[a], ids[b]
                self.assertNotEqual(a, b)
                edges[tuple(sorted((a, b)))] += 1
                graph[a].add(b)
                graph[b].add(a)
        self.assertEqual(set(edges.values()), {2}, 'closed manifold')
        seen, todo = {ids[0]}, [ids[0]]
        while todo:
            for i in graph[todo.pop()]:
                if i not in seen:
                    seen.add(i)
                    todo.append(i)
        self.assertEqual(seen, set(ids), 'one connected surface, no loose segments')
        self.assertLessEqual(len(p.faces), g.SKIN_FACE_BUDGET)
        used = {g.BONES[b][0] for row in p.skin_weights for b, w in row if w > .05}
        for name in g.NAMES:
            self.assertIn(name, used, name+' must deform the connected skin')
        for row in self.w:
            self.assertAlmostEqual(math.fsum(w for b, w in row), 1, places=5)
            self.assertLessEqual(len(row), 4)

    def test_weights_are_quantized_for_cross_python_agreement(self):
        for p in g.build_parts():
            for v in p.vertices[:200]:
                for b, w in g.weights(p, v, None):
                    self.assertEqual(w, round(w, 6))

    def test_legless_annulated_worm_with_petal_maw(self):
        names = {p.name for p in g.build_parts()}
        self.assertFalse(any(n.startswith(('leg', 'arm', 'foot', 'claw', 'eye', 'antenna')) for n in names))
        self.assertFalse(any(('leg' in b or 'arm' in b) for b in (b[0] for b in g.BONES)))
        self.assertEqual(sorted(n for n in names if n.startswith('petal_') and 'ridge' not in n), [f'petal_{k}' for k in range(4)])
        self.assertEqual(len([n for n in names if n.endswith('ridge')]), 4, 'each petal has a ridge line')
        self.assertGreaterEqual(len([n for n in names if n.startswith('cap_')]), 3, 'overlapping plates cap the back of the head')
        self.assertEqual(len([n for n in names if n.startswith('tooth_p')]), 12, 'three hooked teeth per petal')
        self.assertEqual(len(g.PETAL_IDS), 4)
        self.assertGreaterEqual(len([n for n in names if n.startswith('tooth_')]), 20, 'a ring of teeth')
        self.assertGreaterEqual(len([n for n in names if n.startswith('collar_')]), 3, 'overlapping collar plates')
        self.assertEqual(g.PITCH_COUNT, 30, 'about thirty annuli')
        radii = [r for _, _, _, r in g.REST_DENSE]
        self.assertLess(min(radii), 1.6, 'tapering tail')
        self.assertGreater(max(radii), 10, 'thick heavy raised front')
        rest_head = g.matrices(g.pose('idle', 0))[g.HEAD_ID][0]
        self.assertGreater(rest_head[2], 46)
        self.assertLess(rest_head[2], 52)
        self.assertGreater(max(p[2] for p in self.v), 56)
        self.assertLess(max(p[2] for p in self.v), 70, 'under the oblique camera crop')
        ys = [p[1] for p in self.v]
        self.assertGreater(max(ys)-min(ys), 52, 'the coil fills the cell in Y')

    def test_head_is_widest_at_the_mouth_not_a_dome(self):
        head = [p for p in self.parts[0].vertices
                if p[0] > g.HEAD[0]-9 and abs(p[2]-g.HEAD[2]) < 14 and abs(p[1]-g.HEAD[1]) < 20]

        def width(lo, hi):
            ys = [p[1] for p in head if lo <= p[0]-g.HEAD[0] < hi]
            return max(ys)-min(ys)
        self.assertGreater(width(6, 10), width(-9, -5)+3, 'flares toward the mouth')
        self.assertGreater(width(6, 10), width(-3, 1)+2)
        rim = [p for p in head if 6 <= p[0]-g.HEAD[0] < 10]
        self.assertGreater(max(p[1] for p in rim)-min(p[1] for p in rim),
                           1.3*(max(p[2] for p in rim)-min(p[2] for p in rim)), 'flattened: wider than tall')
        joints = g.joints_for(g.controls_for(g.KEYS['rest']))
        closed = g.deform(self.v, self.w, g.frames_from(joints, (0, 0, 0), 0))
        opened = g.deform(self.v, self.w, g.frames_from(joints, (0, 0, 0), 70))
        for k in range(4):
            idx = [i for i, wt in enumerate(self.w) if len(wt) == 1 and wt[0][0] == g.PETAL_IDS[k]]
            self.assertTrue(idx)

            def radial(pts):
                return sum(math.hypot(pts[i][1]-g.HEAD[1], pts[i][2]-g.HEAD[2]) for i in idx)/len(idx)
            self.assertGreater(radial(opened), radial(closed)+3, f'petal {k} opens outward')

    def test_coil_turns_keep_clear_at_rest(self):
        dense = g.REST_DENSE[::4]
        arc = g.S_ARC[::4]
        worst = 99.
        for i, a in enumerate(dense):
            for j in range(i+1, len(dense)):
                if arc[j]-arc[i] > 24:
                    worst = min(worst, g.dist(a[:3], dense[j][:3])-a[3]-dense[j][3])
        self.assertGreater(worst, .8, 'adjacent coil turns must not fuse or intersect')

    def test_all_frames_in_cell_grounded_unit_scale(self):
        for b in self.bounds:
            self.assertGreaterEqual(b[0], -32)
            self.assertGreaterEqual(b[1], -32)
            self.assertLessEqual(b[3], 32)
            self.assertLessEqual(b[4], 32)
            self.assertGreaterEqual(b[2], .069)
        for clip in self.clips:
            count = len(clip['frames'])
            for j, frame in enumerate(clip['frames']):
                self.assertEqual(len(frame), len(g.BONES))
                self.assertTrue(all(row[7:] == (1, 1, 1) or tuple(row[7:]) == (1, 1, 1) for row in frame))
                if j % 4 == 0 or j == count-1:
                    raw = g.pose(clip['name'], j/(count if clip['loop'] else count-1))
                    self.assertLess(abs(frame[0][2]-raw[0][2]), .5, 'automatic floor lift must not disguise a floating pose')

    def test_loops_close_and_actions_recover(self):
        for name in ('idle', 'crawl'):
            a = g.deform(self.v, self.w, g.pose(name, 0))
            b = g.deform(self.v, self.w, g.pose(name, 1))
            self.assertLess(max(math.dist(p, q) for p, q in zip(a, b)), 1e-6)
        for name in ('lunge', 'slam', 'recoil'):
            a = g.deform(self.v, self.w, g.pose(name, 0))
            b = g.deform(self.v, self.w, g.pose(name, 1))
            self.assertLess(max(math.dist(p, q) for p, q in zip(a, b)), 1e-6)

    def test_lunge_key_pose_is_low_and_wide(self):
        rest_pos, rest_axis = self.head(g.pose('idle', 0))
        pos, axis = self.head(self.middle('lunge'))
        self.assertLess(pos[2], .5*rest_pos[2], 'head thrown low')
        self.assertGreater(pos[0], rest_pos[0]-3, 'and not pulled back')
        self.assertGreater(axis[0], .9, 'maw still faces +X')
        petal = self.middle('lunge')[g.PETAL_IDS[0]]
        self.assertGreater(2*math.degrees(math.asin(math.sqrt(sum(c*c for c in petal[3:6])))), 40, 'petals flung open')
        rear = self.head(g.pose('lunge', .30))[0]
        self.assertGreater(rear[2], rest_pos[2]+2, 'rears up before it strikes')
        self.assertLess(rear[0], rest_pos[0]-4)
        mid = g.deform(self.v, self.w, self.middle('lunge'))
        self.assertLess(max(p[2] for p in mid), 44, 'low, so the oblique camera does not crop the strike')

    def test_slam_is_a_different_downward_key_pose(self):
        lunge = self.head(self.middle('lunge'))
        slam_pos, slam_axis = self.head(self.middle('slam'))
        self.assertLess(slam_axis[2], -.4, 'head pitched down into the floor')
        self.assertGreater(math.dist(lunge[0], slam_pos), 8)
        rear = self.head(g.pose('slam', .32))[0]
        self.assertGreater(rear[2], 45)

    def test_recoil_snaps_the_head_back(self):
        rest, _ = self.head(g.pose('idle', 0))
        pos, axis = self.head(self.middle('recoil'))
        self.assertGreater(math.dist(pos, rest), 4, 'head snaps away from rest')
        self.assertGreater(abs(pos[1]-rest[1]), 2)

    def test_collapse_ends_flat_limp_and_low(self):
        alive = max(p[2] for p in g.deform(self.v, self.w, g.pose('idle', 0)))
        dead = g.deform(self.v, self.w, self.clip('collapse')['frames'][-1])
        self.assertLess(max(p[2] for p in dead), .5*alive, 'the dead body lies flat, not standing')
        mid = g.deform(self.v, self.w, self.middle('collapse'))
        self.assertLess(max(p[2] for p in mid), .8*alive, 'already buckled by the middle frame')
        world = g.matrices(self.clip('collapse')['frames'][-1])
        for name in g.NAMES[14:]:
            self.assertLess(world[g.IDS[name]][0][2], 16, name+' lies on the floor')
        petal = self.clip('collapse')['frames'][-1][g.PETAL_IDS[1]]
        self.assertGreater(2*math.degrees(math.asin(math.sqrt(sum(c*c for c in petal[3:6])))), 8, 'petals slack')
        self.assertLess(2*math.degrees(math.asin(math.sqrt(sum(c*c for c in petal[3:6])))), 40, 'and partly closed')
        _, axis = self.head(self.clip('collapse')['frames'][-1])
        self.assertLess(abs(axis[0]), .3, 'maw faces sideways, not the camera')
        self.assertLess(axis[2], -.2, 'and tipped down toward the floor')
        first = self.clip('collapse')['frames'][0]
        self.assertLess(max(math.dist(p, q) for p, q in zip(g.deform(self.v, self.w, first), g.deform(self.v, self.w, g.pose('idle', 0)))), 1e-6)

    def test_pigment_is_longitudinal_and_ventral(self):
        # arc coordinate rises monotonically along the whole coiled centreline (no height streaks)
        last = -1.
        for row in g.REST_DENSE[::6]:
            u, _ = m.pigment(row[:3])
            self.assertGreaterEqual(u, last-1e-9)
            last = u
        self.assertGreater(last, .7*m.UB)
        # belly (0) faces the floor, spine (1) faces up, at a floor-lying and at a raised section
        for index in (60, len(g.REST_DENSE)-90):
            c = g.REST_DENSE[index]
            self.assertLess(m.pigment((c[0], c[1], c[2]-c[3]*.8))[1], .2)
            self.assertGreater(m.pigment((c[0], c[1], c[2]+c[3]*.8))[1], .8)
        for part in g.build_parts():
            if part.name.startswith('tooth_'):
                self.assertTrue(all(m.PALETTE_TEETH[0] <= u < m.PALETTE_TEETH[1] for u, v in part.uv))
            if part.name.startswith(('petal_', 'collar_', 'cap_')):
                self.assertTrue(all(m.PALETTE_CHITIN[0] <= u < m.PALETTE_CHITIN[1] for u, v in part.uv))
            if part.name == 'throat':
                self.assertTrue(all(m.PALETTE_THROAT[0] <= u <= m.PALETTE_THROAT[1] for u, v in part.uv))

    def test_palette_is_earthy_tan_umber_not_pink(self):
        import colorsys
        import io
        from PIL import Image
        image = Image.open(io.BytesIO(m.texture_bytes())).convert('RGB')
        w = int(m.UB*m.SIZE)

        def mean(x0, x1, y0, y1):
            px = [image.getpixel((x, y)) for x in range(x0, x1, 5) for y in range(y0, y1, 5)]
            return tuple(sum(c[i] for c in px)/len(px) for i in range(3))
        dorsal = mean(0, int(.55*w), 0, int(.10*m.SIZE))
        flank = mean(0, int(.55*w), int(.42*m.SIZE), int(.55*m.SIZE))
        belly = mean(0, int(.55*w), int(.76*m.SIZE), int(.86*m.SIZE))
        for name, c in (('dorsal', dorsal), ('flank', flank), ('belly', belly)):
            h, sat, val = colorsys.rgb_to_hsv(*(x/255 for x in c))
            self.assertTrue(.05 < h < .15, f'{name} hue {h:.3f} must be umber/tan/ochre, not pink or red')
        lum = lambda c: .3*c[0]+.59*c[1]+.11*c[2]
        self.assertLess(lum(dorsal), lum(flank)-20)
        self.assertLess(lum(flank), lum(belly)-20)
        lip = image.getpixel((int(.94*m.SIZE), int(.5*m.SIZE)))
        self.assertLess(lip[0], 175, 'lip ring is dark fleshy brown-red, not pink')
        self.assertLess(lip[2], lip[0]-30)

    def test_texture_has_wide_value_range_and_annuli(self):
        from PIL import Image
        import io
        image = Image.open(io.BytesIO(m.texture_bytes())).convert('L')
        body = image.crop((0, 0, int(m.UB*m.SIZE), m.SIZE))
        low, high = body.getextrema()
        self.assertLess(low, 45)
        self.assertGreater(high, 200)
        # the annulus grooves make a strong periodic dark stripe along u at mid-flank
        row = [body.getpixel((x, int(.45*m.SIZE))) for x in range(0, body.width)]
        dips = sum(1 for i in range(2, len(row)-2) if row[i] < min(row[i-2], row[i+2])-24)
        self.assertGreater(dips, 12)

    def test_runtime_and_texture_match_master(self):
        data = iqm.encode(self.v, self.n, self.uv, self.tri, self.w, g.BONES, self.clips, self.bounds,
                          mesh_label='Project_Broom_underworm', material_path=g.SKIN)
        self.assertEqual(data, (g.ROOT/'mod/BrogueDoom'/g.MODEL).read_bytes())
        self.assertEqual(g.texture_bytes(), (g.ROOT/'mod/BrogueDoom'/g.SKIN).read_bytes())
        manifest = json.loads((g.ROOT/'assets/monsters/underworm/animation.json').read_text())
        import hashlib
        self.assertEqual(manifest['sha256'], hashlib.sha256(data).hexdigest())
        self.assertEqual(manifest['workId'], 'BRG-M36')

    def test_registry_row_does_not_scale_the_model(self):
        row = find('MK_UNDERWORM')
        self.assertNotIn('visualScale', row)
        self.assertEqual(row['class'], 'BrogueMonsterK36')


if __name__ == '__main__':
    unittest.main()
