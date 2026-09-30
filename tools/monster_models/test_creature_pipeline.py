"""Fast regressions for the shared creature pipeline (no engine, no Blender)."""
import copy, json, tempfile, unittest
from pathlib import Path
from unittest.mock import patch

from . import bestiary, skeletal_registry, creature_pipeline, review_wall_fixture

ROOT = skeletal_registry.ROOT


def index_with(symbols):
    data = json.loads((ROOT/'assets/monsters/bestiary-index.json').read_text(encoding='utf-8'))
    data = {**data, 'creatures': [c for c in data['creatures'] if c['symbol'] in symbols]}
    return copy.deepcopy(data)


class CardGeneratorTests(unittest.TestCase):
    def test_hand_maintained_cards_are_never_overwritten(self):
        index = index_with({'MK_CENTAUR', 'MK_DART_TURRET'})
        with tempfile.TemporaryDirectory() as tmp, patch.object(bestiary, 'ROOT', Path(tmp)):
            cards = Path(tmp)/'docs/creatures'; cards.mkdir(parents=True)
            hand = cards/'35_centaur.md'; hand.write_bytes(b'hand refined\r\n')
            bestiary.write_docs(index)
            self.assertEqual(hand.read_bytes(), b'hand refined\r\n')
            self.assertIn('authored-skeletal', (cards/'38_dart_turret.md').read_text(encoding='utf-8'))
            # A missing hand-maintained card is still generated rather than lost.
            hand.unlink(); bestiary.write_docs(index)
            self.assertTrue(hand.exists())

    def test_profile_report_is_linked_on_generated_card(self):
        index = index_with({'MK_DART_TURRET'})
        index['creatures'][0]['art']['report'] = 'docs/example-animation.md'
        with tempfile.TemporaryDirectory() as tmp, patch.object(bestiary, 'ROOT', Path(tmp)):
            (Path(tmp)/'docs/creatures').mkdir(parents=True)
            bestiary.write_docs(index)
            card = (Path(tmp)/'docs/creatures/38_dart_turret.md').read_text(encoding='utf-8')
        self.assertIn('[Dart turret authoring and actual verification](../example-animation.md)', card)

    def test_hand_maintained_set_matches_known_refined_cards(self):
        self.assertEqual(bestiary.HAND_MAINTAINED_CARDS, {9, 10, 11, 18, 20, 21, 27, 28, 29, 35})


class PendingRegistryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); root = Path(self.tmp.name)
        self.path = root/'skeletal_profiles.json'; self.pending = root/'pending'; self.pending.mkdir()
        original = json.loads(skeletal_registry.PATH.read_text())
        self.data = {**original, 'enemies': original['enemies'][:2]}
        self.path.write_bytes((json.dumps(self.data, indent=2)+'\n').replace('\n', '\r\n').encode())
        self.row = {**original['enemies'][0], 'symbol': 'MK_TEST_PENDING', 'class': 'BrogueMonsterK99'}
        (self.pending/'MK_TEST_PENDING.json').write_text(json.dumps(self.row, indent=2))
        self.patches = [patch.object(skeletal_registry, 'PATH', self.path), patch.object(skeletal_registry, 'PENDING', self.pending)]
        for p in self.patches: p.start()

    def tearDown(self):
        for p in self.patches: p.stop()
        self.tmp.cleanup()

    def test_find_prefers_registered_then_pending(self):
        self.assertEqual(skeletal_registry.find(self.data['enemies'][0]['symbol']), self.data['enemies'][0])
        self.assertEqual(skeletal_registry.find('MK_TEST_PENDING'), self.row)
        with self.assertRaises(KeyError): skeletal_registry.find('MK_NOT_THERE')

    def test_promote_appends_with_exact_format_and_consumes_pending(self):
        skeletal_registry.promote('MK_TEST_PENDING')
        expected = {**self.data, 'enemies': self.data['enemies']+[self.row]}
        self.assertEqual(self.path.read_bytes(), (json.dumps(expected, indent=2)+'\n').replace('\n', '\r\n').encode())
        self.assertFalse((self.pending/'MK_TEST_PENDING.json').exists())

    def test_promote_rejects_duplicates(self):
        dup = {**self.data['enemies'][0]}
        (self.pending/(dup['symbol']+'.json')).write_text(json.dumps(dup))
        with self.assertRaises(ValueError): skeletal_registry.promote(dup['symbol'])

    def test_generated_outputs_ignore_pending_rows(self):
        self.assertNotIn('MK_TEST_PENDING', {r['symbol'] for r in skeletal_registry.profiles()})


