# Pickup model index

100 Brogue item kinds plus five identity-safe generic forms. All dimensions
are artistic map-unit choices, not Brogue measurements. A cell is 64 units.
Models rest 0.12 units above their origin; no actor collision sizes change.

The editable source is [pickups.blend](../assets/items/pickups.blend): choose
the scene matching the runtime class and export only its ASSET collection.
The shared stage is preview-only. Python definitions remain the reproducible
master; reconcile hand edits before regenerating.

See [verification and scope](pickup-model-refresh.md) and the
[machine-readable index with exact Brogue prose](../assets/items/pickup-model-index.json).

| ID | Category / name | Dimensions X/Y/Z | Triangles | Brogue source |
| --- | --- | --- | --- | --- |
| BRG-P000 | [FOOD / ration of food](../mod/BrogueDoom/models/pickups/food_00.obj) | 14.0 / 10.0 / 6.407 | 380 | [catalog](../src/brogue-mapgen/src/brogue/Globals.c#L1578) |
| BRG-P001 | [FOOD / mango](../mod/BrogueDoom/models/pickups/food_01.obj) | 11.6 / 8.0 / 9.229 | 532 | [catalog](../src/brogue-mapgen/src/brogue/Globals.c#L1579) |
| BRG-P002 | [WEAPON / dagger](../mod/BrogueDoom/models/pickups/weapon_00.obj) | 33.55 / 12.22 / 2.9 | 2184 | [catalog](../src/brogue-mapgen/src/brogue/Globals.c#L1583) |
| BRG-P003 | [WEAPON / sword](../mod/BrogueDoom/models/pickups/weapon_01.obj) | 45.55 / 12.22 / 2.9 | 2184 | [catalog](../src/brogue-mapgen/src/brogue/Globals.c#L1584) |
| BRG-P004 | [WEAPON / broadsword](../mod/BrogueDoom/models/pickups/weapon_02.obj) | 56.0 / 11.302 / 2.682 | 3384 | [catalog](../src/brogue-mapgen/src/brogue/Globals.c#L1585) |
| BRG-P005 | [WEAPON / whip](../mod/BrogueDoom/models/pickups/weapon_03.obj) | 29.325 / 12.99 / 5.287 | 2440 | [catalog](../src/brogue-mapgen/src/brogue/Globals.c#L1587) |
| BRG-P006 | [WEAPON / rapier](../mod/BrogueDoom/models/pickups/weapon_04.obj) | 47.55 / 12.851 / 2.9 | 2484 | [catalog](../src/brogue-mapgen/src/brogue/Globals.c#L1588) |
| BRG-P007 | [WEAPON / flail](../mod/BrogueDoom/models/pickups/weapon_05.obj) | 27.075 / 13.397 / 7.4 | 4320 | [catalog](../src/brogue-mapgen/src/brogue/Globals.c#L1589) |
| BRG-P008 | [WEAPON / mace](../mod/BrogueDoom/models/pickups/weapon_06.obj) | 35.8 / 8.0 / 7.228 | 2028 | [catalog](../src/brogue-mapgen/src/brogue/Globals.c#L1591) |
| BRG-P009 | [WEAPON / war hammer](../mod/BrogueDoom/models/pickups/weapon_07.obj) | 37.2 / 12.5 / 4.8 | 1892 | [catalog](../src/brogue-mapgen/src/brogue/Globals.c#L1592) |
| BRG-P010 | [WEAPON / spear](../mod/BrogueDoom/models/pickups/weapon_08.obj) | 56.0 / 3.333 / 1.667 | 2008 | [catalog](../src/brogue-mapgen/src/brogue/Globals.c#L1594) |
| BRG-P011 | [WEAPON / war pike](../mod/BrogueDoom/models/pickups/weapon_09.obj) | 56.0 / 2.947 / 1.474 | 2008 | [catalog](../src/brogue-mapgen/src/brogue/Globals.c#L1595) |
| BRG-P012 | [WEAPON / axe](../mod/BrogueDoom/models/pickups/weapon_10.obj) | 37.8 / 11.55 / 3.1 | 2000 | [catalog](../src/brogue-mapgen/src/brogue/Globals.c#L1597) |
| BRG-P013 | [WEAPON / war axe](../mod/BrogueDoom/models/pickups/weapon_11.obj) | 46.8 / 14.55 / 3.1 | 2000 | [catalog](../src/brogue-mapgen/src/brogue/Globals.c#L1598) |
| BRG-P014 | [WEAPON / dart](../mod/BrogueDoom/models/pickups/weapon_12.obj) | 28.0 / 3.15 / 3.524 | 140 | [catalog](../src/brogue-mapgen/src/brogue/Globals.c#L1600) |
| BRG-P015 | [WEAPON / incendiary dart](../mod/BrogueDoom/models/pickups/weapon_13.obj) | 28.0 / 3.2 / 3.524 | 272 | [catalog](../src/brogue-mapgen/src/brogue/Globals.c#L1601) |
| BRG-P016 | [WEAPON / javelin](../mod/BrogueDoom/models/pickups/weapon_14.obj) | 56.0 / 3.944 / 1.972 | 2008 | [catalog](../src/brogue-mapgen/src/brogue/Globals.c#L1602) |
| BRG-P017 | [ARMOR / leather armor](../mod/BrogueDoom/models/pickups/armor_00.obj) | 23.6 / 20.75 / 7.5 | 1284 | [catalog](../src/brogue-mapgen/src/brogue/Globals.c#L1606) |
| BRG-P018 | [ARMOR / scale mail](../mod/BrogueDoom/models/pickups/armor_01.obj) | 23.6 / 20.75 / 6.856 | 2844 | [catalog](../src/brogue-mapgen/src/brogue/Globals.c#L1607) |
| BRG-P019 | [ARMOR / chain mail](../mod/BrogueDoom/models/pickups/armor_02.obj) | 23.6 / 20.75 / 6.8 | 6732 | [catalog](../src/brogue-mapgen/src/brogue/Globals.c#L1608) |
| BRG-P020 | [ARMOR / banded mail](../mod/BrogueDoom/models/pickups/armor_03.obj) | 23.6 / 20.75 / 7.7 | 1452 | [catalog](../src/brogue-mapgen/src/brogue/Globals.c#L1609) |
| BRG-P021 | [ARMOR / splint mail](../mod/BrogueDoom/models/pickups/armor_04.obj) | 23.6 / 20.75 / 7.65 | 1452 | [catalog](../src/brogue-mapgen/src/brogue/Globals.c#L1610) |
| BRG-P022 | [ARMOR / plate armor](../mod/BrogueDoom/models/pickups/armor_05.obj) | 23.6 / 20.75 / 7.807 | 1376 | [catalog](../src/brogue-mapgen/src/brogue/Globals.c#L1611) |
| BRG-P023 | [POTION / unidentified potion](../mod/BrogueDoom/models/pickups/potion_generic.obj) | 9.6 / 9.6 / 14.75 | 1072 | category-generic |
| BRG-P024 | [POTION / life](../mod/BrogueDoom/models/pickups/potion_00.obj) | 9.6 / 9.873 / 14.75 | 1228 | [catalog](../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L666) |
| BRG-P025 | [POTION / strength](../mod/BrogueDoom/models/pickups/potion_01.obj) | 9.6 / 9.873 / 14.75 | 1228 | [catalog](../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L667) |
| BRG-P026 | [POTION / telepathy](../mod/BrogueDoom/models/pickups/potion_02.obj) | 9.6 / 9.873 / 14.75 | 1228 | [catalog](../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L668) |
| BRG-P027 | [POTION / levitation](../mod/BrogueDoom/models/pickups/potion_03.obj) | 9.6 / 9.873 / 14.75 | 1264 | [catalog](../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L669) |
| BRG-P028 | [POTION / detect magic](../mod/BrogueDoom/models/pickups/potion_04.obj) | 9.6 / 9.873 / 14.75 | 1264 | [catalog](../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L670) |
| BRG-P029 | [POTION / speed](../mod/BrogueDoom/models/pickups/potion_05.obj) | 9.6 / 9.873 / 14.75 | 1264 | [catalog](../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L671) |
| BRG-P030 | [POTION / fire immunity](../mod/BrogueDoom/models/pickups/potion_06.obj) | 9.6 / 9.873 / 14.75 | 1300 | [catalog](../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L672) |
| BRG-P031 | [POTION / invisibility](../mod/BrogueDoom/models/pickups/potion_07.obj) | 9.6 / 9.873 / 14.75 | 1300 | [catalog](../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L673) |
| BRG-P032 | [POTION / caustic gas](../mod/BrogueDoom/models/pickups/potion_08.obj) | 9.6 / 9.873 / 14.75 | 1300 | [catalog](../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L674) |
| BRG-P033 | [POTION / paralysis](../mod/BrogueDoom/models/pickups/potion_09.obj) | 9.6 / 9.873 / 14.75 | 1336 | [catalog](../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L675) |
| BRG-P034 | [POTION / hallucination](../mod/BrogueDoom/models/pickups/potion_10.obj) | 9.6 / 9.873 / 14.75 | 1336 | [catalog](../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L676) |
| BRG-P035 | [POTION / confusion](../mod/BrogueDoom/models/pickups/potion_11.obj) | 9.6 / 9.873 / 14.75 | 1336 | [catalog](../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L677) |
| BRG-P036 | [POTION / incineration](../mod/BrogueDoom/models/pickups/potion_12.obj) | 9.6 / 9.873 / 14.75 | 1372 | [catalog](../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L678) |
| BRG-P037 | [POTION / darkness](../mod/BrogueDoom/models/pickups/potion_13.obj) | 9.6 / 9.873 / 14.75 | 1372 | [catalog](../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L679) |
| BRG-P038 | [POTION / descent](../mod/BrogueDoom/models/pickups/potion_14.obj) | 9.6 / 9.873 / 14.75 | 1372 | [catalog](../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L680) |
| BRG-P039 | [POTION / creeping death](../mod/BrogueDoom/models/pickups/potion_15.obj) | 9.6 / 9.873 / 14.75 | 1408 | [catalog](../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L681) |
| BRG-P040 | [SCROLL / unidentified scroll](../mod/BrogueDoom/models/pickups/scroll_generic.obj) | 20.1 / 11.04 / 3.3 | 2236 | category-generic |
| BRG-P041 | [SCROLL / enchanting](../mod/BrogueDoom/models/pickups/scroll_00.obj) | 20.1 / 11.04 / 3.3 | 2326 | [catalog](../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L685) |
| BRG-P042 | [SCROLL / identify](../mod/BrogueDoom/models/pickups/scroll_01.obj) | 20.1 / 11.04 / 3.3 | 2326 | [catalog](../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L686) |
| BRG-P043 | [SCROLL / teleportation](../mod/BrogueDoom/models/pickups/scroll_02.obj) | 20.1 / 11.04 / 3.3 | 2326 | [catalog](../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L687) |
| BRG-P044 | [SCROLL / remove curse](../mod/BrogueDoom/models/pickups/scroll_03.obj) | 20.1 / 11.04 / 3.3 | 2326 | [catalog](../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L688) |
| BRG-P045 | [SCROLL / recharging](../mod/BrogueDoom/models/pickups/scroll_04.obj) | 20.1 / 11.04 / 3.3 | 2326 | [catalog](../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L689) |
| BRG-P046 | [SCROLL / protect armor](../mod/BrogueDoom/models/pickups/scroll_05.obj) | 20.1 / 11.04 / 3.3 | 2326 | [catalog](../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L690) |
| BRG-P047 | [SCROLL / protect weapon](../mod/BrogueDoom/models/pickups/scroll_06.obj) | 20.1 / 11.04 / 3.3 | 2326 | [catalog](../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L691) |
| BRG-P048 | [SCROLL / sanctuary](../mod/BrogueDoom/models/pickups/scroll_07.obj) | 20.1 / 11.04 / 3.3 | 2326 | [catalog](../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L692) |
| BRG-P049 | [SCROLL / magic mapping](../mod/BrogueDoom/models/pickups/scroll_08.obj) | 20.1 / 11.04 / 3.3 | 2326 | [catalog](../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L693) |
| BRG-P050 | [SCROLL / negation](../mod/BrogueDoom/models/pickups/scroll_09.obj) | 20.1 / 11.04 / 3.3 | 2326 | [catalog](../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L694) |
| BRG-P051 | [SCROLL / shattering](../mod/BrogueDoom/models/pickups/scroll_10.obj) | 20.1 / 11.04 / 3.3 | 2326 | [catalog](../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L695) |
| BRG-P052 | [SCROLL / discord](../mod/BrogueDoom/models/pickups/scroll_11.obj) | 20.1 / 11.04 / 3.3 | 2326 | [catalog](../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L696) |
| BRG-P053 | [SCROLL / aggravate monsters](../mod/BrogueDoom/models/pickups/scroll_12.obj) | 20.1 / 11.04 / 3.3 | 2326 | [catalog](../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L697) |
| BRG-P054 | [SCROLL / summon monsters](../mod/BrogueDoom/models/pickups/scroll_13.obj) | 20.1 / 11.04 / 3.3 | 2326 | [catalog](../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L698) |
| BRG-P055 | [STAFF / unidentified staff](../mod/BrogueDoom/models/pickups/staff_generic.obj) | 46.223 / 4.4 / 4.0 | 624 | category-generic |
| BRG-P056 | [STAFF / lightning](../mod/BrogueDoom/models/pickups/staff_00.obj) | 46.223 / 4.4 / 4.114 | 714 | [catalog](../src/brogue-mapgen/src/brogue/Globals.c#L1642) |
| BRG-P057 | [STAFF / firebolt](../mod/BrogueDoom/models/pickups/staff_01.obj) | 46.223 / 4.4 / 4.114 | 714 | [catalog](../src/brogue-mapgen/src/brogue/Globals.c#L1643) |
| BRG-P058 | [STAFF / poison](../mod/BrogueDoom/models/pickups/staff_02.obj) | 46.223 / 4.4 / 4.114 | 714 | [catalog](../src/brogue-mapgen/src/brogue/Globals.c#L1644) |
| BRG-P059 | [STAFF / tunneling](../mod/BrogueDoom/models/pickups/staff_03.obj) | 46.223 / 4.4 / 4.114 | 714 | [catalog](../src/brogue-mapgen/src/brogue/Globals.c#L1645) |
| BRG-P060 | [STAFF / blinking](../mod/BrogueDoom/models/pickups/staff_04.obj) | 46.223 / 4.4 / 4.114 | 714 | [catalog](../src/brogue-mapgen/src/brogue/Globals.c#L1646) |
| BRG-P061 | [STAFF / entrancement](../mod/BrogueDoom/models/pickups/staff_05.obj) | 46.223 / 4.4 / 4.114 | 714 | [catalog](../src/brogue-mapgen/src/brogue/Globals.c#L1647) |
| BRG-P062 | [STAFF / obstruction](../mod/BrogueDoom/models/pickups/staff_06.obj) | 46.223 / 4.4 / 4.114 | 714 | [catalog](../src/brogue-mapgen/src/brogue/Globals.c#L1648) |
| BRG-P063 | [STAFF / discord](../mod/BrogueDoom/models/pickups/staff_07.obj) | 46.223 / 4.4 / 4.114 | 714 | [catalog](../src/brogue-mapgen/src/brogue/Globals.c#L1649) |
| BRG-P064 | [STAFF / conjuration](../mod/BrogueDoom/models/pickups/staff_08.obj) | 46.223 / 4.4 / 4.114 | 714 | [catalog](../src/brogue-mapgen/src/brogue/Globals.c#L1650) |
| BRG-P065 | [STAFF / healing](../mod/BrogueDoom/models/pickups/staff_09.obj) | 46.223 / 4.4 / 4.114 | 714 | [catalog](../src/brogue-mapgen/src/brogue/Globals.c#L1651) |
| BRG-P066 | [STAFF / haste](../mod/BrogueDoom/models/pickups/staff_10.obj) | 46.223 / 4.4 / 4.114 | 714 | [catalog](../src/brogue-mapgen/src/brogue/Globals.c#L1652) |
| BRG-P067 | [STAFF / protection](../mod/BrogueDoom/models/pickups/staff_11.obj) | 46.223 / 4.4 / 4.114 | 714 | [catalog](../src/brogue-mapgen/src/brogue/Globals.c#L1653) |
| BRG-P068 | [WAND / unidentified wand](../mod/BrogueDoom/models/pickups/wand_generic.obj) | 24.247 / 4.4 / 4.0 | 624 | category-generic |
| BRG-P069 | [WAND / teleportation](../mod/BrogueDoom/models/pickups/wand_00.obj) | 24.247 / 4.4 / 4.114 | 714 | [catalog](../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L702) |
| BRG-P070 | [WAND / slowness](../mod/BrogueDoom/models/pickups/wand_01.obj) | 24.247 / 4.4 / 4.114 | 714 | [catalog](../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L703) |
| BRG-P071 | [WAND / polymorphism](../mod/BrogueDoom/models/pickups/wand_02.obj) | 24.247 / 4.4 / 4.114 | 714 | [catalog](../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L704) |
| BRG-P072 | [WAND / negation](../mod/BrogueDoom/models/pickups/wand_03.obj) | 24.247 / 4.4 / 4.114 | 714 | [catalog](../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L705) |
| BRG-P073 | [WAND / domination](../mod/BrogueDoom/models/pickups/wand_04.obj) | 24.247 / 4.4 / 4.114 | 714 | [catalog](../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L706) |
| BRG-P074 | [WAND / beckoning](../mod/BrogueDoom/models/pickups/wand_05.obj) | 24.247 / 4.4 / 4.114 | 714 | [catalog](../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L707) |
| BRG-P075 | [WAND / plenty](../mod/BrogueDoom/models/pickups/wand_06.obj) | 24.247 / 4.4 / 4.114 | 714 | [catalog](../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L708) |
| BRG-P076 | [WAND / invisibility](../mod/BrogueDoom/models/pickups/wand_07.obj) | 24.247 / 4.4 / 4.114 | 714 | [catalog](../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L709) |
| BRG-P077 | [WAND / empowerment](../mod/BrogueDoom/models/pickups/wand_08.obj) | 24.247 / 4.4 / 4.114 | 714 | [catalog](../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L710) |
| BRG-P078 | [RING / unidentified ring](../mod/BrogueDoom/models/pickups/ring_generic.obj) | 9.693 / 11.06 / 3.086 | 744 | category-generic |
| BRG-P079 | [RING / clairvoyance](../mod/BrogueDoom/models/pickups/ring_00.obj) | 9.693 / 11.06 / 3.2 | 834 | [catalog](../src/brogue-mapgen/src/brogue/Globals.c#L1657) |
| BRG-P080 | [RING / stealth](../mod/BrogueDoom/models/pickups/ring_01.obj) | 9.693 / 11.06 / 3.2 | 834 | [catalog](../src/brogue-mapgen/src/brogue/Globals.c#L1658) |
| BRG-P081 | [RING / regeneration](../mod/BrogueDoom/models/pickups/ring_02.obj) | 9.693 / 11.06 / 3.2 | 834 | [catalog](../src/brogue-mapgen/src/brogue/Globals.c#L1659) |
| BRG-P082 | [RING / transference](../mod/BrogueDoom/models/pickups/ring_03.obj) | 9.693 / 11.06 / 3.2 | 834 | [catalog](../src/brogue-mapgen/src/brogue/Globals.c#L1660) |
| BRG-P083 | [RING / light](../mod/BrogueDoom/models/pickups/ring_04.obj) | 9.693 / 11.06 / 3.2 | 834 | [catalog](../src/brogue-mapgen/src/brogue/Globals.c#L1661) |
| BRG-P084 | [RING / awareness](../mod/BrogueDoom/models/pickups/ring_05.obj) | 9.693 / 11.06 / 3.2 | 834 | [catalog](../src/brogue-mapgen/src/brogue/Globals.c#L1662) |
| BRG-P085 | [RING / wisdom](../mod/BrogueDoom/models/pickups/ring_06.obj) | 9.693 / 11.06 / 3.2 | 834 | [catalog](../src/brogue-mapgen/src/brogue/Globals.c#L1663) |
| BRG-P086 | [RING / reaping](../mod/BrogueDoom/models/pickups/ring_07.obj) | 9.693 / 11.06 / 3.2 | 834 | [catalog](../src/brogue-mapgen/src/brogue/Globals.c#L1664) |
| BRG-P087 | [CHARM / health](../mod/BrogueDoom/models/pickups/charm_00.obj) | 20.058 / 21.004 / 3.464 | 6426 | [catalog](../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L714) |
| BRG-P088 | [CHARM / protection](../mod/BrogueDoom/models/pickups/charm_01.obj) | 20.058 / 21.004 / 3.464 | 6426 | [catalog](../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L715) |
| BRG-P089 | [CHARM / haste](../mod/BrogueDoom/models/pickups/charm_02.obj) | 20.058 / 21.004 / 3.464 | 6426 | [catalog](../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L716) |
| BRG-P090 | [CHARM / fire immunity](../mod/BrogueDoom/models/pickups/charm_03.obj) | 20.058 / 21.004 / 3.464 | 6426 | [catalog](../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L717) |
| BRG-P091 | [CHARM / invisibility](../mod/BrogueDoom/models/pickups/charm_04.obj) | 20.058 / 21.004 / 3.464 | 6426 | [catalog](../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L718) |
| BRG-P092 | [CHARM / telepathy](../mod/BrogueDoom/models/pickups/charm_05.obj) | 20.058 / 21.004 / 3.464 | 6426 | [catalog](../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L719) |
| BRG-P093 | [CHARM / levitation](../mod/BrogueDoom/models/pickups/charm_06.obj) | 20.058 / 21.004 / 3.464 | 6426 | [catalog](../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L720) |
| BRG-P094 | [CHARM / shattering](../mod/BrogueDoom/models/pickups/charm_07.obj) | 20.058 / 21.004 / 3.464 | 6426 | [catalog](../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L721) |
| BRG-P095 | [CHARM / guardian](../mod/BrogueDoom/models/pickups/charm_08.obj) | 20.058 / 21.004 / 3.464 | 6426 | [catalog](../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L722) |
| BRG-P096 | [CHARM / teleportation](../mod/BrogueDoom/models/pickups/charm_09.obj) | 20.058 / 21.004 / 3.464 | 6426 | [catalog](../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L724) |
| BRG-P097 | [CHARM / recharging](../mod/BrogueDoom/models/pickups/charm_10.obj) | 20.058 / 21.004 / 3.464 | 6426 | [catalog](../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L725) |
| BRG-P098 | [CHARM / negation](../mod/BrogueDoom/models/pickups/charm_11.obj) | 20.058 / 21.004 / 3.464 | 6426 | [catalog](../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L726) |
| BRG-P099 | [GOLD / gold](../mod/BrogueDoom/models/pickups/gold_00.obj) | 16.639 / 17.463 / 1.645 | 3744 | catalog category |
| BRG-P100 | [AMULET / Amulet of Yendor](../mod/BrogueDoom/models/pickups/amulet_00.obj) | 20.058 / 21.004 / 3.464 | 6426 | catalog category |
| BRG-P101 | [GEM / lumenstone](../mod/BrogueDoom/models/pickups/gem_00.obj) | 12.206 / 9.045 / 10.7 | 116 | catalog category |
| BRG-P102 | [KEY / door key](../mod/BrogueDoom/models/pickups/key_00.obj) | 28.25 / 9.2 / 1.888 | 448 | [catalog](../src/brogue-mapgen/src/brogue/Globals.c#L1572) |
| BRG-P103 | [KEY / cage key](../mod/BrogueDoom/models/pickups/key_01.obj) | 20.6 / 9.2 / 1.617 | 556 | [catalog](../src/brogue-mapgen/src/brogue/Globals.c#L1573) |
| BRG-P104 | [KEY / crystal orb](../mod/BrogueDoom/models/pickups/key_02.obj) | 11.413 / 9.045 / 10.0 | 80 | [catalog](../src/brogue-mapgen/src/brogue/Globals.c#L1574) |
