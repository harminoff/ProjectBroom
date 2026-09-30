# Indexed Brogue creature models

Generated from the pinned Brogue CE catalog and exact `monsterText` in `Globals.c`.
Stable work IDs are `BRG-M00` through `BRG-M67`; they match catalog kinds, not live entity IDs.

## Scale and authority

Brogue gives no meter/foot dimensions. `isLarge`, prose, color, anatomy and relative comparisons are facts; all numerical dimensions below are presentation decisions. Do not infer body size from HP. A cell is 64 map units; the humanoid art reference is about 58 units and the existing rat is about 15 units tall. Large coils and wings are posed compactly, not used to widen collision. The underworm is intentionally bulkier than the ogre. The mirrored totem is shoulder-high. Pixies are smaller than humanoids. Dar are elves, not flying creatures; the dragon has no flight flag and is not given wings.

Dimensions are rest-pose X/Y/Z mesh extents including equipment and appendages, before separate flight clearance. Feet touch the local floor; levitating meshes have a documented 16-unit visual gap. Profile-specific visual scale is recorded in MODELDEF. Existing bridge visibility/submersion behavior is unchanged. Entries marked authored-skeletal use weighted IQMs; the other forms remain static references. See their work cards and the shared skeletal workflow.

Work IDs follow catalog order, not encounter order. Prioritize ordinary hostile horde ranges when choosing the next enemy; captive, machine and out-of-depth appearances can differ. The toad and pink jelly both begin at nominal depth 4, before regular goblin mystic groups at depth 6. See [the toad report](toad-animation.md) for this encounter-order review.

## Work index

