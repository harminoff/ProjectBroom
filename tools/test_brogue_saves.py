"""Native saves and copied lifecycle contract; files are isolated per test."""
import ctypes as C
import os
import re
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / 'src/brogue-mapgen/bin'


class Request(C.Structure):
    _fields_ = [('version', C.c_uint32), ('operation', C.c_int32),
                ('revision', C.c_uint64), ('session', C.c_uint64),
                ('consume', C.c_uint8), ('path', C.c_char * 4096)]


class State(C.Structure):
    _fields_ = [('version', C.c_uint32), ('errorCode', C.c_int32),
                ('phase', C.c_int32), ('session', C.c_uint64),
                ('revision', C.c_uint64), ('seed', C.c_uint64),
                ('turns', C.c_uint64), ('total', C.c_uint64),
                ('mode', C.c_int32), ('nativeVersion', C.c_char * 16),
                ('error', C.c_char * 256)]


class NativeSaveTests(unittest.TestCase):
    def test_launcher_offers_validated_seeded_new_game(self):
        launcher=(ROOT/'tools/BrogueDoomLauncher/NativeSaves.cs').read_text(encoding='utf-8')
        self.assertIn('Add("New Game with Seed"', launcher)
        self.assertIn('PromptForSeed(window)', launcher)
        self.assertIn('ulong.TryParse(seedBox.Text.Trim()', launcher)
        self.assertIn('seed == 0', launcher)
        self.assertIn('selection = new(seed, null)', launcher)

    def test_launcher_uses_current_bridge_contract(self):
        header=(ROOT/'src/brogue-mapgen/src/brogue/BrogueBridge.h').read_text(encoding='utf-8')
        launcher=(ROOT/'tools/BrogueDoomLauncher/NativeSaves.cs').read_text(encoding='utf-8')
        api=re.search(r'#define BROGUE_BRIDGE_API_VERSION (\d+)u',header).group(1)
        self.assertEqual(api,re.search(r'BridgeApiVersion = (\d+);',launcher).group(1))
        self.assertIn('Version = BridgeApiVersion,',launcher)

    @classmethod
    def setUpClass(cls):
        cls.dll = C.CDLL(str(BIN / 'brogue-bridge.dll'))
        cls.dll.brogue_bridge_persistence.argtypes = [C.POINTER(Request), C.POINTER(State)]
        cls.dll.brogue_bridge_start_game.argtypes = [C.c_uint64]

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix='broom-save-')
        self.root = Path(self.directory.name)
        self.dll.brogue_bridge_shutdown()
        self.state = State()
        self.call(7)

    def tearDown(self):
        self.dll.brogue_bridge_shutdown()
        self.directory.cleanup()

    def call(self, operation, path='', expected=0, consume=False, version=20, stale=False):
        request = Request(version, operation, self.state.revision + int(stale),
                          self.state.session, consume, str(path).encode('utf-8'))
        result = self.dll.brogue_bridge_persistence(C.byref(request), C.byref(self.state))
        self.assertEqual(result, expected, self.state.error.decode())
        return self.state

    def new(self, seed=42):
        self.call(0, self.root / 'working-å.broguesave')
        self.assertEqual(self.dll.brogue_bridge_start_game(seed), 0)
        self.call(7)

    def wait(self):
        result = C.create_string_buffer(1024 * 1024)
        self.assertEqual(self.dll.brogue_bridge_perform_action(8, result), 0)
        self.call(7)

    def test_native_roundtrips_and_rng(self):
        for seed in (1, 2, 42, 12345, 99999, 18446744073709551615):
            result = subprocess.run([str(BIN / 'brogue-bridge.exe'), '--seed', str(seed), '--save-smoke'],
                                    cwd=self.root, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('subsequent-wait=OK', result.stdout)

    def test_native_depth_transition_roundtrips(self):
        for seed in (1, 2, 42, 12345, 99999):
            result = subprocess.run([str(BIN / 'brogue-bridge.exe'), '--seed', str(seed), '--save-depth-smoke'],
                                    cwd=self.root, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('subsequent-wait=OK depth=2', result.stdout)

    def test_suspend_resume_and_repeated_load(self):
        self.new(18446744073709551615)
        self.wait()
        saved = self.root / '悬停.broguesave'
        self.call(2, saved)
        original = saved.read_bytes()
        old_session = self.state.session
        old_revision = self.state.revision
        self.dll.brogue_bridge_shutdown()
        self.call(7)
        self.call(0, self.root / 'resumed.broguesave')
        self.call(3, saved)
        self.assertGreater(self.state.session, old_session)
        self.assertGreater(self.state.revision, old_revision)
        self.call(4)
        self.assertEqual((self.state.phase, self.state.turns), (3, 1))
        self.call(5, consume=False)
        self.assertEqual(saved.read_bytes(), original)
        self.wait()
        second = self.root / 'second.broguesave'
        self.call(2, second)
        self.dll.brogue_bridge_shutdown()
        self.call(7)
        self.call(0, self.root / 'again.broguesave')
        self.call(3, second)
        self.call(4)
        self.assertEqual(self.state.turns, 2)
        self.call(5, consume=True)
        self.assertFalse(second.exists())

    def test_cancel_stale_version_and_failed_save(self):
        self.new()
        self.call(2, self.root / 'missing' / 'save.broguesave', expected=8)
        self.assertEqual((self.state.phase, self.state.turns), (1, 0))
        self.call(2, self.root / 'save.broguesave', expected=10, stale=True)
        self.call(2, self.root / 'save.broguesave', expected=5, version=17)
        saved = self.root / 'save.broguesave'
        self.call(2, saved)
        original = saved.read_bytes()
        self.dll.brogue_bridge_shutdown()
        self.call(7)
        self.call(0, self.root / 'resume.broguesave')
        self.call(4, expected=5)
        self.call(3, saved)
        self.call(6)
        self.assertEqual(saved.read_bytes(), original)
        self.call(3, saved)
        self.call(4)
        self.assertEqual(self.state.total, 0)
        self.call(5)

    def test_invalid_headers_are_rejected_without_session(self):
        self.new()
        saved = self.root / 'save.broguesave'
        self.call(2, saved)
        data = saved.read_bytes()
        self.dll.brogue_bridge_shutdown()
        self.call(7)
        for corrupt in (b'', data[:20], data[:-1], b'BAD VERSION\0' + data[12:]):
            path = self.root / 'bad.broguesave'
            path.write_bytes(corrupt)
            self.call(1, path, expected=5)
            self.assertEqual(self.state.phase, 0)

    def test_current_level_export_and_compilation_are_deterministic(self):
        from tools.mapcompiler.runtime import compile_current
        self.new()
        self.wait()
        before = (self.state.turns, self.state.revision)
        first, second = self.root / 'one.json', self.root / 'two.json'
        self.call(8, first)
        self.call(8, second)
        self.assertEqual(first.read_bytes(), second.read_bytes())
        self.assertEqual((self.state.turns, self.state.revision), before)
        wad1, wad2 = self.root / 'one.wad', self.root / 'two.wad'
        self.assertEqual(compile_current(first, wad1), compile_current(second, wad2))
        self.assertEqual(wad1.read_bytes(), wad2.read_bytes())
        from tools.mapcompiler.verify import wad_textmap, blocks, int_property
        text=wad_textmap(wad1.read_bytes(), 'BRG01')
        sectors=blocks(text, 'sector')
        self.assertEqual(len(sectors), 2291*3)
        tags={int_property(s,'id') for s in sectors}
        for base in (10000,30000,40000):
            self.assertTrue(set(range(base,base+2291)).issubset(tags))
        wad1.write_bytes(b'truncated cache')
        compile_current(first, wad1)
        self.assertEqual(wad1.read_bytes(), wad2.read_bytes())

    def test_bounded_load_hides_intermediate_snapshots(self):
        self.new(1)
        for _ in range(40):
            self.wait()
        saved = self.root / 'long.broguesave'
        self.call(2, saved)
        self.dll.brogue_bridge_shutdown()
        self.call(7)
        self.call(0, self.root / 'resume.broguesave')
        self.call(3, saved)
        self.call(4)
        self.assertEqual((self.state.phase, self.state.turns), (2, 32))
        output = C.create_string_buffer(2 * 1024 * 1024)
        self.assertEqual(self.dll.brogue_bridge_get_state(output), 5)
        self.assertEqual(self.dll.brogue_bridge_inspect_cell(0, 0, output), 5)
        self.call(4)
        self.assertEqual((self.state.phase, self.state.turns), (3, 40))
        self.call(6)
        self.assertTrue(saved.exists())

    def test_out_of_sync_native_input_preserves_the_save(self):
        self.new()
        self.wait()
        saved = self.root / 'bad-event.broguesave'
        self.call(2, saved)
        data = bytearray(saved.read_bytes())
        data[36] = 255
        saved.write_bytes(data)
        self.dll.brogue_bridge_shutdown()
        self.call(7)
        self.call(0, self.root / 'resume.broguesave')
        self.call(3, saved, expected=8)
        self.call(6)
        self.assertEqual(saved.read_bytes(), data)


if __name__ == '__main__':
    unittest.main()
