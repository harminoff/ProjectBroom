/* Private deterministic fixtures; no runtime API mutators. */
static int runTargetSmoke(BrogueBridgeState *state) {
    uint64_t seed = state->gameSeed;
    const char *names[] = {"throw-open", "throw-wall", "throw-range", "unknown-staff", "unknown-wand",
        "blink-warning", "blink-refusal", "tunneling", "fiery", "pass-through", "reflector",
        "hidden", "submerged", "telepathic", "hallucinated", "ally", "multiple", "zero", "throw-confirm", "unexplored", "healing-ally"};
    for (int scenario = 0; scenario < 21; ++scenario) {
        uint64_t reference = 0;
        unsigned long continuation[2] = {0};
        for (int route = 0; route < 2; ++route) {
#define TARGET_CHECK(c) do { if (!(c)) { fprintf(stderr, "Target %s route=%d line=%d failed.\n", names[scenario], route, __LINE__); return 1; } } while (0)
            brogue_bridge_shutdown();
            TARGET_CHECK(brogue_bridge_start_game(seed) == BROGUE_BRIDGE_OK);
            pmapAt(player.loc)->flags &= ~HAS_PLAYER;
            player.loc = (pos){32,12};
            player.currentHP = player.info.maxHP = 10000;
            for (int x = 30; x < DCOLS-1; ++x) for (int y = 10; y <= 14; ++y) {
                for (int l = 0; l < NUMBER_TERRAIN_LAYERS; ++l) pmap[x][y].layers[l] = NOTHING;
                pmap[x][y].layers[DUNGEON] = FLOOR;
                pmap[x][y].flags |= DISCOVERED;
            }
            pmapAt(player.loc)->flags |= HAS_PLAYER;
            boolean throwing = scenario < 3 || scenario == 18;
            item *device = generateItem(throwing ? WEAPON : scenario == 4 ? WAND : STAFF,
                throwing ? DART : scenario == 4 ? WAND_SLOW : scenario == 5 || scenario == 6 ? STAFF_BLINKING :
                scenario == 20 ? STAFF_HEALING : scenario == 7 ? STAFF_TUNNELING : scenario == 8 || (scenario >= 10 && scenario <= 17) ? STAFF_FIRE : STAFF_LIGHTNING);
            device->charges = 3;
            device->enchant1 = 2;
            device->flags &= ~(ITEM_IDENTIFIED | ITEM_MAX_CHARGES_KNOWN);
            if (scenario != 3 && scenario != 4) identify(device);
            if (scenario == 5) device->flags &= ~(ITEM_IDENTIFIED | ITEM_MAX_CHARGES_KNOWN);
            if (scenario == 18) { device->timesEnchanted = 1; device->quantity = 1; }
            addItemToPack(device);
            creature *target = generateMonster(MK_RAT, false, false);
            target->loc = (pos){36,12}; target->ticksUntilTurn = 10000;
            pmapAt(target->loc)->flags |= HAS_MONSTER;
            if (scenario == 16) {
                creature *second = generateMonster(MK_RAT, false, false);
                second->loc = (pos){36,13}; second->ticksUntilTurn = 10000;
                pmapAt(second->loc)->flags |= HAS_MONSTER;
            }
            TARGET_CHECK(brogue_bridge_perform_action(BROGUE_ACTION_WAIT, &(BrogueBridgeTurnResult){0}) == BROGUE_BRIDGE_OK);
            TARGET_CHECK(brogue_bridge_get_state(state) == BROGUE_BRIDGE_OK);
            uint64_t id = 0;
            for (uint32_t i = 0; i < state->itemCount; ++i)
                if (state->items[i].carried && state->items[i].inventoryLetter == device->inventoryLetter) id = state->items[i].id;
            TARGET_CHECK(id != 0);
            for (creatureIterator it = iterateCreatures(monsters); hasNextCreature(it);) {
                creature *other = nextCreature(&it);
                if (other != target && !(scenario == 16 && posEq(other->loc, ((pos){36,13})))) other->status[STATUS_INVISIBLE] = 100;
            }
            // Changes below are fixture setup only, identical in both routes.
            if (scenario == 5 || scenario == 6) { pmapAt(target->loc)->flags &= ~HAS_MONSTER; target->loc.x = 44; pmapAt(target->loc)->flags |= HAS_MONSTER; }
            if (scenario == 2) { pmapAt(target->loc)->flags &= ~HAS_MONSTER; target->loc.y = 14; pmapAt(target->loc)->flags |= HAS_MONSTER; }
            if (scenario == 1 || scenario == 7) pmap[34][12].layers[DUNGEON] = WALL;
            if (scenario == 8) pmap[34][12].layers[DUNGEON] = FOLIAGE;
            if (scenario == 5) pmap[34][12].layers[LIQUID] = LAVA;
            if (scenario == 6) for (int x = 33; x <= 45; ++x) pmap[x][12].layers[LIQUID] = LAVA;
            if (scenario == 10) target->info.abilityFlags |= MA_REFLECT_100;
            if (scenario == 11) target->status[STATUS_INVISIBLE] = 100;
            if (scenario == 12) target->bookkeepingFlags |= MB_SUBMERGED;
            if (scenario == 13) { pmapAt(target->loc)->flags &= ~VISIBLE; player.status[STATUS_TELEPATHIC] = 100; }
            if (scenario == 14) player.status[STATUS_HALLUCINATING] = 100;
            if (scenario == 15 || scenario == 20) target->creatureState = MONSTER_ALLY;
            if (scenario == 20) { target->currentHP = 1; player.currentHP = 5000; }
            if (scenario == 17) target->status[STATUS_INVISIBLE] = 100;
            if (scenario == 19) pmap[34][12].flags &= ~DISCOVERED;
            for (int i = 0; i < ROWS*2; ++i) rogue.sidebarLocationList[i] = INVALID_POS;
            BrogueBridgeTargetRequest request = {BROGUE_BRIDGE_API_VERSION,
                throwing ? BROGUE_COMMAND_THROW_ITEM : scenario == 4 ? BROGUE_COMMAND_USE_WAND : BROGUE_COMMAND_USE_STAFF,
                state->revision, id, scenario == 2 ? 60 : 36, 12};
            if (route == 0) {
                static BrogueBridgeTargetPreview preview, repeated;
                static playerCharacter savedRogue;
                savedRogue = rogue;
                item savedItem = *device;
                unsigned long rng = randomNumbersGenerated;
                TARGET_CHECK(brogue_bridge_preview_target(&request, &preview) == BROGUE_BRIDGE_OK);
                for (int n = 0; n < 8; ++n) {
                    memset(&repeated, 0xa5, sizeof(repeated));
                    TARGET_CHECK(brogue_bridge_preview_target(&request, &repeated) == BROGUE_BRIDGE_OK);
                    TARGET_CHECK(memcmp(&preview, &repeated, sizeof(preview)) == 0);
                }
                TARGET_CHECK(memcmp(&savedRogue, &rogue, sizeof(rogue)) == 0);
                TARGET_CHECK(memcmp(&savedItem, device, sizeof(savedItem)) == 0 && rng == randomNumbersGenerated);
                TARGET_CHECK(preview.aim.valid && preview.aim.revision == request.expectedRevision);
                TARGET_CHECK(!preview.pathTruncated && preview.aim.pathCount <= BROGUE_BRIDGE_MAX_PROJECTILE_PATH);
                for (uint32_t i = 0; i < preview.targetCount; ++i) {
                    TARGET_CHECK(preview.targets[i].id != 0);
                    for (uint32_t j = 0; j < i; ++j) TARGET_CHECK(preview.targets[i].id != preview.targets[j].id);
                }
                if (scenario == 1) TARGET_CHECK(preview.termination == BROGUE_GUIDE_TERRAIN && !preview.reachesTarget);
                if (scenario == 2) TARGET_CHECK(preview.termination == BROGUE_GUIDE_RANGE && !preview.reachesTarget);
                if (scenario == 3 || scenario == 4) TARGET_CHECK(!preview.hasRange && !preview.aim.requiresConfirmation);
                if (scenario == 5) TARGET_CHECK(preview.aim.requiresConfirmation && strcmp(preview.aim.message, "Blink across lava with unknown range?") == 0);
                if (scenario == 6) TARGET_CHECK(preview.certainDeath && strcmp(preview.aim.message, "that would be certain death!") == 0);
                if (scenario == 7 || scenario == 8 || scenario == 9) TARGET_CHECK(preview.reachesTarget);
                if (scenario == 10 || scenario == 11 || scenario == 14 || scenario == 15 || scenario == 17)
                    TARGET_CHECK(preview.targetCount == 0 && !preview.hasNextTarget);
                if (scenario == 0 || scenario == 13 || scenario == 20) TARGET_CHECK(preview.targetCount == 1 && !preview.hasNextTarget);
                if (scenario == 10) TARGET_CHECK(preview.reachesTarget && preview.termination == BROGUE_GUIDE_CREATURE);
                if (scenario == 11 || scenario == 12) TARGET_CHECK(preview.termination != BROGUE_GUIDE_CREATURE);
                if (scenario == 6) TARGET_CHECK(preview.hasRange && preview.aim.maxDistance == staffBlinkDistance(netEnchant(device)));
                if (scenario == 16) {
                    TARGET_CHECK(preview.targetCount == 2 && preview.hasNextTarget);
                    TARGET_CHECK(preview.nextTarget.location.x == 36 && preview.nextTarget.location.y == 13);
                    creature *bounded[1]; boolean truncated;
                    TARGET_CHECK(collectTargetCreatures(device, false, bounded, 1, &truncated) == 1 && truncated);
                }
                if (scenario == 18) TARGET_CHECK(preview.aim.requiresConfirmation && strstr(preview.aim.message, "Are you sure you want to throw your ") == preview.aim.message);
                if (scenario == 19) TARGET_CHECK(preview.termination == BROGUE_GUIDE_UNEXPLORED && !preview.reachesTarget);
                request.expectedRevision++;
                TARGET_CHECK(brogue_bridge_preview_target(&request, &repeated) == BROGUE_BRIDGE_STALE_REVISION);
                request.expectedRevision = 0;
                TARGET_CHECK(brogue_bridge_preview_target(&request, &repeated) == BROGUE_BRIDGE_OK);
                request.apiVersion--;
                TARGET_CHECK(brogue_bridge_preview_target(&request, &repeated) == BROGUE_BRIDGE_INVALID_ACTION);
                request.apiVersion++;
                request.type = BROGUE_COMMAND_ACTION;
                TARGET_CHECK(brogue_bridge_preview_target(&request, &repeated) == BROGUE_BRIDGE_INVALID_ACTION);
                request.type = BROGUE_COMMAND_USE_WAND; request.itemId = 0;
                TARGET_CHECK(brogue_bridge_preview_target(&request, &repeated) == BROGUE_BRIDGE_ITEM_NOT_FOUND);
            }
            // Both substantive and cosmetic RNG continuation, then identical WAIT.
            for (int stream = 0; stream < 2; ++stream) {
                rogue.RNG = stream;
                unsigned long value = rand_range(0, 1000000000);
                if (!route) continuation[stream] = value;
                else TARGET_CHECK(value == continuation[stream]);
            }
            rogue.RNG = RNG_SUBSTANTIVE;
            TARGET_CHECK(brogue_bridge_perform_action(BROGUE_ACTION_WAIT, &(BrogueBridgeTurnResult){0}) == BROGUE_BRIDGE_OK);
            TARGET_CHECK(brogue_bridge_get_state(state) == BROGUE_BRIDGE_OK);
            if (!route) reference = state->stateHash;
            else TARGET_CHECK(reference == state->stateHash);
#undef TARGET_CHECK
        }
        printf("TARGET case=%s unchanged=true hash=%016llx\n", names[scenario], (unsigned long long)reference);
    }
    return 0;
}


