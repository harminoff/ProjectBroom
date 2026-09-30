/* Test-only deterministic fixtures for the ABI v24 interaction contract. They
 * drive the public bridge API against a synthetic arena; no gameplay hooks. */
#define IX_CHECK(c) do { if (!(c)) { fprintf(stderr, "Interaction smoke line=%d failed: %s\n", __LINE__, #c); return 1; } } while (0)

static BrogueBridgeTurnResult ixTurn;
static BrogueBridgeState ixState;

static int ixArena(uint64_t seed) {
    brogue_bridge_shutdown();
    if (brogue_bridge_start_game(seed) != BROGUE_BRIDGE_OK) return 1;
    pmapAt(player.loc)->flags &= ~HAS_PLAYER;
    player.loc = (pos){32, 12};
    player.currentHP = player.info.maxHP = 10000;
    for (int x = 20; x <= 45; ++x) for (int y = 5; y <= 20; ++y) {
        for (int l = 0; l < NUMBER_TERRAIN_LAYERS; ++l) pmap[x][y].layers[l] = NOTHING;
        pmap[x][y].layers[DUNGEON] = (x == 20 || x == 45 || y == 5 || y == 20) ? WALL : FLOOR;
        pmap[x][y].flags |= DISCOVERED;
        pmap[x][y].flags &= ~HAS_MONSTER;
    }
    for (creatureIterator it = iterateCreatures(monsters); hasNextCreature(it);) {
        creature *m = nextCreature(&it);
        m->ticksUntilTurn = 10000;
    }
    pmapAt(player.loc)->flags |= HAS_PLAYER;
    return brogue_bridge_perform_action(BROGUE_ACTION_WAIT, &ixTurn) == BROGUE_BRIDGE_OK ? 0 : 1;
}

static const BrogueBridgeItemState *ixItem(const item *it) {
    brogue_bridge_get_state(&ixState);
    for (uint32_t i = 0; i < ixState.itemCount; ++i)
        if (ixState.items[i].carried && ixState.items[i].inventoryLetter == (uint8_t) it->inventoryLetter)
            return &ixState.items[i];
    return NULL;
}

static BrogueBridgeResult ixCommand(BrogueBridgeCommandType type, uint64_t itemId) {
    BrogueBridgeCommand command = {0};
    command.apiVersion = BROGUE_BRIDGE_API_VERSION;
    command.type = type;
    command.itemId = itemId;
    return brogue_bridge_perform_command(&command, &ixTurn);
}

static BrogueBridgeResult ixRespond(const BrogueBridgeInteraction *pending, BrogueBridgeInteractionAnswerKind answer,
                                    uint64_t itemId, const char *text) {
    BrogueBridgeInteractionResponse response = {0};
    response.apiVersion = BROGUE_BRIDGE_API_VERSION;
    response.token = pending->token;
    response.answer = answer;
    response.itemId = itemId;
    if (text) strncpy(response.text, text, sizeof(response.text) - 1);
    return brogue_bridge_respond(&response, &ixTurn);
}

