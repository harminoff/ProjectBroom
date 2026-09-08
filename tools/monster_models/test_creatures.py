"""All-kind asset, source fidelity, scale, and authority regression gates."""
import hashlib
import json
import math
import re
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

from . import creatures, rat
from .bestiary import ROOT, INDEX, profiles, source_records, c_records, horde_references


class CreatureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records=source_records()
        cls.index=json.loads(INDEX.read_text(encoding='utf-8'))

    def test_source_index_complete_and_aligned(self):
        self.assertEqual(len(self.records),68)
        self.assertEqual(set(profiles()),{r['symbol'] for r in self.records if r['kind']>1})
        self.assertEqual([r['kind'] for r in self.records],list(range(68)))
        for actual,indexed in zip(self.records,self.index['creatures']):
            with self.subTest(kind=actual['kind']):
                self.assertEqual(indexed['indexId'],f"BRG-M{actual['kind']:02d}")
                for field in ('name','symbol','isLarge','color','description','sourceTextStrings','catalogTokens','source'):
                    self.assertEqual(actual[field],indexed[field])
                self.assertTrue(actual['description'])

    def test_c_parser_ignores_braces_inside_comments_and_strings(self):
        source='const table[] = { /* } */ {"curly { }", {0}}, // {\n {"other"} };'
        self.assertEqual(len(list(c_records(source,'const table['))),2)

    def test_verification_preserved_until_asset_hash_changes(self):
        from . import bestiary
        with tempfile.TemporaryDirectory() as folder:
            target=Path(folder)/'index.json'
            baseline=json.loads(INDEX.read_text(encoding='utf-8'))
            baseline['creatures'][4]['verification']={'review':'accepted-for-test'}
            target.write_text(json.dumps(baseline),encoding='utf-8')
            with patch.object(bestiary,'INDEX',target), patch.object(bestiary,'write_docs'):
                same=bestiary.write_index()
                self.assertEqual(same['creatures'][4]['verification'],{'review':'accepted-for-test'})
                original=baseline['creatures'][4]['art']
                changed={key:original[key] for key in ('triangles','parts','bounds','objSha256','skinSha256')}
                changed['objSha256']='different-geometry'
                result=bestiary.write_index({'MK_EEL':changed})
                self.assertTrue(result['creatures'][4]['verification']['stale'])
                self.assertEqual(result['creatures'][4]['verification']['previousAssetVerification'],
                                 {'review':'accepted-for-test'})

    def test_horde_references_preserve_roles_and_expressions(self):
        refs=horde_references()
        self.assertEqual(refs['MK_RAT'][0]['minLevelExpression'],'1')
        self.assertEqual(refs['MK_RAT'][0]['maxLevelExpression'],'5')
        self.assertTrue(any(r['maxLevelExpression']=='DEEPEST_LEVEL-1' for r in refs['MK_DRAGON']))
        self.assertTrue(any('HORDE_IS_SUMMONED' in r['flags'] and 'member' in r['roles'] for r in refs['MK_LICH']))
        for entry in self.index['creatures']:
            self.assertEqual(entry['hordeReferences'],refs.get(entry['symbol'],[]))

    def test_geometry_all_kinds_floor_extents_uv_normals(self):
        for record in self.records[2:]:
            with self.subTest(kind=record['kind']):
                parts=creatures.build_parts(record)
                vertices=[v for p in parts for v in p.vertices]
                plan=profiles()[record['symbol']]
                minimum=[min(v[a] for v in vertices) for a in range(3)]
                maximum=[max(v[a] for v in vertices) for a in range(3)]
                self.assertAlmostEqual(minimum[2],16 if 'MONST_FLIES' in record['catalogTokens'] else 0,places=5)
                for a in range(3): self.assertAlmostEqual(maximum[a]-minimum[a],plan['dimensions'][a],places=5)
                self.assertLessEqual(plan['dimensions'][0],64)
                self.assertLessEqual(plan['dimensions'][1],64)
                count=0
                for part in parts:
                    self.assertEqual(len(part.vertices),len(part.uv))
                    self.assertTrue(all(math.isfinite(v) for xyz in part.vertices for v in xyz))
                    self.assertTrue(all(0<=v<=1 for uv in part.uv for v in uv))
                    for normal in part.normals(): self.assertAlmostEqual(sum(x*x for x in normal),1,places=5)
                    for face in part.triangles():
                        count+=1
                        self.assertTrue(all(0<=i<len(part.vertices) for i in face))
                        a,b,c=[part.vertices[i] for i in face]
                        cross=rat.cross(rat.sub(b,a),rat.sub(c,a))
                        self.assertGreater(sum(x*x for x in cross),1e-15,part.name)
                self.assertGreater(count,50)
                self.assertLess(count,22000)

    def test_runtime_matches_deterministic_geometry_and_recorded_hashes(self):
        for record in self.records[2:]:
            with self.subTest(kind=record['kind']):
                entry=self.index['creatures'][record['kind']]['art']
                model=(ROOT/entry.get('staticReference',entry['runtimeModel'])).read_bytes()
                self.assertEqual(model,creatures.obj_bytes(creatures.build_parts(record),record['symbol']))
                if 'objSha256' in entry: self.assertEqual(hashlib.sha256(model).hexdigest(),entry['objSha256'])
                skin=json.loads((ROOT/entry['animationManifest']).read_text())['skin'] if 'animationManifest' in entry else f"graphics/BRGM{record['kind']:02d}.png"
                self.assertEqual(hashlib.sha256((ROOT/'mod/BrogueDoom'/skin).read_bytes()).hexdigest(),entry['skinSha256'])

    def test_texture_deterministic(self):
        for k in (2,13,50):
            expected=creatures.texture_bytes(self.records[k])
            self.assertEqual(expected,(ROOT/f'mod/BrogueDoom/graphics/BRGM{k:02d}.png').read_bytes())

    def test_distinctive_source_requirements(self):
        lookup={r['symbol']:r for r in self.records}
        # Prior placeholders incorrectly classified dar as flying, fury as goo.
        self.assertEqual(profiles()['MK_DAR_BLADEMASTER']['recipe'],'humanoid')
        self.assertEqual(profiles()['MK_FURY']['recipe'],'winged')
        self.assertNotIn('MONST_FLIES',lookup['MK_DRAGON']['catalogTokens'])
        self.assertNotIn('weapon',','.join(p.name.lower() for p in creatures.build_parts(lookup['MK_GOBLIN_MYSTIC'])))
        self.assertGreater(profiles()['MK_GOBLIN_CHIEFTAN']['dimensions'][2],profiles()['MK_GOBLIN']['dimensions'][2])
        self.assertGreater(profiles()['MK_UNDERWORM']['dimensions'][2],profiles()['MK_OGRE']['dimensions'][2])
        self.assertLess(profiles()['MK_PIXIE']['dimensions'][2],profiles()['MK_KOBOLD']['dimensions'][2])
        self.assertEqual(profiles()['MK_MIRRORED_TOTEM']['dimensions'][2],46)

    def test_registry_preserves_authority_and_identity(self):
        registry=json.loads((ROOT/'assets/monsters/brogue_monster_registry.json').read_text())
        self.assertEqual(len(registry['monsters']),68)
        for expected,entry in zip(self.records,registry['monsters']):
            self.assertEqual(expected['kind'],entry['kind'])
            self.assertEqual(expected['symbol'],entry['symbol'])
            self.assertEqual(entry['class'],f"BrogueMonsterK{expected['kind']:02d}")
            if expected['kind']>1:
                expected_skin=json.loads((ROOT/entry['animationManifest']).read_text())['skin'] if 'animationManifest' in entry else f"graphics/BRGM{expected['kind']:02d}.png"
                self.assertEqual(entry['skin'],expected_skin)
                dimensions=json.loads((ROOT/entry['animationManifest']).read_text())['dimensions'] if 'animationManifest' in entry else profiles()[expected['symbol']]['dimensions']
                self.assertEqual(entry['authoredDimensions'],dimensions)
        zscript=(ROOT/'mod/BrogueDoom/brogue_monsters.zs').read_text()
        for flag in ('+NOBLOCKMAP','+NOGRAVITY','+NOINTERACTION','+NOTONAUTOMAP'): self.assertIn(flag,zscript)
        for forbidden in ('A_Chase','A_CustomMeleeAttack','A_Damage','Random('): self.assertNotIn(forbidden,zscript)
        bindings=(ROOT/'mod/BrogueDoom/models/monsters/MODELDEF.txt').read_text()
        self.assertEqual(bindings.count('Scale 1.0 1.0 1.0'),68) # 67 normal-size kinds plus captive presentation.
        self.assertEqual(bindings.count('Scale 1.28 1.28 1.28'),1)


if __name__=='__main__': unittest.main()
