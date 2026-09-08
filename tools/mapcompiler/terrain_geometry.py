"""Addressable terrain foundation; no Brogue rules or state mutation.

Control planes are allocated at map load, below every possible bed. Type 3
3D floors are render-only; 2049 means no shading and no damage transfer in
the pinned engine's MapLoader::Set3DFloor. Runtime updates use these existing
planes, never new BSP geometry. Primary/control tags occupy disjoint ranges.
"""
from __future__ import annotations

PRIMARY_BASE = 10000
LIQUID_BASE = 30000
DECK_BASE = 40000
HIDDEN_PLANE_Z = -512


def reserve_planes(positions, vertex_count: int, side_count: int) -> str:
    parts = []
    count = len(positions)
    for role, base in ((1, LIQUID_BASE), (2, DECK_BASE)):
        for index, (x, y) in enumerate(positions):
            control = (role - 1) * count + index
            sector = count + control
            v = vertex_count + control * 4
            s = side_count + control * 4
            # Detached clockwise squares, within Doom's coordinate range.
            px, py = x * 16, -1024 - (y + (role - 1) * 29) * 16
            for vx, vy in ((px, py), (px + 8, py), (px + 8, py - 8), (px, py - 8)):
                parts.append(f'vertex {{ x = {vx}; y = {vy}; }}\n')
            for edge in range(4):
                setup = (f'special = 160; arg0 = {PRIMARY_BASE + y * 79 + x}; '
                         'arg1 = 3; arg2 = 2049; arg3 = 255;' if edge == 0 else '')
                parts.append(f'linedef {{ v1 = {v + edge}; v2 = {v + (edge + 1) % 4}; '
                             f'sidefront = {s + edge}; twosided = false; blocking = true; '
                             f'blockplayers = true; dontdraw = true; {setup} }}\n')
                parts.append(f'sidedef {{ sector = {sector}; texturemiddle = "BRGCLIFF"; '
                             'texturetop = "-"; texturebottom = "-"; }\n')
            parts.append(f'sector {{ id = {base + y * 79 + x}; user_brogue_role = {role}; '
                         f'user_brogue_owner = {y * 79 + x}; heightfloor = -520; '
                         'heightceiling = -512; texturefloor = "BRGEARTH"; '
                         'textureceiling = "BRGEARTH"; lightlevel = 192; special = 0; }\n')
    return ''.join(parts)


