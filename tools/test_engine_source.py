"""The engine gate must preserve unexpected work and reject stale binaries."""
import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from tools.engine_source import validate, validate_build, build_record, ENGINE_FILES


class EngineSourceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.checkout = self.root / ".deps/uzdoom-source"
        self.checkout.mkdir(parents=True)
        self.git("init", "-q")
        self.file = self.checkout / "source.cpp"
        self.file.write_text("upstream\n")
        self.git("add", "source.cpp")
        self.git("-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                 "commit", "-qm", "fixture")
        self.file.write_text("upstream\nbridge hook\n")
        patch = self.root / "patches/uzdoom-project-broom.patch"
        patch.parent.mkdir()
        patch.write_text(self.git("diff", "--no-ext-diff", "--binary", "--full-index"))
        component = {"commit": self.git("rev-parse", "HEAD").strip(),
                     "patch": "patches/uzdoom-project-broom.patch",
                     "patchSha256": hashlib.sha256(patch.read_bytes()).hexdigest()}
        (self.root / "dependencies.lock.json").write_text(json.dumps({"components": {"uzdoom": component}}))

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.checkout), *args],
                              check=True, capture_output=True, text=True).stdout

    def test_pristine_and_repeated_bootstrap(self):
        self.file.write_text("upstream\n")
        validate(self.root, apply=True)
        validate(self.root, apply=True)
        self.assertEqual(self.file.read_text(), "upstream\nbridge hook\n")

    def test_preserves_unexpected_tracked_edit(self):
        self.file.write_text("user work\n")
        with self.assertRaises(ValueError):
            validate(self.root, apply=True)
        self.assertEqual(self.file.read_text(), "user work\n")

    def test_rejects_untracked_and_staged_changes(self):
        extra = self.checkout / "extra.cpp"
        extra.write_text("user work")
        with self.assertRaises(ValueError):
            validate(self.root)
        self.git("add", "extra.cpp")
        with self.assertRaises(ValueError):
            validate(self.root)

    def test_rejects_modified_patch(self):
        (self.root / "patches/uzdoom-project-broom.patch").write_text("unexpected")
        with self.assertRaises(ValueError):
            validate(self.root)

    def test_source_archive_keeps_build_named_sources_and_patched_content(self):
        from tools.packaging.package_release import copy_corresponding_source
        (self.checkout / "buildtexture.cpp").write_text("required source")
        self.git("add", "buildtexture.cpp")
        (self.checkout / "untracked-cache").write_text("cache")
        target = self.root / "corresponding-source"
        copy_corresponding_source(self.checkout, target)
        self.assertEqual((target / "buildtexture.cpp").read_text(), "required source")
        self.assertEqual((target / "source.cpp").read_text(), "upstream\nbridge hook\n")
        self.assertFalse((target / "untracked-cache").exists())
        self.assertFalse((target / ".git").exists())

    def test_rejects_changed_binary_and_frontend(self):
        for name in ("src/gzdoom-bridge/brogue_bridge_frontend.cpp",
                     "src/gzdoom-bridge/brogue_bridge_frontend.h",
              "src/gzdoom-bridge/brogue_persistence_frontend.inc",
              "src/gzdoom-bridge/brogue_terrain_geometry_fixture.inc",
              "src/gzdoom-bridge/brogue_terrain_frontend.inc",
              "src/gzdoom-bridge/brogue_shoreline_frontend.inc",
              "src/gzdoom-bridge/shoreline.h",
              "src/gzdoom-bridge/terrain_reconciler.h",
              "src/gzdoom-bridge/terrain_animation.h",
              "src/gzdoom-bridge/brogue_terrain_animation.inc",
              "src/gzdoom-bridge/brogue_terrain_animation_probe.inc",
              "src/gzdoom-bridge/brogue_shoreline_probe.inc",
              "src/gzdoom-bridge/terrain_presentation.generated.h",
              "src/gzdoom-bridge/skeletal_presentation.generated.h",
              "src/gzdoom-bridge/enemy_movement.h",
              "src/gzdoom-bridge/held_movement.h",
                     "src/brogue-mapgen/src/brogue/BrogueBridge.h"):
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("fixture")
        engine = self.root / "engine"
        engine.mkdir()
        for name in ENGINE_FILES:
            (engine / name).write_bytes(b"fixture")
        receipt = build_record(self.root, engine)
        (engine / "project-broom-build.json").write_text(json.dumps(receipt))
        validate_build(self.root, engine)
        for name in ("shoreline.h", "brogue_shoreline_frontend.inc", "brogue_shoreline_probe.inc"):
            source = self.root / "src/gzdoom-bridge" / name
            source.write_text("changed shoreline")
            with self.assertRaises(ValueError):
                validate_build(self.root, engine)
            source.write_text("fixture")
        (engine / "uzdoom.exe").write_bytes(b"changed")
        with self.assertRaises(ValueError):
            validate_build(self.root, engine)
        (engine / "uzdoom.exe").write_bytes(b"fixture")
        (self.root / "src/gzdoom-bridge/brogue_bridge_frontend.cpp").write_text("changed")
        with self.assertRaises(ValueError):
            validate_build(self.root, engine)


if __name__ == "__main__":
    unittest.main()
