"""Shared creature-queue pipeline: one command per phase, identical for every model.

Authoring agents only author art (creature-local files plus a pending profile row)
and review it with `review_skeletal --preview`. The coordinator then integrates
and gates whole batches serially with this tool, replacing the per-agent
take-baseline / restore-cards / prove-determinism / verify-fresh-blender /
final-evidence / preservation-audit / finalize-metadata scripts.

  python -m tools.monster_models.creature_pipeline precheck  MK_A MK_B        # authoring agents, before hand-back
  python -m tools.monster_models.creature_pipeline baseline  --batch B01
  python -m tools.monster_models.creature_pipeline integrate --batch B01 MK_A MK_B
  python -m tools.monster_models.creature_pipeline gate      --batch B01 MK_A MK_B
  python -m tools.monster_models.creature_pipeline archive   MK_A MK_B

`baseline` must run before `integrate`; it refuses to overwrite. `archive` runs
only after the coordinator has visually accepted the final galleries.

The gate fails fast: it first prechecks every batch creature (registry/binary
agreement plus the creature's own tests, in parallel), then runs determinism
and Blender in parallel, galleries serially (one GPU), and the remaining test
modules in parallel. Each creature's determinism, Blender and gallery results
are cached in its evidence folder under a key of their input hashes, so a gate
re-run redoes only what changed; `--force` ignores the cache. A frozen or
timed-out gallery capture is retried automatically.
"""
from __future__ import annotations

import argparse, ast, concurrent.futures, difflib, hashlib, json, os, shutil, struct, subprocess, sys, time, zipfile
from pathlib import Path

from .skeletal_registry import ROOT, PATH as PROFILES, PENDING, find, promote

QUEUE = ROOT/'artifacts/creature-queue'
MOD = ROOT/'mod/BrogueDoom'
BLENDER = r'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
PY = sys.executable
BACKENDS = (('vulkan', '1', 'Vulkan'), ('opengl', '0', 'OpenGL'))
SHARED_TEXT = ('assets/monsters/bestiary-index.json', 'assets/monsters/brogue_monster_registry.json',
               'assets/monsters/brogue_monster_catalog.json', 'assets/monsters/skeletal_profiles.json',
               'docs/creature-model-index.md', 'mod/BrogueDoom/models/monsters/MODELDEF.txt',
               'mod/BrogueDoom/brogue_monsters.zs', 'mod/BrogueDoom/GLDEFS',
               'src/gzdoom-bridge/skeletal_presentation.generated.h')
# Generated or registry files a batch may legitimately change.
SHARED_INTENDED = {'assets/monsters/bestiary-index.json', 'assets/monsters/brogue_monster_registry.json',
                   'assets/monsters/skeletal_profiles.json', 'docs/creature-model-index.md',
                   'mod/BrogueDoom/models/monsters/MODELDEF.txt', 'mod/BrogueDoom/brogue_monsters.zs',
                   'src/gzdoom-bridge/skeletal_presentation.generated.h'}
SHARED_TESTS = ['tools.monster_models.test_skeletal', 'tools.monster_models.test_connected_skin',
                'tools.monster_models.test_creatures', 'tools.test_broguedoom_resources']
BASELINE_GLOBS = ('assets/monsters/**/*', 'docs/creatures/*.md', 'docs/creature-*', 'mod/BrogueDoom/**/*',
                  'src/gzdoom-bridge/*', 'tools/monster_models/*.py', 'tools/*.py')
