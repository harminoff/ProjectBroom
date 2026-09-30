"""Presentation metadata for natural reviews beyond a small startup campaign."""
import re
from zipfile import ZipFile


def missing_depth_mapinfo(campaign, target_depth):
    """Declare missing Brogue depths only; maps remain bridge-reconstructed."""
    if not 1 <= target_depth <= 40:
        raise ValueError('Brogue campaign depth must be in 1..40')
    with ZipFile(campaign) as archive:
        name = next(name for name in archive.namelist() if name.upper() == 'MAPINFO')
        text = archive.read(name).decode('utf-8')
    declared = {int(depth) for depth in re.findall(r'\bmap\s+BRG(\d+)\b', text, re.I)}
    return ''.join(
        f'map BRG{depth:02d} "Project Broom - Depth {depth}" '
        f'{{ levelnum={depth} cluster=1 nointermission '
        + ('sky1="BRGSKY",0 ' if depth > 1 else '') + '}\n'
        for depth in range(1, target_depth + 1) if depth not in declared)
