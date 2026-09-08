"""Capture the unrefactored terminal command oracle; never overwrite a baseline."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
EXE = ROOT / "src/brogue-mapgen/bin/brogue-bridge.exe"
SCENARIOS = (
    "inscribe", "inscribe-clear", "inscribe-cancel", "inscribe-maximum",
    "inscribe-invalid", "inscribe-delete", "ring-inscribe", "kind-no",
    "kind-escape", "kind-clear", "relabel-uppercase", "relabel-swap",
    "relabel-unchanged", "relabel-invalid", "relabel-cancel",
    "food-yes", "food-no", "food-escape",
    "identify-valid", "identify-escape", "identify-empty",
    "enchant-valid", "enchant-escape", "enchant-empty",
    "equip-weapon", "equip-cursed", "equip-third-ring", "equip-third-ring-cancel", "equip-third-ring-cursed",
    "remove-weapon", "remove-cursed", "drop-weapon", "drop-cursed",
    "chasm-no", "chasm-escape", "chasm-yes",
    "throw-cancel", "throw-target", "throw-cycle-cancel",
    "staff-cancel", "staff-target", "wand-cancel", "wand-target",
    "acid-yes", "acid-no", "acid-escape", "sequential-yes", "sequential-no", "sequential-escape",
    "nested-inscribe", "nested-relabel",
)
SEEDS = (1, 2, 42, 12345, 99999)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def capture(destination, seeds=SEEDS, scenarios=SCENARIOS):
    destination = destination.resolve()
    destination.mkdir(parents=True, exist_ok=False)
    manifest = {"format": 1, "entry": "executeKeystroke", "cases": [], "sources": {}}
    manifest["head"] = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    manifest["status"] = subprocess.check_output(["git", "status", "--porcelain=v1"], cwd=ROOT, text=True)
    with zipfile.ZipFile(destination / "native-source.zip", "w", zipfile.ZIP_DEFLATED) as archive:
        for folder in ("src/brogue-mapgen/src", "src/brogue-mapgen/tools", "src/brogue-mapgen/make"):
            for path in sorted((ROOT / folder).rglob("*")):
                if not path.is_file() or path.suffix not in (".c", ".h", ".mk", ".def"):
                    continue
                data = path.read_bytes()
                relative = path.relative_to(ROOT).as_posix()
                manifest["sources"][relative] = sha(data)
                archive.writestr(relative, data)
    shutil.copy2(EXE, destination / "native-oracle.exe")
    manifest["executable_sha256"] = sha(EXE.read_bytes())
    for seed in seeds:
        for scenario in scenarios:
            case = {"seed": seed, "scenario": scenario}
            hashes = []
            for repeat in range(2):
                folder = destination / f"{seed}-{scenario}" / str(repeat)
                folder.mkdir(parents=True)
                run = subprocess.run([str(EXE), "--seed", str(seed), "--native-interaction-fixture", scenario],
                                     cwd=folder, capture_output=True, timeout=30)
                (folder / "terminal.txt").write_bytes(run.stdout)
                (folder / "stderr.txt").write_bytes(run.stderr)
                if run.returncode:
                    raise RuntimeError(f"{seed}/{scenario}: exit {run.returncode}: {run.stderr.decode(errors='replace')}")
                hashes.append({"terminal": sha(run.stdout),
                               "recording": sha((folder / "native-command.broguesave").read_bytes())})
            if hashes[0] != hashes[1]:
                raise RuntimeError(f"Non-deterministic native fixture: {seed}/{scenario}")
            case.update(hashes[0])
            manifest["cases"].append(case)
            print(f"NATIVE seed={seed} scenario={scenario} repeat=identical", flush=True)
    (destination / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def verify(baseline):
    manifest = json.loads((baseline / "manifest.json").read_text(encoding="utf-8"))
    for case in manifest["cases"]:
        with tempfile.TemporaryDirectory(prefix="broom-native-oracle-") as directory:
            run = subprocess.run([str(EXE), "--seed", str(case["seed"]), "--native-interaction-fixture", case["scenario"]],
                                 cwd=directory, capture_output=True, timeout=30)
            if run.returncode:
                raise RuntimeError(f"{case['seed']}/{case['scenario']}: {run.stderr.decode(errors='replace')}")
            recording = (Path(directory) / "native-command.broguesave").read_bytes()
            if sha(run.stdout) != case["terminal"] or sha(recording) != case["recording"]:
                raise RuntimeError(f"Frozen native oracle mismatch: {case['seed']}/{case['scenario']}")
    print(f"Frozen native oracle: {len(manifest['cases'])} transcript and recording comparisons passed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--seed", type=int, action="append")
    parser.add_argument("--scenario", choices=SCENARIOS, action="append")
    parser.add_argument("--verify", action="store_true", help="Compare current native execution against the frozen manifest")
    args = parser.parse_args()
    if args.verify:
        verify(args.destination)
    else:
        capture(args.destination, args.seed or SEEDS, args.scenario or SCENARIOS)
