import os
from pathlib import Path
import subprocess
import tempfile
import unittest
import re
from tools.terrain_presentation import FALLING_VOID_SYMBOLS, generate, NATIVE, load, symbols

ROOT = Path(__file__).resolve().parents[1]


class TerrainSyncTests(unittest.TestCase):
    def test_safe_chasm_edges_keep_supporting_ground_material(self):
        registry = load()
        self.assertEqual(registry['CHASM']['floor'], 'BRGVOID')
        self.assertEqual(registry['HOLE']['floor'], 'BRGVOID')
        self.assertEqual(registry['CHASM_EDGE']['floor'], 'BRGEARTH')
        self.assertEqual(registry['MACHINE_CHASM_EDGE']['floor'], 'BRGEARTH')
        self.assertNotIn('CHASM_EDGE', FALLING_VOID_SYMBOLS)
        self.assertNotIn('MACHINE_CHASM_EDGE', FALLING_VOID_SYMBOLS)

        frontend = (ROOT / 'src/gzdoom-bridge/brogue_bridge_frontend.cpp').read_text()
        description = frontend[frontend.index('FString CellDescription'):
                               frontend.index('void DrawBrogueMinimap')]
        hole = 'cell->appearance.flags & BROGUE_APPEARANCE_HOLE'
        edge = 'if (cell->isChasm) return "Chasm edge";'
        self.assertIn(hole, description)
        self.assertIn(edge, description)
        self.assertLess(description.index(hole), description.index(edge))

    def test_registry_is_complete_and_generation_is_identical(self):
        self.assertEqual(set(load()), set(symbols()))
        before = NATIVE.read_bytes()
        generate()
        self.assertEqual(before, NATIVE.read_bytes())
        classes = set()
        for source in (ROOT / 'mod/BrogueDoom').rglob('*.zs'):
            classes.update(re.findall(r'\bclass\s+(\w+)', source.read_text()))
        for symbol, record in load().items():
            self.assertTrue(not record['actor'] or record['actor'] in classes, symbol)

    def test_planner(self):
        with tempfile.TemporaryDirectory() as folder:
            exe = Path(folder) / 'planner.exe'
            subprocess.run(['g++', '-std=c++17', '-static', str(ROOT/'tools/terrain_reconciler_test.cpp'), '-o', str(exe)], check=True, capture_output=True)
            subprocess.run([str(exe)], check=True, capture_output=True)

    def test_appearance_and_native_parity_five_seeds_repeated(self):
        for seed in (1, 2, 42, 12345, 99999):
            with self.subTest(seed=seed):
                outputs = []
                for repeat in range(2):
                    with tempfile.TemporaryDirectory() as folder:
                        run = subprocess.run([str(ROOT/'src/brogue-mapgen/bin/brogue-bridge.exe'), '--seed', str(seed), '--terrain-smoke'],
                                             cwd=folder, capture_output=True, text=True, timeout=90)
                        self.assertEqual(run.returncode, 0, run.stderr + run.stdout)
                        outputs.append(run.stdout)
                self.assertEqual(outputs[0], outputs[1])


if __name__ == '__main__': unittest.main()
