/* Round-trip the real command recording, without synthetic gameplay fixtures. */
static int saveSmokeTravel(void) {
    const int dx[4] = {0, 1, 0, -1}, dy[4] = {-1, 0, 1, 0};
    for (int step = 0; step < 200 && rogue.depthLevel == 1 && !rogue.gameHasEnded; ++step) {
        int distances[DCOLS][DROWS];
        pos queue[DCOLS * DROWS];
        int head = 0, tail = 0;
        memset(distances, -1, sizeof(distances));
        queue[tail++] = rogue.downLoc;
        distances[rogue.downLoc.x][rogue.downLoc.y] = 0;
        while (head < tail) {
            pos cell = queue[head++];
            for (int d = 0; d < 4; ++d) {
                pos next = {cell.x + dx[d], cell.y + dy[d]};
                if (!isPosInMap(next) || distances[next.x][next.y] >= 0) continue;
                if (cellHasTerrainFlag(next, T_AUTO_DESCENT | T_LAVA_INSTA_DEATH | T_IS_DEEP_WATER)) continue;
                if (cellHasTerrainFlag(next, T_OBSTRUCTS_PASSABILITY) && pmapAt(next)->layers[DUNGEON] != DOOR) continue;
                distances[next.x][next.y] = distances[cell.x][cell.y] + 1;
                queue[tail++] = next;
            }
        }
        int best = -1, distance = 100000;
        for (int d = 0; d < 4; ++d) {
            pos next = {player.loc.x + dx[d], player.loc.y + dy[d]};
            if (isPosInMap(next) && distances[next.x][next.y] >= 0 && distances[next.x][next.y] < distance) {
                best = d; distance = distances[next.x][next.y];
            }
        }
        if (best < 0) { fprintf(stderr, "Travel route missing at turn %lu\n", rogue.playerTurnNumber); return 1; }
        BrogueBridgeTurnResult result;
        BrogueBridgeResult status = brogue_bridge_perform_action((BrogueBridgeAction)(best * 2), &result);
        if (status == BROGUE_BRIDGE_CONFIRMATION_REQUIRED) {
            BrogueBridgeCommand move = {0};
            move.apiVersion = BROGUE_BRIDGE_API_VERSION;
            move.type = BROGUE_COMMAND_ACTION;
            move.action = (BrogueBridgeAction)(best * 2);
            move.confirmed = 1;
            status = brogue_bridge_perform_command(&move, &result);
        }
        if (status != BROGUE_BRIDGE_OK) {
            fprintf(stderr, "Travel command rejected: %s\n", brogue_bridge_result_name(status)); return 1;
        }
    }
    if (rogue.depthLevel != 2) fprintf(stderr, "Travel ended at turn %lu hp=%d depth=%d\n", rogue.playerTurnNumber, player.currentHP, rogue.depthLevel);
    return rogue.depthLevel == 2 && !rogue.gameHasEnded ? 0 : 1;
}

static int runSaveSmoke(uint64_t seed, boolean travel) {
    BrogueBridgeTurnResult result;
    const char *working = "save-smoke-working.broguesave";
    const char *saved = "save-smoke-suspended.broguesave";
    const char *resumed = "save-smoke-resumed.broguesave";
    unsigned long turns, rng;
    pos location;
    int hp, nutrition, progress;
#define SAVE_CHECK(c) do { if (!(c)) { fprintf(stderr, "Save line=%d: %s\n", __LINE__, recordingLastError()); return 1; } } while (0)
    brogue_bridge_shutdown();
    strcpy(currentFilePath, working);
    SAVE_CHECK(brogue_bridge_start_game(seed) == BROGUE_BRIDGE_OK);
    if (travel) SAVE_CHECK(saveSmokeTravel() == 0);
    if (!travel) {
    BrogueBridgeState snapshot;
    SAVE_CHECK(brogue_bridge_get_state(&snapshot) == BROGUE_BRIDGE_OK);
    uint64_t dart = 0;
    for (uint32_t i = 0; i < snapshot.itemCount; ++i)
        if (snapshot.items[i].carried && snapshot.items[i].category == WEAPON && snapshot.items[i].kind == DART)
            dart = snapshot.items[i].id;
    SAVE_CHECK(dart != 0);
    BrogueBridgeCommand command = {0};
    command.apiVersion = BROGUE_BRIDGE_API_VERSION;
    command.itemId = dart;
    command.type = BROGUE_COMMAND_THROW_ITEM;
    command.targetX = player.loc.x;
    command.targetY = player.loc.y - 1;
    SAVE_CHECK(brogue_bridge_perform_command(&command, &result) == BROGUE_BRIDGE_OK && result.consumedTurn);
    command.type = BROGUE_COMMAND_EQUIP_ITEM;
    SAVE_CHECK(brogue_bridge_perform_command(&command, &result) == BROGUE_BRIDGE_OK);
    command.type = BROGUE_COMMAND_UNEQUIP_ITEM;
    SAVE_CHECK(brogue_bridge_perform_command(&command, &result) == BROGUE_BRIDGE_OK);
    command.type = BROGUE_COMMAND_DROP_ITEM;
    SAVE_CHECK(brogue_bridge_perform_command(&command, &result) == BROGUE_BRIDGE_OK);
    for (int i = 0; i < 7; ++i) {
        SAVE_CHECK(brogue_bridge_perform_action(i % 2 ? BROGUE_ACTION_SEARCH : BROGUE_ACTION_WAIT, &result) == BROGUE_BRIDGE_OK);
    }
    for (int i = 0; i < 5; ++i)
        SAVE_CHECK(brogue_bridge_perform_action(BROGUE_ACTION_SEARCH, &result) == BROGUE_BRIDGE_OK);
    for (int i = 0; i < 8; ++i)
        SAVE_CHECK(brogue_bridge_perform_action((BrogueBridgeAction)i, &result) == BROGUE_BRIDGE_OK);
    }
    turns = rogue.playerTurnNumber;
    location = player.loc;
    hp = player.currentHP;
    nutrition = player.status[STATUS_NUTRITION];
    progress = player.status[STATUS_SEARCHING];
    SAVE_CHECK(saveGameToPath(saved));
    rogue.gameHasEnded = false;
    currentFilePath[0] = '\0';
    executeKeystroke(REST_KEY, false, false);
    rng = rand_range(0, 1000000);
    brogue_bridge_shutdown();
    SAVE_CHECK(beginSavedGameLoad(saved));
    int status;
    do { status = stepSavedGameLoad(1); } while (status == 0);
    SAVE_CHECK(status == 1);
    SAVE_CHECK(rogue.playerTurnNumber == turns && player.loc.x == location.x && player.loc.y == location.y);
    SAVE_CHECK(player.currentHP == hp && player.status[STATUS_NUTRITION] == nutrition && player.status[STATUS_SEARCHING] == progress);
    SAVE_CHECK(finishSavedGameLoad(resumed, false));
    executeKeystroke(REST_KEY, false, false);
    SAVE_CHECK(rand_range(0, 1000000) == rng);
    freeEverything();
    currentFilePath[0] = '\0';
    remove(working); if (!travel) remove(saved); remove(resumed);
    printf("SAVE seed=%llu native-roundtrip=OK turns=%lu subsequent-wait=OK depth=%d\n", (unsigned long long)seed, turns, travel ? 2 : 1);
    return 0;
#undef SAVE_CHECK
}
