"""Lossless, shared-entry storage for this rollout's reproducible review PK3s.

The original ZIP byte stream is retained in content-addressed segments. Adjacent
local ZIP header offsets form boundaries, so unchanged resources deduplicate
across creature/backend packages. No source, captures or logs are removed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[2] / 'artifacts/creature-queue'


def contained(path, root):
    path, root = Path(path).resolve(), Path(root).resolve()
    path.relative_to(root)  # Reject paths outside this task's artifact tree.
    return path


def verify(manifest_path, root=ROOT):
    manifest_path = contained(manifest_path, root)
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    if manifest['schemaVersion'] != 1:
        raise ValueError('Unsupported archive version')
    digest, size = hashlib.sha256(), 0
    for segment in manifest['segments']:
        key = segment['sha256']
        if not re.fullmatch('[0-9a-f]{64}', key):
            raise ValueError('Invalid segment identity')
        blob = contained(Path(root) / '.review-package-blobs' / key, root)
        data = blob.read_bytes()
        if len(data) != segment['bytes'] or hashlib.sha256(data).hexdigest() != key:
            raise ValueError('Corrupt archive segment: ' + key)
        digest.update(data)
        size += len(data)
    if digest.hexdigest() != manifest['sha256'] or size != manifest['bytes']:
        raise ValueError('Package reconstruction mismatch')
    return manifest


def archive(package, compact=False, root=ROOT):
    package = contained(package, root)
    if package.name != 'ProjectBroom-review.pk3':
        raise ValueError('Only rollout review packages may be archived')
    data = package.read_bytes()
    with zipfile.ZipFile(package) as source:
        offsets = sorted({0, len(data), *(i.header_offset for i in source.infolist())})
    store = Path(root) / '.review-package-blobs'
    store.mkdir(parents=True, exist_ok=True)
    segments = []
    for start, end in zip(offsets, offsets[1:]):
        part = data[start:end]
        key = hashlib.sha256(part).hexdigest()
        blob = store / key
        if not blob.exists():
            with blob.open('xb') as stream:
                stream.write(part)
        segments.append(dict(sha256=key, bytes=len(part)))
    manifest = dict(schemaVersion=1, package=package.relative_to(Path(root).resolve()).as_posix(),
                    sha256=hashlib.sha256(data).hexdigest(), bytes=len(data), segments=segments)
    target = package.with_suffix('.pk3.archive.json')
    if target.exists() and json.loads(target.read_text()) != manifest:
        raise FileExistsError('Preserve the previous archive manifest: ' + str(target))
    target.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    verify(target, root)
    if compact:
        # A concurrent rewrite must never be removed based on an older archive.
        if hashlib.sha256(package.read_bytes()).hexdigest() != manifest['sha256']:
            raise RuntimeError('Review package changed during archival')
        package.unlink()
    return target


def restore(manifest_path, root=ROOT):
    manifest = verify(manifest_path, root)
    package = contained(Path(root) / manifest['package'], root)
    if package.name != 'ProjectBroom-review.pk3':
        raise ValueError('Unexpected restored package name')
    if package.exists():
        if hashlib.sha256(package.read_bytes()).hexdigest() != manifest['sha256']:
            raise FileExistsError('Preserve existing package: ' + str(package))
        return package
    temporary = package.with_suffix('.pk3.restoring')
    with temporary.open('xb') as output:
        for segment in manifest['segments']:
            output.write((Path(root) / '.review-package-blobs' / segment['sha256']).read_bytes())
    if hashlib.sha256(temporary.read_bytes()).hexdigest() != manifest['sha256']:
        raise RuntimeError('Restored package failed verification; original path untouched')
    temporary.rename(package)
    return package


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('archive', 'restore', 'verify'))
    parser.add_argument('path', type=Path)
    parser.add_argument('--compact', action='store_true', help='Remove only the fully recoverable original PK3')
    args = parser.parse_args()
    if args.compact and args.action != 'archive':
        parser.error('--compact applies only to archive')
    if args.action == 'archive':
        print(archive(args.path, args.compact))
    elif args.action == 'restore':
        print(restore(args.path))
    else:
        result = verify(args.path)
        print(result['sha256'], result['bytes'])


if __name__ == '__main__':
    main()
