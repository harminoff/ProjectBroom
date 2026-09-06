/* Test-only deterministic differential fixtures; no public gameplay hooks. */
static int runSearchSmoke(BrogueBridgeState *state) {
    const uint64_t seed = state->gameSeed;
    const int secrets[] = {SECRET_DOOR, WALL_LEVER_HIDDEN, GAS_TRAP_POISON_HIDDEN,
        TRAP_DOOR_HIDDEN, GAS_TRAP_PARALYSIS_HIDDEN, MACHINE_PARALYSIS_VENT_HIDDEN,
        GAS_TRAP_CONFUSION_HIDDEN, FLAMETHROWER_HIDDEN, FLOOD_TRAP_HIDDEN,
        NET_TRAP_HIDDEN, ALARM_TRAP_HIDDEN, MACHINE_POISON_GAS_VENT_HIDDEN,
        MACHINE_METHANE_VENT_HIDDEN};
    for (int scenario = 0; scenario < 21; ++scenario) {
        uint64_t referenceHash = 0, referenceTurn = 0;
        unsigned long referenceRng = 0;
        int referenceProgress = 0;
        for (int route = 0; route < 2; ++route) {
            BrogueBridgeCommand command = {0};
            BrogueBridgeTurnResult turn;
            unsigned long rngBefore;
            uint64_t beforeTurn;
            int steps = 0;
#define SEARCH_CHECK(c) do { if (!(c)) { fprintf(stderr, "Search case=%d route=%d line=%d failed.\n", scenario, route, __LINE__); return 1; } } while (0)
            brogue_bridge_shutdown();
            SEARCH_CHECK(brogue_bridge_start_game(seed) == BROGUE_BRIDGE_OK);
            pmapAt(player.loc)->flags &= ~HAS_PLAYER;
            player.loc = (pos){32, 12};
            player.currentHP = player.info.maxHP = 10000;
            // Keep generated monsters outside a fully explored enclosed arena.
            for (int x = 25; x <= 40; ++x) for (int y = 5; y <= 20; ++y) {
                for (int l = 0; l < NUMBER_TERRAIN_LAYERS; ++l) pmap[x][y].layers[l] = NOTHING;
                pmap[x][y].layers[DUNGEON] = (x == 25 || x == 40 || y == 5 || y == 20) ? WALL : FLOOR;
                pmap[x][y].flags |= DISCOVERED;
                pmap[x][y].flags &= ~HAS_MONSTER;
            }
            for (creatureIterator it = iterateCreatures(monsters); hasNextCreature(it);) {
                creature *m = nextCreature(&it);
                m->ticksUntilTurn = 10000;
            }
            pmapAt(player.loc)->flags |= HAS_PLAYER;
            SEARCH_CHECK(brogue_bridge_perform_action(BROGUE_ACTION_WAIT, &turn) == BROGUE_BRIDGE_OK);
            if (scenario < 13) {
                pmap[33][12].layers[DUNGEON] = secrets[scenario];
                pmap[33][12].flags |= VISIBLE;
            }
            if (scenario >= 19) {
                pmap[33][12].layers[DUNGEON] = GAS_TRAP_POISON_HIDDEN;
                pmap[33][12].flags |= VISIBLE;
            }
            if (scenario == 19) pmapAt(player.loc)->flags &= ~SEARCHED_FROM_HERE;
            rogue.awarenessBonus = scenario == 15 ? -20 : (scenario < 13 || scenario == 16 || scenario >= 19 ? 200 : 0);
            if (scenario == 14) {
                executeKeystroke(SEARCH_KEY, false, false);
                executeKeystroke(SEARCH_KEY, false, false);
            }
            rngBefore = randomNumbersGenerated;
            beforeTurn = rogue.absoluteTurnNumber;
            if (route == 0) {
                command.apiVersion = BROGUE_BRIDGE_API_VERSION;
                command.type = BROGUE_COMMAND_SEARCH_CONTINUE;
                SEARCH_CHECK(brogue_bridge_perform_command(&command, &turn) == BROGUE_BRIDGE_INVALID_STATE);
                command.type = BROGUE_COMMAND_SEARCH_START;
                command.apiVersion--;
                SEARCH_CHECK(brogue_bridge_perform_command(&command, &turn) == BROGUE_BRIDGE_INVALID_ACTION);
                command.apiVersion++;
                SEARCH_CHECK(brogue_bridge_get_state(state) == BROGUE_BRIDGE_OK);
                command.expectedRevision = state->revision + 1;
                SEARCH_CHECK(brogue_bridge_perform_command(&command, &turn) == BROGUE_BRIDGE_STALE_REVISION);
                command.expectedRevision = 0;
                SEARCH_CHECK(randomNumbersGenerated == rngBefore && rogue.absoluteTurnNumber == beforeTurn);
                if (scenario == 19) {
                    SEARCH_CHECK(brogue_bridge_perform_action(BROGUE_ACTION_WAIT, &turn) == BROGUE_BRIDGE_OK);
                } else if (scenario < 13 || scenario == 17) {
                    SEARCH_CHECK(brogue_bridge_perform_action(BROGUE_ACTION_SEARCH, &turn) == BROGUE_BRIDGE_OK);
                } else if (scenario == 18) {
                    SEARCH_CHECK(brogue_bridge_perform_command(&command, &turn) == BROGUE_BRIDGE_OK);
                    SEARCH_CHECK(brogue_bridge_get_state(state) == BROGUE_BRIDGE_OK && state->player.searchActive);
                    const uint64_t revision = state->revision;
                    const uint64_t cancelTurn = rogue.absoluteTurnNumber;
                    const unsigned long cancelRng = randomNumbersGenerated;
                    command.type = BROGUE_COMMAND_SEARCH_CANCEL;
                    SEARCH_CHECK(brogue_bridge_perform_command(&command, &turn) == BROGUE_BRIDGE_OK);
                    SEARCH_CHECK(!turn.consumedTurn && turn.revision == revision + 1);
                    SEARCH_CHECK(randomNumbersGenerated == cancelRng && rogue.absoluteTurnNumber == cancelTurn);
                } else {
                    do {
                        SEARCH_CHECK(++steps <= 5);
                        SEARCH_CHECK(brogue_bridge_perform_command(&command, &turn) == BROGUE_BRIDGE_OK && turn.consumedTurn);
                        SEARCH_CHECK(brogue_bridge_get_state(state) == BROGUE_BRIDGE_OK);
                        SEARCH_CHECK(state->player.searchProgress == player.status[STATUS_SEARCHING]);
                        SEARCH_CHECK(state->player.searchMaximum == player.maxStatus[STATUS_SEARCHING]);
                        command.type = BROGUE_COMMAND_SEARCH_CONTINUE;
                    } while (state->player.searchActive);
                }
            } else {
                executeKeystroke(scenario == 19 ? REST_KEY : SEARCH_KEY,
                    scenario >= 13 && scenario != 17 && scenario != 18 && scenario != 19, false);
            }
            if (scenario == 13) SEARCH_CHECK(player.status[STATUS_SEARCHING] == 0 && rogue.absoluteTurnNumber - beforeTurn == 5);
            if (scenario == 14) SEARCH_CHECK(player.status[STATUS_SEARCHING] == 0 && rogue.absoluteTurnNumber - beforeTurn == 3);
            if (scenario < 13) SEARCH_CHECK(!cellHasTMFlag(((pos){33, 12}), TM_IS_SECRET));
            if (scenario >= 19) SEARCH_CHECK(!cellHasTMFlag(((pos){33, 12}), TM_IS_SECRET));
            if (scenario == 20) SEARCH_CHECK(rogue.absoluteTurnNumber - beforeTurn == 1);
            const int progress = player.status[STATUS_SEARCHING];
            SEARCH_CHECK(!rogue.repeatedSearchActive);
            SEARCH_CHECK(brogue_bridge_perform_action(BROGUE_ACTION_WAIT, &turn) == BROGUE_BRIDGE_OK);
            SEARCH_CHECK(brogue_bridge_get_state(state) == BROGUE_BRIDGE_OK);
            if (route == 0) {
                referenceHash = state->stateHash;
                referenceTurn = state->absoluteTurn;
                referenceRng = randomNumbersGenerated - rngBefore;
                referenceProgress = progress;
            } else {
                SEARCH_CHECK(referenceHash == state->stateHash && referenceTurn == state->absoluteTurn);
                SEARCH_CHECK(referenceRng == randomNumbersGenerated - rngBefore && referenceProgress == progress);
                printf("SEARCH case=%d parity=true hash=%016llx rng=%lu progress=%d\n", scenario,
                    (unsigned long long)state->stateHash, referenceRng, progress);
            }
#undef SEARCH_CHECK
        }
    }
    // Cancellation preserves the complete snapshot. A separate blocked-move
    // fixture forces terrain deltas beyond the bounded event buffer.
    {
        BrogueBridgeCommand command = {0};
        BrogueBridgeTurnResult turn;
        brogue_bridge_shutdown();
        if (brogue_bridge_start_game(seed) != BROGUE_BRIDGE_OK) return 1;
        command.apiVersion = BROGUE_BRIDGE_API_VERSION;
        command.type = BROGUE_COMMAND_SEARCH_START;
        if (brogue_bridge_perform_command(&command, &turn) != BROGUE_BRIDGE_OK) return 1;
        // The fixture needs an undisturbed sequence, independent of seed.
        if (!rogue.repeatedSearchActive) beginRepeatedSearch();
        const unsigned long rngBefore = randomNumbersGenerated;
        const uint64_t turnBefore = rogue.absoluteTurnNumber;
        command.type = BROGUE_COMMAND_SEARCH_CANCEL;
        if (brogue_bridge_perform_command(&command, &turn) != BROGUE_BRIDGE_OK
            || turn.consumedTurn || randomNumbersGenerated != rngBefore
            || rogue.absoluteTurnNumber != turnBefore) return 1;
        if (brogue_bridge_perform_command(&command, &turn) != BROGUE_BRIDGE_INVALID_STATE) return 1;
        for (int x=1; x<DCOLS-1; ++x) for (int y=1; y<DROWS-1; ++y) {
            if (abs(x-player.loc.x) < 20 && abs(y-player.loc.y) < 20) continue;
            pmap[x][y].layers[DUNGEON] = TRAP_DOOR;
            pmap[x][y].flags &= ~ANY_KIND_OF_VISIBLE;
            pmap[x][y].flags |= DISCOVERED;
            pmap[x][y].rememberedTerrain = GAS_TRAP_POISON;
        }
        pmap[player.loc.x][player.loc.y-1].layers[DUNGEON] = WALL;
        command.type = BROGUE_COMMAND_ACTION;
        command.action = BROGUE_ACTION_MOVE_N;
        if (brogue_bridge_perform_command(&command, &turn) != BROGUE_BRIDGE_OK
            || !turn.eventsTruncated || turn.consumedTurn
            || randomNumbersGenerated != rngBefore || rogue.absoluteTurnNumber != turnBefore) return 1;
        if (brogue_bridge_get_state(state) != BROGUE_BRIDGE_OK) return 1;
        for (uint32_t i=0; i<state->cellCount; ++i) {
            const BrogueBridgeCellState *cell = &state->cells[i];
            if (cell->x > 0 && cell->x < DCOLS-1 && cell->y > 0 && cell->y < DROWS-1
                && (abs(cell->x-player.loc.x) >= 20 || abs(cell->y-player.loc.y) >= 20)
                && cell->terrainFeature != BROGUE_FEATURE_GAS_PLATE) return 1;
        }
        brogue_bridge_shutdown();
        if (brogue_bridge_start_game(seed) != BROGUE_BRIDGE_OK
            || brogue_bridge_get_state(state) != BROGUE_BRIDGE_OK || state->player.searchActive) return 1;
        puts("SEARCH contract=truncation-memory-reset cancelTurn=false cancelRng=false");
    }
    return 0;
}
