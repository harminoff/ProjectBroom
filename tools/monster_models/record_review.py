"""Record evidence for the current asset hashes, not blanket art approval.

Run after the isolated before/after galleries and Blender reopen verification.
Evidence is local/ignored; verification records remain in the source index.
"""
import hashlib
import json
import re
import zipfile
import argparse

from .bestiary import ROOT, INDEX, write_docs
from .review import EVIDENCE


def record(include_kobold_encounter=False):
    index = json.loads(INDEX.read_text(encoding='utf-8'))
    for phase in ('runtime-before', 'runtime-after'):
        log = (EVIDENCE / f'{phase}.log').read_text(errors='replace')
        events = re.findall(r'CREATURE_GALLERY kind=(\d+) actor=BrogueMonsterK(\d+)|Captured (\d+)\.png', log)
        expected = []
        for kind in range(1, 68):
            expected.extend([(str(kind), f'{kind:02d}', ''), ('', '', f'{kind:02d}')])
            assert (EVIDENCE / phase / f'{kind:02d}.png').stat().st_size > 1000
        assert events == expected, f'{phase}: missing or out-of-order capture'
    reopened = {e['kind']: e for e in json.loads((EVIDENCE / 'blender-reopen-verification.json').read_text())}
    assert set(reopened) == set(range(2, 68))
    package = EVIDENCE / 'ProjectBroom-creatures.pk3'
    with zipfile.ZipFile(package) as archive:
        for item in index['creatures'][1:]:
            kind, art = item['kind'], item['art']
            obj = ROOT / art['runtimeModel']
            skin = ROOT / ('mod/BrogueDoom/graphics/BRGRAT.png' if kind == 1 else f'mod/BrogueDoom/graphics/BRGM{kind:02d}.png')
            hashes = {'objSha256': hashlib.sha256(obj.read_bytes()).hexdigest(),
                      'skinSha256': hashlib.sha256(skin.read_bytes()).hexdigest()}
            for path in (obj, skin):
                member = path.relative_to(ROOT / 'mod/BrogueDoom').as_posix()
                assert archive.read(member) == path.read_bytes(), member
            if kind > 1:
                assert all(art[key] == value for key, value in hashes.items())
                assert reopened[kind]['boundsVerified'] and reopened[kind]['packedImages'] == 1
            verification = dict(item.get('verification', {}))
            verification.update({
                'stale': False, **hashes,
                'engineGallery': {'status': 'captured-and-reviewed-contact-sheet',
                    'before': f'artifacts/creature-models/runtime-before/{kind:02d}.png',
                    'after': f'artifacts/creature-models/runtime-after/{kind:02d}.png',
                    'scope': 'isolated ART01; fixed 64-unit grid and 58-unit reference; not an encounter'},
                'packagedBytesMatchSource': True,
                'individualArtApproval': 'pending',
                'skeletalAnimation': ('see-rat-animation-manifest' if art.get('format')=='IQM v2'
                                      else 'not-authored-static-pose'),
            })
            if kind > 1:
                verification['blenderSourceReopen'] = reopened[kind]
            item['verification'] = verification
    if include_kobold_encounter:
        # Opt in only after visually inspecting the screenshot. A visible
        # bridge flag alone is not proof the model is unobscured on screen.
        log = (EVIDENCE / 'normal.log').read_text(errors='replace')
        assert 'turn=38 revision=39 player=12,22' in log
        assert 'id=10 kind=2 presentation=2 cell=13,23 hp=7/7 visibility=2' in log
        assert 'Captured normal-visible-kobold.png' in log
        assert (EVIDENCE / 'normal-visible-kobold.png').stat().st_size > 1000
        index['creatures'][2]['verification']['naturalEncounter'] = {
            'status': 'captured-and-visually-reviewed', 'seed': 1, 'depth': 1,
            'turn': 38, 'playerCell': [12, 22], 'creatureCell': [13, 23],
            'capture': 'artifacts/creature-models/normal-visible-kobold.png',
            'scope': 'real player eye; diagnostic camera hides player reference model only; no omniscience or moved creatures'}
    INDEX.write_text(json.dumps(index, indent=2) + '\n', encoding='utf-8')
    write_docs(index)
    summary = {'galleryPairs': 67, 'newBlenderSourcesReopened': len(reopened),
               'packageSha256': hashlib.sha256(package.read_bytes()).hexdigest(),
               'newTriangles': sum(e['art']['triangles'] for e in index['creatures'][2:]),
               'maxTriangles': max(e['art']['triangles'] for e in index['creatures'][2:])}
    (EVIDENCE / 'review-verification.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--include-kobold-encounter', action='store_true',
                        help='Record the fixed-seed encounter after its screenshot is visually inspected')
    record(parser.parse_args().include_kobold_encounter)
