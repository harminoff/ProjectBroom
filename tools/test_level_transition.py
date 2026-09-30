"""Queued natural depth-transition lifetime regression.

Run the native seed-26 route on either renderer, or audit an existing capture:
python -m tools.test_level_transition --backend 1 --package PATH --output DIR
python -m tools.test_level_transition --check DIR
"""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from zipfile import ZipFile
from tools.monster_models.review_campaign import missing_depth_mapinfo


def transition_barriers(text):
    """No command or proxy attachment may occur between request and map load."""
    pending = None
    transitions = []
    for line in text.splitlines():
        match = re.search(r'authoritative level change to (BRG\d+)\.', line)
        if match:
            assert pending is None, 'Nested level request before engine map load'
            pending = match[1]
            transitions.append(pending)
        elif pending and line.startswith(pending + ' - '):
            pending = None
        elif pending:
            assert not any(marker in line for marker in (
                'Brogue command=', 'Brogue monsters: synced',
                'Brogue pickups: synced', 'Brogue presentation: attached',
            )), 'Destination work before engine map load: ' + line
    assert pending is None, 'Engine never loaded ' + str(pending)
    return transitions


def verify(output):
    text = (output / 'runtime.log').read_text(errors='replace')
    route = (output / 'bridge-route.log').read_text().splitlines()[-1].split()
    transitions = transition_barriers(text)
    assert transitions == ['BRG02', 'BRG03', 'BRG04', 'BRG05'], transitions
    names = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'WAIT']
    commands = re.findall(r'Brogue command=0 action=(\d+) item=0 source=brg_actions .*?hash=([0-9a-f]+)', text)
    assert [names[int(action)] for action, _ in commands] == route + ['WAIT', 'WAIT'], 'Lost, reordered or extra intents'
    assert commands[len(route)-1][1] == '2dcb11e9c4d62ec5'
    result = dict(transitions=transitions, routeIntents=len(route),
                  encounterHash=commands[len(route)-1][1], queuePreserved=True,
                  noCommandsOrProxiesBeforeMapLoad=True)
    (output / 'transition-verification.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


class TransitionLogTests(unittest.TestCase):
    def test_review_metadata_extends_without_replacing_existing_depths(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'campaign.pk3'
            with ZipFile(path, 'w') as archive:
                archive.writestr('MAPINFO', 'map BRG01 "Existing" { levelnum=1 }')
            before = path.read_bytes()
            overlay = missing_depth_mapinfo(path, 5)
            self.assertNotIn('BRG01', overlay)
            self.assertEqual(re.findall(r'levelnum=(\d+)', overlay), ['2', '3', '4', '5'])
            self.assertEqual(path.read_bytes(), before)
            self.assertEqual(missing_depth_mapinfo(path, 1), '')

    def test_review_metadata_rejects_non_brogue_depth(self):
        for depth in (0, 41):
            with self.assertRaises(ValueError):
                missing_depth_mapinfo(None, depth)

    def test_detects_original_queue_race(self):
        with self.assertRaisesRegex(AssertionError, 'Destination work'):
            transition_barriers('Brogue bridge: authoritative level change to BRG02.\n'
                                'Brogue command=0 action=6\nBRG02 - Depth 2')

    def test_detects_proxy_repopulation_without_command(self):
        with self.assertRaisesRegex(AssertionError, 'Destination work'):
            transition_barriers('Brogue bridge: authoritative level change to BRG02.\n'
                                'Brogue monsters: synced 7 live entities\nBRG02 - Depth 2')

    def test_accepts_delayed_map_then_command(self):
        self.assertEqual(transition_barriers(
            'Brogue bridge: authoritative level change to BRG02.\n'
            'loading\nBRG02 - Depth 2\nBrogue command=0 action=6'), ['BRG02'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', type=Path)
    parser.add_argument('--backend', choices=('0', '1'))
    parser.add_argument('--package', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.check:
        print(verify(args.check))
    else:
        if args.backend is None or not args.package or not args.output:
            parser.error('--backend, --package and --output are required for a native replay')
        subprocess.run([sys.executable, '-m', 'tools.monster_models.review_goblin_totem',
                        '--backend', args.backend, '--package', str(args.package),
                        '--output', str(args.output)], check=True)
        print(verify(args.output))