class CreatureLocalSkinConfigTests(unittest.TestCase):
    def test_module_hook_overrides_shared_selector_only_for_that_creature(self):
        import sys, types
        from . import connected_skin
        fake = types.ModuleType('tools.monster_models.hooktest_animation')
        fake.CONNECTED_SKIN = lambda name: name == 'body'
        with patch.dict(sys.modules, {fake.__name__: fake}):
            self.assertTrue(connected_skin.selected('hooktest', 'body'))
            self.assertFalse(connected_skin.selected('hooktest', 'Rat_continuous_coat'))
        # Creatures without a hook keep their existing shared selection exactly.
        self.assertTrue(connected_skin.selected('ogre_shaman', 'torso'))
        self.assertFalse(connected_skin.selected('ogre_shaman', 'staff'))
        self.assertTrue(connected_skin.selected('hooktest', 'Rat_continuous_coat'))


class PipelineRuleTests(unittest.TestCase):
    def test_wall_fixture_samples_match_accepted_dart_turret_fixture(self):
        row = skeletal_registry.find('MK_DART_TURRET')
        self.assertEqual(review_wall_fixture.stages_for(row), [('idle', 0), ('loose', 12), ('jam', 35)])
        row = skeletal_registry.find('MK_FLAME_TURRET')
        self.assertEqual(review_wall_fixture.stages_for(row), [('idle', 0), ('spit', 12), ('extinguish', 35)])

    def test_owned_paths_do_not_claim_related_creatures(self):
        ogre = skeletal_registry.find('MK_OGRE')
        owned = creature_pipeline.owned_paths(ogre)
        self.assertIn('tools/monster_models/ogre_animation.py', owned)
        self.assertFalse([p for p in owned if 'ogre_shaman' in p or 'ogre_totem' in p], owned)
        self.assertFalse(owned & creature_pipeline.SHARED_INTENDED)

    def test_runtime_files_cover_model_skin_and_maps(self):
        row = skeletal_registry.find('MK_ACID_JELLY')
        files = creature_pipeline.runtime_files(row)
        for f in ('mod/BrogueDoom/models/monsters/34_acid_jelly.iqm', 'mod/BrogueDoom/graphics/BRGACJLY.png',
                  'mod/BrogueDoom/graphics/BRGACJLY_S.png', row['manifest']):
            self.assertIn(f, files)

    def test_package_check_skips_only_creatures_still_in_authoring(self):
        import zipfile
        with tempfile.TemporaryDirectory() as tmp:
            mod, pending = Path(tmp)/'mod', Path(tmp)/'pending'
            (mod/'models/monsters').mkdir(parents=True); (mod/'graphics').mkdir(); pending.mkdir()
            (mod/'graphics/BATCH.png').write_bytes(b'batch')
            (mod/'models/monsters/99_wip.iqm').write_bytes(b'new export')
            (mod/'graphics/BRGWIP.png').write_bytes(b'wip skin')
            (pending/'MK_WIP.json').write_text(json.dumps(dict(symbol='MK_WIP', module='wip_animation', model='99_wip.iqm',
                                                              skin='graphics/BRGWIP.png', manifest='assets/monsters/wip/animation.json')))
            def pk3(name, wip_bytes):
                path = Path(tmp)/name
                with zipfile.ZipFile(path, 'w') as z:
                    z.writestr('graphics/BATCH.png', b'batch'); z.writestr('graphics/BRGWIP.png', b'wip skin')
                    z.writestr('models/monsters/99_wip.iqm', wip_bytes)
                return path
            with patch.object(creature_pipeline, 'MOD', mod), patch.object(creature_pipeline, 'PENDING', pending):
                old, new = pk3('a.pk3', b'old export'), pk3('b.pk3', b'new export')
                checked = creature_pipeline.package_mismatches(old, ('MK_BATCH',))
                self.assertEqual(checked['mismatches'], [])
                self.assertEqual(checked['inProgressSkipped'], ['graphics/BRGWIP.png', 'models/monsters/99_wip.iqm'])
                # A re-export between the Vulkan and OpenGL packages must not change the compared digest.
                self.assertEqual(checked['checkedSha256'], creature_pipeline.package_mismatches(new, ('MK_BATCH',))['checkedSha256'])
                # A creature inside the checked batch is compared, and batch files still fail on drift.
                self.assertEqual(creature_pipeline.package_mismatches(old, ('MK_WIP',))['mismatches'], ['models/monsters/99_wip.iqm'])
                (mod/'graphics/BATCH.png').write_bytes(b'drifted')
                self.assertEqual(creature_pipeline.package_mismatches(old, ('MK_BATCH',))['mismatches'], ['graphics/BATCH.png'])


if __name__ == '__main__':
    unittest.main()
