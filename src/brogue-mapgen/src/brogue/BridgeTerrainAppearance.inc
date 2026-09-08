/* Read-only knowledge projection. Included after terrainFeatureForTile. */
static enum tileType appearanceTile(enum tileType tile) {
    if (!validTile(tile)) return NOTHING;
    if (tileCatalog[tile].mechFlags & TM_IS_SECRET) {
        return tileCatalog[tile].displayChar == tileCatalog[GRANITE].displayChar
            || tileCatalog[tile].displayChar == tileCatalog[WALL].displayChar ? WALL : FLOOR;
    }
    /* These catalog forms have identical visible chasm/ground presentation. */
    if (tile == CHASM_WITH_HIDDEN_BRIDGE || tile == CHASM_WITH_HIDDEN_BRIDGE_ACTIVE) return CHASM;
    return tile;
}

static void appearanceAddTile(BrogueBridgeTerrainAppearance *out, enum tileType tile,
                              int layer, boolean remembered) {
    tile = appearanceTile(tile);
    if (tile == NOTHING) return;
    const unsigned long flags = tileCatalog[tile].flags;
    const BrogueBridgeTerrainFeature feature = terrainFeatureForTile(tile);
    if (tile == MACHINE_PRESSURE_PLATE || tile == MACHINE_PRESSURE_PLATE_USED) {
        out->mechanism = tile;
        if (tile == MACHINE_PRESSURE_PLATE_USED) out->flags |= BROGUE_APPEARANCE_DEPRESSED;
    }
    if (layer == GAS) { out->gas = tile; return; }
    if (flags & T_IS_FIRE) { out->fire = tile; return; }
    if (tileIsBridge(tile)) { out->deck = tile; out->flags |= BROGUE_APPEARANCE_BRIDGE; return; }
    if (tile == ICE_DEEP || tile == ICE_DEEP_MELT || tile == ICE_SHALLOW || tile == ICE_SHALLOW_MELT) {
        out->deck = tile; out->flags |= BROGUE_APPEARANCE_ICE;
        out->liquidKind = tile == ICE_DEEP || tile == ICE_DEEP_MELT ? BROGUE_LIQUID_DEEP_WATER : BROGUE_LIQUID_SHALLOW_WATER;
        out->bedKind = out->liquidKind;
        return;
    }
    if (tileIsLiquid(tile) || tileIsLava(tile)) {
        out->liquid = tile;
        out->liquidKind = tileIsLava(tile) ? BROGUE_LIQUID_LAVA : tile == MUD || tile == MACHINE_MUD_DORMANT
            ? BROGUE_LIQUID_MUD : flags & T_IS_DEEP_WATER ? BROGUE_LIQUID_DEEP_WATER : BROGUE_LIQUID_SHALLOW_WATER;
        if (layer == SURFACE || tile == FLOOD_WATER_SHALLOW || tile == FLOOD_WATER_DEEP
            || tile == MACHINE_FLOOD_WATER_SPREADING || tile == MACHINE_FLOOD_WATER_DORMANT)
            out->flags |= BROGUE_APPEARANCE_FLOOD;
        else out->bedKind = out->liquidKind;
        return;
    }
    if (flags & T_AUTO_DESCENT) { out->ground = tile; out->flags |= BROGUE_APPEARANCE_HOLE; return; }
    if (feature >= BROGUE_FEATURE_DOOR_CLOSED && feature != BROGUE_FEATURE_HOLE) out->mechanism = tile;
    if ((flags & T_OBSTRUCTS_PASSABILITY) && (flags & T_OBSTRUCTS_VISION)
        && feature != BROGUE_FEATURE_DOOR_CLOSED) {
        out->structure = tile;
        out->flags |= BROGUE_APPEARANCE_WALL | BROGUE_APPEARANCE_OPAQUE;
    } else if (feature == BROGUE_FEATURE_DOOR_CLOSED) {
        out->structure = FLOOR;
    } else if (layer == DUNGEON || remembered) out->structure = tile;
    else out->ground = tile;
}

static void captureTerrainAppearance(BrogueBridgeTerrainAppearance *out, int x, int y) {
    const pcell *cell = &pmap[x][y];
    memset(out, 0, sizeof(*out));
    if (playerCanSeeOrSense(x, y)) {
        out->knowledge = BROGUE_TERRAIN_VISIBLE;
        for (int layer = 0; layer < NUMBER_TERRAIN_LAYERS; ++layer)
            appearanceAddTile(out, cell->layers[layer], layer, false);
        if (out->gas) {
            out->gasVolume = cell->volume;
            const color *gasColor = tileCatalog[out->gas].backColor;
            if (gasColor) {
                out->gasRed = clamp(gasColor->red, 0, 100) * 255 / 100;
                out->gasGreen = clamp(gasColor->green, 0, 100) * 255 / 100;
                out->gasBlue = clamp(gasColor->blue, 0, 100) * 255 / 100;
            }
        }
        if (out->mechanism && (cell->flags & PRESSURE_PLATE_DEPRESSED)) out->flags |= BROGUE_APPEARANCE_DEPRESSED;
    } else if (cell->flags & (DISCOVERED | MAGIC_MAPPED)) {
        out->knowledge = cell->flags & DISCOVERED ? BROGUE_TERRAIN_REMEMBERED : BROGUE_TERRAIN_MAPPED;
        appearanceAddTile(out, cell->rememberedTerrain, DUNGEON, true);
        /* Memory flags recover support information without inspecting live layers. */
        if (!(out->flags & (BROGUE_APPEARANCE_BRIDGE | BROGUE_APPEARANCE_ICE))
            && !(cell->rememberedTMFlags & TM_IS_SECRET)
            && (cell->rememberedTerrainFlags & T_AUTO_DESCENT)) out->flags |= BROGUE_APPEARANCE_HOLE;
        if (out->mechanism && (cell->rememberedCellFlags & PRESSURE_PLATE_DEPRESSED)) out->flags |= BROGUE_APPEARANCE_DEPRESSED;
        /* A remembered flame is not an observed ongoing fire. */
        out->fire = out->gas = out->gasVolume = 0;
    } else {
        out->flags = BROGUE_APPEARANCE_WALL | BROGUE_APPEARANCE_OPAQUE;
    }
}
