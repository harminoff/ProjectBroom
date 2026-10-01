"""Compare every pinned Brogue terrain description with its presentation binding."""
import argparse
import json
from pathlib import Path
import re
from tools.terrain_presentation import ROOT, load, symbols


def catalog():
    text=(ROOT/'src/brogue-mapgen/src/brogue/Globals.c').read_text().split('const floorTileType tileCatalog')[1].split('};')[0]
    records={}
    for match in re.finditer(r'/\*\s*(\w+),?\s*\*/\s*\{([^\n]+)',text):
        strings=re.findall(r'"([^"\n]*)"',match[2])
        if strings: records[match[1]]={'description':strings[0], 'secret':'TM_IS_SECRET' in match[2]}
    if set(records)!=set(symbols()): raise ValueError('Catalog parser must cover every pinned tile')
    return records


def report(before):
    current=load(); descriptions=catalog(); changed=[]; lines=[]
    for symbol,record in descriptions.items():
        old=before[symbol]; new=current[symbol]
        edits=[f'{key}: {old[key] or "none"} → {new[key] or "none"}' for key in ('floor','wall','actor') if old[key]!=new[key]]
        if edits: changed.append(symbol)
        status='Corrected' if edits else 'Intentional disguise' if record['secret'] else 'Existing presentation'
        if symbol in ('BRIDGE','BRIDGE_EDGE','BRIDGE_FALLING'): edits.append('flush-ground texture corrected; rope side supports added')
        if symbol=='CHASM_WITH_HIDDEN_BRIDGE_ACTIVE': edits.append('visible identity now projects as STONE_BRIDGE, not CHASM')
        lines.append(f'| `{symbol}` | {record["description"] or "(no description)"} | {status} | {"; ".join(edits) if edits else new["floor"]+"; "+(new["actor"] or "shared renderer / base geometry")} |')
    return ('# Terrain description audit\n\n'
        f'All {len(current)} pinned tile identities reviewed; {len(changed)} bindings corrected. '
        'Brogue descriptions and gameplay are unchanged.\n\n'
        'The registry is not the whole renderer: stairs use map geometry; fire, gas, liquids, '
        'doors, wall light, and discovery have dedicated paths. Blank actor fields alone '
        'are not evidence of missing presentation. Secret forms retain Brogue disguises.\n\n'
        'The rope bridge defect also involved a flush primary floor hiding the deck material. '
        'Both settled and shoreline refresh now retain the deck material there. Stone bridges '
        'use masonry; the active extending bridge is visible stone and its dormant form stays a chasm.\n\n'
        'New surfaces and low-poly props are original CC0 assets. These establish the described '
        'material and silhouette; they are not claims of bespoke animation for every transient '
        'catalog phase. Colored light patches are surface treatments, not new lights. '
        'Known liquids keep their existing water/lava shaders and effects.\n\n'
        '| Tile | Exact Brogue description | Audit result | Presentation / correction |\n'
        '|---|---|---|---|\n'+'\n'.join(lines)+'\n')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--before',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    args.output.write_text(report(json.loads(args.before.read_text())),encoding='utf-8')
