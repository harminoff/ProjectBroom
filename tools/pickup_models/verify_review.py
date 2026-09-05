"""Record completed pickup review after inspecting the captured images."""
import hashlib
import json
import re
import subprocess
import sys
import zipfile
from .generate import ROOT, REGISTRY_PATH, MODEL_DIR

OUT=ROOT/'artifacts/pickup-models'


def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def verify():
    registry=json.loads(REGISTRY_PATH.read_text());models=registry['models']
    assert len(models)==105 and registry['itemKindCount']==100
    for m in models:
        assert digest(MODEL_DIR/m['model'])==m['sha256']
        assert (MODEL_DIR/m['model']).read_bytes()!=(OUT/'baseline/pickups'/m['model']).read_bytes()
    for phase in ('before','after'):
        log=(OUT/f'{phase}-stdout.log').read_text(errors='replace')
        assert not re.search(r'Script error|PICKUP_GALLERY MISSING|Could not find|Unknown texture',log)
        actual=re.findall(r'PICKUP_GALLERY index=(\d+) class=(\w+)|Captured (\d+)\.png',log)
        expected=[]
        for i,m in enumerate(models):
            expected.extend([(str(i),m['class'],''),('','',f'{i:03d}')])
            assert (OUT/phase/f'{i:03d}.png').stat().st_size>1000
        assert actual==expected,phase
    source=json.loads((OUT/'blender-verification.json').read_text())
    assert source['freshReopen'] and source['scenes']==105 and source['packedImages']==1
    with zipfile.ZipFile(OUT/'ProjectBroom-pickups.pk3') as archive:
        for m in models: assert archive.read('models/pickups/'+m['model'])==(MODEL_DIR/m['model']).read_bytes()
        assert archive.read('graphics/BRGPICKS.png')==(ROOT/registry['atlas']).read_bytes()
        assert not any(n.endswith(('.blend','.blend1')) for n in archive.namelist())
    # Generic and known bindings are intentionally unchanged, apart from skin.
    old=(OUT/'baseline/pickups/MODELDEF.txt').read_text().replace('BRGITEMS.png','BRGPICKS.png')
    assert old==(MODEL_DIR/'MODELDEF.txt').read_text()
    assert digest(OUT/'baseline/BRGITEMS.png')==digest(ROOT/'mod/BrogueDoom/graphics/BRGITEMS.png')
    route=['E']*9
    command=[str(ROOT/'src/brogue-mapgen/bin/brogue-bridge.exe'),'--seed','1','--actions',','.join(route)]
    headless=subprocess.check_output(command,cwd=ROOT/'src/brogue-mapgen',text=True)
    assert headless==subprocess.check_output(command,cwd=ROOT/'src/brogue-mapgen',text=True)
    states=[]
    for line in headless.splitlines():
        if line.startswith('STATE '):
            fields=dict(re.findall(r'(\w+)=([^ ]+)',line))
            states.append(tuple(fields[k] for k in ('turn','revision','player','hash')))
    native=[]
    for phase in ('normal-before','normal-after'):
        log=(OUT/f'{phase}-stdout.log').read_text(errors='replace')
        assert not re.search(r'Script error|Could not find|Unknown texture',log)
        turns=re.findall(r'Brogue command=[^\n]*?turn=(\d+) revision=(\d+) player=(\d+,\d+) hash=([a-f0-9]+)',log)
        assert turns==states and len(turns)==9
        # The sword is a real seed-one floor item, not a spawned test proxy.
        assert log.count('id=16 category=2 kind=1 cell=47,26 visible=true class=BroguePickupC0002K01')==1
        assert 'Brogue pickups: synced 13 floor items' in log
        assert 'Captured start.png' in log and 'Captured end.png' in log
        for name in ('start','end'): assert (OUT/phase/f'{name}.png').stat().st_size>1000
        native.append(turns)
    assert native[0]==native[1]
    (OUT/'headless-pickup.log').write_text(headless)
    paths=[*sorted(MODEL_DIR.glob('*.obj')),MODEL_DIR/'MODELDEF.txt',ROOT/registry['atlas']]
    baseline={str(path):digest(path) for path in paths}
    subprocess.check_call([sys.executable,'-m','tools.pickup_models.generate'],cwd=ROOT)
    assert baseline=={str(path):digest(path) for path in paths}
    result={'modelCount':105,'itemKindCount':100,'changedModels':105,'galleryBefore':105,'galleryAfter':105,
            'blenderFreshReopen':True,'blenderScenes':105,'deterministicRuntimeRegeneration':True,
            'packageSha256':digest(OUT/'ProjectBroom-pickups.pk3'),'skinSha256':digest(ROOT/registry['atlas']),
            'normalSeed':1,'normalActions':route,'matchedTurns':9,'finalHash':states[-1][-1],
            'pickupEntityId':16,'floorItemCountAfterPickup':13,'userArtApproval':'pending',
            'models':{m['class']:m['sha256'] for m in models}}
    (ROOT/'assets/items/pickup-verification.json').write_text(json.dumps(result,indent=2)+'\n')
    (OUT/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='models'},indent=2))


if __name__=='__main__': verify()
