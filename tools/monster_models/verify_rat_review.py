"""Audit rat runtime evidence and compare every encounter turn to Brogue.

Requires completed gallery/before/normal captures and Blender verification.
Run only after visually inspecting the corresponding images.
"""
import hashlib
import json
import re
import subprocess
import zipfile
from .rat_animation import ROOT
from .bestiary import INDEX, write_docs

OUT=ROOT/'artifacts/rat-animation'


def verify():
    manifest=json.loads((ROOT/'assets/monsters/rat/animation.json').read_text())
    model=(ROOT/manifest['runtimeModel']).read_bytes()
    assert hashlib.sha256(model).hexdigest()==manifest['sha256']
    package=OUT/'ProjectBroom-rat-animated.pk3'
    with zipfile.ZipFile(package) as archive:
        assert archive.read('models/monsters/01_rat.iqm')==model
        assert not any(n.endswith('.blend') for n in archive.namelist())
    source=json.loads((OUT/'blender-verification.json').read_text())
    assert source['freshReopen'] and source['bones']==28 and len(source['sampledPoseChecks'])==18
    for phase in ('gallery','before'):
        log=(OUT/f'{phase}.log').read_text(errors='replace')
        assert 'Script error' not in log and 'Could not find animation' not in log
        events=re.findall(r'RAT_GALLERY shot=(\d+)[^\n]*|Captured (\d+)\.png',log)
        expected=[]
        for i in range(22):
            expected.extend([(f'{i:02d}',''),('',f'{i:02d}')])
            assert (OUT/phase/f'{i:02d}.png').stat().st_size>1000
            if phase=='gallery':
                assert (OUT/phase/f'{i:02d}.png').stat().st_mtime >= (ROOT/manifest['runtimeModel']).stat().st_mtime
        assert events==expected,phase
    log=(OUT/'normal.log').read_text(errors='replace')
    assert 'Script error' not in log and 'Could not find animation' not in log
    for clip in ('scurry','bite','scratch','recoil','death'):
        assert f'id=11 clip={clip} ' in log,clip
    travels=re.findall(r'Brogue rat travel: id=(\d+) distance=([\d.]+) tics=(\d+) rate=([\d.]+)',log)
    assert any(distance=='64.00' and tics=='28' and rate=='40.00'
               for entity,distance,tics,rate in travels),'Missing readable cardinal rat walk'
    assert any(entity=='11' and distance=='90.51' and tics=='40'
               for entity,distance,tics,rate in travels),'Missing captured diagonal rat walk'
    for entity,distance,tics,rate in travels:
        distance=float(distance); tics=int(tics); rate=float(rate)
        assert 0 < distance <= 90.52
        assert abs(tics-28*distance/64) < 1.01
        assert abs(rate-16*35/tics*2*distance/64) < .02
    arrivals=re.findall(r'Brogue rat arrived: id=(\d+) elapsed=(\d+) expected=(\d+)',log)
    assert len(arrivals)==len(travels),'Not every visible rat step finished'
    assert all(elapsed==expected for entity,elapsed,expected in arrivals),arrivals
    assert re.findall(r'Captured (\d+)\.png',log)==[f'{i:02d}' for i in range(55)]
    assert all((OUT/'normal'/f'{i:02d}.png').stat().st_mtime >= (ROOT/manifest['runtimeModel']).stat().st_mtime for i in range(55))
    route=['N']*3+['W']*25+['N','W','WAIT','WAIT','W','W','W','W']
    cmd=[str(ROOT/'src/brogue-mapgen/bin/brogue-bridge.exe'),'--seed','1','--actions',','.join(route)]
    first=subprocess.check_output(cmd,cwd=ROOT/'src/brogue-mapgen',text=True)
    second=subprocess.check_output(cmd,cwd=ROOT/'src/brogue-mapgen',text=True)
    assert first==second,'Repeated Brogue sequence differed'
    (OUT/'headless-encounter.log').write_text(first)
    engine=re.findall(r'Brogue command=[^\n]*?turn=(\d+) revision=(\d+) player=(\d+,\d+) hash=([a-f0-9]+)',log)
    # STATE lines include full normalized authoritative hashes; parse fields
    # rather than treating captured frames as parity evidence.
    states=[]
    for line in first.splitlines():
        if line.startswith('STATE '):
            fields=dict(re.findall(r'(\w+)=([^ ]+)',line))
            states.append(fields)
    assert len(engine)==len(route)==len(states),(len(engine),len(states))
    comparisons=[]
    for native,headless in zip(engine,states):
        turn,revision,player,digest=native
        assert digest==headless['hash'],(native,headless)
        assert (turn,revision,player)==(headless['turn'],headless['revision'],headless['player'])
        comparisons.append({'turn':int(turn),'hash':digest})
    result={'assetSha256':manifest['sha256'],'packageSha256':hashlib.sha256(package.read_bytes()).hexdigest(),
            'galleryCaptures':22,'beforeCaptures':22,'normalCaptures':55,
            'normalEncounter':{'seed':1,'actions':route,'matchedTurns':len(comparisons),'finalHash':engine[-1][3],
                               'repeatByteIdentical':True,'ratEntityId':11,'clipsObserved':['scurry','bite','scratch','recoil','death']},
            'blenderFreshReopen':True,'reviewScope':'sampled poses, four-angle gallery and seed-one normal encounter',
            'ratWalk':{'cardinalTics':28,'cardinalSeconds':.8,'cyclesPerTile':2,'travelSamples':len(travels),
                       'arrivalEngineTicsVerified':len(arrivals)},
            'userArtApproval':'pending','tests':'see unittest output and rat-animation-work.md'}
    (OUT/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    manifest['verification']=result
    (ROOT/'assets/monsters/rat/animation.json').write_text(json.dumps(manifest,indent=2)+'\n')
    index=json.loads(INDEX.read_text())
    index['creatures'][1]['verification']={'stale':False,'modelSha256':manifest['sha256'],
        'skeletalAnimation':'six-clips-verified','naturalEncounter':result['normalEncounter'],
        'blenderSourceReopen':source['source'],'individualArtApproval':'pending-user-review',
        'report':'docs/rat-animation-work.md','localEvidence':'artifacts/rat-animation/verification.json'}
    INDEX.write_text(json.dumps(index,indent=2)+'\n'); write_docs(index)
    print(json.dumps(result,indent=2))


if __name__=='__main__': verify()
