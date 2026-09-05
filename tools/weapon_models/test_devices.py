import unittest
from tools.weapon_models.devices import device_parts, generate
from tools.weapon_models.generate import ROOT
from tools.weapon_models.viewmodel import md3_bytes, obj_text


class DeviceModelsTest(unittest.TestCase):
    def test_assets_match_source_and_animation_returns_to_ready(self):
        for staff, name in ((True,'staff'),(False,'wand')):
            frames=[device_parts(staff,i) for i in range(9)]
            directory=ROOT/'mod/BrogueDoom/models/devices'
            self.assertEqual((directory/(name+'.md3')).read_bytes(),md3_bytes(frames))
            self.assertEqual((directory/(name+'.obj')).read_text(),obj_text(frames[0]))
            self.assertEqual(frames[0],frames[8])
            self.assertNotEqual(frames[0],frames[4])
            for frame in frames:
                self.assertEqual([(p.name,p.faces,p.uv) for p in frame],
                                 [(p.name,p.faces,p.uv) for p in frames[0]])
    def test_device_states_are_inert_and_all_frames_mapped(self):
        zs=(ROOT/'mod/BrogueDoom/brogue_devices.zs').read_text()
        for forbidden in ('A_Fire','A_Custom','A_Spawn','A_Rail','A_Explode','A_TakeInventory'):
            self.assertNotIn(forbidden,zs)
        self.assertEqual(zs.count('BridgeUse:'),2)
        modeldef=(ROOT/'mod/BrogueDoom/models/devices/MODELDEF.txt').read_text()
        textures=(ROOT/'mod/BrogueDoom/TEXTURES.txt').read_text()
        for sprite in ('BDST','BDWA'):
            for i in range(9):
                self.assertIn(f'FrameIndex {sprite} {chr(65+i)} 0 {i}',modeldef)
                self.assertIn(f'Sprite "{sprite}{chr(65+i)}0"',textures)


if __name__=='__main__': unittest.main()
