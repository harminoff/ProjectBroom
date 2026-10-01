# Weapon model generation output

Run `python tools/weapon_models/generate.py` from the repository root.
The generator produces presentation assets only; Brogue rules and RNG are
unchanged.

Weapon and device OBJ/MD3 files and the hand atlas use a shared output writer
in `tools/weapon_models/output.py`. Identical bytes leave the existing file
and timestamp untouched. Changed bytes are written to a temporary file in
the destination directory, closed, and then replaced into place. A failed
replacement preserves the previous model, cleans up the temporary file,
and fails the build with the destination path and original OS error.

This addresses unnecessary overwrite attempts seen with intermittent
Windows `OSError: [Errno 22]` failures on `weapon_02.obj` and `wand.md3`.
The original environmental trigger has not been reproduced. A genuinely
locked or unwritable changed asset still requires releasing its file handle
or correcting its permissions; generation must not silently accept stale data.

Regression coverage is part of `tools.weapon_models.test_devices`, including
unchanged output, failed replacement, complete replacement, and native text
newlines. The weapon/device asset suites check generated geometry and binary
contents against their sources.
