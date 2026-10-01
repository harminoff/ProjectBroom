# Terrain description audit

All 215 pinned tile identities reviewed; 91 bindings corrected. Brogue descriptions and gameplay are unchanged.

The registry is not the whole renderer: stairs use map geometry; fire, gas, liquids, doors, wall light, and discovery have dedicated paths. Blank actor fields alone are not evidence of missing presentation. Secret forms retain Brogue disguises.

The rope bridge defect also involved a flush primary floor hiding the deck material. Both settled and shoreline refresh now retain the deck material there. Stone bridges use masonry; the active extending bridge is visible stone and its dormant form stays a chasm.

New surfaces and low-poly props are original CC0 assets. These establish the described material and silhouette; they are not claims of bespoke animation for every transient catalog phase. Colored light patches are surface treatments, not new lights. Known liquids keep their existing water/lava shaders and effects.

| Tile | Exact Brogue description | Audit result | Presentation / correction |
|---|---|---|---|
| `NOTHING` | a chilly void | Existing presentation | BRGEARTH; shared renderer / base geometry |
| `GRANITE` | a rough granite wall | Existing presentation | BRGEARTH; shared renderer / base geometry |
| `FLOOR` | the ground | Existing presentation | BRGEARTH; shared renderer / base geometry |
| `FLOOR_FLOODABLE` | the ground | Existing presentation | BRGEARTH; shared renderer / base geometry |
| `CARPET` | the carpet | Corrected | floor: BRGEARTH → BTCRPT |
| `MARBLE_FLOOR` | the marble ground | Corrected | floor: BRGEARTH → BTMARB |
| `WALL` | a stone wall | Existing presentation | BRGEARTH; shared renderer / base geometry |
| `DOOR` | a wooden door | Existing presentation | BRGEARTH; BrogueDoorMarker |
| `OPEN_DOOR` | an open door | Existing presentation | BRGEARTH; shared renderer / base geometry |
| `SECRET_DOOR` | a stone wall | Intentional disguise | BRGEARTH; shared renderer / base geometry |
| `LOCKED_DOOR` | a locked iron door | Corrected | actor: BrogueDoorMarker → BrogueCatalogIronDoor |
| `OPEN_IRON_DOOR_INERT` | an open iron door | Corrected | actor: none → BrogueCatalogOpenIronDoor |
| `DOWN_STAIRS` | a downward staircase | Existing presentation | BRGEARTH; shared renderer / base geometry |
| `UP_STAIRS` | an upward staircase | Existing presentation | BRGEARTH; shared renderer / base geometry |
| `DUNGEON_EXIT` | the dungeon exit | Ladder retained | Decorative exit doors removed because they obscure the existing ladder; no additional actor. |
| `DUNGEON_PORTAL` | a crystal portal | Corrected | actor: none → BrogueCatalogCrystalPortal |
| `TORCH_WALL` | a wall-mounted torch | Existing presentation | BRGEARTH; BrogueTerrainTorch |
| `CRYSTAL_WALL` | a crystal formation | Corrected | floor: BRGEARTH → BTCRYST; wall: BRGCAVE → BTCRYST |
| `PORTCULLIS_CLOSED` | a heavy portcullis | Existing presentation | BRGEARTH; BrogueTerrainGate |
| `PORTCULLIS_DORMANT` | the ground | Existing presentation | BRGEARTH; shared renderer / base geometry |
| `WOODEN_BARRICADE` | a dry wooden barricade | Existing presentation | BRGEARTH; BrogueBarricadeMarker |
| `PILOT_LIGHT_DORMANT` | a wall-mounted torch | Corrected | actor: none → BrogueTerrainTorch |
| `PILOT_LIGHT` | a fallen torch | Corrected | actor: none → BrogueCatalogFallenTorch |
| `HAUNTED_TORCH_DORMANT` | a wall-mounted torch | Existing presentation | BRGEARTH; BrogueTerrainTorch |
| `HAUNTED_TORCH_TRANSITIONING` | a wall-mounted torch | Existing presentation | BRGEARTH; BrogueTerrainTorch |
| `HAUNTED_TORCH` | a sputtering torch | Existing presentation | BRGEARTH; BrogueTerrainTorch |
| `WALL_LEVER_HIDDEN` | a stone wall | Intentional disguise | BRGEARTH; shared renderer / base geometry |
| `WALL_LEVER` | a lever | Existing presentation | BRGEARTH; BrogueSearchLever |
| `WALL_LEVER_PULLED` | an inactive lever | Existing presentation | BRGEARTH; BrogueSearchLever |
| `WALL_LEVER_HIDDEN_DORMANT` | a stone wall | Existing presentation | BRGEARTH; shared renderer / base geometry |
| `STATUE_INERT` | a marble statue | Existing presentation | BRGEARTH; BrogueTerrainStatueMarble |
| `STATUE_DORMANT` | a marble statue | Existing presentation | BRGEARTH; BrogueTerrainStatueMarble |
| `STATUE_CRACKING` | a cracking statue | Existing presentation | BRGEARTH; BrogueTerrainStatueCracked |
| `STATUE_INSTACRACK` | a marble statue | Existing presentation | BRGEARTH; BrogueTerrainStatueMarble |
| `PORTAL` | a stone archway | Corrected | actor: none → BrogueCatalogArch |
| `TURRET_DORMANT` | a stone wall | Existing presentation | BRGEARTH; shared renderer / base geometry |
| `WALL_MONSTER_DORMANT` | a stone wall | Existing presentation | BRGEARTH; shared renderer / base geometry |
| `DARK_FLOOR_DORMANT` | the ground | Existing presentation | BRGEARTH; shared renderer / base geometry |
| `DARK_FLOOR_DARKENING` | the ground | Existing presentation | BRGEARTH; shared renderer / base geometry |
| `DARK_FLOOR` | the ground | Existing presentation | BRGEARTH; shared renderer / base geometry |
| `MACHINE_TRIGGER_FLOOR` | the ground | Existing presentation | BRGEARTH; shared renderer / base geometry |
| `ALTAR_INERT` | a candle-lit altar | Corrected | actor: none → BrogueCatalogAltar |
| `ALTAR_KEYHOLE` | a candle-lit altar | Corrected | actor: none → BrogueCatalogAltar |
| `ALTAR_CAGE_OPEN` | a candle-lit altar | Corrected | actor: none → BrogueCatalogAltar |
| `ALTAR_CAGE_CLOSED` | an iron cage | Existing presentation | BRGEARTH; BrogueTerrainCage |
| `ALTAR_SWITCH` | a candle-lit altar | Corrected | actor: none → BrogueCatalogAltar |
| `ALTAR_SWITCH_RETRACTING` | a candle-lit altar | Corrected | actor: none → BrogueCatalogAltar |
| `ALTAR_CAGE_RETRACTABLE` | an iron cage | Existing presentation | BRGEARTH; BrogueTerrainCage |
| `PEDESTAL` | a stone pedestal | Corrected | actor: none → BrogueCatalogPedestal |
| `MONSTER_CAGE_OPEN` | an open cage | Corrected | actor: none → BrogueCatalogOpenCage |
| `MONSTER_CAGE_CLOSED` | a locked iron cage | Existing presentation | BRGEARTH; BrogueTerrainCage |
| `COFFIN_CLOSED` | a sealed coffin | Corrected | actor: none → BrogueCatalogCoffin |
| `COFFIN_OPEN` | an empty coffin | Corrected | actor: none → BrogueCatalogOpenCoffin |
| `GAS_TRAP_POISON_HIDDEN` | the ground | Intentional disguise | BRGEARTH; shared renderer / base geometry |
| `GAS_TRAP_POISON` | a caustic gas trap | Existing presentation | BRGEARTH; BrogueSearchPlate |
| `TRAP_DOOR_HIDDEN` | the ground | Intentional disguise | BRGEARTH; shared renderer / base geometry |
| `TRAP_DOOR` | a hole | Existing presentation | BRGVOID; shared renderer / base geometry |
| `GAS_TRAP_PARALYSIS_HIDDEN` | the ground | Intentional disguise | BRGEARTH; shared renderer / base geometry |
| `GAS_TRAP_PARALYSIS` | a paralysis trigger | Existing presentation | BRGEARTH; BrogueSearchPlate |
| `MACHINE_PARALYSIS_VENT_HIDDEN` | the ground | Intentional disguise | BRGEARTH; shared renderer / base geometry |
| `MACHINE_PARALYSIS_VENT` | an inactive gas vent | Existing presentation | BRGEARTH; BrogueSearchVent |
| `GAS_TRAP_CONFUSION_HIDDEN` | the ground | Intentional disguise | BRGEARTH; shared renderer / base geometry |
| `GAS_TRAP_CONFUSION` | a confusion trap | Existing presentation | BRGEARTH; BrogueSearchPlate |
| `FLAMETHROWER_HIDDEN` | the ground | Intentional disguise | BRGEARTH; shared renderer / base geometry |
| `FLAMETHROWER` | a fire trap | Existing presentation | BRGEARTH; BrogueSearchFire |
| `FLOOD_TRAP_HIDDEN` | the ground | Intentional disguise | BRGEARTH; shared renderer / base geometry |
| `FLOOD_TRAP` | a flood trap | Existing presentation | BRGEARTH; BrogueSearchFlood |
| `NET_TRAP_HIDDEN` | the ground | Intentional disguise | BRGEARTH; shared renderer / base geometry |
| `NET_TRAP` | a net trap | Existing presentation | BRGEARTH; BrogueSearchNet |
| `ALARM_TRAP_HIDDEN` | the ground | Intentional disguise | BRGEARTH; shared renderer / base geometry |
| `ALARM_TRAP` | an alarm trap | Existing presentation | BRGEARTH; BrogueSearchAlarm |
| `MACHINE_POISON_GAS_VENT_HIDDEN` | the ground | Intentional disguise | BRGEARTH; shared renderer / base geometry |
| `MACHINE_POISON_GAS_VENT_DORMANT` | an inactive gas vent | Existing presentation | BRGEARTH; BrogueSearchVent |
| `MACHINE_POISON_GAS_VENT` | a gas vent | Existing presentation | BRGEARTH; BrogueSearchVent |
| `MACHINE_METHANE_VENT_HIDDEN` | the ground | Intentional disguise | BRGEARTH; shared renderer / base geometry |
| `MACHINE_METHANE_VENT_DORMANT` | an inactive gas vent | Existing presentation | BRGEARTH; BrogueSearchVent |
| `MACHINE_METHANE_VENT` | a gas vent | Existing presentation | BRGEARTH; BrogueSearchVent |
| `STEAM_VENT` | a steam vent | Existing presentation | BRGEARTH; BrogueSearchVent |
| `MACHINE_PRESSURE_PLATE` | a pressure plate | Existing presentation | BRGEARTH; BrogueSearchPlate |
| `MACHINE_PRESSURE_PLATE_USED` | an inactive pressure plate | Existing presentation | BRGEARTH; BrogueSearchPlate |
| `MACHINE_GLYPH` | a magical glyph | Corrected | floor: BRGEARTH → BTGLYPH |
| `MACHINE_GLYPH_INACTIVE` | a glowing glyph | Corrected | floor: BRGEARTH → BTGLYPH |
| `DEWAR_CAUSTIC_GAS` | a glass dewar of caustic gas | Corrected | actor: none → BrogueCatalogDewarCaustic |
| `DEWAR_CONFUSION_GAS` | a glass dewar of confusion gas | Corrected | actor: none → BrogueCatalogDewarConfusion |
| `DEWAR_PARALYSIS_GAS` | a glass dewar of paralytic gas | Corrected | actor: none → BrogueCatalogDewarParalysis |
| `DEWAR_METHANE_GAS` | a glass dewar of methane gas | Corrected | actor: none → BrogueCatalogDewarMethane |
| `DEEP_WATER` | the murky waters | Existing presentation | BRGWATR; shared renderer / base geometry |
| `SHALLOW_WATER` | shallow water | Existing presentation | BRGWATR; shared renderer / base geometry |
| `MUD` | a bog | Existing presentation | BRGSLDG; shared renderer / base geometry |
| `CHASM` | a chasm | Existing presentation | BRGVOID; shared renderer / base geometry |
| `CHASM_EDGE` | the brink of a chasm | Existing presentation | BRGEARTH; shared renderer / base geometry |
| `MACHINE_COLLAPSE_EDGE_DORMANT` | the ground | Existing presentation | BRGEARTH; shared renderer / base geometry |
| `MACHINE_COLLAPSE_EDGE_SPREADING` | the crumbling ground | Corrected | floor: BRGEARTH → BTCRUMB |
| `LAVA` | lava | Existing presentation | BRGMOLT; shared renderer / base geometry |
| `LAVA_RETRACTABLE` | lava | Existing presentation | BRGMOLT; shared renderer / base geometry |
| `LAVA_RETRACTING` | cooling lava | Corrected | floor: BRGMOLT → BTCOOL |
| `SUNLIGHT_POOL` | a patch of sunlight | Corrected | floor: BRGEARTH → BTSUN |
| `DARKNESS_PATCH` | a patch of shadows | Corrected | floor: BRGEARTH → BTSHADE |
| `ACTIVE_BRIMSTONE` | hissing brimstone | Corrected | floor: BRGEARTH → BTBRIM |
| `INERT_BRIMSTONE` | hissing brimstone | Corrected | floor: BRGEARTH → BTBRIM |
| `OBSIDIAN` | the obsidian ground | Corrected | floor: BRGEARTH → BTOBSD |
| `BRIDGE` | a rickety rope bridge | Corrected | actor: none → BrogueCatalogRopeBridge; flush-ground texture corrected; rope side supports added |
| `BRIDGE_FALLING` | a plummeting bridge | Corrected | actor: none → BrogueCatalogRopeBridge; flush-ground texture corrected; rope side supports added |
| `BRIDGE_EDGE` | a rickety rope bridge | Corrected | actor: none → BrogueCatalogRopeBridge; flush-ground texture corrected; rope side supports added |
| `STONE_BRIDGE` | a stone bridge | Corrected | floor: BRGBRID → BTMARB |
| `MACHINE_FLOOD_WATER_DORMANT` | shallow water | Existing presentation | BRGWATR; shared renderer / base geometry |
| `MACHINE_FLOOD_WATER_SPREADING` | shallow water | Existing presentation | BRGWATR; shared renderer / base geometry |
| `MACHINE_MUD_DORMANT` | a bog | Existing presentation | BRGSLDG; shared renderer / base geometry |
| `ICE_DEEP` | ice | Existing presentation | BRGICE; shared renderer / base geometry |
| `ICE_DEEP_MELT` | melting ice | Existing presentation | BRGICE; shared renderer / base geometry |
| `ICE_SHALLOW` | ice | Existing presentation | BRGICE; shared renderer / base geometry |
| `ICE_SHALLOW_MELT` | melting ice | Existing presentation | BRGICE; shared renderer / base geometry |
| `HOLE` | a hole | Existing presentation | BRGVOID; shared renderer / base geometry |
| `HOLE_GLOW` | a hole | Existing presentation | BRGVOID; shared renderer / base geometry |
| `HOLE_EDGE` | translucent ground | Corrected | floor: BRGEARTH → BTFADE |
| `FLOOD_WATER_DEEP` | sloshing water | Existing presentation | BRGWATR; shared renderer / base geometry |
| `FLOOD_WATER_SHALLOW` | shallow water | Existing presentation | BRGWATR; shared renderer / base geometry |
| `GRASS` | grass-like fungus | Existing presentation | BRGMOSS; BrogueGrassProp |
| `DEAD_GRASS` | withered fungus | Existing presentation | BRGMOSS; BrogueDeadVegetationProp |
| `GRAY_FUNGUS` | withered fungus | Corrected | actor: BrogueFungusProp → BrogueCatalogWitheredFungus |
| `LUMINESCENT_FUNGUS` | luminescent fungus | Existing presentation | BRGMOSS; BrogueLuminousFungusProp |
| `LICHEN` | deadly lichen | Corrected | floor: BRGEARTH → BTLICHN |
| `HAY` | filthy hay | Corrected | floor: BRGEARTH → BTHAY |
| `RED_BLOOD` | a pool of blood | Corrected | floor: BRGEARTH → BTBLOOD |
| `GREEN_BLOOD` | a pool of green blood | Corrected | floor: BRGEARTH → BTGREEN |
| `PURPLE_BLOOD` | a pool of purple blood | Corrected | floor: BRGEARTH → BTPURPL |
| `ACID_SPLATTER` | a puddle of acid | Corrected | floor: BRGEARTH → BTACID |
| `VOMIT` | a puddle of vomit | Corrected | floor: BRGEARTH → BTVOMIT |
| `URINE` | a puddle of urine | Corrected | floor: BRGEARTH → BTURINE |
| `UNICORN_POOP` | unicorn poop | Corrected | actor: none → BrogueCatalogDroppings |
| `WORM_BLOOD` | a pool of worm entrails | Corrected | floor: BRGEARTH → BTENTRL |
| `ASH` | a pile of ashes | Corrected | floor: BRGEARTH → BTASH |
| `BURNED_CARPET` | burned carpet | Corrected | floor: BRGEARTH → BTBURN |
| `PUDDLE` | a puddle of water | Corrected | floor: BRGEARTH → BTPUDDL |
| `BONES` | a pile of bones | Corrected | actor: none → BrogueCatalogBones |
| `RUBBLE` | a pile of rubble | Corrected | actor: none → BrogueCatalogRubble |
| `JUNK` | a pile of filthy effects | Corrected | actor: none → BrogueCatalogJunk |
| `BROKEN_GLASS` | shattered glass | Corrected | actor: none → BrogueCatalogGlass |
| `ECTOPLASM` | ectoplasmic residue | Corrected | floor: BRGEARTH → BTECTO |
| `EMBERS` | sputtering embers | Corrected | floor: BRGEARTH → BTEMBR |
| `SPIDERWEB` | a spiderweb | Corrected | actor: none → BrogueCatalogWeb |
| `NETTING` | a net | Corrected | actor: none → BrogueCatalogNet |
| `FOLIAGE` | dense foliage | Existing presentation | BRGMOSS; BrogueFoliageProp |
| `DEAD_FOLIAGE` | dead foliage | Existing presentation | BRGMOSS; BrogueDeadVegetationProp |
| `TRAMPLED_FOLIAGE` | trampled foliage | Corrected | actor: BrogueFoliageProp → BrogueCatalogTrampledLeaves |
| `FUNGUS_FOREST` | a luminescent fungal forest | Corrected | actor: BrogueFungusProp → BrogueCatalogFungalForest |
| `TRAMPLED_FUNGUS_FOREST` | trampled fungal foliage | Corrected | actor: BrogueFungusProp → BrogueCatalogTrampledFungus |
| `FORCEFIELD` | a green crystal | Corrected | floor: BRGEARTH → BTCRYST; wall: BRGCAVE → BTCRYST |
| `FORCEFIELD_MELT` | a dissolving crystal | Corrected | floor: BRGEARTH → BTCRYST; wall: BRGCAVE → BTCRYST |
| `SACRED_GLYPH` | a sacred glyph | Corrected | floor: BRGEARTH → BTGLYPH |
| `MANACLE_TL` | an iron manacle | Existing presentation | BRGEARTH; BrogueTerrainManacleCeiling |
| `MANACLE_BR` | an iron manacle | Existing presentation | BRGEARTH; BrogueTerrainManacleFloor |
| `MANACLE_TR` | an iron manacle | Existing presentation | BRGEARTH; BrogueTerrainManacleCeiling |
| `MANACLE_BL` | an iron manacle | Existing presentation | BRGEARTH; BrogueTerrainManacleFloor |
| `MANACLE_T` | an iron manacle | Existing presentation | BRGEARTH; BrogueTerrainManacleWall |
| `MANACLE_B` | an iron manacle | Existing presentation | BRGEARTH; BrogueTerrainManacleWall |
| `MANACLE_L` | an iron manacle | Existing presentation | BRGEARTH; BrogueTerrainManacleWall |
| `MANACLE_R` | an iron manacle | Existing presentation | BRGEARTH; BrogueTerrainManacleWall |
| `PORTAL_LIGHT` | blinding light | Corrected | floor: BRGEARTH → BTSUN |
| `GUARDIAN_GLOW` | a red glow | Corrected | floor: BRGEARTH → BTGLOW |
| `PLAIN_FIRE` | billowing flames | Existing presentation | BRGEARTH; shared renderer / base geometry |
| `BRIMSTONE_FIRE` | sulfurous flames | Existing presentation | BRGEARTH; shared renderer / base geometry |
| `FLAMEDANCER_FIRE` | clouds of infernal flame | Existing presentation | BRGEARTH; shared renderer / base geometry |
| `GAS_FIRE` | a cloud of burning gas | Existing presentation | BRGEARTH; shared renderer / base geometry |
| `GAS_EXPLOSION` | a violent explosion | Existing presentation | BRGEARTH; shared renderer / base geometry |
| `DART_EXPLOSION` | a flash of fire | Existing presentation | BRGEARTH; shared renderer / base geometry |
| `ITEM_FIRE` | crackling flames | Existing presentation | BRGEARTH; shared renderer / base geometry |
| `CREATURE_FIRE` | greasy flames | Existing presentation | BRGEARTH; shared renderer / base geometry |
| `POISON_GAS` | a cloud of caustic gas | Existing presentation | BRGEARTH; shared renderer / base geometry |
| `CONFUSION_GAS` | a cloud of confusion gas | Existing presentation | BRGEARTH; shared renderer / base geometry |
| `ROT_GAS` | a cloud of putrescence | Existing presentation | BRGEARTH; shared renderer / base geometry |
| `STENCH_SMOKE_GAS` | a cloud of putrid smoke | Existing presentation | BRGEARTH; shared renderer / base geometry |
| `PARALYSIS_GAS` | a cloud of paralytic gas | Existing presentation | BRGEARTH; shared renderer / base geometry |
| `METHANE_GAS` | a cloud of explosive gas | Existing presentation | BRGEARTH; shared renderer / base geometry |
| `STEAM` | a cloud of scalding steam | Existing presentation | BRGEARTH; shared renderer / base geometry |
| `DARKNESS_CLOUD` | a cloud of supernatural darkness | Existing presentation | BRGEARTH; shared renderer / base geometry |
| `HEALING_CLOUD` | a cloud of healing spores | Existing presentation | BRGEARTH; shared renderer / base geometry |
| `BLOODFLOWER_STALK` | a bloodwort stalk | Existing presentation | BRGEARTH; BrogueTerrainBloodwortStalk |
| `BLOODFLOWER_POD` | a bloodwort pod | Existing presentation | BRGEARTH; BrogueTerrainBloodwortPod |
| `HAVEN_BEDROLL` | an abandoned bedroll | Corrected | actor: none → BrogueCatalogBedroll |
| `DEEP_WATER_ALGAE_WELL` | the ground | Corrected | floor: BRGWATR → BRGEARTH |
| `DEEP_WATER_ALGAE_1` | luminescent waters | Corrected | actor: none → BrogueCatalogAlgae |
| `DEEP_WATER_ALGAE_2` | luminescent waters | Corrected | actor: none → BrogueCatalogDenseAlgae |
| `ANCIENT_SPIRIT_VINES` | thorned vines | Corrected | actor: none → BrogueCatalogVines |
| `ANCIENT_SPIRIT_GRASS` | a tuft of grass | Existing presentation | BRGMOSS; BrogueGrassProp |
| `AMULET_SWITCH` | the ground | Existing presentation | BRGEARTH; shared renderer / base geometry |
| `COMMUTATION_ALTAR` | a commutation altar | Corrected | actor: none → BrogueCatalogCommuteAltar |
| `COMMUTATION_ALTAR_INERT` | a scorched altar | Corrected | actor: none → BrogueCatalogScorchedAltar |
| `PIPE_GLOWING` | glowing glass pipes | Corrected | actor: none → BrogueCatalogPipes |
| `PIPE_INERT` | charred glass pipes | Corrected | actor: none → BrogueCatalogBurntPipes |
| `RESURRECTION_ALTAR` | a resurrection altar | Corrected | actor: none → BrogueCatalogResurrectAltar |
| `RESURRECTION_ALTAR_INERT` | a scorched altar | Corrected | actor: none → BrogueCatalogScorchedAltar |
| `MACHINE_TRIGGER_FLOOR_REPEATING` | the ground | Existing presentation | BRGEARTH; shared renderer / base geometry |
| `SACRIFICE_ALTAR_DORMANT` | a sacrificial altar | Corrected | actor: none → BrogueCatalogSacrificeAltar |
| `SACRIFICE_ALTAR` | a sacrifice altar | Corrected | actor: none → BrogueCatalogSacrificeAltar |
| `SACRIFICE_LAVA` | a sacrificial pit | Existing presentation | BRGMOLT; shared renderer / base geometry |
| `SACRIFICE_CAGE_DORMANT` | an iron cage | Corrected | actor: none → BrogueTerrainCage |
| `DEMONIC_STATUE` | a demonic statue | Existing presentation | BRGEARTH; BrogueTerrainStatueDemon |
| `STATUE_INERT_DOORWAY` | a broken statue | Existing presentation | BRGEARTH; BrogueTerrainStatueBroken |
| `STATUE_DORMANT_DOORWAY` | a marble statue | Existing presentation | BRGEARTH; BrogueTerrainStatueMarble |
| `CHASM_WITH_HIDDEN_BRIDGE` | a chasm | Corrected | floor: BRGBRID → BRGVOID |
| `CHASM_WITH_HIDDEN_BRIDGE_ACTIVE` | a stone bridge | Corrected | floor: BRGBRID → BTMARB; visible identity now projects as STONE_BRIDGE, not CHASM |
| `MACHINE_CHASM_EDGE` | the brink of a chasm | Existing presentation | BRGEARTH; shared renderer / base geometry |
| `RAT_TRAP_WALL_DORMANT` | a stone wall | Existing presentation | BRGEARTH; shared renderer / base geometry |
| `RAT_TRAP_WALL_CRACKING` | a cracking wall | Corrected | wall: BRGCAVE → BTCRUMB |
| `ELECTRIC_CRYSTAL_OFF` | a darkened crystal globe | Corrected | actor: none → BrogueCatalogCrystalOff |
| `ELECTRIC_CRYSTAL_ON` | a shining crystal globe | Corrected | actor: none → BrogueCatalogCrystalOn |
| `TURRET_LEVER` | a lever | Corrected | actor: none → BrogueSearchLever |
| `WORM_TUNNEL_MARKER_DORMANT` | (no description) | Existing presentation | BRGEARTH; shared renderer / base geometry |
| `WORM_TUNNEL_MARKER_ACTIVE` | a rough granite wall | Existing presentation | BRGEARTH; shared renderer / base geometry |
| `WORM_TUNNEL_OUTER_WALL` | a stone wall | Existing presentation | BRGEARTH; shared renderer / base geometry |
| `BRAZIER` | a ceremonial brazier | Corrected | actor: none → BrogueCatalogBrazier |
| `MUD_FLOOR` | the mud floor | Corrected | floor: BRGEARTH → BTMUD |
| `MUD_WALL` | a mud-covered wall | Corrected | wall: BRGCAVE → BTMUD |
| `MUD_DOORWAY` | hanging animal skins | Corrected | wall: BRGCAVE → BTMUD; actor: none → BrogueCatalogSkins |