def verify_geometry(level, textmap: str) -> dict[str, int]:
    """Independently validate role ownership, closed polygons and shared edges."""
    from collections import Counter, defaultdict
    from .verify import blocks, int_property, optional_int_property, bool_property, string_property, VerifyError

    sectors, sides = blocks(textmap, 'sector'), blocks(textmap, 'sidedef')
    vertices, lines = blocks(textmap, 'vertex'), blocks(textmap, 'linedef')
    coordinates = [(int_property(v, 'x'), int_property(v, 'y')) for v in vertices]
    if len(set(coordinates)) != len(coordinates):
        raise VerifyError('duplicate physical vertex')
    for side in sides:
        for tier in ('top', 'middle', 'bottom'):
            string_property(side, 'texture' + tier)
    if len(sectors) != 3 * 2291:
        raise VerifyError('addressable map requires 2291 primary and 4582 control sectors')
    cells = {(int(c['x']), int(c['y'])): c for c in level['cells']}
    owners = set()
    roles = []
    sector_keys = []
    for sector in sectors:
        if int_property(sector, 'special') != 0:
            raise VerifyError('terrain sector has gameplay special')
        for plane in ('floor', 'ceiling'):
            if string_property(sector, 'texture' + plane) == '-':
                raise VerifyError('missing terrain plane texture')
        role = int_property(sector, 'user_brogue_role')
        if role not in (0, 1, 2):
            raise VerifyError('invalid terrain sector role')
        if role == 0:
            x, y = int_property(sector, 'user_brogue_x'), int_property(sector, 'user_brogue_y')
            if (x, y) not in cells:
                raise VerifyError('primary sector has no Brogue cell')
            key = y * 79 + x
            if int_property(sector, 'user_brogue_depth') != level['depth']:
                raise VerifyError('primary sector has incorrect depth')
            for layer in ('dungeon', 'liquid', 'gas', 'surface'):
                if int_property(sector, 'user_brogue_' + layer) != cells[x, y]['layers'][layer]['id']:
                    raise VerifyError('primary terrain metadata changed')
        else:
            key = int_property(sector, 'user_brogue_owner')
            if not 0 <= key < 2291:
                raise VerifyError('control owner outside map')
        if (role, key) in owners:
            raise VerifyError('duplicate terrain role ownership')
        owners.add((role, key))
        if int_property(sector, 'id') != (PRIMARY_BASE, LIQUID_BASE, DECK_BASE)[role] + key:
            raise VerifyError('unstable terrain sector tag')
        if int_property(sector, 'heightfloor') >= int_property(sector, 'heightceiling'):
            raise VerifyError('degenerate startup sector')
        roles.append(role)
        sector_keys.append(key)
    degrees = defaultdict(Counter)
    edge_set = set()
    setups = Counter()
    shared_cells = set()
    for line in lines:
        a, b = int_property(line, 'v1'), int_property(line, 'v2')
        if not (0 <= a < len(vertices) and 0 <= b < len(vertices)) or a == b:
            raise VerifyError('invalid boundary vertices')
        edge = tuple(sorted((a, b)))
        if edge in edge_set:
            raise VerifyError('duplicate boundary')
        edge_set.add(edge)
        back = optional_int_property(line, 'sideback')
        adjacent = []
        for side in (int_property(line, 'sidefront'), back):
            if side is None:
                continue
            if not 0 <= side < len(sides):
                raise VerifyError('invalid sidedef')
            sector = int_property(sides[side], 'sector')
            if not 0 <= sector < len(sectors):
                raise VerifyError('invalid sidedef sector')
            adjacent.append(sector)
            degrees[sector][a] += 1
            degrees[sector][b] += 1
        if bool_property(line, 'twosided') != (back is not None):
            raise VerifyError('inconsistent two-sided boundary')
        if back is None and roles[adjacent[0]] == 0:
            ax, ay = int_property(vertices[a], 'x'), int_property(vertices[a], 'y')
            bx, by = int_property(vertices[b], 'x'), int_property(vertices[b], 'y')
            if not ((ax == bx and ax in (0, 79*64)) or (ay == by and ay in (0, 29*64))):
                raise VerifyError('one-sided internal boundary')
        if back is not None:
            if adjacent[0] == adjacent[1] or any(roles[s] for s in adjacent):
                raise VerifyError('invalid shared primary boundary')
            if bool_property(line, 'blocking') or bool_property(line, 'blockplayers'):
                raise VerifyError('stale internal presentation blocker')
            shared_cells.add(tuple(sorted(sector_keys[s] for s in adjacent)))
        special = optional_int_property(line, 'special') or 0
        if special:
            if special != 160 or roles[adjacent[0]] == 0:
                raise VerifyError('unexpected terrain action special')
            owner = int_property(sectors[adjacent[0]], 'user_brogue_owner')
            if [int_property(line, f'arg{i}') for i in range(4)] != [10000+owner, 3, 2049, 255]:
                raise VerifyError('3D floor is not a reserved render-only plane')
            setups[adjacent[0]] += 1
    if len(degrees) != len(sectors) or any(any(d != 2 for d in degree.values()) for degree in degrees.values()):
        raise VerifyError('terrain polygon is open')
    expected_neighbors = {(key, key + delta) for key in range(2291)
                          for delta in (1, 79) if (delta == 1 and key % 79 < 78)
                          or (delta == 79 and key < 2212)}
    if shared_cells != expected_neighbors:
        raise VerifyError('shared boundaries changed Brogue cardinal adjacency')
    if {s for s, role in enumerate(roles) if role} != set(setups) or any(n != 1 for n in setups.values()):
        raise VerifyError('each control must attach exactly one plane')
    return dict(primarySectors=2291, controlSectors=4582, vertices=len(vertices), lines=len(lines))