TOOLS = ROOT/'tools/monster_models'
JOBS = max(1, min(4, (os.cpu_count() or 2)//4))
GALLERY_ATTEMPTS = 3
# Engine inputs that change what a packaged gallery shows for any creature.
GALLERY_INPUTS = ('mod/BrogueDoom/GLDEFS', 'mod/BrogueDoom/models/monsters/MODELDEF.txt', 'mod/BrogueDoom/brogue_monsters.zs',
                  'src/gzdoom-bridge/skeletal_presentation.generated.h', 'tools/monster_models/review_skeletal.py',
                  'tools/monster_models/review_wall_fixture.py', '.build/uzdoom/Release/project-broom-build.json')
BLENDER_INPUTS = ('tools/monster_models/blender_skeletal.py', 'tools/monster_models/blender_verify.py')


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def catalog_kind(symbol: str) -> int:
    kinds = json.loads((ROOT/'assets/monsters/brogue_monster_catalog.json').read_text(encoding='utf-8'))['kinds']
    return next(k['kind'] for k in kinds if k['symbol'] == symbol)


EVIDENCE_ROOT = QUEUE  # --evidence-root redirects a pipeline self-test away from accepted evidence


def evidence(symbol: str) -> Path:
    return EVIDENCE_ROOT/f'BRG-M{catalog_kind(symbol):02d}'


def batch_dir(name: str) -> Path:
    return QUEUE/'batches'/name


def run(cmd, log: Path, timeout=3600):
    """Run a command to a log file; raise with the log tail on failure."""
    log.parent.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    with log.open('w', encoding='utf-8', errors='replace') as handle:
        proc = subprocess.run([str(c) for c in cmd], cwd=ROOT, stdout=handle, stderr=subprocess.STDOUT, timeout=timeout)
    if proc.returncode:
        raise SystemExit(f'FAILED ({proc.returncode}): {" ".join(map(str, cmd))}\n'+log.read_text(errors='replace')[-4000:])
    return round(time.monotonic()-start, 1)


def card_path(symbol: str) -> Path:
    return ROOT/'docs/creatures'/f"{catalog_kind(symbol):02d}_{symbol.removeprefix('MK_').lower()}.md"


def owned_paths(row: dict) -> set[str]:
    """Files that belong to one creature and may change or appear during its integration."""
    prefix = row['module'].removesuffix('_animation')
    manifest_dir = Path(row['manifest']).parent.as_posix()
    skin = Path(row['skin'])
    owned = {row['source'], row['manifest'], 'mod/BrogueDoom/models/monsters/'+row['model'],
             'mod/BrogueDoom/'+row['skin'], rel(card_path(row['symbol']))}
    owned |= {rel(p) for p in (ROOT/manifest_dir).glob('*') if p.is_file()}
    owned |= {rel(p) for p in (MOD/skin.parent).glob(skin.stem+'_*') if p.is_file()}
    tools = ROOT/'tools/monster_models'
    # `ogre_*` must not claim ogre_shaman_* or ogre_totem_* files.
    others = {r['module'].removesuffix('_animation') for r in json.loads(PROFILES.read_text())['enemies']}
    others |= {json.loads(p.read_text())['module'].removesuffix('_animation') for p in PENDING.glob('MK_*.json')} if PENDING.is_dir() else set()
    longer = [o for o in others if o != prefix and o.startswith(prefix+'_')]
    owned |= {rel(p) for p in tools.glob(prefix+'_*.py') if not any(p.name.startswith(o+'_') for o in longer)}
    owned |= {rel(tools/f) for f in (f'test_{prefix}.py', f'blender_{prefix}.py', f'review_{prefix}.py')}
    owned |= {rel(p) for p in tools.glob(f'review_{prefix}_*.py')}
    owned |= set(row.get('ownedFiles', []))
    if row.get('report'):
        owned.add(row['report'])
    return owned


def runtime_files(row: dict) -> list[str]:
    files = ['mod/BrogueDoom/models/monsters/'+row['model'], 'mod/BrogueDoom/'+row['skin'], row['manifest']]
    skin = Path(row['skin'])
    files += sorted(rel(p) for p in (MOD/skin.parent).glob(skin.stem+'_*') if p.is_file())
    files += [f for f in row.get('ownedFiles', []) if f.startswith('mod/BrogueDoom/')]
    return sorted(set(files))


def in_progress_entries(symbols) -> set[str]:
    """Package entry names (relative to mod/BrogueDoom) owned by creatures still in authoring.

    Their pending rows sit outside `symbols`; their agents may re-export at any time, so the
    gate and archive package checks must not compare those entries against live source."""
    entries = set()
    if PENDING.is_dir():
        for p in PENDING.glob('MK_*.json'):
            row = json.loads(p.read_text())
            if row['symbol'] not in symbols:
                entries |= {f.removeprefix('mod/BrogueDoom/') for f in runtime_files(row) if f.startswith('mod/BrogueDoom/')}
    return entries


def package_mismatches(package: Path, symbols) -> dict:
    """Compare a review pk3 with source, skipping entries of creatures still in authoring.

    `checkedSha256` digests only the compared entries, so two packages built minutes apart
    (Vulkan, then OpenGL) agree even when an authoring agent re-exported in between."""
    skip = in_progress_entries(symbols)
    digest = hashlib.sha256()
    with zipfile.ZipFile(package) as z:
        names = sorted(n for n in z.namelist() if not n.endswith('/'))
        mismatch = []
        for n in names:
            if n in skip: continue
            data = z.read(n)
            digest.update(n.encode()+b'\0'+hashlib.sha256(data).digest())
            if data != (MOD/n).read_bytes(): mismatch.append(n)
    return dict(entries=len(names), mismatches=mismatch, checkedSha256=digest.hexdigest(),
                inProgressSkipped=sorted(n for n in names if n in skip))


# --------------------------------------------------------------------------- input hashing and stage cache
def module_deps(module: str) -> list[str]:
    """tools/monster_models source files a generator imports, found statically (recursive)."""
    seen, todo = set(), [module]
    while todo:
        name = todo.pop()
        path = TOOLS/(name+'.py')
        if name in seen or not path.is_file(): continue
        seen.add(name)
        for node in ast.walk(ast.parse(path.read_text(encoding='utf-8'))):
            if isinstance(node, ast.ImportFrom):
                if node.level == 1 and node.module: todo.append(node.module.split('.')[0])
                elif node.level == 1: todo += [a.name for a in node.names]
                elif (node.module or '').startswith('tools.monster_models.'): todo.append(node.module.split('.')[2])
                elif node.module == 'tools.monster_models': todo += [a.name for a in node.names]
            elif isinstance(node, ast.Import):
                todo += [a.name.split('.')[2] for a in node.names if a.name.startswith('tools.monster_models.')]
    return sorted(rel(TOOLS/(n+'.py')) for n in seen)


def fingerprint(paths, extra=None) -> str:
    h = hashlib.sha256()
    for p in sorted(set(map(str, paths))):
        f = ROOT/p
        h.update(p.encode()+b'\0'+(sha(f).encode() if f.is_file() else b'missing')+b'\n')
    if extra is not None: h.update(json.dumps(extra, sort_keys=True).encode())
    return h.hexdigest()


def cached(ev: Path, stage: str, key: str, force: bool):
    """Previous result of `stage` if its input key is unchanged, else None."""
    if force: return None
    path = ev/'gate-cache.json'
    entry = json.loads(path.read_text()).get(stage) if path.is_file() else None
    return entry['result'] if entry and entry['key'] == key else None


def remember(ev: Path, stage: str, key: str, result):
    path = ev/'gate-cache.json'
    data = json.loads(path.read_text()) if path.is_file() else {}
    data[stage] = dict(key=key, result=result)
    path.write_text(json.dumps(data, indent=2))


def parallel(fn, items, jobs=None):
    """Run fn over items in threads (each fn mostly waits on a subprocess); re-raise the first failure."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs or JOBS) as pool:
        futures = [pool.submit(fn, item) for item in items]
        return [f.result() for f in futures]


# --------------------------------------------------------------------------- precheck
def check_binary(symbol: str) -> dict:
    """In-process twin of test_skeletal's registry/binary agreement for one creature (pending or registered)."""
    import importlib, math
    from . import iqm
    row = find(symbol)
    rig = importlib.import_module('tools.monster_models.'+row['module'])
    parts, v, n, uv, t, w = rig.geometry(); clips, bounds = rig.animation_data(v, w)
    label = 'Project_Broom_'+symbol[3:].lower()
    data = (MOD/'models/monsters'/row['model']).read_bytes()
    problems = []
    if data != iqm.encode(v, n, uv, t, w, rig.BONES, clips, bounds, mesh_label=label, material_path=row['skin']):
        problems.append(f'IQM bytes differ from a fresh encode (mesh label must be {label}; re-export if the generator changed)')
    names = [a['name'] for a in iqm.inspect(data)['animations']]
    extra = row.get('captivity', {})
    if names != row['clips']+([extra['idle'], extra['release']] if extra else []):
        problems.append(f'clip names {names} differ from the profile row')
    if sha(MOD/'models/monsters'/row['model']) != json.loads((ROOT/row['manifest']).read_text())['sha256']:
        problems.append('manifest sha256 is stale')
    if 'visualScale' in row: problems.append('profile row must not use visualScale')
    for role in range(2, 6):
        need = math.ceil(len(clips[role]['frames'])*35/clips[role]['fps'])
        if row['durations'][role] < need: problems.append(f'durations[{role}]={row["durations"][role]} < {need} tics')
    for f in runtime_files(row):
        if not (ROOT/f).is_file(): problems.append(f'missing runtime file {f}')
    return dict(symbol=symbol, ok=not problems, problems=problems)


def creature_test_module(row: dict) -> str | None:
    name = 'test_'+row['module'].removesuffix('_animation')
    return 'tools.monster_models.'+name if (TOOLS/(name+'.py')).is_file() else None


def precheck(symbols, log_dir: Path) -> dict:
    """Fast, parallel: binary agreement then each creature's own tests. Raises on failure."""
    log_dir.mkdir(parents=True, exist_ok=True)

    def one(symbol):
        start = time.monotonic()
        out = log_dir/f'precheck-{symbol}.log'
        proc = subprocess.run([PY, '-m', 'tools.monster_models.creature_pipeline', 'check-binary', symbol], cwd=ROOT,
                              capture_output=True, text=True)
        result = json.loads(proc.stdout.strip().splitlines()[-1]) if proc.returncode == 0 else \
            dict(symbol=symbol, ok=False, problems=[proc.stderr[-2000:]])
        module = creature_test_module(find(symbol))
        if result['ok'] and module:
            test = subprocess.run([PY, '-m', 'unittest', module], cwd=ROOT, capture_output=True, text=True)
            tail = (test.stdout+test.stderr).strip().splitlines()
            result.update(testModule=module, testSummary=next((l for l in reversed(tail) if l.startswith('Ran ')), ''),
                          testResult=tail[-1] if tail else '')
            if test.returncode: result['ok'] = False; result['problems'].append(f'{module} failed')
            out.write_text(test.stdout+test.stderr, encoding='utf-8', errors='replace')
        result['seconds'] = round(time.monotonic()-start, 1)
        return result

    results = parallel(one, symbols, jobs=max(1, min(len(symbols), (os.cpu_count() or 2)//2)))
    (log_dir/'precheck.json').write_text(json.dumps(results, indent=2))
    bad = [r for r in results if not r['ok']]
    if bad:
        raise SystemExit('PRECHECK FAILED:\n'+'\n'.join(f'  {r["symbol"]}: {"; ".join(r["problems"])}' for r in bad)
                         +f'\n(logs in {rel(log_dir) if log_dir.is_relative_to(ROOT) else log_dir})')
    return {r['symbol']: r for r in results}


def cmd_contact(a):
    shots = sorted(a.folder.glob('*.png'))
    if not shots: raise SystemExit(f'no captures in {a.folder}')
    dest = a.folder.with_name(a.folder.name+'-contact.jpg'); contact(shots, dest, a.cols); print(dest)


def cmd_check_binary(a):
    print(json.dumps(check_binary(a.symbol)))


def cmd_precheck(a):
    out = a.log_dir or Path(os.environ.get('TEMP', ROOT))/'broom-precheck'
    results = precheck(a.symbols, out)
    for s, r in results.items(): print(f'{s}: OK ({r.get("testSummary", "no creature test module")}, {r["seconds"]}s)')
    print('PRECHECK PASSED')


# --------------------------------------------------------------------------- baseline
def cmd_baseline(a):
    out = batch_dir(a.batch)
    if (out/'baseline.json').exists():
        raise SystemExit(f'{out} already has a baseline; never overwrite it (use a new batch name)')
    paths = sorted({rel(p) for g in BASELINE_GLOBS for p in ROOT.glob(g)
                    if p.is_file() and '__pycache__' not in p.parts})
    base = {p: sha(ROOT/p) for p in paths}
    raw = [p for p in paths if p in SHARED_TEXT or p.startswith('docs/creatures/') or p.startswith('assets/monsters/skeletal_pending/')]
    for p in raw:
        dest = out/'baseline-bytes'/p; dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT/p, dest)
        assert sha(dest) == base[p]
    (out/'baseline.json').write_text(json.dumps(base, indent=1))
    (out/'git-status-before.txt').write_bytes(subprocess.check_output(['git', 'status', '--short'], cwd=ROOT))
    print(f'baseline {a.batch}: {len(base)} hashed, {len(raw)} raw copies')


# --------------------------------------------------------------------------- integrate
def regenerate(log: Path):
    for step in ('skeletal_registry', 'generate', 'bestiary'):
        run([PY, '-m', 'tools.monster_models.'+step], log.with_name(log.stem+f'-{step}.log'))


def cmd_integrate(a):
    out = batch_dir(a.batch)
    if not (out/'baseline.json').exists():
        raise SystemExit('run baseline first')
    for symbol in a.symbols:
        pending = PENDING/(symbol+'.json')
        registered = any(r['symbol'] == symbol for r in json.loads(PROFILES.read_text())['enemies'])
        if not registered:
            if not pending.exists():
                raise SystemExit(f'{symbol}: no pending row at {rel(pending)}')
            row = json.loads(pending.read_text())
            for f in runtime_files(row):
                if not (ROOT/f).is_file():
                    raise SystemExit(f'{symbol}: missing runtime file {f}; run python -m tools.monster_models.{row["module"]}')
            snippet = PENDING/(symbol+'.gldefs')
            if snippet.exists():
                gldefs = MOD/'GLDEFS'
                text = gldefs.read_bytes()
                block = snippet.read_bytes().replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')
                gldefs.write_bytes(text+(b'' if text.endswith(b'\r\n') else b'\r\n')+block)
                snippet.unlink()
            promote(symbol)
            print('promoted', symbol)
    regenerate(out/'regenerate.log')
    for symbol in a.symbols:
        card = card_path(symbol).read_text(encoding='utf-8')
        row = find(symbol)
        assert 'authored-skeletal' in card, f'{symbol} card not skeletal'
        if row.get('report'):
            assert Path(row['report']).name in card, f'{symbol} card lacks its report link'
    print('integrated', ', '.join(a.symbols))


# --------------------------------------------------------------------------- gate
def determinism(row: dict, ev: Path):
    files = runtime_files(row)
    runs = [{f: sha(ROOT/f) for f in files}]
    for i in range(2):
        run([PY, '-m', 'tools.monster_models.'+row['module']], ev/f'export-{i}.log')
        runs.append({f: sha(ROOT/f) for f in files})
    ok = runs[0] == runs[1] == runs[2]
    (ev/'determinism.json').write_text(json.dumps(dict(identical=ok, freshProcessExports=2, runs=runs), indent=2))
    if not ok:
        raise SystemExit(f'{row["symbol"]}: runtime export is not deterministic; see {rel(ev)}/determinism.json')


def blender(row: dict, ev: Path):
    symbol = row['symbol']
    base = [BLENDER, '--background', '--factory-startup', '--disable-autoexec', '--python-exit-code', '1']
    run(base+['--python', 'tools/monster_models/blender_skeletal.py', '--', symbol], ev/'blender-build.log')
    run(base+[ROOT/row['source'], '--python', 'tools/monster_models/blender_verify.py', '--', symbol,
              ev/'blender-verification.json'], ev/'blender-fresh.log')


def build_stage(row: dict, force: bool) -> dict:
    """Determinism + Blender for one creature, skipped when its inputs and outputs are unchanged."""
    ev = evidence(row['symbol']); ev.mkdir(parents=True, exist_ok=True)
    inputs = module_deps(row['module'])+list(BLENDER_INPUTS)
    key = fingerprint(inputs+runtime_files(row)+[row['source']], extra=row)
    hit = cached(ev, 'build', key, force)
    if hit is not None and (ev/'blender-verification.json').is_file():
        return dict(json.loads((ev/'blender-verification.json').read_text()), cached=True)
    determinism(row, ev)
    blender(row, ev)
    # Key on the post-build files so an unchanged re-run matches.
    remember(ev, 'build', fingerprint(inputs+runtime_files(row)+[row['source']], extra=row), 'ok')
    return json.loads((ev/'blender-verification.json').read_text())


def native(out: Path):
    sys.path.insert(0, str(ROOT/'tools'))
    from engine_source import validate_build
    engine = ROOT/'.build/uzdoom/Release'
    try:
        validate_build(ROOT, engine); return 'up-to-date'
    except Exception:
        pass
    run([PY, 'tools/run_native.py', 'cmake', '--build', '.build/uzdoom', '--config', 'Release', '-j4'], out/'native-build.log')
    run([PY, 'tools/engine_source.py', '--root', '.', '--record-build', '.build/uzdoom/Release'], out/'native-fingerprint.log')
    validate_build(ROOT, engine)
    return 'rebuilt-and-fingerprinted'


def contact(paths, dest: Path, cols: int):
    from PIL import Image, ImageDraw
    w = 1920//cols; h = w*9//16
    sheet = Image.new('RGB', (1920, ((len(paths)+cols-1)//cols)*(h+22)), (22, 22, 22)); draw = ImageDraw.Draw(sheet)
    for i, p in enumerate(paths):
        im = Image.open(p); assert im.size == (1920, 1080), p
        x = (i % cols)*w; y = (i//cols)*(h+22)
        sheet.paste(im.resize((w, h)), (x, y)); draw.text((x+5, y+h+3), p.name, fill='white')
    sheet.save(dest, quality=90)


def frozen(shots) -> list[str]:
    """Consecutive captures that must differ (camera or distance changes) but are byte-identical.

    Gallery order: 00-18 oblique (before, clips), 19-22 front, 23-26 side, 27-30 rear,
    31-33 front idle at three distances. A capture that freezes under load repeats
    its last frame, so an identical pair across a camera or distance change is a freeze.
    """
    h = [sha(p) for p in shots]
    return [f'{shots[k-1].name}=={shots[k].name}' for k in (19, 23, 27, 31, 32, 33) if h[k] == h[k-1]]


def capture(row: dict, ev: Path, name: str, backend: str, label: str) -> list[Path]:
    """One packaged backend gallery, retried when it times out or freezes."""
    folder = ev/('final-'+name); problems = []
    for attempt in range(1, GALLERY_ATTEMPTS+1):
        if folder.exists(): shutil.rmtree(folder)
        try:
            run([PY, '-m', 'tools.monster_models.review_skeletal', '--symbol', row['symbol'], '--backend', backend, '--packaged',
                 '--all-angles', '--distances', '--width', '1920', '--height', '1080', '--output', folder],
                ev/f'final-{name}.log', 600)
        except (SystemExit, subprocess.TimeoutExpired) as error:
            problems.append(f'attempt {attempt}: capture failed ({str(error).splitlines()[0][:160]})'); continue
        shots = sorted(folder.glob('*.png'))
        if len(shots) != 34:
            problems.append(f'attempt {attempt}: {len(shots)} captures'); continue
        repeats = frozen(shots)
        if repeats:
            problems.append(f'attempt {attempt}: frozen capture {repeats}'); continue
        if problems: (ev/f'final-{name}-retries.json').write_text(json.dumps(problems, indent=2))
        return shots
    raise SystemExit(f'{row["symbol"]} {label}: gallery failed {GALLERY_ATTEMPTS} times: {problems}')


def galleries(row: dict, ev: Path, force: bool = False):
    symbol = row['symbol']; result = {}
    key = fingerprint(runtime_files(row)+list(GALLERY_INPUTS), extra=row)
    hit = cached(ev, 'galleries', key, force)
    if hit is not None and all(len(list((ev/('final-'+n)).glob('*.png'))) == 34 for n, _, _ in BACKENDS):
        return dict(hit, cached=True)
    for name, backend, label in BACKENDS:
        folder = ev/('final-'+name)
        shots = capture(row, ev, name, backend, label)
        contact(shots, ev/f'final-{name}-contact.jpg', 4)
        log = (folder/'runtime.log').read_text(errors='replace')
        assert log.count('blocking=0') == 34 and 'blocking=1' not in log and f'Selecting {label} backend' in log
        package = folder/'ProjectBroom-review.pk3'
        check = package_mismatches(package, (symbol,))
        assert not check['mismatches'], (symbol, name, check['mismatches'][:5])
        entry = dict(packageSha256=sha(package), checkedSha256=check['checkedSha256'], entries=check['entries'],
                     allEntriesMatchSource=True, inProgressSkipped=check['inProgressSkipped'], galleryCaptures=34,
                     nonBlocking=True, logWarnings=sorted({l.strip() for l in log.splitlines()
                                                          if any(k in l.lower() for k in ('warning', 'error', 'missing', 'unknown'))}))
        if row.get('wallMountBack'):
            wall = ev/('wall-'+name)
            if wall.exists(): shutil.rmtree(wall)
            run([PY, '-m', 'tools.monster_models.review_wall_fixture', '--symbol', symbol, '--backend', backend,
                 '--package', package, '--output', wall], ev/f'wall-{name}.log', 600)
            shots = sorted(wall.glob('*.png'))
            for p in shots: assert struct.unpack('>II', p.read_bytes()[16:24]) == (1920, 1080)
            contact(shots, ev/f'wall-{name}-contact.jpg', 3)
            entry['wallCaptures'] = len(shots)
        result[name] = entry
    assert result['vulkan']['checkedSha256'] == result['opengl']['checkedSha256']
    (ev/'package-verification.json').write_text(json.dumps(result, indent=2))
    remember(ev, 'galleries', key, result)
    return result


def tests(symbols, rows, out: Path, extra, already: dict | None = None):
    """Run every test module in its own process, several at once; creature modules that
    passed in the precheck (same inputs, verified deterministic since) are not re-run."""
    already = already or {}
    modules = [m for m in (creature_test_module(r) for r in rows) if m]
    modules = list(dict.fromkeys(modules+list(extra)+SHARED_TESTS))
    reused = [m for m in modules if any(r.get('testModule') == m for r in already.values())]
    todo = [m for m in modules if m not in reused]
    logs = out/'tests'; logs.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()

    def one(module):
        log = logs/(module.rsplit('.', 1)[1]+'.log')
        with log.open('w', encoding='utf-8', errors='replace') as handle:
            code = subprocess.run([PY, '-m', 'unittest', module], cwd=ROOT, stdout=handle, stderr=subprocess.STDOUT,
                                  timeout=7200).returncode
        tail = log.read_text(errors='replace').strip().splitlines()
        ran = next((l for l in reversed(tail) if l.startswith('Ran ')), 'Ran 0 tests')
        return dict(module=module, code=code, ran=int(ran.split()[1]), result=tail[-1] if tail else 'NO OUTPUT')

    # Slowest suites first so they overlap the many short ones.
    order = sorted(todo, key=lambda m: m not in SHARED_TESTS)
    runs = parallel(one, order, jobs=max(1, min(len(order), (os.cpu_count() or 2)//3)))
    with (out/'tests.log').open('w', encoding='utf-8') as handle:
        for r in runs:
            handle.write(f'===== {r["module"]}: {r["result"]}\n'+(logs/(r['module'].rsplit('.', 1)[1]+'.log')).read_text(errors='replace')+'\n')
        for m in reused:
            handle.write(f'===== {m}: passed in precheck ({next(r["testSummary"] for r in already.values() if r.get("testModule") == m)})\n')
    total = sum(r['ran'] for r in runs)+sum(int((r.get('testSummary') or 'Ran 0').split()[1]) for r in already.values() if r.get('testModule') in reused)
    failed = [r['module'] for r in runs if r['code']]
    return dict(modules=modules, precheckModules=reused, summary=f'Ran {total} tests', perModule={r['module']: r['result'] for r in runs},
                result='OK' if not failed else f'FAILED ({", ".join(failed)})', seconds=round(time.monotonic()-start, 1))


def preservation(symbols, rows, out: Path, declared: dict | None = None):
    """`declared` maps coordinator-declared maintenance changes (path -> reason); they are
    recorded in preservation.json, never silently ignored."""
    declared = declared or {}
    base = json.loads((out/'baseline.json').read_text())
    intended = set(SHARED_INTENDED)
    for row in rows: intended |= owned_paths(row)
    if any((PENDING/(s+'.gldefs')).exists() for s in symbols) or \
            sha(MOD/'GLDEFS') != base.get('mod/BrogueDoom/GLDEFS'):
        intended.add('mod/BrogueDoom/GLDEFS')
    pending_now = {rel(p) for p in PENDING.glob('*')} if PENDING.is_dir() else set()
    # Creatures still in authoring (pending rows outside this batch) own their
    # local files; they are reported separately, never counted as batch changes.
    in_progress = set()
    if PENDING.is_dir():
        for p in PENDING.glob('MK_*.json'):
            row = json.loads(p.read_text())
            if row['symbol'] not in symbols:
                in_progress |= owned_paths(row) - SHARED_INTENDED
    changed, missing = [], []
    for p, h in base.items():
        f = ROOT/p
        if not f.exists():
            # Promoted pending rows are consumed by design.
            if not (p.startswith('assets/monsters/skeletal_pending/') and Path(p).stem in symbols): missing.append(p)
        elif sha(f) != h: changed.append(p)
    unexpected = [p for p in changed if p not in intended and p not in in_progress and p not in declared]
    current = {rel(p) for g in BASELINE_GLOBS for p in ROOT.glob(g) if p.is_file() and '__pycache__' not in p.parts}
    new = sorted(current-set(base))
    unowned_new = [p for p in new if p not in intended and p not in pending_now and p not in in_progress and p not in declared]
    # Shared registries: only batch entries may differ.
    entries = {}
    for f, key, field in (('assets/monsters/bestiary-index.json', 'creatures', 'symbol'),
                          ('assets/monsters/brogue_monster_registry.json', 'monsters', 'symbol'),
                          ('assets/monsters/skeletal_profiles.json', 'enemies', 'symbol')):
        old = json.loads((out/'baseline-bytes'/f).read_text(encoding='utf-8'))
        now = json.loads((ROOT/f).read_text(encoding='utf-8'))
        a = {r[field]: r for r in old[key]}; b = {r[field]: r for r in now[key]}
        diff = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
        header = {k: v for k, v in old.items() if k != key} == {k: v for k, v in now.items() if k != key}
        entries[f] = dict(changedEntries=diff, outsideBatch=[k for k in diff if k not in symbols], headerUnchanged=header)
    line_diffs = {}
    for f in ('docs/creature-model-index.md', 'mod/BrogueDoom/models/monsters/MODELDEF.txt', 'mod/BrogueDoom/brogue_monsters.zs',
              'src/gzdoom-bridge/skeletal_presentation.generated.h', 'mod/BrogueDoom/GLDEFS'):
        old = (out/'baseline-bytes'/f).read_bytes().splitlines(True); new_lines = (ROOT/f).read_bytes().splitlines(True)
        line_diffs[f] = [l.decode(errors='replace').rstrip() for l in difflib.diff_bytes(difflib.unified_diff, old, new_lines, n=0)
                         if l[:1] in (b'+', b'-') and not l.startswith((b'+++', b'---'))]
    ok = not unexpected and not missing and not unowned_new and \
        all(not e['outsideBatch'] and e['headerUnchanged'] for e in entries.values())
    result = dict(ok=ok, baselineFiles=len(base), unchanged=len(base)-len(changed)-len(missing), intendedChanged=sorted(set(changed)-set(unexpected)),
                  unexpectedChanged=unexpected, missing=missing, newFiles=new, unownedNewFiles=unowned_new,
                  declaredMaintenance={p: dict(reason=r, changed=p in changed, new=p in new) for p, r in sorted(declared.items())},
                  inProgressOtherCreatures=sorted((set(changed) | set(new)) & in_progress),
                  sharedEntries=entries, generatedLineDiffs=line_diffs)
    (out/'preservation.json').write_text(json.dumps(result, indent=2))
    return result


def record_verification(row, ev: Path, batch: str, pkg, fresh, test_summary):
    """Write this creature's verification object; regeneration preserves it."""
    path = ROOT/'assets/monsters/bestiary-index.json'
    raw = path.read_bytes()
    data = json.loads(raw)
    crlf = b'\r\n' in raw
    for c in data['creatures']:
        if c['symbol'] != row['symbol']: continue
        previous = c.get('verification') or {}
        c['verification'] = {
            'stale': False, 'modelSha256': c['art'].get('modelSha256'), 'skinSha256': c['art'].get('skinSha256'),
            'deterministicExports': 'identical-two-fresh-process-runtime-exports',
            'skeletalAnimation': 'six-roles-authored-and-tested',
            'engineGallery': {'status': 'both-packaged-galleries-captured', 'backends': ['Vulkan', 'OpenGL'],
                              'viewsPerBackend': 34, 'resolution': [1920, 1080],
                              'evidence': rel(ev/'package-verification.json'), 'scope': 'isolated ART01, not natural encounter'},
            **({'wallMountFixture': {'backends': ['Vulkan', 'OpenGL'], 'viewsPerBackend': pkg['vulkan'].get('wallCaptures'),
                                     'wallMountBack': row['wallMountBack'], 'scope': 'isolated ART02 pillar; synthetic'}}
               if row.get('wallMountBack') else {}),
            'packagedBytesMatchSource': True, 'packageSha256': pkg['vulkan']['packageSha256'],
            'blenderSourceReopen': {k: fresh[k] for k in ('freshProcess', 'bones', 'actions', 'sampledPoses', 'maxError', 'linkedLibraries')},
            'regressionTests': test_summary, 'nativeCompilation': 'passed-and-fingerprint-validated',
            'naturalEncounter': False,
            'naturalEncounterStatus': {'status': 'deferred',
                                       'reason': 'deferred to a single deeper-route census covering all deep creatures; no overrides used'},
            'individualArtApproval': 'pending', 'pipelineBatch': batch, 'report': row.get('report'),
            **({'previousAssetVerification': previous} if previous else {})}
    text = json.dumps(data, indent=2)+'\n'
    path.write_bytes((text.replace('\n', '\r\n') if crlf else text).encode())


def cmd_gate(a):
    out = batch_dir(a.batch)
    if not (out/'baseline.json').exists():
        raise SystemExit('run baseline and integrate first')
    rows = [find(s) for s in a.symbols]
    registered = {r['symbol'] for r in json.loads(PROFILES.read_text())['enemies']}
    for s in a.symbols:
        if s not in registered: raise SystemExit(f'{s} is not integrated; run integrate first')
    timings = {}
    t = time.monotonic()
    # Fail fast: a stale export or wrong mesh label surfaces in minutes, not after the galleries.
    checked = precheck(a.symbols, out/'precheck')
    timings['precheck'] = round(time.monotonic()-t, 1); t = time.monotonic()
    built = parallel(lambda row: build_stage(row, a.force), rows)
    fresh = {row['symbol']: b for row, b in zip(rows, built)}
    timings['determinismAndBlender'] = round(time.monotonic()-t, 1)
    timings['buildCached'] = [s for s, b in fresh.items() if b.get('cached')]; t = time.monotonic()
    timings['native'] = native(out); timings['nativeSeconds'] = round(time.monotonic()-t, 1); t = time.monotonic()
    packages = {row['symbol']: galleries(row, evidence(row['symbol']), a.force) for row in rows}  # serial: one GPU
    timings['galleries'] = round(time.monotonic()-t, 1)
    timings['galleriesCached'] = [s for s, p in packages.items() if p.get('cached')]; t = time.monotonic()
    packages = {s: {k: v for k, v in p.items() if k != 'cached'} for s, p in packages.items()}
    fresh = {s: {k: v for k, v in b.items() if k != 'cached'} for s, b in fresh.items()}
    test_summary = tests(a.symbols, rows, out, a.extra_tests, checked)
    timings['tests'] = test_summary['seconds']
    if not a.no_record:
        # Refresh the index's art hashes first: a re-export after integrate would
        # otherwise be recorded against stale hashes and marked stale by regeneration.
        regenerate(out/'pre-record-regenerate.log')
        for row in rows:
            record_verification(row, evidence(row['symbol']), a.batch, packages[row['symbol']], fresh[row['symbol']], test_summary)
    # Verification records must survive a full regeneration unchanged.
    before = sha(ROOT/'assets/monsters/bestiary-index.json')
    regenerate(out/'post-verification-regenerate.log')
    assert sha(ROOT/'assets/monsters/bestiary-index.json') == before, 'regeneration altered verification records'
    declared = dict(d.split('=', 1) for d in a.declare_change)
    keep = preservation(set(a.symbols), rows, out, declared)
    summary = dict(batch=a.batch, symbols=a.symbols, timings=timings, tests=test_summary, preservation=keep['ok'],
                   creatures={row['symbol']: dict(evidence=rel(evidence(row['symbol'])), packageSha256=packages[row['symbol']]['vulkan']['packageSha256'],
                                                  entries=packages[row['symbol']]['vulkan']['entries'],
                                                  wallCaptures=packages[row['symbol']]['vulkan'].get('wallCaptures'),
                                                  blenderMaxError=fresh[row['symbol']]['maxError'])
                              for row in rows})
    (out/'gate-summary.json').write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=1))
    if not keep['ok']:
        raise SystemExit(f'PRESERVATION FAILED: see {rel(out)}/preservation.json')
    if not test_summary['result'].startswith('OK'):
        raise SystemExit(f'TESTS FAILED: see {rel(out)}/tests.log')
    print('GATE PASSED', a.batch)


# --------------------------------------------------------------------------- archive
def cmd_archive(a):
    for symbol in a.symbols:
        ev = evidence(symbol); result = []
        for name, _, _ in BACKENDS:
            package = ev/f'final-{name}/ProjectBroom-review.pk3'
            check = package_mismatches(package, a.symbols)
            result.append(dict(backend='final-'+name, entries=check['entries'], sha256=sha(package),
                               checkedSha256=check['checkedSha256'], allEntriesMatchSource=not check['mismatches'],
                               mismatches=check['mismatches'], inProgressSkipped=check['inProgressSkipped']))
        (ev/'parent-final-package-verification.json').write_text(json.dumps(result, indent=2))
        if any(r['mismatches'] for r in result) or result[0]['checkedSha256'] != result[1]['checkedSha256']:
            raise SystemExit(f'{symbol}: package no longer matches source; re-run gate')
        for name, _, _ in BACKENDS:
            package = ev/f'final-{name}/ProjectBroom-review.pk3'
            for args in (['archive', package], ['verify', str(package)+'.archive.json'], ['--compact', 'archive', package]):
                run([PY, '-m', 'tools.monster_models.review_archive', *args], ev/f'archive-{name}.log')
        print('archived', symbol, result[0]['sha256'][:12], result[0]['entries'])


def main():
    global EVIDENCE_ROOT, JOBS
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='command', required=True)
    c = sub.add_parser('precheck', help='fast parallel registry/binary + creature-test check (authoring agents run this)')
    c.add_argument('symbols', nargs='+'); c.add_argument('--log-dir', type=Path); c.set_defaults(func=cmd_precheck)
    ct = sub.add_parser('contact', help='contact sheet <folder>-contact.jpg from a capture folder')
    ct.add_argument('folder', type=Path); ct.add_argument('--cols', type=int, default=4); ct.set_defaults(func=cmd_contact)
    cb = sub.add_parser('check-binary'); cb.add_argument('symbol'); cb.set_defaults(func=cmd_check_binary)
    b = sub.add_parser('baseline'); b.add_argument('--batch', required=True); b.set_defaults(func=cmd_baseline)
    i = sub.add_parser('integrate'); i.add_argument('--batch', required=True); i.add_argument('symbols', nargs='+'); i.set_defaults(func=cmd_integrate)
    g = sub.add_parser('gate'); g.add_argument('--batch', required=True); g.add_argument('symbols', nargs='+')
    g.add_argument('--extra-tests', nargs='*', default=[], help='family regression modules, e.g. tools.monster_models.test_flame_turret')
    g.add_argument('--no-record', action='store_true', help='self-test only: do not write bestiary verification records')
    g.add_argument('--declare-change', action='append', default=[], metavar='PATH=REASON',
                   help='intended maintenance change to a baselined file; recorded in preservation.json')
    g.add_argument('--force', action='store_true', help='ignore cached determinism/Blender/gallery results')
    g.add_argument('--jobs', type=int, help=f'parallel determinism/Blender workers (default {JOBS})')
    g.set_defaults(func=cmd_gate)
    r = sub.add_parser('archive'); r.add_argument('symbols', nargs='+'); r.set_defaults(func=cmd_archive)
    p.add_argument('--evidence-root', type=Path, help='self-test only: write per-creature evidence under this directory')
    a = p.parse_args()
    if a.evidence_root:
        EVIDENCE_ROOT = a.evidence_root.resolve()
    if getattr(a, 'jobs', None):
        JOBS = a.jobs
    a.func(a)


if __name__ == '__main__':
    main()
