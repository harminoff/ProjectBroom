# Indexed Brogue creature models

Generated from the pinned Brogue CE catalog and exact `monsterText` in `Globals.c`.
Stable work IDs are `BRG-M00` through `BRG-M67`; they match catalog kinds, not live entity IDs.

## Scale and authority

Brogue gives no meter/foot dimensions. `isLarge`, prose, color, anatomy and relative comparisons are facts; all numerical dimensions below are presentation decisions. Do not infer body size from HP. A cell is 64 map units; the humanoid art reference is about 58 units and the existing rat is about 15 units tall. Large coils and wings are posed compactly, not used to widen collision. The underworm is intentionally bulkier than the ogre. The mirrored totem is shoulder-high. Pixies are smaller than humanoids. Dar are elves, not flying creatures; the dragon has no flight flag and is not given wings.

Dimensions are rest-pose X/Y/Z mesh extents including equipment and appendages, before separate flight clearance. Runtime bindings remain scale 1. Feet touch the local floor; levitating meshes have a documented 16-unit visual gap. Existing bridge visibility/submersion behavior is unchanged. Most forms remain static OBJs; the rat and kobold use weighted IQMs with six clips. See their work cards and the shared skeletal workflow.

## Work index

| ID | Brogue kind | Recipe | Size X/Y/Z | State |
| --- | --- | --- | --- | --- |
| [BRG-M00](creatures/00_you.md) | you (`MK_YOU`) | existing | reference | reference-only |
| [BRG-M01](creatures/01_rat.md) | rat (`MK_RAT`) | weighted-rat | 51.12 / 18.44 / 15 | authored-skeletal |
| [BRG-M02](creatures/02_kobold.md) | kobold (`MK_KOBOLD`) | weighted-kobold | 22.4004 / 18.6767 / 40.6239 | authored-skeletal |
| [BRG-M03](creatures/03_jackal.md) | jackal (`MK_JACKAL`) | weighted-jackal | 53.7992 / 13.4069 / 33.9777 | authored-skeletal |
| [BRG-M04](creatures/04_eel.md) | eel (`MK_EEL`) | serpent | 54 / 22 / 9 | authored-static |
| [BRG-M05](creatures/05_monkey.md) | monkey (`MK_MONKEY`) | weighted-monkey | 29.49 / 19.4024 / 32.2037 | authored-skeletal |
| [BRG-M06](creatures/06_bloat.md) | bloat (`MK_BLOAT`) | bloat | 28 / 28 / 32 | authored-static |
| [BRG-M07](creatures/07_pit_bloat.md) | pit bloat (`MK_PIT_BLOAT`) | bloat | 28 / 28 / 32 | authored-static |
| [BRG-M08](creatures/08_goblin.md) | goblin (`MK_GOBLIN`) | humanoid | 34 / 29 / 40 | authored-static |
| [BRG-M09](creatures/09_goblin_conjurer.md) | goblin conjurer (`MK_GOBLIN_CONJURER`) | humanoid | 24 / 32 / 40 | authored-static |
| [BRG-M10](creatures/10_goblin_mystic.md) | goblin mystic (`MK_GOBLIN_MYSTIC`) | humanoid | 24 / 32 / 40 | authored-static |
| [BRG-M11](creatures/11_goblin_totem.md) | goblin totem (`MK_GOBLIN_TOTEM`) | totem | 24 / 26 / 46 | authored-static |
| [BRG-M12](creatures/12_pink_jelly.md) | pink jelly (`MK_PINK_JELLY`) | slime | 50 / 46 / 30 | authored-static |
| [BRG-M13](creatures/13_toad.md) | toad (`MK_TOAD`) | toad | 38 / 35 / 25 | authored-static |
| [BRG-M14](creatures/14_vampire_bat.md) | vampire bat (`MK_VAMPIRE_BAT`) | winged | 24 / 58 / 28 | authored-static |
| [BRG-M15](creatures/15_arrow_turret.md) | arrow turret (`MK_ARROW_TURRET`) | turret | 30 / 32 / 38 | authored-static |
| [BRG-M16](creatures/16_acid_mound.md) | acid mound (`MK_ACID_MOUND`) | slime | 34 / 32 / 20 | authored-static |
| [BRG-M17](creatures/17_centipede.md) | centipede (`MK_CENTIPEDE`) | centipede | 56 / 35 / 13 | authored-static |
| [BRG-M18](creatures/18_ogre.md) | ogre (`MK_OGRE`) | humanoid | 44 / 46 / 82 | authored-static |
| [BRG-M19](creatures/19_bog_monster.md) | bog monster (`MK_BOG_MONSTER`) | tentacles | 58 / 58 / 42 | authored-static |
| [BRG-M20](creatures/20_ogre_totem.md) | ogre totem (`MK_OGRE_TOTEM`) | totem | 32 / 32 / 60 | authored-static |
| [BRG-M21](creatures/21_spider.md) | spider (`MK_SPIDER`) | spider | 52 / 58 / 24 | authored-static |
| [BRG-M22](creatures/22_spark_turret.md) | spark turret (`MK_SPARK_TURRET`) | turret | 30 / 32 / 42 | authored-static |
| [BRG-M23](creatures/23_will_o_the_wisp.md) | wisp (`MK_WILL_O_THE_WISP`) | flame | 20 / 20 / 30 | authored-static |
| [BRG-M24](creatures/24_wraith.md) | wraith (`MK_WRAITH`) | humanoid | 30 / 32 / 65 | authored-static |
| [BRG-M25](creatures/25_zombie.md) | zombie (`MK_ZOMBIE`) | humanoid | 32 / 36 / 62 | authored-static |
| [BRG-M26](creatures/26_troll.md) | troll (`MK_TROLL`) | humanoid | 46 / 50 / 86 | authored-static |
| [BRG-M27](creatures/27_ogre_shaman.md) | ogre shaman (`MK_OGRE_SHAMAN`) | humanoid | 42 / 44 / 70 | authored-static |
| [BRG-M28](creatures/28_naga.md) | naga (`MK_NAGA`) | serpent | 50 / 48 / 68 | authored-static |
| [BRG-M29](creatures/29_salamander.md) | salamander (`MK_SALAMANDER`) | serpent | 54 / 50 / 70 | authored-static |
| [BRG-M30](creatures/30_explosive_bloat.md) | explosive bloat (`MK_EXPLOSIVE_BLOAT`) | bloat | 30 / 30 / 34 | authored-static |
| [BRG-M31](creatures/31_dar_blademaster.md) | dar blademaster (`MK_DAR_BLADEMASTER`) | humanoid | 36 / 34 / 57 | authored-static |
| [BRG-M32](creatures/32_dar_priestess.md) | dar priestess (`MK_DAR_PRIESTESS`) | humanoid | 28 / 32 / 57 | authored-static |
| [BRG-M33](creatures/33_dar_battlemage.md) | dar battlemage (`MK_DAR_BATTLEMAGE`) | humanoid | 28 / 34 / 57 | authored-static |
| [BRG-M34](creatures/34_acid_jelly.md) | acidic jelly (`MK_ACID_JELLY`) | slime | 52 / 48 / 32 | authored-static |
| [BRG-M35](creatures/35_centaur.md) | centaur (`MK_CENTAUR`) | centaur | 58 / 42 / 78 | authored-static |
| [BRG-M36](creatures/36_underworm.md) | underworm (`MK_UNDERWORM`) | worm | 60 / 58 / 94 | authored-static |
| [BRG-M37](creatures/37_sentinel.md) | sentinel (`MK_SENTINEL`) | humanoid | 32 / 32 / 58 | authored-static |
| [BRG-M38](creatures/38_dart_turret.md) | dart turret (`MK_DART_TURRET`) | turret | 28 / 30 / 35 | authored-static |
| [BRG-M39](creatures/39_kraken.md) | kraken (`MK_KRAKEN`) | tentacles | 60 / 60 / 66 | authored-static |
| [BRG-M40](creatures/40_lich.md) | lich (`MK_LICH`) | humanoid | 30 / 36 / 66 | authored-static |
| [BRG-M41](creatures/41_phylactery.md) | phylactery (`MK_PHYLACTERY`) | gem | 18 / 18 / 22 | authored-static |
| [BRG-M42](creatures/42_pixie.md) | pixie (`MK_PIXIE`) | winged | 18 / 34 / 20 | authored-static |
| [BRG-M43](creatures/43_phantom.md) | phantom (`MK_PHANTOM`) | specter | 32 / 38 / 66 | authored-static |
| [BRG-M44](creatures/44_flame_turret.md) | flame turret (`MK_FLAME_TURRET`) | turret | 32 / 34 / 42 | authored-static |
| [BRG-M45](creatures/45_imp.md) | imp (`MK_IMP`) | humanoid | 30 / 30 / 35 | authored-static |
| [BRG-M46](creatures/46_fury.md) | fury (`MK_FURY`) | winged | 30 / 58 / 40 | authored-static |
| [BRG-M47](creatures/47_revenant.md) | revenant (`MK_REVENANT`) | specter | 34 / 40 / 70 | authored-static |
| [BRG-M48](creatures/48_tentacle_horror.md) | tentacle horror (`MK_TENTACLE_HORROR`) | tentacles | 60 / 60 / 106 | authored-static |
| [BRG-M49](creatures/49_golem.md) | golem (`MK_GOLEM`) | humanoid | 40 / 48 / 88 | authored-static |
| [BRG-M50](creatures/50_dragon.md) | dragon (`MK_DRAGON`) | dragon | 62 / 58 / 100 | authored-static |
| [BRG-M51](creatures/51_goblin_chieftan.md) | goblin warlord (`MK_GOBLIN_CHIEFTAN`) | humanoid | 38 / 36 / 51 | authored-static |
| [BRG-M52](creatures/52_black_jelly.md) | black jelly (`MK_BLACK_JELLY`) | slime | 54 / 50 / 34 | authored-static |
| [BRG-M53](creatures/53_vampire.md) | vampire (`MK_VAMPIRE`) | humanoid | 32 / 40 / 64 | authored-static |
| [BRG-M54](creatures/54_flamedancer.md) | flamedancer (`MK_FLAMEDANCER`) | flame | 40 / 46 / 80 | authored-static |
| [BRG-M55](creatures/55_spectral_blade.md) | spectral blade (`MK_SPECTRAL_BLADE`) | blade | 12 / 10 / 34 | authored-static |
| [BRG-M56](creatures/56_spectral_image.md) | spectral sword (`MK_SPECTRAL_IMAGE`) | blade | 16 / 12 / 42 | authored-static |
| [BRG-M57](creatures/57_guardian.md) | stone guardian (`MK_GUARDIAN`) | humanoid | 38 / 38 / 64 | authored-static |
| [BRG-M58](creatures/58_winged_guardian.md) | winged guardian (`MK_WINGED_GUARDIAN`) | humanoid | 32 / 60 / 66 | authored-static |
| [BRG-M59](creatures/59_charm_guardian.md) | guardian spirit (`MK_CHARM_GUARDIAN`) | humanoid | 38 / 38 / 64 | authored-static |
| [BRG-M60](creatures/60_warden_of_yendor.md) | Warden of Yendor (`MK_WARDEN_OF_YENDOR`) | humanoid | 44 / 48 / 92 | authored-static |
| [BRG-M61](creatures/61_eldritch_totem.md) | eldritch totem (`MK_ELDRITCH_TOTEM`) | totem | 30 / 30 / 56 | authored-static |
| [BRG-M62](creatures/62_mirrored_totem.md) | mirrored totem (`MK_MIRRORED_TOTEM`) | prism | 24 / 24 / 46 | authored-static |
| [BRG-M63](creatures/63_unicorn.md) | unicorn (`MK_UNICORN`) | quadruped | 60 / 30 / 70 | authored-static |
| [BRG-M64](creatures/64_ifrit.md) | ifrit (`MK_IFRIT`) | humanoid | 42 / 50 / 70 | authored-static |
| [BRG-M65](creatures/65_phoenix.md) | phoenix (`MK_PHOENIX`) | winged | 42 / 62 / 64 | authored-static |
| [BRG-M66](creatures/66_phoenix_egg.md) | phoenix egg (`MK_PHOENIX_EGG`) | egg | 26 / 26 / 25 | authored-static |
| [BRG-M67](creatures/67_ancient_spirit.md) | mangrove dryad (`MK_ANCIENT_SPIRIT`) | dryad | 48 / 58 / 84 | authored-static |

## Rebuild and verification

Run `python -m tools.monster_models.creatures`, then `python -m tools.monster_models.generate`. For a single work card use `python -m tools.monster_models.creatures --kind 2` (existing metrics for other kinds are retained). Build Blender sources with `tools/monster_models/blender_creatures.py` in Blender. The procedural Python definitions are the reproducible master; reconcile Blender hand edits before regeneration.

See [creature-model-rollout.md](creature-model-rollout.md) for actual verification evidence and remaining gates.