| ID | Brogue kind | Recipe | Size X/Y/Z | State |
| --- | --- | --- | --- | --- |
| [BRG-M00](creatures/00_you.md) | you (`MK_YOU`) | existing | reference | reference-only |
| [BRG-M01](creatures/01_rat.md) | rat (`MK_RAT`) | weighted-rat | 51.12 / 18.44 / 15 | authored-skeletal |
| [BRG-M02](creatures/02_kobold.md) | kobold (`MK_KOBOLD`) | weighted-kobold | 22.4004 / 18.6767 / 40.6239 | authored-skeletal |
| [BRG-M03](creatures/03_jackal.md) | jackal (`MK_JACKAL`) | weighted-jackal | 53.7992 / 13.4069 / 33.9777 | authored-skeletal |
| [BRG-M04](creatures/04_eel.md) | eel (`MK_EEL`) | weighted-eel | 54.8 / 7.3019 / 7.1643 | authored-skeletal |
| [BRG-M05](creatures/05_monkey.md) | monkey (`MK_MONKEY`) | weighted-monkey | 29.49 / 19.4024 / 32.2037 | authored-skeletal |
| [BRG-M06](creatures/06_bloat.md) | bloat (`MK_BLOAT`) | weighted-bloat | 28 / 26.3268 / 32 | authored-skeletal |
| [BRG-M07](creatures/07_pit_bloat.md) | pit bloat (`MK_PIT_BLOAT`) | weighted-pit_bloat | 28 / 26.3268 / 32 | authored-skeletal |
| [BRG-M08](creatures/08_goblin.md) | goblin (`MK_GOBLIN`) | weighted-goblin | 45.6812 / 30.8421 / 39.2134 | authored-skeletal |
| [BRG-M09](creatures/09_goblin_conjurer.md) | goblin conjurer (`MK_GOBLIN_CONJURER`) | weighted-goblin_conjurer | 11.8988 / 19.342 / 39.2134 | authored-skeletal |
| [BRG-M10](creatures/10_goblin_mystic.md) | goblin mystic (`MK_GOBLIN_MYSTIC`) | weighted-goblin_mystic | 11.8644 / 19.342 / 39.2134 | authored-skeletal |
| [BRG-M11](creatures/11_goblin_totem.md) | goblin totem (`MK_GOBLIN_TOTEM`) | weighted-goblin_totem | 17.8834 / 30.2326 / 49.9077 | authored-skeletal |
| [BRG-M12](creatures/12_pink_jelly.md) | pink jelly (`MK_PINK_JELLY`) | weighted-pink_jelly | 51.3996 / 44.4528 / 30.8001 | authored-skeletal |
| [BRG-M13](creatures/13_toad.md) | toad (`MK_TOAD`) | weighted-toad | 37.6618 / 44.0596 / 22.7728 | authored-skeletal |
| [BRG-M14](creatures/14_vampire_bat.md) | vampire bat (`MK_VAMPIRE_BAT`) | weighted-vampire_bat | 27.0483 / 55.7391 / 15.9853 | authored-skeletal |
| [BRG-M15](creatures/15_arrow_turret.md) | arrow turret (`MK_ARROW_TURRET`) | weighted-arrow_turret | 33.1 / 40.3246 / 41.76 | authored-skeletal |
| [BRG-M16](creatures/16_acid_mound.md) | acid mound (`MK_ACID_MOUND`) | weighted-acid_mound | 51.8415 / 38.9553 / 21.8001 | authored-skeletal |
| [BRG-M17](creatures/17_centipede.md) | centipede (`MK_CENTIPEDE`) | weighted-centipede | 55.0156 / 25.4424 / 10.4787 | authored-skeletal |
| [BRG-M18](creatures/18_ogre.md) | ogre (`MK_OGRE`) | weighted-ogre | 21.7472 / 44.9857 / 75.9189 | authored-skeletal |
| [BRG-M19](creatures/19_bog_monster.md) | bog monster (`MK_BOG_MONSTER`) | weighted-bog_monster | 50.9048 / 49.9174 / 29.9561 | authored-skeletal |
| [BRG-M20](creatures/20_ogre_totem.md) | ogre totem (`MK_OGRE_TOTEM`) | weighted-ogre_totem | 26.4058 / 44 / 64.45 | authored-skeletal |
| [BRG-M21](creatures/21_spider.md) | spider (`MK_SPIDER`) | weighted-spider | 44.8453 / 48.4549 / 19.0259 | authored-skeletal |
| [BRG-M22](creatures/22_spark_turret.md) | spark turret (`MK_SPARK_TURRET`) | weighted-spark_turret | 33 / 39 / 39 | authored-skeletal |
| [BRG-M23](creatures/23_will_o_the_wisp.md) | wisp (`MK_WILL_O_THE_WISP`) | weighted-will_o_the_wisp | 17.2263 / 17.0042 / 34 | authored-skeletal |
| [BRG-M24](creatures/24_wraith.md) | wraith (`MK_WRAITH`) | weighted-wraith | 18.3375 / 20.1193 / 60.6976 | authored-skeletal |
| [BRG-M25](creatures/25_zombie.md) | zombie (`MK_ZOMBIE`) | weighted-zombie | 15.005 / 19.9326 / 60.9856 | authored-skeletal |
| [BRG-M26](creatures/26_troll.md) | troll (`MK_TROLL`) | weighted-troll | 28.8988 / 51.2658 / 70.2376 | authored-skeletal |
| [BRG-M27](creatures/27_ogre_shaman.md) | ogre shaman (`MK_OGRE_SHAMAN`) | weighted-ogre_shaman | 30.8818 / 41.2218 / 76.3851 | authored-skeletal |
| [BRG-M28](creatures/28_naga.md) | naga (`MK_NAGA`) | weighted-naga | 43.5641 / 44.2237 / 57.3528 | authored-skeletal |
| [BRG-M29](creatures/29_salamander.md) | salamander (`MK_SALAMANDER`) | weighted-salamander | 43.6199 / 44.3444 / 62.7797 | authored-skeletal |
| [BRG-M30](creatures/30_explosive_bloat.md) | explosive bloat (`MK_EXPLOSIVE_BLOAT`) | weighted-explosive_bloat | 28 / 26.3268 / 32 | authored-skeletal |
| [BRG-M31](creatures/31_dar_blademaster.md) | dar blademaster (`MK_DAR_BLADEMASTER`) | weighted-dar_blademaster | 12.2682 / 21.1153 / 60.6471 | authored-skeletal |
| [BRG-M32](creatures/32_dar_priestess.md) | dar priestess (`MK_DAR_PRIESTESS`) | weighted-dar_priestess | 22.1681 / 22.5497 / 63.2855 | authored-skeletal |
| [BRG-M33](creatures/33_dar_battlemage.md) | dar battlemage (`MK_DAR_BATTLEMAGE`) | weighted-dar_battlemage | 13.2144 / 21.7189 / 63.9787 | authored-skeletal |
| [BRG-M34](creatures/34_acid_jelly.md) | acidic jelly (`MK_ACID_JELLY`) | weighted-acid_jelly | 54.2353 / 47.8787 / 21.2939 | authored-skeletal |
| [BRG-M35](creatures/35_centaur.md) | centaur (`MK_CENTAUR`) | weighted-centaur | 55.0225 / 28.5856 / 76.4161 | authored-skeletal |
| [BRG-M36](creatures/36_underworm.md) | underworm (`MK_UNDERWORM`) | weighted-underworm | 55.6958 / 55.1619 / 62.1957 | authored-skeletal |
| [BRG-M37](creatures/37_sentinel.md) | sentinel (`MK_SENTINEL`) | weighted-sentinel | 19.9058 / 26.1467 / 58.3936 | authored-skeletal |
| [BRG-M38](creatures/38_dart_turret.md) | dart turret (`MK_DART_TURRET`) | weighted-dart_turret | 35.7071 / 33 / 38 | authored-skeletal |
| [BRG-M39](creatures/39_kraken.md) | kraken (`MK_KRAKEN`) | weighted-kraken | 54.2565 / 53.0869 / 50.5231 | authored-skeletal |
| [BRG-M40](creatures/40_lich.md) | lich (`MK_LICH`) | weighted-lich | 25.0006 / 32.2392 / 65.7569 | authored-skeletal |
| [BRG-M41](creatures/41_phylactery.md) | phylactery (`MK_PHYLACTERY`) | weighted-phylactery | 37.4182 / 37.4182 / 48.49 | authored-skeletal |
| [BRG-M42](creatures/42_pixie.md) | pixie (`MK_PIXIE`) | weighted-pixie | 11.6068 / 29.0138 / 31.5074 | authored-skeletal |
| [BRG-M43](creatures/43_phantom.md) | phantom (`MK_PHANTOM`) | weighted-phantom | 30.5833 / 27.7051 / 58.8536 | authored-skeletal |
| [BRG-M44](creatures/44_flame_turret.md) | flame turret (`MK_FLAME_TURRET`) | weighted-flame_turret | 42.1101 / 35.24 / 42.9 | authored-skeletal |
| [BRG-M45](creatures/45_imp.md) | imp (`MK_IMP`) | weighted-imp | 23.4078 / 18.9453 / 46.3672 | authored-skeletal |
| [BRG-M46](creatures/46_fury.md) | fury (`MK_FURY`) | weighted-fury | 13.0074 / 49.9984 / 38.8254 | authored-skeletal |
| [BRG-M47](creatures/47_revenant.md) | revenant (`MK_REVENANT`) | weighted-revenant | 20.5227 / 40.8273 / 61.0307 | authored-skeletal |
| [BRG-M48](creatures/48_tentacle_horror.md) | tentacle horror (`MK_TENTACLE_HORROR`) | weighted-tentacle_horror | 55.8764 / 56.3155 / 80.9514 | authored-skeletal |
| [BRG-M49](creatures/49_golem.md) | golem (`MK_GOLEM`) | weighted-golem | 25.4562 / 50.1698 / 71.2235 | authored-skeletal |
| [BRG-M50](creatures/50_dragon.md) | dragon (`MK_DRAGON`) | weighted-dragon | 55.3107 / 39.1386 / 50.5965 | authored-skeletal |
| [BRG-M51](creatures/51_goblin_chieftan.md) | goblin warlord (`MK_GOBLIN_CHIEFTAN`) | weighted-goblin_chieftan | 30.5426 / 38.9821 / 54.7898 | authored-skeletal |
| [BRG-M52](creatures/52_black_jelly.md) | black jelly (`MK_BLACK_JELLY`) | weighted-black_jelly | 53.2612 / 50.6634 / 25.2147 | authored-skeletal |
| [BRG-M53](creatures/53_vampire.md) | vampire (`MK_VAMPIRE`) | weighted-vampire | 19.6499 / 24.9548 / 62.0759 | authored-skeletal |
| [BRG-M54](creatures/54_flamedancer.md) | flamedancer (`MK_FLAMEDANCER`) | weighted-flamedancer | 45.3604 / 51.2179 / 67.9 | authored-skeletal |
| [BRG-M55](creatures/55_spectral_blade.md) | spectral blade (`MK_SPECTRAL_BLADE`) | weighted-spectral_blade | 26.4946 / 48.2482 / 55.3674 | authored-skeletal |
| [BRG-M56](creatures/56_spectral_image.md) | spectral sword (`MK_SPECTRAL_IMAGE`) | weighted-spectral_image | 3.1231 / 19.6995 / 47.05 | authored-skeletal |
| [BRG-M57](creatures/57_guardian.md) | stone guardian (`MK_GUARDIAN`) | weighted-guardian | 26.4299 / 37.7507 / 64.481 | authored-skeletal |
| [BRG-M58](creatures/58_winged_guardian.md) | winged guardian (`MK_WINGED_GUARDIAN`) | weighted-winged_guardian | 34.5551 / 54.1001 / 69.7543 | authored-skeletal |
| [BRG-M59](creatures/59_charm_guardian.md) | guardian spirit (`MK_CHARM_GUARDIAN`) | weighted-charm_guardian | 25.3744 / 44.0904 / 61.6279 | authored-skeletal |
| [BRG-M60](creatures/60_warden_of_yendor.md) | Warden of Yendor (`MK_WARDEN_OF_YENDOR`) | weighted-warden_of_yendor | 21.7553 / 40.4183 / 69.1812 | authored-skeletal |
| [BRG-M61](creatures/61_eldritch_totem.md) | eldritch totem (`MK_ELDRITCH_TOTEM`) | weighted-eldritch_totem | 27.7142 / 28.2752 / 57.9 | authored-skeletal |
| [BRG-M62](creatures/62_mirrored_totem.md) | mirrored totem (`MK_MIRRORED_TOTEM`) | weighted-mirrored_totem | 26.154 / 30.2 / 56.9 | authored-skeletal |
| [BRG-M63](creatures/63_unicorn.md) | unicorn (`MK_UNICORN`) | weighted-unicorn | 57.7732 / 19.6421 / 66.7401 | authored-skeletal |
| [BRG-M64](creatures/64_ifrit.md) | ifrit (`MK_IFRIT`) | weighted-ifrit | 36.9518 / 57.1654 / 66.2329 | authored-skeletal |
| [BRG-M65](creatures/65_phoenix.md) | phoenix (`MK_PHOENIX`) | weighted-phoenix | 41.2597 / 53.8743 / 56.4399 | authored-skeletal |
| [BRG-M66](creatures/66_phoenix_egg.md) | phoenix egg (`MK_PHOENIX_EGG`) | weighted-phoenix_egg | 39.8315 / 38.9066 / 32.12 | authored-skeletal |
| [BRG-M67](creatures/67_ancient_spirit.md) | mangrove dryad (`MK_ANCIENT_SPIRIT`) | weighted-ancient_spirit | 50.1709 / 53.7189 / 72.8993 | authored-skeletal |

## Rebuild and verification

Run `python -m tools.monster_models.creatures`, then `python -m tools.monster_models.generate`. For a single work card use `python -m tools.monster_models.creatures --kind 2` (existing metrics for other kinds are retained). Build Blender sources with `tools/monster_models/blender_creatures.py` in Blender. The procedural Python definitions are the reproducible master; reconcile Blender hand edits before regeneration.

See [creature-model-rollout.md](creature-model-rollout.md) for actual verification evidence and remaining gates.
