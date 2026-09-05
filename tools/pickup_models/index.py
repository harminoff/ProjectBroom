"""Source-backed pickup work index. No inferred physical dimensions are rules."""
import json
import re
from .generate import ROOT, REGISTRY_PATH
from tools.monster_models.bestiary import c_records


def source_facts():
    result={}
    for symbol in ('FOOD','WEAPON','ARMOR','POTION','SCROLL','STAFF','WAND','RING','CHARM','KEY'):
        variant=symbol in ('POTION','SCROLL','WAND','CHARM')
        path='src/brogue-mapgen/src/'+('variants/GlobalsBrogue.c' if variant else 'brogue/Globals.c')
        text=(ROOT/path).read_text()
        declaration=f'itemTable {symbol.lower()}Table'+('_Brogue' if variant else '')+'['
        for kind,(row,line) in enumerate(c_records(text,declaration)):
            strings=[json.loads(s) for s in re.findall(r'"(?:\\.|[^"\\])*"',row)]
            result[(symbol,kind)]={'name':strings[0],'description':strings[-1],'source':path,'line':line}
    return result


def main():
    registry=json.loads(REGISTRY_PATH.read_text());facts=source_facts()
    records=[]
    for i,m in enumerate(registry['models']):
        fact=facts.get((m['categorySymbol'],m['kind']))
        if fact: assert fact['name']==m['name'],(fact,m)
        records.append({'workId':f'BRG-P{i:03d}',**m,'brogue':fact,
                        'authoringScene':m['class'],'authoringSource':registry['authoringSource'],
                        'status':'authored-static','userArtApproval':'pending'})
    (ROOT/'assets/items/pickup-model-index.json').write_text(json.dumps({'schemaVersion':1,'models':records},indent=2)+'\n')
    lines=['# Pickup model index','',
           '100 Brogue item kinds plus five identity-safe generic forms. All dimensions',
           'are artistic map-unit choices, not Brogue measurements. A cell is 64 units.',
           'Models rest 0.12 units above their origin; no actor collision sizes change.','',
           'The editable source is [pickups.blend](../assets/items/pickups.blend): choose',
           'the scene matching the runtime class and export only its ASSET collection.',
           'The shared stage is preview-only. Python definitions remain the reproducible',
           'master; reconcile hand edits before regenerating.','',
           'See [verification and scope](pickup-model-refresh.md) and the',
           '[machine-readable index with exact Brogue prose](../assets/items/pickup-model-index.json).','',
           '| ID | Category / name | Dimensions X/Y/Z | Triangles | Brogue source |',
           '| --- | --- | --- | --- | --- |']
    for m in records:
        f=m['brogue'];source=f'[catalog](../{f["source"]}#L{f["line"]})' if f else ('category-generic' if m['kind'] is None else 'catalog category')
        lines.append(f'| {m["workId"]} | [{m["categorySymbol"]} / {m["name"]}](../mod/BrogueDoom/models/pickups/{m["model"]}) | '+
                     ' / '.join(str(v) for v in m['dimensions'])+f' | {m["triangles"]} | {source} |')
    (ROOT/'docs/pickup-model-index.md').write_text('\n'.join(lines)+'\n')
    print('Indexed 105 models; exact Brogue prose for 97 catalog items')


if __name__=='__main__': main()
