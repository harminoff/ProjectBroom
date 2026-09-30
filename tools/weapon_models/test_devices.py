import unittest
from pathlib import Path
import tempfile
from unittest.mock import patch
from tools.weapon_models.output import write_asset, write_asset_text
from tools.weapon_models.devices import device_parts, generate
from tools.weapon_models.generate import ROOT
from tools.weapon_models.viewmodel import md3_bytes, obj_text


class AssetOutputTest(unittest.TestCase):
    def test_unchanged_asset_is_not_opened_for_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'weapon_02.obj'
            path.write_bytes(b'original')
            before = path.stat().st_mtime_ns
            with patch('tools.weapon_models.output.tempfile.NamedTemporaryFile',
                       side_effect=AssertionError('must not stage unchanged assets')):
                self.assertFalse(write_asset(path, b'original'))
            self.assertEqual(path.stat().st_mtime_ns, before)

    def test_failed_replacement_preserves_old_model_and_reports_path(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'wand.md3'
            path.write_bytes(b'valid old model')
            with patch('tools.weapon_models.output.os.replace',
                       side_effect=OSError(22, 'Invalid argument')):
                with self.assertRaises(OSError) as raised:
                    write_asset(path, b'new model')
            self.assertEqual(raised.exception.errno, 22)
            self.assertEqual(raised.exception.filename, str(path))
            self.assertEqual(path.read_bytes(), b'valid old model')
            self.assertEqual(list(Path(directory).iterdir()), [path])

    def test_new_and_changed_assets_replace_complete_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'weapon.md3'
            self.assertTrue(write_asset(path, b'new model'))
            self.assertTrue(write_asset(path, b'changed model'))
            self.assertEqual(path.read_bytes(), b'changed model')
            self.assertEqual(list(Path(directory).iterdir()), [path])

    def test_text_preserves_native_output_encoding_and_newlines(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'weapon.obj'
            path.write_text('o weapon\nv 0 0 0\n', encoding='ascii')
            self.assertFalse(write_asset_text(path, 'o weapon\nv 0 0 0\n'))


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
