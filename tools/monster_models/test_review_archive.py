"""Proof that storage compaction retains exact packages and fails safely."""
import json
from pathlib import Path
import tempfile
import unittest
import zipfile
from . import review_archive as archive


class ReviewArchiveTests(unittest.TestCase):
    def setUp(self):
        archive.ROOT.mkdir(parents=True, exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=archive.ROOT)
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()

    def package(self, folder, variant):
        path = self.root / folder / 'ProjectBroom-review.pk3'
        path.parent.mkdir()
        with zipfile.ZipFile(path, 'w') as output:
            for name, content in [('common.bin', bytes(range(256))*20), ('variant.txt', variant)]:
                entry = zipfile.ZipInfo(name, (2020, 1, 1, 0, 0, 0))
                entry.compress_type = zipfile.ZIP_DEFLATED
                output.writestr(entry, content)
        return path

    def test_exact_roundtrip_and_shared_segments(self):
        first = self.package('first', 'one')
        original = first.read_bytes()
        manifest = archive.archive(first, compact=True, root=self.root)
        self.assertFalse(first.exists())
        self.assertEqual(archive.restore(manifest, self.root).read_bytes(), original)
        second = self.package('second', 'two')
        other = archive.archive(second, root=self.root)
        a = json.loads(manifest.read_text())['segments']
        b = json.loads(other.read_text())['segments']
        self.assertEqual(a[0], b[0])
        self.assertLess(len(list((self.root/'.review-package-blobs').iterdir())), len(a)+len(b))

    def test_corrupt_storage_never_removes_original(self):
        package = self.package('corrupt', 'keep me')
        manifest = archive.archive(package, root=self.root)
        key = json.loads(manifest.read_text())['segments'][0]['sha256']
        (self.root/'.review-package-blobs'/key).write_bytes(b'corrupt')
        with self.assertRaises(ValueError):
            archive.archive(package, compact=True, root=self.root)
        self.assertTrue(package.exists())

    def test_containment_and_existing_package_protection(self):
        with self.assertRaises(ValueError):
            archive.archive(self.root.parent/'ProjectBroom-review.pk3', root=self.root)
        package = self.package('existing', 'original')
        manifest = archive.archive(package, root=self.root)
        package.write_bytes(b'new user data')
        with self.assertRaises(FileExistsError):
            archive.restore(manifest, self.root)
        self.assertEqual(package.read_bytes(), b'new user data')


if __name__ == '__main__':
    unittest.main()
