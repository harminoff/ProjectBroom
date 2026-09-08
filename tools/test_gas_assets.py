"""Check gas alpha edges, usable density, and cell-local deterministic geometry."""
import math
from pathlib import Path
import unittest
from PIL import Image
from tools.gas_assets import cloud_geometry, cloud_texture
from tools.bloodwort_models import geometry as bloodwort_geometry


class GasAssetsTests(unittest.TestCase):
    def test_feathered_density_without_rectangular_edges(self):
        image = cloud_texture()
        self.assertEqual(image.tobytes(), cloud_texture().tobytes())
        alpha = image.getchannel('A')
        size = image.width
        for i in range(size):
            for point in ((i,0),(i,size-1),(0,i),(size-1,i)):
                self.assertEqual(alpha.getpixel(point), 0)
        self.assertGreater(alpha.getpixel((size//2,size//2)), 100)
        self.assertGreater(len(set(alpha.getdata())), 100)
        self.assertLess(max(alpha.getdata()), 230)
        shipped = Path(__file__).resolve().parents[1]/'mod/BrogueDoom/graphics/BRGTCLOUD.png'
        with Image.open(shipped) as generated:
            self.assertEqual(image.tobytes(), generated.tobytes())

    def test_cloud_stays_in_its_cell_during_drift(self):
        vertices, faces = cloud_geometry()
        self.assertEqual((vertices,faces), cloud_geometry())
        self.assertEqual(len(faces),9)
        for x,y,z in vertices + bloodwort_geometry('spores')[0]:
            # Any yaw, maximum native scale and two-unit translation.
            self.assertLess(math.hypot(x,y)*1.035+2,32)
            self.assertGreaterEqual(z-2,0)
            self.assertLess(z+2,64)
        for face in faces:
            self.assertEqual(len(set(face)),4)


if __name__ == '__main__': unittest.main()
