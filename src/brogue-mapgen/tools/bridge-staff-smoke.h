/* Harness-only fixtures. Never exported by the runtime DLL. */
static int runStaffSmoke(BrogueBridgeState *state) {
    const uint64_t seed = state->gameSeed;
    const char *cases[] = {"fire", "blocked", "reflected", "known-empty", "unknown-empty", "blink-warning"};
    int scenario, x, y, layer;
    for (scenario = 0; scenario < 6; ++scenario) {
        item *staff;
        creature *target;
        BrogueBridgeCommand command = {0};
        BrogueBridgeTurnResult turn;
        BrogueBridgeStaffPreview preview, repeated;
        BrogueBridgeState before;
        uint64_t staffId = 0;
        unsigned long rngBefore;
        int chargesBefore, hpBefore;
        uint32_t i;
        BrogueBridgeResult result;
#define STAFF_CHECK(condition) do { if (!(condition)) { fprintf(stderr, "Staff smoke %s failed at line %d.\n", cases[scenario], __LINE__); return 1; } } while (0)
        brogue_bridge_shutdown();
        STAFF_CHECK(brogue_bridge_start_game(seed) == BROGUE_BRIDGE_OK);
        // A fixed arena isolates bolt behavior from generated topology while
        // the seed still controls real Brogue effects and the turn scheduler.
        pmapAt(player.loc)->flags &= ~HAS_PLAYER;
        player.loc = (pos){32, 12};
        player.currentHP = player.info.maxHP = 10000;
        for (x = 30; x <= 45; ++x) for (y = 10; y <= 14; ++y) {
            for (layer = 0; layer < NUMBER_TERRAIN_LAYERS; ++layer) pmap[x][y].layers[layer] = NOTHING;
            pmap[x][y].layers[DUNGEON] = FLOOR;
            pmap[x][y].flags |= DISCOVERED;
        }
        pmapAt(player.loc)->flags |= HAS_PLAYER;
        target = generateMonster(MK_RAT, false, false);
        target->loc = (pos){36, 12};
        target->currentHP = target->info.maxHP = 10000;
        target->ticksUntilTurn = 10000;
        pmapAt(target->loc)->flags |= HAS_MONSTER;
        if (scenario == 2) target->info.abilityFlags |= MA_REFLECT_100;
        if (scenario == 1) pmap[34][12].layers[DUNGEON] = WALL;
        staff = generateItem(STAFF, scenario == 5 ? STAFF_BLINKING : STAFF_LIGHTNING);
        staff->charges = (scenario == 3 || scenario == 4) ? 0 : 3;
        staff->enchant1 = 3;
        staff->flags &= ~(ITEM_IDENTIFIED | ITEM_MAX_CHARGES_KNOWN);
        if (scenario != 4 && scenario != 5) identify(staff);
        if (scenario == 5) {
            identifyItemKind(staff); // Known effect, unknown blinking range.
            pmap[34][12].layers[LIQUID] = LAVA;
            pmapAt(target->loc)->flags &= ~HAS_MONSTER;
            target->loc.x = 44;
            pmapAt(target->loc)->flags |= HAS_MONSTER;
        }
        addItemToPack(staff);
        STAFF_CHECK(brogue_bridge_perform_action(BROGUE_ACTION_WAIT, &turn) == BROGUE_BRIDGE_OK);
        STAFF_CHECK(brogue_bridge_get_state(state) == BROGUE_BRIDGE_OK);
        for (i = 0; i < state->itemCount; ++i) {
            if (state->items[i].carried && state->items[i].category == STAFF) {
                staffId = state->items[i].id;
                STAFF_CHECK(state->items[i].actionFlags & BROGUE_ITEM_ACTION_TARGET_STAFF);
            }
        }
        STAFF_CHECK(staffId != 0);
        chargesBefore = staff->charges;
        hpBefore = player.currentHP;
        before = *state;
        rngBefore = randomNumbersGenerated;
        STAFF_CHECK(brogue_bridge_preview_staff(staffId, 36, 12, &preview) == BROGUE_BRIDGE_OK);
        STAFF_CHECK(brogue_bridge_preview_staff(staffId, 36, 12, &repeated) == BROGUE_BRIDGE_OK);
        STAFF_CHECK(memcmp(&preview, &repeated, sizeof(preview)) == 0);
        STAFF_CHECK(preview.aim.apiVersion == BROGUE_BRIDGE_API_VERSION && preview.aim.valid);
        STAFF_CHECK(randomNumbersGenerated == rngBefore && staff->charges == chargesBefore);
        STAFF_CHECK(brogue_bridge_get_state(state) == BROGUE_BRIDGE_OK);
        STAFF_CHECK(state->revision == before.revision && state->stateHash == before.stateHash);
        if (scenario == 1) STAFF_CHECK(preview.aim.pathCount == 2);
        // Closing the frontend cursor sends no command: the preview above is
        // the entire cancellation path and must be observationally pure.
        command.apiVersion = BROGUE_BRIDGE_API_VERSION - 1;
        command.type = BROGUE_COMMAND_USE_STAFF;
        command.itemId = staffId;
        command.targetX = 36;
        command.targetY = 12;
        STAFF_CHECK(brogue_bridge_perform_command(&command, &turn) == BROGUE_BRIDGE_INVALID_ACTION);
        command.apiVersion = BROGUE_BRIDGE_API_VERSION;
        command.expectedRevision = state->revision + 1;
        STAFF_CHECK(brogue_bridge_perform_command(&command, &turn) == BROGUE_BRIDGE_STALE_REVISION);
        command.expectedRevision = state->revision;
        command.targetX = 32;
        STAFF_CHECK(brogue_bridge_perform_command(&command, &turn) == BROGUE_BRIDGE_OUT_OF_RANGE);
        command.targetX = -1;
        STAFF_CHECK(brogue_bridge_perform_command(&command, &turn) == BROGUE_BRIDGE_OUT_OF_RANGE);
        command.targetX = 36;
        STAFF_CHECK(staff->charges == chargesBefore && randomNumbersGenerated == rngBefore);
        result = brogue_bridge_perform_command(&command, &turn);
        if (scenario == 5) {
            STAFF_CHECK(result == BROGUE_BRIDGE_CONFIRMATION_REQUIRED);
            STAFF_CHECK(strcmp(turn.prompt, "Blink across lava with unknown range?") == 0);
            STAFF_CHECK(staff->charges == chargesBefore && rogue.absoluteTurnNumber == before.absoluteTurn);
            STAFF_CHECK(randomNumbersGenerated == rngBefore);
            STAFF_CHECK(brogue_bridge_get_state(state) == BROGUE_BRIDGE_OK && state->revision == before.revision);
            // Reopening and cancelling the same warning must remain safe.
            STAFF_CHECK(brogue_bridge_perform_command(&command, &turn) == BROGUE_BRIDGE_CONFIRMATION_REQUIRED);
            command.confirmed = 1;
            result = brogue_bridge_perform_command(&command, &turn);
        }
        STAFF_CHECK(result == BROGUE_BRIDGE_OK);
        STAFF_CHECK(turn.consumedTurn == (scenario != 3));
        STAFF_CHECK(turn.actionAccepted == (scenario != 3));
        if (scenario < 3 || scenario == 5) STAFF_CHECK(staff->charges == chargesBefore - 1);
        else STAFF_CHECK(staff->charges == 0);
        if (scenario == 0) STAFF_CHECK(target->currentHP < 10000);
        if (scenario == 1) STAFF_CHECK(target->currentHP == 10000);
        if (scenario == 2) STAFF_CHECK(target->currentHP == 10000 && player.currentHP < hpBefore);
        if (scenario == 4) STAFF_CHECK(staff->flags & ITEM_MAX_CHARGES_KNOWN);
        if (scenario == 5) STAFF_CHECK(player.loc.x != 32);
        STAFF_CHECK(brogue_bridge_get_state(state) == BROGUE_BRIDGE_OK);
        printf("STAFF case=%s accepted=%s consumedTurn=%s charges=%d hash=%016llx rng=%lu\n",
               cases[scenario], turn.actionAccepted ? "true" : "false", turn.consumedTurn ? "true" : "false",
               staff->charges, (unsigned long long) state->stateHash, randomNumbersGenerated);
#undef STAFF_CHECK
    }
    return 0;
}
