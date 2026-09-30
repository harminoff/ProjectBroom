import math
import unittest
from tools.terrain_catalog_assets import model
from tools.terrain_debris import REBUILT


class TerrainDebrisTests(unittest.TestCase):
    def test_shapes_are_grounded_bounded_and_have_valid_faces(self):
        for name in sorted(REBUILT):
            with self.subTest(name=name):
                mesh=model(name)
                self.assertLess(sum(len(f)-2 for f in mesh.faces),2500)
                self.assertTrue(all(math.isfinite(v) for p in mesh.vertices for v in p))
                self.assertGreaterEqual(min(p[1] for p in mesh.vertices),0)
                self.assertLess(max(max(abs(p[0]),abs(p[2])) for p in mesh.vertices),32)
                for face in mesh.faces:
                    a,b,c=[mesh.vertices[v-1] for v,_ in face[:3]]
                    u=[b[i]-a[i] for i in range(3)]; v=[c[i]-a[i] for i in range(3)]
                    cross=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
                    self.assertGreater(sum(x*x for x in cross),1e-12)
                repeat=model(name)
                self.assertEqual((mesh.vertices,mesh.uvs,mesh.faces),(repeat.vertices,repeat.uvs,repeat.faces))

    def test_trampled_growth_stays_flat_and_distinct_from_standing_growth(self):
        for name in ('TrampledLeaves','TrampledFungus'):
            mesh=model(name)
            self.assertLess(max(p[1] for p in mesh.vertices),2)
            self.assertGreater(len({round(p[0],2) for p in mesh.vertices}),40)
        self.assertGreater(max(p[1] for p in model('FungalForest').vertices),25)


if __name__=='__main__': unittest.main()
