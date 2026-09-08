"""Bloodwort asset integrity and repeated native input differential gates."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from tools.bloodwort_models import generate, geometry

ROOT=Path(__file__).resolve().parents[1]


class BloodwortTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        (ROOT/'artifacts/bloodwort').mkdir(parents=True,exist_ok=True)

    def test_original_geometry_and_identical_regeneration(self):
        paths=list((ROOT/'mod/BrogueDoom/models/terrain').glob('bloodwort_*.obj'))
        paths+=list((ROOT/'mod/BrogueDoom/graphics').glob('BRGBW*.png'))
        paths=sorted(paths)
        self.assertEqual(len(paths),8)
        before={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
        generate()
        self.assertEqual(before,{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
        output=ROOT/'artifacts/bloodwort'
        output.mkdir(parents=True,exist_ok=True)
        (output/'asset-hashes.json').write_text(json.dumps(before,indent=2)+'\n')
        for kind in ('stalk','pod','shell','spores'):
            v,f=geometry(kind)
            for x,y,z in v:
                self.assertLess(abs(x),32); self.assertLess(abs(y),32)
                self.assertGreaterEqual(z,0); self.assertLessEqual(z,70)
            for face in f:
                self.assertIn(len(face),(3,4))
                self.assertEqual(len(set(face)),len(face))
                points=[v[i-1] for i in face]
                a=[points[1][i]-points[0][i] for i in range(3)]
                b=[points[2][i]-points[0][i] for i in range(3)]
                normal=(a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
                self.assertGreater(sum(c*c for c in normal),1e-9)

    def test_native_input_five_seeds_repeated(self):
        for seed in (1,2,42,12345,99999):
            outputs=[]
            for repeat in range(2):
                with tempfile.TemporaryDirectory() as folder:
                    run=subprocess.run([str(ROOT/'src/brogue-mapgen/bin/brogue-bridge.exe'),
                        '--seed',str(seed),'--bloodwort-smoke'],cwd=folder,capture_output=True,text=True,timeout=90)
                self.assertEqual(run.returncode,0,run.stdout+run.stderr)
                outputs.append(run.stdout)
            self.assertEqual(outputs[0],outputs[1])
            self.assertIn('steps=300',outputs[0])
            (ROOT/f'artifacts/bloodwort/native-{seed}.log').write_text(outputs[0])


if __name__=='__main__': unittest.main()
