"""Pit-bloat identity, shared deformation, and deterministic export checks."""
import io
import unittest
from PIL import Image
from . import pit_bloat_animation as pit, bloat_animation as bloat, iqm


class PitBloatTests(unittest.TestCase):
    def test_shared_subspecies_anatomy(self):
        self.assertEqual(pit.geometry(), bloat.geometry())
        self.assertEqual(pit.BONES, bloat.BONES)
        self.assertEqual(len(pit.CLIPS), 6)

    def test_blue_diffuse_identity(self):
        image = Image.open(io.BytesIO(pit.texture_bytes()))
        self.assertEqual(image.mode, 'RGB')
        self.assertEqual(image.size, (512, 512))
        self.assertTrue(all(b > r+80 and b > g+70 for r,g,b in image.getdata()))
        self.assertNotEqual(pit.texture_bytes(), bloat.texture_bytes())

    def test_deterministic_runtime(self):
        _,v,n,uv,t,w = pit.geometry()
        clips,bounds = pit.animation_data(v,w)
        data = iqm.encode(v,n,uv,t,w,pit.BONES,clips,bounds,
            mesh_label='Project_Broom_pit_bloat',material_path=pit.SKIN)
        self.assertEqual(data,(pit.ROOT/'mod/BrogueDoom/models/monsters/07_pit_bloat.iqm').read_bytes())
        self.assertEqual(pit.texture_bytes(),(pit.ROOT/'mod/BrogueDoom'/pit.SKIN).read_bytes())


if __name__=='__main__': unittest.main()
