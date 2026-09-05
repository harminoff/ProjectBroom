/* Headless fixtures and terminal-input adapter, never public bridge exports. */
static boolean wandSmokeCancel;
static int wandSmokeInputs;
static void wandSmokeInput(rogueEvent *event, boolean textInput, boolean colorsDance) {
    (void) textInput;
    (void) colorsDance;
    if (++wandSmokeInputs > 100) {
        fputs("Wand smoke unexpected terminal input loop.\n", stderr);
        exit(1);
    }
    memset(event, 0, sizeof(*event));
    event->eventType = wandSmokeCancel ? KEYSTROKE : MOUSE_UP;
    event->param1 = wandSmokeCancel ? ESCAPE_KEY : mapToWindowX(36);
    event->param2 = mapToWindowY(12);
    event->controlKey = true;
}

static int runWandSmoke(BrogueBridgeState *state) {
    const uint64_t seed = state->gameSeed;
    const char *names[] = {"teleport", "slow", "polymorph", "negation", "domination", "beckoning",
                          "plenty", "invisibility", "empowerment", "blocked", "reflected", "known-empty", "unknown-empty", "identify"};
    int scenario, route, x, y, layer;
    for (scenario = 0; scenario < 14; ++scenario) {
        uint64_t referenceHash = 0, referenceTurn = 0;
        unsigned long referenceRng = 0;
        int referenceCharges = 0, referenceDischarges = 0;
        for (route = 0; route < 2; ++route) {
            item *wand;
            creature *target;
            BrogueBridgeCommand command = {0};
            BrogueBridgeTurnResult turn;
            BrogueBridgeWandPreview preview, repeated;
            static BrogueBridgeState before;
            uint64_t wandId = 0;
            unsigned long rngBefore, usedRng;
            int initialDischarges;
            uint32_t i;
            boolean consumed;
#define WAND_CHECK(condition) do { if (!(condition)) { fprintf(stderr, "Wand smoke %s route=%d failed at line %d.\n", names[scenario], route, __LINE__); return 1; } } while (0)
            brogue_bridge_shutdown();
            WAND_CHECK(brogue_bridge_start_game(seed) == BROGUE_BRIDGE_OK);
            // Controlled arena; every effect and turn still runs Brogue code.
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
            if (scenario == 3) target->status[STATUS_HASTED] = target->maxStatus[STATUS_HASTED] = 100;
            if (scenario == 4) target->currentHP = 1; // Brogue's guaranteed domination range.
            if (scenario == 9) pmap[34][12].layers[DUNGEON] = WALL;
            if (scenario == 10) target->info.abilityFlags |= MA_REFLECT_100;
            wand = generateItem(WAND, scenario < 9 ? scenario : WAND_SLOW);
            wand->charges = (scenario == 11 || scenario == 12) ? 0 : 3;
            wand->flags &= ~(ITEM_IDENTIFIED | ITEM_MAX_CHARGES_KNOWN);
            if (scenario < 12) identify(wand);
            addItemToPack(wand);
            WAND_CHECK(brogue_bridge_perform_action(BROGUE_ACTION_WAIT, &turn) == BROGUE_BRIDGE_OK);
            WAND_CHECK(brogue_bridge_get_state(state) == BROGUE_BRIDGE_OK);
            for (i = 0; i < state->itemCount; ++i) if (state->items[i].carried && state->items[i].category == WAND) {
                wandId = state->items[i].id;
                WAND_CHECK(state->items[i].actionFlags & BROGUE_ITEM_ACTION_TARGET_WAND);
                WAND_CHECK(!(state->items[i].actionFlags & BROGUE_ITEM_ACTION_TARGET_STAFF));
            }
            WAND_CHECK(wandId != 0);
            before = *state;
            initialDischarges = wand->enchant2;
            rngBefore = randomNumbersGenerated;
            WAND_CHECK(brogue_bridge_preview_wand(wandId, 36, 12, &preview) == BROGUE_BRIDGE_OK);
            WAND_CHECK(brogue_bridge_preview_wand(wandId, 36, 12, &repeated) == BROGUE_BRIDGE_OK);
            WAND_CHECK(memcmp(&preview, &repeated, sizeof(preview)) == 0);
            WAND_CHECK(preview.aim.apiVersion == BROGUE_BRIDGE_API_VERSION && preview.aim.valid && preview.aim.maxDistance == -1);
            WAND_CHECK(randomNumbersGenerated == rngBefore && wand->enchant2 == initialDischarges);
            WAND_CHECK(brogue_bridge_get_state(state) == BROGUE_BRIDGE_OK && state->revision == before.revision && state->stateHash == before.stateHash);
            if (scenario == 9) WAND_CHECK(preview.aim.pathCount == 2);
            WAND_CHECK(brogue_bridge_preview_staff(wandId, 36, 12, &repeated) == BROGUE_BRIDGE_INVALID_ACTION);
            command.type = BROGUE_COMMAND_USE_WAND;
            command.apiVersion = BROGUE_BRIDGE_API_VERSION - 1;
            command.itemId = wandId;
            command.targetX = 36;
            command.targetY = 12;
            WAND_CHECK(brogue_bridge_perform_command(&command, &turn) == BROGUE_BRIDGE_INVALID_ACTION);
            command.apiVersion = BROGUE_BRIDGE_API_VERSION;
            command.expectedRevision = state->revision + 1;
            WAND_CHECK(brogue_bridge_perform_command(&command, &turn) == BROGUE_BRIDGE_STALE_REVISION);
            command.expectedRevision = state->revision;
            command.itemId = 0;
            WAND_CHECK(brogue_bridge_perform_command(&command, &turn) == BROGUE_BRIDGE_ITEM_NOT_FOUND);
            command.itemId = before.player.equippedWeaponId;
            WAND_CHECK(brogue_bridge_perform_command(&command, &turn) == BROGUE_BRIDGE_INVALID_ACTION);
            command.itemId = wandId;
            command.type = BROGUE_COMMAND_USE_STAFF;
            WAND_CHECK(brogue_bridge_perform_command(&command, &turn) == BROGUE_BRIDGE_INVALID_ACTION);
            command.type = BROGUE_COMMAND_USE_WAND;
            command.targetX = -1;
            WAND_CHECK(brogue_bridge_perform_command(&command, &turn) == BROGUE_BRIDGE_OUT_OF_RANGE);
            command.targetX = 32;
            WAND_CHECK(brogue_bridge_perform_command(&command, &turn) == BROGUE_BRIDGE_OUT_OF_RANGE);
            command.targetX = 36;
            WAND_CHECK(randomNumbersGenerated == rngBefore && rogue.absoluteTurnNumber == before.absoluteTurn);
            if (route == 0) {
                WAND_CHECK(brogue_bridge_perform_command(&command, &turn) == BROGUE_BRIDGE_OK);
                WAND_CHECK(turn.consumedTurn == (scenario != 11) && turn.actionAccepted == (scenario != 11));
            } else {
                // Execute the standalone apply/chooseTarget route, supplying
                // terminal events through the platform callback, not through
                // applyDeviceAtTarget or any simulation override.
                void (*oldInput)(rogueEvent *, boolean, boolean) = currentConsole.nextKeyOrMouseEvent;
                currentConsole.nextKeyOrMouseEvent = wandSmokeInput;
                wandSmokeInputs = 0;
                wandSmokeCancel = true;
                // An identified empty wand returns before any target prompt;
                // attempting it twice would add an extra depletion message.
                if (scenario != 11) apply(wand);
                WAND_CHECK(rogue.absoluteTurnNumber == before.absoluteTurn && randomNumbersGenerated == rngBefore);
                WAND_CHECK(wand->enchant2 == initialDischarges);
                wandSmokeCancel = false;
                apply(wand);
                currentConsole.nextKeyOrMouseEvent = oldInput;
            }
            consumed = rogue.absoluteTurnNumber != before.absoluteTurn;
            WAND_CHECK(consumed == (scenario != 11));
            WAND_CHECK(wand->charges == ((scenario == 11 || scenario == 12) ? 0 : 2));
            WAND_CHECK(wand->enchant2 == initialDischarges + ((scenario == 11 || scenario == 12) ? 0 : 1));
            if (scenario == 0) WAND_CHECK(!posEq(target->loc, ((pos){36, 12})));
            if (scenario == 1 || scenario == 13) WAND_CHECK(target->status[STATUS_SLOWED] > 0);
            if (scenario == 2) WAND_CHECK(target->info.monsterID != MK_RAT);
            if (scenario == 3) WAND_CHECK(target->status[STATUS_HASTED] == 0);
            if (scenario == 4) WAND_CHECK(target->creatureState == MONSTER_ALLY);
            if (scenario == 5) WAND_CHECK(distanceBetween(player.loc, target->loc) <= 1);
            if (scenario == 6) WAND_CHECK(target->currentHP <= 5000);
            if (scenario == 7) WAND_CHECK(target->status[STATUS_INVISIBLE] > 0);
            if (scenario == 8) WAND_CHECK(target->totalPowerCount > 0);
            if (scenario == 9) WAND_CHECK(target->status[STATUS_SLOWED] == 0);
            if (scenario == 10) WAND_CHECK(target->status[STATUS_SLOWED] == 0 && player.status[STATUS_SLOWED] > 0);
            if (scenario == 12) WAND_CHECK(wand->flags & ITEM_MAX_CHARGES_KNOWN);
            if (scenario == 13) WAND_CHECK(tableForItemCategory(WAND)[WAND_SLOW].identified);
            // One identical continuation turn refreshes the copied snapshot
            // after direct standalone apply, and checks future RNG behavior.
            WAND_CHECK(brogue_bridge_perform_action(BROGUE_ACTION_WAIT, &turn) == BROGUE_BRIDGE_OK);
            WAND_CHECK(brogue_bridge_get_state(state) == BROGUE_BRIDGE_OK);
            usedRng = randomNumbersGenerated - rngBefore;
            if (route == 0) {
                referenceHash = state->stateHash;
                referenceTurn = state->absoluteTurn;
                referenceRng = usedRng;
                referenceCharges = wand->charges;
                referenceDischarges = wand->enchant2;
            } else {
                WAND_CHECK(state->stateHash == referenceHash && state->absoluteTurn == referenceTurn);
                WAND_CHECK(usedRng == referenceRng && wand->charges == referenceCharges && wand->enchant2 == referenceDischarges);
                printf("WAND case=%s parity=true consumedTurn=%s charges=%d discharges=%d hash=%016llx rng=%lu\n",
                       names[scenario], consumed ? "true" : "false", wand->charges, wand->enchant2,
                       (unsigned long long) state->stateHash, usedRng);
            }
#undef WAND_CHECK
        }
    }
    return 0;
}
