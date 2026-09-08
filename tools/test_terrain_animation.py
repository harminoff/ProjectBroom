import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from tools.terrain_assets import generate, ROOT

class TerrainAnimationTests(unittest.TestCase):
    def test_all_manacles_have_physical_forms(self):
        registry=json.loads((ROOT/'assets/terrain/terrain_presentation.json').read_text())
        for name in ('TL','TR','BL','BR','T','B','L','R'):
            role='Ceiling' if name in ('TL','TR') else 'Floor' if name in ('BL','BR') else 'Wall'
            self.assertEqual(registry['MANACLE_'+name]['actor'],'BrogueTerrainManacle'+role)
    def test_torch_knowledge_aliases(self):
        registry=json.loads((ROOT/'assets/terrain/terrain_presentation.json').read_text())
        for name in ('TORCH_WALL','HAUNTED_TORCH_DORMANT','HAUNTED_TORCH_TRANSITIONING','HAUNTED_TORCH'):
            self.assertEqual(registry[name]['actor'],'BrogueTerrainTorch')
    def test_statues_preserve_camouflage_and_geometry(self):
        from tools.statue_models import sculpture
        registry=json.loads((ROOT/'assets/terrain/terrain_presentation.json').read_text())
        for name in ('STATUE_DORMANT','STATUE_INSTACRACK','STATUE_DORMANT_DOORWAY'):
            self.assertEqual(registry[name]['actor'],registry['STATUE_INERT']['actor'])
        for name in ('marble','cracked','broken','demon'):
            vertices,faces=sculpture(name)
            self.assertEqual(min(p[2] for p in vertices),0)
            self.assertLessEqual(max(p[2] for p in vertices),82)
            self.assertLessEqual(max(abs(p[0]) for p in vertices),20)
            self.assertLessEqual(max(abs(p[1]) for p in vertices),20)
            for face in faces:
                self.assertIn(len(face),(3,4)) # UZDoom OBJ loader cannot render ngons.
                p,q,r=(vertices[i-1] for i in face[:3])
                a=[q[i]-p[i] for i in range(3)]; b=[r[i]-p[i] for i in range(3)]
                normal=(a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
                self.assertGreater(sum(x*x for x in normal),1e-12)
    def test_retargeting_and_exact_settling(self):
        with tempfile.TemporaryDirectory() as folder:
            exe=Path(folder)/'animation.exe'
            subprocess.run(['g++','-std=c++17','-static',str(ROOT/'tools/terrain_animation_test.cpp'),'-o',str(exe)],check=True,capture_output=True)
            subprocess.run([str(exe)],check=True)

    def test_assets_are_byte_identical_and_have_valid_faces(self):
        def hashes():
            files=list((ROOT/'mod/BrogueDoom/models/terrain').glob('*'))
            files += [ROOT/'mod/BrogueDoom/graphics'/n for n in ('BRGICE.png','BRGTFLAM.png','BRGTCLOUD.png','BRGSTMAR.png','BRGSTCRK.png','BRGSTBRK.png','BRGSTOBS.png','BRGTORCH.png','BRGTORFL.png','BRGTHAFL.png','BRGIRON.png')]
            return {str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
        generate(); before=hashes(); generate(); self.assertEqual(before,hashes())
        for path in (ROOT/'mod/BrogueDoom/models/terrain').glob('*.obj'):
            lines=path.read_text().splitlines()
            vertices=sum(line.startswith('v ') for line in lines)
            for line in lines:
                if line.startswith('f '):
                    face=[int(v.split('/')[0]) for v in line.split()[1:]]
                    self.assertGreaterEqual(len(set(face)),3)
                    self.assertTrue(all(1<=v<=vertices for v in face))
        self.assertTrue((ROOT/'assets/terrain/ANIMATION-LICENSE.md').is_file())

if __name__=='__main__': unittest.main()
