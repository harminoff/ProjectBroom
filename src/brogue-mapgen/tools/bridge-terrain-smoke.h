/* Synthetic setup is harness-only; execution uses normal Brogue action paths. */
static int runTerrainSmoke(BrogueBridgeState *state) {
    const uint64_t seed = state->gameSeed;
    BrogueBridgeTurnResult result;
    const int x = 32, y = 12;
#define TERRAIN_CHECK(c) do { if (!(c)) { fprintf(stderr, "TERRAIN check failed line=%d\n", __LINE__); return 1; } } while (0)
#define TERRAIN_REFRESH() do { \
    pmap[player.loc.x][player.loc.y-1].layers[DUNGEON] = WALL; \
    TERRAIN_CHECK(brogue_bridge_perform_action(BROGUE_ACTION_MOVE_N, &result) == BROGUE_BRIDGE_OK); \
    TERRAIN_CHECK(!result.consumedTurn); \
    TERRAIN_CHECK(brogue_bridge_get_state(state) == BROGUE_BRIDGE_OK); \
} while(0)
    pcell *cell = &pmap[x][y];
    memset(cell, 0, sizeof(*cell));
    cell->layers[DUNGEON] = SECRET_DOOR;
    cell->flags = VISIBLE | DISCOVERED;
    TERRAIN_REFRESH();
    BrogueBridgeTerrainAppearance a = state->cells[y*DCOLS+x].appearance;
    TERRAIN_CHECK(a.knowledge == BROGUE_TERRAIN_VISIBLE && !a.mechanism && (a.flags & BROGUE_APPEARANCE_WALL));
    cell->layers[DUNGEON] = FLOOR;
    cell->layers[SURFACE] = FLOOD_WATER_DEEP;
    cell->layers[LIQUID] = SHALLOW_WATER;
    cell->layers[GAS] = POISON_GAS;
    cell->volume = 37;
    TERRAIN_REFRESH();
    a = state->cells[y*DCOLS+x].appearance;
    TERRAIN_CHECK(a.liquidKind == BROGUE_LIQUID_DEEP_WATER && a.bedKind == BROGUE_LIQUID_SHALLOW_WATER
        && (a.flags & BROGUE_APPEARANCE_FLOOD) && a.gas == POISON_GAS && a.gasVolume == 37);
    cell->flags = DISCOVERED;
    cell->rememberedTerrain = FLOOR;
    cell->rememberedTerrainFlags = 0;
    cell->rememberedTMFlags = 0;
    cell->layers[DUNGEON] = WALL;
    TERRAIN_REFRESH();
    a = state->cells[y*DCOLS+x].appearance;
    TERRAIN_CHECK(a.knowledge == BROGUE_TERRAIN_REMEMBERED && a.structure == FLOOR && !a.gas && !a.liquid);
    cell->flags = MAGIC_MAPPED;
    cell->rememberedTerrain = SHALLOW_WATER;
    TERRAIN_REFRESH();
    a = state->cells[y*DCOLS+x].appearance;
    TERRAIN_CHECK(a.knowledge == BROGUE_TERRAIN_MAPPED && a.liquidKind == BROGUE_LIQUID_SHALLOW_WATER
        && !a.gas && !a.mechanism && !a.deck);
    cell->flags = 0;
    TERRAIN_REFRESH();
    a = state->cells[y*DCOLS+x].appearance;
    TERRAIN_CHECK(!a.knowledge && (a.flags & BROGUE_APPEARANCE_OPAQUE) && !a.gas && !a.structure);
    cell->flags = VISIBLE | DISCOVERED;
    cell->layers[DUNGEON] = FLOOR;
    cell->layers[LIQUID] = ICE_DEEP;
    cell->layers[SURFACE] = PLAIN_FIRE;
    TERRAIN_REFRESH();
    a = state->cells[y*DCOLS+x].appearance;
    TERRAIN_CHECK((a.flags & BROGUE_APPEARANCE_ICE) && a.fire == PLAIN_FIRE && a.gas == POISON_GAS);
    cell->layers[DUNGEON] = MACHINE_PRESSURE_PLATE_USED;
    TERRAIN_REFRESH();
    a = state->cells[y*DCOLS+x].appearance;
    TERRAIN_CHECK(a.mechanism == MACHINE_PRESSURE_PLATE_USED && (a.flags & BROGUE_APPEARANCE_DEPRESSED));
    unsigned long rng = randomNumbersGenerated;
    uint64_t turn = rogue.absoluteTurnNumber;
    for (int i = 0; i < 10; ++i) TERRAIN_REFRESH();
    TERRAIN_CHECK(rng == randomNumbersGenerated && turn == rogue.absoluteTurnNumber);
    printf("TERRAIN appearance=secret,memory,mapping,unknown,flood,ice,fire,gas captures=no-turn-no-rng\n");

    // Door promotion, discovered wall, blocked movement and ordinary wait:
    // compare native playerMoves/playerTurnEnded with bridge dispatch, including
    // a subsequent substantive RNG sample, on freshly repeated seeded sessions.
    for (int scenario = 0; scenario < 4; ++scenario) {
        uint64_t hash = 0, turns = 0; short continuation = 0;
        for (int route = 0; route < 2; ++route) {
            brogue_bridge_shutdown();
            TERRAIN_CHECK(brogue_bridge_start_game(seed) == BROGUE_BRIDGE_OK);
            const int px = player.loc.x, py = player.loc.y;
            for (int layer = 0; layer < NUMBER_TERRAIN_LAYERS; ++layer) pmap[px][py-1].layers[layer] = NOTHING;
            pmap[px][py-1].layers[DUNGEON] = scenario == 0 ? DOOR : scenario == 1 ? SECRET_DOOR : WALL;
            if (scenario == 1) discover(px, py-1);
            if (route) {
                TERRAIN_CHECK(brogue_bridge_perform_action(scenario == 3 ? BROGUE_ACTION_WAIT : BROGUE_ACTION_MOVE_N, &result) == BROGUE_BRIDGE_OK);
            } else if (scenario == 3) { rogue.justRested = true; playerTurnEnded(); }
            else playerMoves(UP);
            TERRAIN_REFRESH();
            /* Brogue's first appearance read can set STABLE_MEMORY after the
             * raw cell flags were copied. Settle both observers equally. */
            TERRAIN_REFRESH();
            rogue.RNG = RNG_SUBSTANTIVE;
            short sample = rand_range(0, 30000);
            if (!route) { hash = state->stateHash; turns = state->absoluteTurn; continuation = sample; }
            else {
                if (hash != state->stateHash || turns != state->absoluteTurn || continuation != sample)
                    fprintf(stderr, "TERRAIN mismatch scenario=%d hash=%016llx/%016llx turn=%llu/%llu rng=%d/%d\n", scenario,
                        (unsigned long long)hash, (unsigned long long)state->stateHash,
                        (unsigned long long)turns, (unsigned long long)state->absoluteTurn, continuation, sample);
                TERRAIN_CHECK(hash == state->stateHash && turns == state->absoluteTurn && continuation == sample);
            }
        }
        printf("TERRAIN parity=%d hash=%016llx turn=%llu rng=%d\n", scenario,
            (unsigned long long)hash, (unsigned long long)turns, continuation);
    }
#undef TERRAIN_REFRESH
#undef TERRAIN_CHECK
    return 0;
}