static int runTargetActionSmoke(BrogueBridgeState *state) {
    uint64_t seed = state->gameSeed;
    for (int throwing = 0; throwing < 2; ++throwing) for (int scenario = 0; scenario < 4; ++scenario) {
        uint64_t hash = 0, turnNumber = 0;
        unsigned long rng = 0;
        for (int route = 0; route < 2; ++route) {
#define ACTION_CHECK(c) do { if (!(c)) { fprintf(stderr, "Target action throw=%d case=%d route=%d line=%d failed.\n", throwing, scenario, route, __LINE__); return 1; } } while (0)
            brogue_bridge_shutdown();
            ACTION_CHECK(brogue_bridge_start_game(seed) == BROGUE_BRIDGE_OK);
            pmapAt(player.loc)->flags &= ~HAS_PLAYER; player.loc = (pos){32,12};
            player.currentHP = player.info.maxHP = 10000;
            for (int x = 30; x <= 45; ++x) for (int y = 10; y <= 14; ++y) {
                for (int l = 0; l < NUMBER_TERRAIN_LAYERS; ++l) pmap[x][y].layers[l] = NOTHING;
                pmap[x][y].layers[DUNGEON] = FLOOR; pmap[x][y].flags |= DISCOVERED;
            }
            pmapAt(player.loc)->flags |= HAS_PLAYER;
            item *device = generateItem(throwing ? WEAPON : STAFF, throwing ? DART : scenario == 3 ? STAFF_BLINKING : STAFF_FIRE);
            device->charges = scenario == 2 ? 0 : 3; device->enchant1 = 2;
            identify(device);
            if (throwing) { device->quantity = 3; if (scenario >= 2) { device->quantity = 1; device->timesEnchanted = 1; } }
            if (throwing && scenario == 2) device->flags |= ITEM_CURSED;
            if (!throwing && scenario == 3) { device->flags &= ~(ITEM_IDENTIFIED | ITEM_MAX_CHARGES_KNOWN); pmap[34][12].layers[LIQUID] = LAVA; }
            if (scenario == 1) pmap[34][12].layers[DUNGEON] = WALL;
            addItemToPack(device);
            BrogueBridgeTurnResult turn;
            ACTION_CHECK(brogue_bridge_perform_action(BROGUE_ACTION_WAIT, &turn) == BROGUE_BRIDGE_OK);
            ACTION_CHECK(brogue_bridge_get_state(state) == BROGUE_BRIDGE_OK);
            uint64_t id = 0, beforeTurn = state->absoluteTurn;
            for (uint32_t i = 0; i < state->itemCount; ++i) if (state->items[i].carried && state->items[i].inventoryLetter == device->inventoryLetter) id = state->items[i].id;
            ACTION_CHECK(id);
            unsigned long rngBefore = randomNumbersGenerated;
            BrogueBridgeCommand command = {0};
            command.apiVersion = BROGUE_BRIDGE_API_VERSION;
            command.type = throwing ? BROGUE_COMMAND_THROW_ITEM : BROGUE_COMMAND_USE_STAFF;
            command.expectedRevision = state->revision; command.itemId = id; command.targetX = 36; command.targetY = 12;
            if (!route) {
                BrogueBridgeResult result = brogue_bridge_perform_command(&command, &turn);
                if (result == BROGUE_BRIDGE_CONFIRMATION_REQUIRED) {
                    ACTION_CHECK(turn.prompt[0] && rogue.absoluteTurnNumber == beforeTurn);
                    command.confirmed = 1;
                    result = brogue_bridge_perform_command(&command, &turn);
                }
                ACTION_CHECK(result == BROGUE_BRIDGE_OK);
                ACTION_CHECK(turn.actionAccepted == (scenario != 2));
            } else {
                void (*oldInput)(rogueEvent *, boolean, boolean) = currentConsole.nextKeyOrMouseEvent;
                currentConsole.nextKeyOrMouseEvent = wandSmokeInput;
                // The same terminal target cancellation used by wand parity.
                wandSmokeInputs = 0; wandSmokeCancel = true;
                if (scenario != 2) {
                    if (throwing) throwCommand(device, false); else apply(device);
                    ACTION_CHECK(rogue.absoluteTurnNumber == beforeTurn);
                }
                wandSmokeInputs = 0; wandSmokeCancel = false;
                if (throwing) throwCommand(device, false); else apply(device);
                currentConsole.nextKeyOrMouseEvent = oldInput;
            }
            ACTION_CHECK(brogue_bridge_perform_action(BROGUE_ACTION_WAIT, &turn) == BROGUE_BRIDGE_OK);
            ACTION_CHECK(brogue_bridge_get_state(state) == BROGUE_BRIDGE_OK);
            if (!route) { hash = state->stateHash; turnNumber = state->absoluteTurn; rng = randomNumbersGenerated - rngBefore; }
            else {
                ACTION_CHECK(hash == state->stateHash && turnNumber == state->absoluteTurn && rng == randomNumbersGenerated - rngBefore);
                printf("TARGET_ACTION throw=%d case=%d parity=true hash=%016llx\n", throwing, scenario, (unsigned long long)hash);
            }
#undef ACTION_CHECK
        }
    }
    return 0;
}
