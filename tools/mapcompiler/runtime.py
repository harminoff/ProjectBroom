"""Compile one restored native level to an addressable external WAD."""
import argparse
import hashlib
import json
from pathlib import Path

from tools.mapcompiler.compile import (COMPILER_VERSION, make_map_text, make_wad,
                                       resource_pack_hash, validate_model, DOOR_GEOMETRY_SYMBOLS)

PROJECTION_VERSION = b'3'


def project_features(model):
    """Give physical proxies a reversible base and preserve door camouflage.

    A trapdoor starts as an addressable floor, which the copied snapshot lowers
    only when known. This also lets removal restore the floor without topology
    regeneration. Native chasms keep the compiler's ordinary bounded geometry.
    """
    catalog = {entry['symbol']: entry for entry in model['terrainCatalog']}
    names = {entry['id']: entry['symbol'] for entry in model['terrainCatalog']}
    def layer(name):
        return {'id': catalog[name]['id'], 'symbol': name}
    for cell in model['levels'][0]['cells']:
        layers = cell['layers']
        for name, value in layers.items():
            if value['symbol'] == 'TRAP_DOOR':
                layers[name] = layer('FLOOR' if name == 'dungeon' else 'NOTHING')
                cell['semantic']['isChasm'] = False
        dungeon = layers['dungeon']['symbol']
        if dungeon in DOOR_GEOMETRY_SYMBOLS and not cell['currentlyVisible']:
            remembered = names.get(cell['remembered']['terrain']) if cell['discovered'] else None
            if remembered not in DOOR_GEOMETRY_SYMBOLS:
                layers['dungeon'] = layer('SECRET_DOOR')
                cell['semantic']['isSecret'] = True


def compile_current(input_path: Path, output_path: Path) -> str:
    payload = input_path.read_bytes()
    model = json.loads(payload)
    if model.get('currentLevel') is not True:
        raise ValueError('runtime compilation requires an active-level export')
    width, height, _ = validate_model(model)
    key = hashlib.sha256(payload + PROJECTION_VERSION + COMPILER_VERSION.encode() + resource_pack_hash().encode()).hexdigest()
    marker = output_path.with_suffix('.sha256')
    if output_path.is_file() and marker.is_file():
        existing_hash = hashlib.sha256(output_path.read_bytes()).hexdigest()
        if marker.read_text() == key + ' ' + existing_hash:
            return key
    project_features(model)
    level = model['levels'][0]
    name = f"BRG{level['depth']:02d}"
    text, _, _ = make_map_text(level, width, height, name, model['seed'], addressable=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_suffix('.pending')
    wad = make_wad(name, text)
    temporary.write_bytes(wad)
    temporary.replace(output_path)
    marker.write_text(key + ' ' + hashlib.sha256(wad).hexdigest())
    return key


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    print(compile_current(args.input, args.output))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