static int runInteractionSmoke(BrogueBridgeState *unused) {
    static BrogueBridgeInteraction pending, copy;
    const uint64_t seed = unused->gameSeed;
    uint64_t revision;
    (void) unused;

    /* Run until disturbed: the bridge stepper and Brogue's own playerRuns()
     * must agree on where the run stops and on every consumed turn. */
    static const enum directions nativeDirections[8] = {UP, UPRIGHT, RIGHT, DOWNRIGHT, DOWN, DOWNLEFT, LEFT, UPLEFT};
    for (int dir = 0; dir < 8; ++dir) {
        uint64_t referenceTurn, referenceHash;
        pos referenceLoc;
        IX_CHECK(ixArena(seed) == 0);
        rogue.disturbed = false;
        playerRuns((short) nativeDirections[dir]);
        referenceTurn = rogue.absoluteTurnNumber;
        referenceLoc = player.loc;
        IX_CHECK(ixArena(seed) == 0);
        {
            BrogueBridgeCommand command = {0};
            int steps = 0;
            command.apiVersion = BROGUE_BRIDGE_API_VERSION;
            command.type = BROGUE_COMMAND_RUN_START;
            command.action = (BrogueBridgeAction) dir;
            IX_CHECK(brogue_bridge_perform_command(&command, &ixTurn) == BROGUE_BRIDGE_OK);
            IX_CHECK(ixTurn.actionAccepted && ixTurn.consumedTurn);
            while (ixTurn.playerAfter.runActive && steps++ < 200) {
                command.type = BROGUE_COMMAND_RUN_CONTINUE;
                IX_CHECK(brogue_bridge_perform_command(&command, &ixTurn) == BROGUE_BRIDGE_OK);
            }
            IX_CHECK(steps < 200);
        }
        (void) referenceHash;
        if (rogue.absoluteTurnNumber != referenceTurn || !posEq(player.loc, referenceLoc)) fprintf(stderr, "dir=%d turn=%llu/%llu loc=%d,%d/%d,%d\n", dir, (unsigned long long) rogue.absoluteTurnNumber, (unsigned long long) referenceTurn, player.loc.x, player.loc.y, referenceLoc.x, referenceLoc.y);
        IX_CHECK(rogue.absoluteTurnNumber == referenceTurn);
        IX_CHECK(posEq(player.loc, referenceLoc));
        IX_CHECK(!rogue.runActive);
    }
    {
        BrogueBridgeCommand command = {0};
        command.apiVersion = BROGUE_BRIDGE_API_VERSION;
        IX_CHECK(ixArena(seed) == 0);
        command.type = BROGUE_COMMAND_RUN_CONTINUE;
        IX_CHECK(brogue_bridge_perform_command(&command, &ixTurn) == BROGUE_BRIDGE_INVALID_STATE);
        command.type = BROGUE_COMMAND_RUN_CANCEL;
        IX_CHECK(brogue_bridge_perform_command(&command, &ixTurn) == BROGUE_BRIDGE_INVALID_STATE);
        command.type = BROGUE_COMMAND_RUN_START;
        command.action = BROGUE_ACTION_WAIT;
        IX_CHECK(brogue_bridge_perform_command(&command, &ixTurn) == BROGUE_BRIDGE_INVALID_ACTION);
        command.action = BROGUE_ACTION_MOVE_E;
        IX_CHECK(brogue_bridge_perform_command(&command, &ixTurn) == BROGUE_BRIDGE_OK);
        IX_CHECK(ixTurn.playerAfter.runActive);
        IX_CHECK(brogue_bridge_perform_command(&command, &ixTurn) == BROGUE_BRIDGE_INVALID_STATE);
        command.type = BROGUE_COMMAND_RUN_CANCEL;
        IX_CHECK(brogue_bridge_perform_command(&command, &ixTurn) == BROGUE_BRIDGE_OK);
        IX_CHECK(!ixTurn.playerAfter.runActive && !ixTurn.consumedTurn);
        /* Any other command interrupts an active run, as Brogue's next key would. */
        command.type = BROGUE_COMMAND_RUN_START;
        IX_CHECK(brogue_bridge_perform_command(&command, &ixTurn) == BROGUE_BRIDGE_OK);
        IX_CHECK(brogue_bridge_perform_action(BROGUE_ACTION_WAIT, &ixTurn) == BROGUE_BRIDGE_OK);
        IX_CHECK(!ixTurn.playerAfter.runActive);
    }

    /* Call: kind naming, cancellation, validation and a retained frame. */
    IX_CHECK(ixArena(seed) == 0);
    {
        item *potion = addItemToPack(generateItem(POTION, POTION_TELEPATHY));
        const BrogueBridgeItemState *state;
        uint64_t potionId;
        IX_CHECK(brogue_bridge_perform_action(BROGUE_ACTION_WAIT, &ixTurn) == BROGUE_BRIDGE_OK);
        state = ixItem(potion);
        IX_CHECK(state != NULL);
        potionId = state->id;
        revision = ixState.revision;

        IX_CHECK(ixCommand(BROGUE_COMMAND_CALL_ITEM, potionId) == BROGUE_BRIDGE_INTERACTION_REQUIRED);
        IX_CHECK(ixTurn.interaction.kind == BROGUE_INTERACTION_TEXT && ixTurn.interaction.token != 0);
        IX_CHECK(ixTurn.interaction.textLimit > 0 && ixTurn.interaction.cancelAllowed);
        pending = ixTurn.interaction;
        IX_CHECK(brogue_bridge_get_interaction(&copy) == BROGUE_BRIDGE_OK && copy.token == pending.token);
        /* Paused: state revision is unchanged and other commands are refused. */
        brogue_bridge_get_state(&ixState);
        IX_CHECK(ixState.revision == revision);
        IX_CHECK(brogue_bridge_perform_action(BROGUE_ACTION_WAIT, &ixTurn) == BROGUE_BRIDGE_INVALID_STATE);
        IX_CHECK(ixCommand(BROGUE_COMMAND_RUN_START, 0) == BROGUE_BRIDGE_INVALID_STATE);
        {
            BrogueBridgePersistenceRequest request = {0};
            BrogueBridgePersistenceState persisted;
            request.apiVersion = BROGUE_BRIDGE_API_VERSION;
            request.operation = BROGUE_PERSIST_SAVE;
            brogue_bridge_get_state(&ixState);
            request.expectedRevision = ixState.revision;
            request.expectedSession = ixState.session;
            strcpy(request.path, "interaction-smoke.broguesave");
            IX_CHECK(brogue_bridge_persistence(&request, &persisted) == BROGUE_BRIDGE_INVALID_STATE);
        }
        /* Bad answers keep the same pending frame. */
        IX_CHECK(ixRespond(&pending, BROGUE_ANSWER_YES, 0, NULL) == BROGUE_BRIDGE_INVALID_ACTION);
        IX_CHECK(ixRespond(&pending, BROGUE_ANSWER_TEXT, 0,
                           "this name is far longer than brogue allows here") == BROGUE_BRIDGE_INVALID_ACTION);
        IX_CHECK(ixRespond(&pending, BROGUE_ANSWER_TEXT, 0, "bad\x01" "char") == BROGUE_BRIDGE_INVALID_ACTION);
        {
            BrogueBridgeInteractionResponse stale = {0};
            stale.apiVersion = BROGUE_BRIDGE_API_VERSION;
            stale.token = pending.token + 1;
            stale.answer = BROGUE_ANSWER_CANCEL;
            IX_CHECK(brogue_bridge_respond(&stale, &ixTurn) == BROGUE_BRIDGE_INVALID_ACTION);
            stale.token = pending.token;
            stale.expectedRevision = revision + 1;
            IX_CHECK(brogue_bridge_respond(&stale, &ixTurn) == BROGUE_BRIDGE_STALE_REVISION);
        }
        {
            const uint64_t turnBefore = rogue.absoluteTurnNumber;
            IX_CHECK(ixRespond(&pending, BROGUE_ANSWER_TEXT, 0, "mind reader") == BROGUE_BRIDGE_OK);
            IX_CHECK(ixTurn.success && ixTurn.actionAccepted && !ixTurn.consumedTurn);
            IX_CHECK(ixTurn.revision == revision + 1);
            IX_CHECK(rogue.absoluteTurnNumber == turnBefore);
        }
        IX_CHECK(potionTable[POTION_TELEPATHY].called);
        IX_CHECK(strcmp(potionTable[POTION_TELEPATHY].callTitle, "mind reader") == 0);
        IX_CHECK(strstr(ixItem(potion)->displayName, "mind reader") != NULL);
        IX_CHECK(brogue_bridge_get_interaction(&copy) == BROGUE_BRIDGE_OK && copy.kind == BROGUE_INTERACTION_NONE);
        IX_CHECK(ixRespond(&pending, BROGUE_ANSWER_CANCEL, 0, NULL) == BROGUE_BRIDGE_INVALID_STATE);

        /* Escape cancels without a change; empty text clears the name. */
        IX_CHECK(ixCommand(BROGUE_COMMAND_CALL_ITEM, potionId) == BROGUE_BRIDGE_INTERACTION_REQUIRED);
        pending = ixTurn.interaction;
        IX_CHECK(ixRespond(&pending, BROGUE_ANSWER_CANCEL, 0, NULL) == BROGUE_BRIDGE_OK);
        IX_CHECK(ixTurn.success && !ixTurn.actionAccepted);
        IX_CHECK(strcmp(potionTable[POTION_TELEPATHY].callTitle, "mind reader") == 0);
        IX_CHECK(ixCommand(BROGUE_COMMAND_CALL_ITEM, potionId) == BROGUE_BRIDGE_INTERACTION_REQUIRED);
        pending = ixTurn.interaction;
        IX_CHECK(ixRespond(&pending, BROGUE_ANSWER_TEXT, 0, "") == BROGUE_BRIDGE_OK);
        IX_CHECK(!potionTable[POTION_TELEPATHY].called);

        /* Without an item Brogue asks which one, with stable IDs as choices. */
        IX_CHECK(ixCommand(BROGUE_COMMAND_CALL_ITEM, 0) == BROGUE_BRIDGE_INTERACTION_REQUIRED);
        IX_CHECK(ixTurn.interaction.kind == BROGUE_INTERACTION_ITEM_CHOICE && ixTurn.interaction.choiceCount > 0);
        pending = ixTurn.interaction;
        IX_CHECK(ixRespond(&pending, BROGUE_ANSWER_ITEM, 0xfffffff, NULL) == BROGUE_BRIDGE_INVALID_ACTION);
        IX_CHECK(ixRespond(&pending, BROGUE_ANSWER_ITEM, potionId, NULL) == BROGUE_BRIDGE_INTERACTION_REQUIRED);
        IX_CHECK(ixTurn.interaction.kind == BROGUE_INTERACTION_TEXT);
        pending = ixTurn.interaction;
        IX_CHECK(ixRespond(&pending, BROGUE_ANSWER_TEXT, 0, "telepathy?") == BROGUE_BRIDGE_OK);
        IX_CHECK(strcmp(potionTable[POTION_TELEPATHY].callTitle, "telepathy?") == 0);
    }

    /* Relabel: swap with an occupied letter and ignore non-letters. */
    IX_CHECK(ixArena(seed) == 0);
    {
        item *first = packItems->nextItem, *second = first->nextItem;
        const char firstLetter = first->inventoryLetter, secondLetter = second->inventoryLetter;
        const BrogueBridgeItemState *state = ixItem(first);
        uint64_t firstId;
        IX_CHECK(state != NULL);
        firstId = state->id;
        IX_CHECK(ixCommand(BROGUE_COMMAND_RELABEL_ITEM, firstId) == BROGUE_BRIDGE_INTERACTION_REQUIRED);
        IX_CHECK(ixTurn.interaction.kind == BROGUE_INTERACTION_TEXT && ixTurn.interaction.textIsSingleLetter
                 && ixTurn.interaction.textLimit == 1);
        pending = ixTurn.interaction;
        IX_CHECK(ixRespond(&pending, BROGUE_ANSWER_TEXT, 0, "ab") == BROGUE_BRIDGE_INVALID_ACTION);
        IX_CHECK(ixRespond(&pending, BROGUE_ANSWER_TEXT, 0, "") == BROGUE_BRIDGE_INVALID_ACTION);
        {
            char text[2] = { (char) (secondLetter - 'a' + 'A'), 0 };
            const uint64_t turnBefore = rogue.absoluteTurnNumber;
            IX_CHECK(ixRespond(&pending, BROGUE_ANSWER_TEXT, 0, text) == BROGUE_BRIDGE_OK);
            IX_CHECK(ixTurn.actionAccepted && !ixTurn.consumedTurn);
            IX_CHECK(rogue.absoluteTurnNumber == turnBefore);
        }
        IX_CHECK(first->inventoryLetter == secondLetter && second->inventoryLetter == firstLetter);
        IX_CHECK(ixCommand(BROGUE_COMMAND_RELABEL_ITEM, firstId) == BROGUE_BRIDGE_INTERACTION_REQUIRED);
        pending = ixTurn.interaction;
        IX_CHECK(ixRespond(&pending, BROGUE_ANSWER_TEXT, 0, "1") == BROGUE_BRIDGE_OK);
        IX_CHECK(first->inventoryLetter == secondLetter);
    }

    /* A third ring asks which equipped ring to replace. */
    IX_CHECK(ixArena(seed) == 0);
    {
        item *rings[3];
        for (int i = 0; i < 3; ++i) {
            rings[i] = generateItem(RING, RING_CLAIRVOYANCE + i);
            rings[i]->flags &= ~ITEM_CURSED;
            rings[i]->enchant1 = 1;
            addItemToPack(rings[i]);
        }
        IX_CHECK(brogue_bridge_perform_action(BROGUE_ACTION_WAIT, &ixTurn) == BROGUE_BRIDGE_OK);
        IX_CHECK(ixCommand(BROGUE_COMMAND_EQUIP_ITEM, ixItem(rings[0])->id) == BROGUE_BRIDGE_OK);
        IX_CHECK(ixTurn.actionAccepted && ixTurn.consumedTurn && (rings[0]->flags & ITEM_EQUIPPED));
        IX_CHECK(ixCommand(BROGUE_COMMAND_EQUIP_ITEM, ixItem(rings[1])->id) == BROGUE_BRIDGE_OK);
        IX_CHECK(ixTurn.actionAccepted && (rings[1]->flags & ITEM_EQUIPPED));
        {
            const uint64_t thirdId = ixItem(rings[2])->id, turnBefore = rogue.absoluteTurnNumber;
            IX_CHECK(ixCommand(BROGUE_COMMAND_EQUIP_ITEM, thirdId) == BROGUE_BRIDGE_INTERACTION_REQUIRED);
            IX_CHECK(ixTurn.interaction.kind == BROGUE_INTERACTION_ITEM_CHOICE && ixTurn.interaction.choiceCount == 2);
            pending = ixTurn.interaction;
            IX_CHECK(ixRespond(&pending, BROGUE_ANSWER_ITEM, thirdId, NULL) == BROGUE_BRIDGE_INVALID_ACTION);
            IX_CHECK(ixRespond(&pending, BROGUE_ANSWER_CANCEL, 0, NULL) == BROGUE_BRIDGE_OK);
            IX_CHECK(!ixTurn.actionAccepted && rogue.absoluteTurnNumber == turnBefore);
            IX_CHECK(!(rings[2]->flags & ITEM_EQUIPPED));
            IX_CHECK(ixCommand(BROGUE_COMMAND_EQUIP_ITEM, thirdId) == BROGUE_BRIDGE_INTERACTION_REQUIRED);
            pending = ixTurn.interaction;
            IX_CHECK(ixRespond(&pending, BROGUE_ANSWER_ITEM, ixItem(rings[0])->id, NULL) == BROGUE_BRIDGE_OK);
            IX_CHECK(ixTurn.actionAccepted && ixTurn.consumedTurn);
            IX_CHECK((rings[2]->flags & ITEM_EQUIPPED) && !(rings[0]->flags & ITEM_EQUIPPED));
        }
    }

    /* Swap-last-equipment and rethrow. */
    IX_CHECK(ixArena(seed) == 0);
    {
        item *sword = addItemToPack(generateItem(WEAPON, SWORD));
        item *dart = addItemToPack(generateItem(WEAPON, DART));
        dart->quantity = 5;
        sword->flags &= ~ITEM_CURSED;
        IX_CHECK(brogue_bridge_perform_action(BROGUE_ACTION_WAIT, &ixTurn) == BROGUE_BRIDGE_OK);
        IX_CHECK(!ixTurn.playerAfter.canSwapEquipment);
        IX_CHECK(ixCommand(BROGUE_COMMAND_SWAP_LAST_EQUIPMENT, 0) == BROGUE_BRIDGE_OK);
        IX_CHECK(!ixTurn.actionAccepted && !ixTurn.consumedTurn);
        IX_CHECK(ixCommand(BROGUE_COMMAND_EQUIP_ITEM, ixItem(sword)->id) == BROGUE_BRIDGE_OK);
        IX_CHECK(ixTurn.actionAccepted && ixTurn.playerAfter.canSwapEquipment);
        IX_CHECK(rogue.weapon == sword);
        IX_CHECK(ixCommand(BROGUE_COMMAND_SWAP_LAST_EQUIPMENT, 0) == BROGUE_BRIDGE_OK);
        IX_CHECK(ixTurn.actionAccepted && ixTurn.consumedTurn && rogue.weapon != sword);
        IX_CHECK(ixCommand(BROGUE_COMMAND_SWAP_LAST_EQUIPMENT, 0) == BROGUE_BRIDGE_OK);
        IX_CHECK(ixTurn.actionAccepted && rogue.weapon == sword);

        /* No throw yet: Brogue ignores rethrow. */
        IX_CHECK(ixCommand(BROGUE_COMMAND_RETHROW_LAST, 0) == BROGUE_BRIDGE_OK);
        IX_CHECK(!ixTurn.actionAccepted && !ixTurn.consumedTurn);
        {
            BrogueBridgeCommand throwCommand = {0};
            throwCommand.apiVersion = BROGUE_BRIDGE_API_VERSION;
            throwCommand.type = BROGUE_COMMAND_THROW_ITEM;
            throwCommand.itemId = ixItem(dart)->id;
            throwCommand.targetX = 38;
            throwCommand.targetY = 12;
            IX_CHECK(brogue_bridge_perform_command(&throwCommand, &ixTurn) == BROGUE_BRIDGE_OK);
            IX_CHECK(ixTurn.actionAccepted && dart->quantity == 4);
            IX_CHECK(ixTurn.playerAfter.lastThrownItemId != 0);
        }
        rogue.lastTarget = NULL;
        IX_CHECK(ixCommand(BROGUE_COMMAND_RETHROW_LAST, 0) == BROGUE_BRIDGE_INTERACTION_REQUIRED);
        IX_CHECK(ixTurn.interaction.kind == BROGUE_INTERACTION_TARGET_LOCATION
                 && ixTurn.interaction.itemId == ixItem(dart)->id && ixTurn.interaction.maxDistance > 0);
        pending = ixTurn.interaction;
        {
            BrogueBridgeInteractionResponse response = {0};
            response.apiVersion = BROGUE_BRIDGE_API_VERSION;
            response.token = pending.token;
            response.answer = BROGUE_ANSWER_LOCATION;
            response.targetX = -1;
            response.targetY = 0;
            IX_CHECK(brogue_bridge_respond(&response, &ixTurn) == BROGUE_BRIDGE_INVALID_ACTION);
            response.targetX = 39;
            response.targetY = 12;
            IX_CHECK(brogue_bridge_respond(&response, &ixTurn) == BROGUE_BRIDGE_OK);
            IX_CHECK(ixTurn.actionAccepted && ixTurn.consumedTurn && dart->quantity == 3);
        }
        IX_CHECK(ixCommand(BROGUE_COMMAND_RETHROW_LAST, 0) == BROGUE_BRIDGE_INTERACTION_REQUIRED);
        pending = ixTurn.interaction;
        IX_CHECK(ixRespond(&pending, BROGUE_ANSWER_CANCEL, 0, NULL) == BROGUE_BRIDGE_OK);
        IX_CHECK(!ixTurn.actionAccepted && dart->quantity == 3);

        /* An equipped, enchanted item asks Brogue's throw confirmation first. */
        IX_CHECK(ixCommand(BROGUE_COMMAND_THROW_ITEM, 0) == BROGUE_BRIDGE_ITEM_NOT_FOUND);
    }

    /* Session commands. */
    IX_CHECK(ixArena(seed) == 0);
    {
        BrogueBridgeCommand command = {0};
        command.apiVersion = BROGUE_BRIDGE_API_VERSION;
        command.type = BROGUE_COMMAND_NEW_GAME;
        command.seed = 4242;
        rogue.playerTurnNumber = 10;
        IX_CHECK(brogue_bridge_perform_command(&command, &ixTurn) == BROGUE_BRIDGE_OK);
        IX_CHECK(ixTurn.sessionChange == BROGUE_SESSION_CHANGE_NEW_GAME && ixTurn.requestedSeed == 4242);
        IX_CHECK(!rogue.gameHasEnded);
        rogue.playerTurnNumber = 80;
        IX_CHECK(brogue_bridge_perform_command(&command, &ixTurn) == BROGUE_BRIDGE_INTERACTION_REQUIRED);
        IX_CHECK(ixTurn.interaction.kind == BROGUE_INTERACTION_CONFIRM);
        pending = ixTurn.interaction;
        IX_CHECK(ixRespond(&pending, BROGUE_ANSWER_NO, 0, NULL) == BROGUE_BRIDGE_OK);
        IX_CHECK(ixTurn.sessionChange == BROGUE_SESSION_CHANGE_NONE && !ixTurn.actionAccepted);
        IX_CHECK(brogue_bridge_perform_command(&command, &ixTurn) == BROGUE_BRIDGE_INTERACTION_REQUIRED);
        pending = ixTurn.interaction;
        IX_CHECK(ixRespond(&pending, BROGUE_ANSWER_YES, 0, NULL) == BROGUE_BRIDGE_OK);
        IX_CHECK(ixTurn.sessionChange == BROGUE_SESSION_CHANGE_NEW_GAME && ixTurn.requestedSeed == 4242);
        /* The frontend then starts the requested seed. */
        IX_CHECK(brogue_bridge_start_game(ixTurn.requestedSeed) == BROGUE_BRIDGE_OK);
        brogue_bridge_get_state(&ixState);
        IX_CHECK(ixState.gameSeed == 4242 && !ixState.player.gameHasEnded);
        IX_CHECK(brogue_bridge_get_interaction(&copy) == BROGUE_BRIDGE_OK && copy.kind == BROGUE_INTERACTION_NONE);

        command.type = BROGUE_COMMAND_ABANDON_GAME;
        IX_CHECK(brogue_bridge_perform_command(&command, &ixTurn) == BROGUE_BRIDGE_INTERACTION_REQUIRED);
        IX_CHECK(ixTurn.interaction.kind == BROGUE_INTERACTION_CONFIRM);
        pending = ixTurn.interaction;
        IX_CHECK(ixRespond(&pending, BROGUE_ANSWER_CANCEL, 0, NULL) == BROGUE_BRIDGE_OK);
        IX_CHECK(!rogue.gameHasEnded && ixTurn.sessionChange == BROGUE_SESSION_CHANGE_NONE);
        IX_CHECK(brogue_bridge_perform_command(&command, &ixTurn) == BROGUE_BRIDGE_INTERACTION_REQUIRED);
        pending = ixTurn.interaction;
        IX_CHECK(ixRespond(&pending, BROGUE_ANSWER_YES, 0, NULL) == BROGUE_BRIDGE_OK);
        IX_CHECK(ixTurn.sessionChange == BROGUE_SESSION_CHANGE_ABANDONED);
        brogue_bridge_get_state(&ixState);
        IX_CHECK(ixState.player.gameHasEnded && ixState.gameResult.outcome == BROGUE_GAME_OUTCOME_QUIT);
        IX_CHECK(brogue_bridge_perform_action(BROGUE_ACTION_WAIT, &ixTurn) == BROGUE_BRIDGE_GAME_ENDED);
    }
    printf("INTERACTION_SMOKE ok seed=%llu\n", (unsigned long long) seed);
    return 0;
}
#undef IX_CHECK
