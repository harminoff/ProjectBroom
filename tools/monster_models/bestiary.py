"""Source-backed, stable-ID creature work index and explicit presentation scale.

Never modifies Brogue catalogs. Exact upstream prose stays separate from art
direction. Dimensions are authored map units, NOT authoritative body sizes.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'src/brogue-mapgen/src/brogue/Globals.c'
CATALOG = ROOT / 'assets/monsters/brogue_monster_catalog.json'
HORDES = ROOT / 'src/brogue-mapgen/src/variants/GlobalsBrogue.c'
INDEX = ROOT / 'assets/monsters/bestiary-index.json'

# symbol | construction recipe | X length,Y width,Z height | art direction
# Dimensions include appendages; flying clearance is stored separately.
PROFILES = '''
KOBOLD|humanoid|28,24,38|lizard,club,scales
JACKAL|quadruped|52,22,32|canine,jaws,fur
EEL|serpent|54,22,9|eel,fins,scales
MONKEY|humanoid|40,27,32|primate,tail,fur
BLOAT|bloat|28,28,32|membrane,veins
PIT_BLOAT|bloat|28,28,32|membrane,veins,pit
GOBLIN|humanoid|34,29,40|primate,spear,fur
GOBLIN_CONJURER|humanoid|24,32,40|primate,sigils,fur
GOBLIN_MYSTIC|humanoid|24,32,40|primate,golden_eyes,fur
GOBLIN_TOTEM|totem|24,26,46|wood,bone,shaman
PINK_JELLY|slime|50,46,30|goo,lobes
TOAD|toad|38,35,25|warts,slime
VAMPIRE_BAT|winged|24,58,28|bat,membrane,fangs
ARROW_TURRET|turret|30,32,38|mechanism,crossbow
ACID_MOUND|slime|34,32,20|goo,acid
CENTIPEDE|centipede|56,35,13|segments,incisors,chitin
OGRE|humanoid|44,46,82|brute,club,skin
BOG_MONSTER|tentacles|58,58,42|pale,tentacles,mud
OGRE_TOTEM|totem|32,32,60|wood,bone,occult
SPIDER|spider|52,58,24|eight_legs,red_eyes,chitin
SPARK_TURRET|turret|30,32,42|mechanism,crystals,sigils
WILL_O_THE_WISP|flame|20,20,30|blue,flame
WRAITH|humanoid|30,32,65|gaunt,sockets,blood_nails
ZOMBIE|humanoid|32,36,62|undead,ribs,torn_flesh
TROLL|humanoid|46,50,86|brute,warts,misshapen
OGRE_SHAMAN|humanoid|42,44,70|brute,hunched,staff,relics
NAGA|serpent|50,48,68|naga,claws,scales
SALAMANDER|serpent|54,50,70|naga,lash,flame,scales
EXPLOSIVE_BLOAT|bloat|30,30,34|membrane,veins,explosive
DAR_BLADEMASTER|humanoid|36,34,57|elf,sword,armor
DAR_PRIESTESS|humanoid|28,32,57|elf,relics,robe
DAR_BATTLEMAGE|humanoid|28,34,57|elf,ember_eyes,hot_hands,robe
ACID_JELLY|slime|52,48,32|goo,acid,lobes
CENTAUR|centaur|58,42,78|horse,bow,quiver
UNDERWORM|worm|60,58,94|coil,segments,maw
SENTINEL|humanoid|32,32,58|stone,raised_crystal,faceless
DART_TURRET|turret|28,30,35|mechanism,darts
KRAKEN|tentacles|60,60,66|mantle,tentacles,suckers
LICH|humanoid|30,36,66|undead,robe,phylactery,ribs
PHYLACTERY|gem|18,18,22|gem,setting
PIXIE|winged|18,34,20|fairy,membrane
PHANTOM|specter|32,38,66|ectoplasm,ragged
FLAME_TURRET|turret|32,34,42|mechanism,nozzle,flame
IMP|humanoid|30,30,35|demon,tail,claws
FURY|winged|30,58,40|demon,membrane,claws
REVENANT|specter|34,40,70|specter,hood
TENTACLE_HORROR|tentacles|60,60,106|tower,tentacles,suckers
GOLEM|humanoid|40,48,88|stone,plates,cracks
DRAGON|dragon|62,58,100|serpent,scales,jaws,claws
GOBLIN_CHIEFTAN|humanoid|38,36,51|primate,spear,crest,fur
BLACK_JELLY|slime|54,50,34|goo,black,lobes
VAMPIRE|humanoid|32,40,64|cloak,fangs,pale
FLAMEDANCER|flame|40,46,80|humanoid,white_hot
SPECTRAL_BLADE|blade|12,10,34|spectral,sword
SPECTRAL_IMAGE|blade|16,12,42|spectral,sword,echo
GUARDIAN|humanoid|38,38,64|stone,knight,axe
WINGED_GUARDIAN|humanoid|32,60,66|stone,angel,sword,wings
CHARM_GUARDIAN|humanoid|38,38,64|spectral,knight,axe
WARDEN_OF_YENDOR|humanoid|44,48,92|warden,armor,faceless
ELDRITCH_TOTEM|totem|30,30,56|stone,occult,sigils
MIRRORED_TOTEM|prism|24,24,46|mirror,prism
UNICORN|quadruped|60,30,70|horse,horn,rainbow
IFRIT|humanoid|42,50,70|storm,twin_scimitars,ember_eyes
PHOENIX|winged|42,62,64|bird,feathers,embers
PHOENIX_EGG|egg|26,26,25|egg,ash,yolk
ANCIENT_SPIRIT|dryad|48,58,84|bark,roots,branches
'''.strip()


def profiles():
    result = {}
    for line in PROFILES.splitlines():
        symbol, recipe, dimensions, traits = line.split('|')
        result['MK_' + symbol] = dict(recipe=recipe, dimensions=list(map(float, dimensions.split(','))),
                                     traits=traits.split(','))
    return result


def c_records(text, declaration):
    """Top-level C initializer records, ignoring braces in strings/comments."""
    start = text.index('{', text.index(declaration))
    token = re.compile(r'"(?:\\.|[^"\\])*"|//[^\n]*|/\*[\s\S]*?\*/|[{}]')
    depth, begin = 0, None
    for match in token.finditer(text, start):
        value = match.group()
        if value == '{':
            depth += 1
            if depth == 2:
                begin = match.start()
        elif value == '}':
            if depth == 2:
                yield text[begin:match.end()], text.count('\n', 0, begin)+1
            depth -= 1
            if depth == 0:
                return
    raise ValueError('Unterminated C initializer: ' + declaration)


def source_records():
    text = SOURCE.read_text(encoding='utf-8')
    words = list(c_records(text, 'const monsterWords monsterText['))
    catalog_rows = list(c_records(text, 'creatureType monsterCatalog['))
    catalog = json.loads(CATALOG.read_text(encoding='utf-8'))['kinds']
    if len(words) != len(catalog) or len(catalog_rows) != len(catalog):
        raise ValueError('Brogue prose/catalog count changed; review stable-ID mapping')
    entries = []
    for kind, (prose, prose_line), (row, catalog_line) in zip(catalog, words, catalog_rows):
        strings = re.findall(r'"(?:\\.|[^"\\])*"', prose)
        # JSON decoding covers the escape syntax used by the pinned prose.
        strings = [json.loads(s) for s in strings]
        source_name = json.loads(re.search(r'"(?:\\.|[^"\\])*"', row).group())
        if source_name != kind['name']:
            raise ValueError(f"Catalog name mismatch at {kind['kind']}: {source_name}")
        entries.append({**kind, 'description': strings[0], 'sourceTextStrings': strings,
                        'catalogTokens': sorted(set(re.findall(r'\b(?:MONST_|MA_|BOLT_|DF_)[A-Z0-9_]+', row))),
                        'source': {'path': str(SOURCE.relative_to(ROOT)).replace('\\','/'),
                                   'catalogLine': catalog_line, 'descriptionLine': prose_line}})
    return entries


def horde_references():
    """Copy nominal table ranges and roles, not a replacement spawn algorithm."""
    text=HORDES.read_text(encoding='utf-8')
    references={}
    for row,line in c_records(text,'const hordeType hordeCatalog_Brogue['):
        row=re.sub(r'//[^\n]*|/\*[\s\S]*?\*/','',row)
        fields=[]; start=1; depth=0
        for i,char in enumerate(row[1:-1],1):
            if char in '{(': depth+=1
            elif char in '})': depth-=1
            elif char==',' and depth==0:
                fields.append(row[start:i].strip()); start=i+1
        fields.append(row[start:-1].strip())
        if len(fields)<7: raise ValueError('Unexpected horde layout')
        members=re.findall(r'MK_[A-Z0-9_]+',fields[2])
        for symbol in sorted(set([fields[0]]+members)):
            roles=[]
            if symbol==fields[0]: roles.append('leader/summoner')
            if symbol in members: roles.append('member')
            references.setdefault(symbol,[]).append({'line':line,'roles':roles,'leader':fields[0],
                'minLevelExpression':fields[4],'maxLevelExpression':fields[5],
                'frequencyWeightExpression':fields[6], 'terrain':fields[7] if len(fields)>7 else '0',
                'machine':fields[8] if len(fields)>8 else '0','flags':fields[9] if len(fields)>9 else '0'})
    return references


def write_index(metrics=None):
    plans = profiles()
    records = source_records()
    hordes = horde_references()
    if set(plans) != {r['symbol'] for r in records if r['kind'] > 1}:
        raise ValueError('Art profiles must cover exactly the 66 remaining non-player kinds')
    existing = {}
    previous_art = {}
    if INDEX.exists():
        existing = {e['symbol']: e.get('verification', {}) for e in json.loads(INDEX.read_text())['creatures']}
        previous_art = {e['symbol']: e['art'] for e in json.loads(INDEX.read_text())['creatures']}
    from .skeletal_registry import profiles as skeletal_profiles
    skeletons={row['symbol']:row for row in skeletal_profiles()}
    creatures = []
    for record in records:
        k, symbol = record['kind'], record['symbol']
        slug = symbol.removeprefix('MK_').lower()
        plan = plans.get(symbol, {})
        status = 'reference-only' if k == 0 else 'rat-proof-of-concept' if k == 1 else 'authored-static'
        metric = (metrics or {}).get(symbol, {key:value for key,value in previous_art.get(symbol,{}).items()
                                            if key in ('triangles','parts','bounds','objSha256','skinSha256')})
        skeletal_art={}
        if symbol in skeletons:
            row=skeletons[symbol]
            animated=json.loads((ROOT/row['manifest']).read_text())
            status='authored-skeletal'
            skeletal_art={'runtimeModel':animated['runtimeModel'],'sourceBlend':animated['authoringSource'],
                          'format':animated['format'],'boneCount':animated['boneCount'],
                          'animationManifest':row['manifest'],
                          'staticReference':f'mod/BrogueDoom/models/monsters/{k:02d}_{slug}.obj',
                          'dimensions':animated.get('dimensions',[51.12,18.44,15]),
                          'recipe':'weighted-'+slug}
            if k==1:
                skeletal_art['traits']=['gray scavenger','articulated jaw','four-paw scurry','ear twitch','segmented tail']
            metric={'modelSha256':animated['sha256'],'skinSha256':animated['skinSha256'],
                    'triangles':animated['triangles'],'parts':animated['parts']}
        verification=existing.get(symbol,{})
        if verification and any(previous_art.get(symbol,{}).get(key)!=metric.get(key)
                                for key in ('objSha256','modelSha256','skinSha256')):
            verification={'stale':True,'previousAssetVerification':verification}
        creatures.append({**record, 'hordeReferences':hordes.get(symbol,[]), 'indexId': f'BRG-M{k:02d}', 'role': 'player-reference' if k==0 else
                          'legendary-ally-or-associated-form' if k>=63 else 'creature-or-construct',
                          'art': {**plan, 'status': status, 'scaleAuthority': 'artistic inference; not Brogue physical dimensions',
                                  'units': 'one Blender unit = one GZDoom map unit; cell = 64',
                                  'clearance': 16 if 'MONST_FLIES' in record['catalogTokens'] else 0,
                                  'runtimeModel': f'mod/BrogueDoom/models/monsters/{k:02d}_{slug}.obj',
                                  'sourceBlend': 'assets/monsters/rat/rat.blend' if k==1 else
                                  f'assets/monsters/sources/{k:02d}_{slug}.blend' if k>1 else None,
                                  **metric, **skeletal_art}, 'verification': verification})
    INDEX.parent.mkdir(parents=True, exist_ok=True)
    result = {'schemaVersion': 1, 'sourceSha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              'hordeSource':str(HORDES.relative_to(ROOT)).replace('\\','/'),
              'hordeSourceSha256':hashlib.sha256(HORDES.read_bytes()).hexdigest(),
              'catalogCount': len(creatures), 'nonPlayerCount': len(creatures)-1,
              'scalePolicy': 'Explicit silhouette dimensions, never HP-derived; no collision changes. IsLarge is a Brogue flag, not a metric measurement.',
              'creatures': creatures}
    INDEX.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    write_docs(result)
    return result


def write_docs(index):
    folder = ROOT/'docs/creatures'
    folder.mkdir(parents=True, exist_ok=True)
    lines = ['# Indexed Brogue creature models', '',
             'Generated from the pinned Brogue CE catalog and exact `monsterText` in `Globals.c`.',
             'Stable work IDs are `BRG-M00` through `BRG-M67`; they match catalog kinds, not live entity IDs.', '',
             '## Scale and authority', '',
             'Brogue gives no meter/foot dimensions. `isLarge`, prose, color, anatomy and relative comparisons are facts; all numerical dimensions below are presentation decisions. Do not infer body size from HP. A cell is 64 map units; the humanoid art reference is about 58 units and the existing rat is about 15 units tall. Large coils and wings are posed compactly, not used to widen collision. The underworm is intentionally bulkier than the ogre. The mirrored totem is shoulder-high. Pixies are smaller than humanoids. Dar are elves, not flying creatures; the dragon has no flight flag and is not given wings.', '',
             'Dimensions are rest-pose X/Y/Z mesh extents including equipment and appendages, before separate flight clearance. Runtime bindings remain scale 1. Feet touch the local floor; levitating meshes have a documented 16-unit visual gap. Existing bridge visibility/submersion behavior is unchanged. Most forms remain static OBJs; the rat and kobold use weighted IQMs with six clips. See their work cards and the shared skeletal workflow.', '',
             '## Work index', '', '| ID | Brogue kind | Recipe | Size X/Y/Z | State |', '| --- | --- | --- | --- | --- |']
    for item in index['creatures']:
        art = item['art']; symbol = item['symbol']; slug = symbol.removeprefix('MK_').lower()
        filename = f"{item['kind']:02d}_{slug}.md"
        dims = ' / '.join(f'{n:g}' for n in art.get('dimensions', [])) or ('51.12 / 18.44 / 15' if item['kind']==1 else 'reference')
        lines.append(f"| [{item['indexId']}](creatures/{filename}) | {item['name']} (`{symbol}`) | {art.get('recipe','existing')} | {dims} | {art['status']} |")
        ref = '../../'+item['source']['path']
        doc = [f"# {item['indexId']} — {item['name']}", '', f"Brogue kind **{item['kind']}**, `{symbol}`; runtime class `BrogueMonsterK{item['kind']:02d}`.", '',
               '## Brogue facts', '', f"> {item['description']}", '',
               f"Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source]({ref}#L{item['source']['catalogLine']}); [prose source]({ref}#L{item['source']['descriptionLine']}).", '',
               f"- Large flag: `{str(item['isLarge']).lower()}` (not a physical measurement).",
               f"- Base glyph RGB: {item['color']['red']}, {item['color']['green']}, {item['color']['blue']} on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.",
               f"- Catalog tokens: {', '.join('`'+t+'`' for t in item['catalogTokens']) or 'none'}.",
               f"- Source action/prose strings: {json.dumps(item['sourceTextStrings'][1:], ensure_ascii=False)}", '',
               '## Model work card', '', f"- Status: {art['status']}.", f"- Recipe: `{art.get('recipe','existing')}`.",
               f"- Authored silhouette dimensions: {dims} map units. Clearance: {art['clearance']} units.",
               '- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.',
               f"- Visual construction cues: {', '.join(art.get('traits',[])) or 'see existing rat authoring guide'}.",
               f"- [Runtime model](../../{art['runtimeModel']})."]
        if art['sourceBlend']:
            doc.append(f"- [Editable Blender source](../../{art['sourceBlend']}).")
        if art.get('animationManifest'):
            doc.extend([f"- [Animation manifest](../../{art['animationManifest']}); {art['boneCount']} bones.",
                        '- [Shared skeletal workflow and verification](../skeletal-enemy-workflow.md).'])
        doc.extend(['', '## Brogue encounter-table references', '',
                    'These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.', '',
                    '| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |',
                    '| --- | --- | --- | --- | --- | --- |'])
        for h in item.get('hordeReferences',[]):
            flags=h['flags'].replace('|',' / ')
            doc.append(f"| [L{h['line']}](../../{index['hordeSource']}#L{h['line']}) | {', '.join(h['roles'])} | `{h['leader']}` | `{h['minLevelExpression']}`–`{h['maxLevelExpression']}` | `{h['terrain']}` | `{flags}` |")
        if not item.get('hordeReferences'): doc.append('| — | No direct table reference; may be created by another Brogue path. | — | — | — | — |')
        doc.extend(['', '## Acceptance gates', '',
                    'Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.', '',
                    '- [ ] Individual art/signature-feature approval.',
                    ('- [x] Fixed-seed normal encounter captured; see verification object for limited scope.'
                     if item.get('verification',{}).get('naturalEncounter') and not item.get('verification',{}).get('stale')
                     else '- [ ] Normal encounter at gameplay distance and lighting.'),
                    '- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.',
                    ('- [x] Skeletal clips authored; see animation report for actual verification and approval scope.'
                     if art.get('format')=='IQM v2' else '- [ ] Animation refinement if later requested (current pose is static).'), '',
                    'Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.', ''])
        (folder/filename).write_text('\n'.join(doc), encoding='utf-8')
    lines.extend(['', '## Rebuild and verification', '',
                  'Run `python -m tools.monster_models.creatures`, then `python -m tools.monster_models.generate`. For a single work card use `python -m tools.monster_models.creatures --kind 2` (existing metrics for other kinds are retained). Build Blender sources with `tools/monster_models/blender_creatures.py` in Blender. The procedural Python definitions are the reproducible master; reconcile Blender hand edits before regeneration.', '',
                  'See [creature-model-rollout.md](creature-model-rollout.md) for actual verification evidence and remaining gates.', ''])
    (ROOT/'docs/creature-model-index.md').write_text('\n'.join(lines), encoding='utf-8')


if __name__ == '__main__':
    write_index()
