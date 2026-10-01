"""Eel skin continuity, deterministic export, and actual native water projection."""
import collections
import subprocess
import tempfile
import unittest
from pathlib import Path
from . import eel_animation as eel, iqm


class EelTests(unittest.TestCase):
    def test_continuous_skin_and_repeatable_export(self):
        parts, v, n, uv, t, w = eel.geometry()
        body = parts[0]
        keys = [tuple(round(c, 6) for c in p) for p in body.vertices]
        edges = collections.Counter()
        for a, b, c in body.triangles():
            for i, j in ((a, b), (b, c), (c, a)):
                edges[tuple(sorted((keys[i], keys[j])))] += 1
        self.assertEqual(set(edges.values()), {2})
        clips, bounds = eel.animation_data(v, w)
        binary = iqm.encode(v,n,uv,t,w,eel.BONES,clips,bounds,
                            mesh_label='Project_Broom_eel',material_path=eel.SKIN)
        self.assertEqual(binary, (eel.ROOT/'mod/BrogueDoom/models/monsters/04_eel.iqm').read_bytes())
        self.assertEqual(eel.texture_bytes(), (eel.ROOT/'mod/BrogueDoom'/eel.SKIN).read_bytes())
        self.assertLess(max(b[3]-b[0] for b in bounds), 64)
        self.assertLess(max(b[4]-b[1] for b in bounds), 64)

    def test_native_projection_uses_copied_visibility_and_water(self):
        # Compile the production function itself with minimal engine stubs.
        source=(eel.ROOT/'src/gzdoom-bridge/brogue_bridge_frontend.cpp').read_text()
        function='DVector3 MonsterWorldPosition'+source.split('DVector3 MonsterWorldPosition',1)[1].split('AActor *SpawnMonsterProxy',1)[0]
        header=(eel.ROOT/'src/brogue-mapgen/src/brogue/BrogueBridge.h').as_posix()
        harness=f'''#include "{header}"
#include <cassert>
struct DVector3 {{ double X,Y,Z; }};
BrogueBridgeCellState cell{{}};
DVector3 BrogueCellToWorld(int x,int y) {{ return {{x*64.0+32,(28-y)*64.0+32,-24}}; }}
const BrogueBridgeCellState *FindStateCell(int,int) {{ return &cell; }}
{function}
int main() {{
 BrogueBridgeCreatureState c{{}}; c.kind=4; c.presentationKind=4; c.x=2;c.y=3;
 cell.appearance.knowledge=BROGUE_TERRAIN_VISIBLE;
 cell.appearance.liquidKind=BROGUE_LIQUID_DEEP_WATER;
 c.visibility=BROGUE_VISIBILITY_HIDDEN; assert(MonsterWorldPosition(c).Z==-24);
 c.visibility=BROGUE_VISIBILITY_DIRECT; assert(MonsterWorldPosition(c).Z==-7);
 assert(MonsterWorldPosition(c).X==160 && MonsterWorldPosition(c).Y==1632);
 c.visibility=BROGUE_VISIBILITY_SENSED; assert(MonsterWorldPosition(c).Z==-7);
 cell.appearance.flags=BROGUE_APPEARANCE_FLOOD; assert(MonsterWorldPosition(c).Z==17);
 cell.appearance.liquidKind=BROGUE_LIQUID_SHALLOW_WATER; assert(MonsterWorldPosition(c).Z==1);
 cell.appearance.flags=BROGUE_APPEARANCE_ICE; assert(MonsterWorldPosition(c).Z==-24);
 cell.appearance.flags=BROGUE_APPEARANCE_BRIDGE; assert(MonsterWorldPosition(c).Z==-24);
 cell.appearance.flags=0;c.presentationKind=2;assert(MonsterWorldPosition(c).Z==-24);
 c.kind=2;c.presentationKind=4;assert(MonsterWorldPosition(c).Z==-7);
 cell.appearance.knowledge=BROGUE_TERRAIN_UNKNOWN;assert(MonsterWorldPosition(c).Z==-24);
}}
'''
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'eel.cpp';path.write_text(harness)
            exe=Path(folder)/'eel.exe'
            subprocess.run(['g++','-std=c++17','-static',str(path),'-o',str(exe)],check=True,capture_output=True)
            subprocess.run([str(exe)],check=True)


if __name__=='__main__': unittest.main()
