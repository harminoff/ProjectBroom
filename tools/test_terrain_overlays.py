import unittest
from PIL import Image
from tools.terrain_overlays import OVERLAYS, coating
from tools.terrain_catalog_assets import SURFACES


class TerrainOverlayTests(unittest.TestCase):
    def test_coatings_leave_the_substrate_visible(self):
        for name,_,color,_ in SURFACES:
            if name not in OVERLAYS: continue
            with self.subTest(name=name):
                image=coating(name,color)
                self.assertEqual(image.mode,'RGBA')
                alpha=image.getchannel('A')
                self.assertEqual(alpha.getextrema()[0],0)
                self.assertGreater(alpha.getextrema()[1],0)
                for xy in ((0,0),(127,0),(0,127),(127,127)):
                    self.assertEqual(alpha.getpixel(xy),0)
                # Transparent portions preserve distinct underlying materials exactly.
                for base in ((28,34,40,255),(180,160,140,255),(110,20,25,255)):
                    result=Image.alpha_composite(Image.new('RGBA',image.size,base),image)
                    self.assertEqual(result.getpixel((0,0)),base)
                self.assertEqual(image.tobytes(),coating(name,color).tobytes())

    def test_light_has_soft_alpha_and_stains_have_clear_surrounds(self):
        light=coating('BTSUN',(174,155,97)).getchannel('A')
        self.assertGreater(len(set(light.getdata())),32)
        blood=coating('BTBLOOD',(100,10,15)).getchannel('A')
        self.assertGreater(list(blood.getdata()).count(0),128*128//3)


if __name__=='__main__': unittest.main()
