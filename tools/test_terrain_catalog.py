import unittest
from tools.audit_terrain_catalog import catalog
from tools.terrain_presentation import ROOT, load, symbols
from tools.terrain_catalog_assets import SURFACES, OBJECTS, model, surface


class TerrainCatalogTest(unittest.TestCase):
    def test_every_description_is_audited(self):
        self.assertEqual(set(catalog()),set(symbols()))
        self.assertEqual(catalog()['BRIDGE']['description'],'a rickety rope bridge')

    def test_semantic_materials_and_prop_bindings(self):
        registry=load()
        for material,tiles,*_ in SURFACES:
            for tile in tiles.split(): self.assertEqual(registry[tile]['floor'],material,tile)
        for name,tiles in OBJECTS.items():
            for tile in tiles.split(): self.assertEqual(registry[tile]['actor'],'BrogueCatalog'+name,tile)
        self.assertNotEqual(registry['BRIDGE']['floor'],registry['STONE_BRIDGE']['floor'])
        self.assertEqual(registry['DEEP_WATER_ALGAE_WELL']['floor'],'BRGEARTH')

    def test_hidden_forms_do_not_receive_new_props(self):
        for name,entry in catalog().items():
            if entry['secret']: self.assertFalse(load()[name]['actor'],name)
        self.assertEqual(load()['CHASM_WITH_HIDDEN_BRIDGE']['floor'],'BRGVOID')

    def test_materials_and_meshes_are_repeatable_and_nonempty(self):
        for material,tiles,color,treatment in SURFACES:
            a=surface(color,treatment); b=surface(color,treatment)
            self.assertEqual(a.tobytes(),b.tobytes(),material)
        for name in OBJECTS:
            a,b=model(name),model(name)
            self.assertTrue(a.faces,name)
            self.assertEqual((a.vertices,a.uvs,a.faces),(b.vertices,b.uvs,b.faces),name)
            for face in a.faces:
                self.assertGreaterEqual(len(face),3)
                self.assertTrue(all(1<=v<=len(a.vertices) and 1<=uv<=len(a.uvs) for v,uv in face))


if __name__=='__main__': unittest.main()
