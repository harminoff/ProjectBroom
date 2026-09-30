# Explorer set pieces

Project Broom adds sparse visual traces of previous expeditions to otherwise
empty dry rooms. Current motifs are abandoned camps, lost explorers, discarded
supplies, and creature dens. They combine original bedroll, bone, hide, junk,
rubble, and fallen-torch meshes from the terrain catalog.

This is presentation-only work. The map compiler selects at most three anchors
per ordinary floor, places them beside solid walls, keeps them away from stairs,
and rejects liquids, gas, machines, special dungeon terrain, and occupied
surface layers. The actors inherit `BrogueTerrainStone`, which has
`NOINTERACTION`, `NOBLOCKMAP`, and `NOGRAVITY`; they cannot block movement,
be targeted, contain loot, deal damage, or consume turns.

Placement uses SHA-256 over game seed, depth, and cell coordinates. This is a
separate cosmetic stream and never calls or advances Brogue CE's RNG. Identical
map inputs therefore remain byte-identical. The package verifier recomputes the
complete set-piece layout and rejects missing, moved, or extra actors.

All reused meshes and `BTATLAS.png` are original Project Broom assets dedicated
to CC0-1.0. See `assets/terrain/CATALOG-LICENSE.md`.
