/* Independent oracle: terminal executeKeystroke(), with a finite console input
 * tape. Never submits a bridge command or enables its confirmation broker.
 * An unexpected input boundary fails immediately instead of inventing an answer.
 */
#include "ItemCommandFrame.h"
static const unsigned char *fixtureInput;
static size_t fixtureInputIndex, fixtureInputLength;
static boolean fixtureShiftFirst;

static void fixtureHex(const char *text) {
    for (const unsigned char *p = (const unsigned char *)text; *p; ++p) printf("%02x", *p);
}

static void fixtureRead(rogueEvent *event, boolean textInput, boolean colorsDance) {
    (void)colorsDance;
    if (fixtureInputIndex >= fixtureInputLength) {
        fprintf(stderr, "Native fixture exhausted input at boundary %llu (text=%d).\n",
                (unsigned long long)fixtureInputIndex, textInput);
        for (int i = 0; i < MESSAGE_LINES; ++i) fprintf(stderr, "MESSAGE %s\n", displayedMessage[i]);
        exit(3);
    }
    printf("INPUT index=%llu text=%d key=%u turn=%lu rng=%lu recording=%lu\n",
           (unsigned long long)fixtureInputIndex, textInput, fixtureInput[fixtureInputIndex],
           rogue.playerTurnNumber, randomNumbersGenerated, recordingLocation);
    /* Preserve the native terminal prompt at every input boundary, including
     * confirmations and inventory overlays. Glyph numbers avoid lossy encoding. */
    for (int y = 0; y < ROWS; ++y) {
        printf("SCREEN y=%d", y);
        for (int x = 0; x < COLS; ++x) printf(" %x", displayBuffer.cells[x][y].character);
        putchar('\n');
    }
    memset(event, 0, sizeof(*event));
    event->eventType = KEYSTROKE;
    event->shiftKey = fixtureShiftFirst && fixtureInputIndex == 0;
    event->param1 = fixtureInput[fixtureInputIndex++];
}

static void fixtureState(const char *phase) {
    printf("STATE phase=%s turn=%lu absolute=%lu rng=%lu recording=%lu player=%d,%d hp=%d\n",
           phase, rogue.playerTurnNumber, rogue.absoluteTurnNumber, randomNumbersGenerated,
           recordingLocation, player.loc.x, player.loc.y, player.currentHP);
    for (int i = 0; i < NUMBER_OF_STATUS_EFFECTS; ++i)
        printf("STATUS index=%d value=%d maximum=%d\n", i, player.status[i], player.maxStatus[i]);
    for (int y = 0; y < DROWS; ++y) for (int x = 0; x < DCOLS; ++x) {
        printf("CELL x=%d y=%d flags=%lu volume=%d machine=%d layers=", x, y,
               pmap[x][y].flags, pmap[x][y].volume, pmap[x][y].machineNumber);
        for (int layer = 0; layer < NUMBER_TERRAIN_LAYERS; ++layer)
            printf("%s%d", layer ? "," : "", pmap[x][y].layers[layer]);
        putchar('\n');
    }
    creatureIterator iterator = iterateCreatures(monsters);
    while (hasNextCreature(iterator)) {
        creature *monst = nextCreature(&iterator);
        printf("CREATURE kind=%d loc=%d,%d hp=%d state=%d flags=%lu\n", monst->info.monsterID,
               monst->loc.x, monst->loc.y, monst->currentHP, monst->creatureState, monst->bookkeepingFlags);
    }
    for (item *it = packItems->nextItem; it; it = it->nextItem) {
        printf("ITEM category=%u kind=%d letter=%d flags=%lu quantity=%d enchant=%d,%d charges=%d inscription=",
               it->category, it->kind, it->inventoryLetter, it->flags, it->quantity,
               it->enchant1, it->enchant2, it->charges);
        fixtureHex(it->inscription);
        itemTable *table = tableForItemCategory(it->category);
        if (table) {
            printf(" identified=%d called=%d title=", table[it->kind].identified, table[it->kind].called);
            fixtureHex(table[it->kind].callTitle);
        }
        putchar('\n');
    }
    printf("MESSAGES position=%d\n", messageArchivePosition);
    for (int i = 0; i < MESSAGE_ARCHIVE_ENTRIES; ++i) {
        if (!messageArchive[i].message[0]) continue;
        printf("MESSAGE index=%d count=%u turn=%lu flags=%lu text=", i,
               messageArchive[i].count, messageArchive[i].turn, messageArchive[i].flags);
        fixtureHex(messageArchive[i].message);
        putchar('\n');
    }
    printf("RECORDING buffered=%u bytes=", locationInRecordingBuffer);
    for (int i = 0; i < locationInRecordingBuffer; ++i) printf("%02x", inputRecordBuffer[i]);
    putchar('\n');
}

static int fixtureCheckFrames(void) {
    nativeItemCommandFrame frame, pending;
    nativeItemAnswer answer = {0};
    unsigned long turn = rogue.absoluteTurnNumber, rng = randomNumbersGenerated, recording = recordingLocation;
    item *weapon = rogue.weapon, *armor = rogue.armor;
    char weaponLetter = weapon->inventoryLetter, armorLetter = armor->inventoryLetter;
#define FRAME_CHECK(c) do { if (!(c)) { fprintf(stderr, "Native frame check failed at line %d: %s\n", __LINE__, #c); return 4; } } while (0)
    beginNativeItemCommand(&frame, NATIVE_ITEM_CALL, weapon);
    FRAME_CHECK(frame.promptKind == NATIVE_ITEM_TEXT && frame.textLimit > 0 && frame.textLimit < 29);
    FRAME_CHECK(!weapon->inscription[0] && recordingLocation == recording && rogue.absoluteTurnNumber == turn);
    pending = frame;
    answer.kind = NATIVE_ITEM_ANSWER_YES;
    FRAME_CHECK(!stepNativeItemCommand(&frame, &answer) && !memcmp(&frame, &pending, sizeof(frame)));
    answer.kind = NATIVE_ITEM_ANSWER_TEXT;
    strcpy(answer.text, "bad\001text");
    FRAME_CHECK(!stepNativeItemCommand(&frame, &answer) && !memcmp(&frame, &pending, sizeof(frame)));
    memset(answer.text, 'x', frame.textLimit + 1); answer.text[frame.textLimit + 1] = 0;
    FRAME_CHECK(!stepNativeItemCommand(&frame, &answer) && !memcmp(&frame, &pending, sizeof(frame)));
    memset(answer.text, 'x', sizeof(answer.text));
    FRAME_CHECK(!stepNativeItemCommand(&frame, &answer));
    strcpy(answer.text, "frame");
    FRAME_CHECK(stepNativeItemCommand(&frame, &answer) && frame.promptKind == NATIVE_ITEM_COMPLETE);
    FRAME_CHECK(!strcmp(weapon->inscription, "frame") && rogue.absoluteTurnNumber == turn && randomNumbersGenerated == rng);
    recording = recordingLocation;
    FRAME_CHECK(!stepNativeItemCommand(&frame, &answer) && recordingLocation == recording);
    beginNativeItemCommand(&frame, NATIVE_ITEM_RELABEL, weapon);
    FRAME_CHECK(frame.promptKind == NATIVE_ITEM_TEXT && frame.relabelLetter && frame.textLimit == 1);
    memset(&answer, 0, sizeof(answer)); answer.kind = NATIVE_ITEM_ANSWER_TEXT;
    answer.text[0] = armorLetter - 'a' + 'A';
    FRAME_CHECK(stepNativeItemCommand(&frame, &answer));
    FRAME_CHECK(itemOfPackLetter(armorLetter) == weapon && itemOfPackLetter(weaponLetter) == armor);
    FRAME_CHECK(rogue.absoluteTurnNumber == turn && randomNumbersGenerated == rng);
    item *ring = addItemToPack(generateItem(RING, RING_CLAIRVOYANCE));
    ring->flags &= ~ITEM_IDENTIFIED;
    tableForItemCategory(RING)[ring->kind].identified = false;
    beginNativeItemCommand(&frame, NATIVE_ITEM_CALL, ring);
    FRAME_CHECK(frame.promptKind == NATIVE_ITEM_CONFIRMATION && frame.escapeMeansNo);
    recording = recordingLocation;
    answer.kind = NATIVE_ITEM_ANSWER_ESCAPE;
    FRAME_CHECK(stepNativeItemCommand(&frame, &answer) && frame.promptKind == NATIVE_ITEM_TEXT);
    FRAME_CHECK(!strcmp(frame.prompt, "call them: \"") && !frame.escapeMeansNo && recordingLocation == recording);
    FRAME_CHECK(stepNativeItemCommand(&frame, &answer) && frame.promptKind == NATIVE_ITEM_COMPLETE);
    FRAME_CHECK(recordingLocation == recording && rogue.absoluteTurnNumber == turn);
    item *second = addItemToPack(generateItem(RING, RING_STEALTH));
    item *third = addItemToPack(generateItem(RING, RING_REGENERATION));
    ring->flags &= ~ITEM_CURSED; second->flags &= ~ITEM_CURSED;
    equipItem(ring, true, NULL); equipItem(second, true, NULL);
    rng = randomNumbersGenerated;
    beginNativeItemCommand(&frame, NATIVE_ITEM_EQUIP, third);
    FRAME_CHECK(frame.promptKind == NATIVE_ITEM_CHOICE && frame.selected == third);
    FRAME_CHECK(rogue.ringLeft == ring && rogue.ringRight == second && recordingLocation == recording);
    pending = frame;
    answer.kind = NATIVE_ITEM_ANSWER_YES;
    FRAME_CHECK(!stepNativeItemCommand(&frame, &answer) && !memcmp(&pending, &frame, sizeof(frame)));
    answer.kind = NATIVE_ITEM_ANSWER_ESCAPE;
    FRAME_CHECK(stepNativeItemCommand(&frame, &answer) && frame.promptKind == NATIVE_ITEM_COMPLETE);
    FRAME_CHECK(rogue.ringLeft == ring && rogue.ringRight == second && !(third->flags & ITEM_EQUIPPED));
    FRAME_CHECK(rogue.absoluteTurnNumber == turn && recordingLocation == recording && randomNumbersGenerated == rng);
    puts("NATIVE-FRAMES pending=retained invalid=unchanged duplicate=no-effect relabel=pointers-preserved escape=continues-kind");
    return 0;
#undef FRAME_CHECK
}

static int runNativeInteractionFixture(uint64_t seed, const char *scenario) {
    unsigned char tape[256] = {0};
    size_t n = 0;
    item *selected;
    int key = CALL_KEY;
    gameVariant = VARIANT_BROGUE;
    initializeGameVariant();
    currentConsole = nullConsole;
    currentConsole.nextKeyOrMouseEvent = fixtureRead;
    serverMode = false;
    nonInteractivePlayback = false;
    hasGraphics = false;
    graphicsMode = TEXT_GRAPHICS;
    rogue.mode = GAME_MODE_NORMAL;
    rogue.playbackMode = false;
    rogue.nextGame = NG_NOTHING;
    strcpy(currentFilePath, "native-input.broguesave");
    initializeRogue(seed);
    startLevel(rogue.depthLevel, 1);
    selected = rogue.weapon;
    if (!strcmp(scenario, "frame-check")) {
        int result = fixtureCheckFrames();
        freeEverything(); currentFilePath[0] = 0;
        return result;
    }

    if (!strncmp(scenario, "nested-", 7)) {
        key = APPLY_KEY;
        fixtureShiftFirst = true;
        tape[n++] = selected->inventoryLetter;
        if (!strcmp(scenario, "nested-relabel")) {
            tape[n++] = RELABEL_KEY; tape[n++] = 'Z';
        } else {
            tape[n++] = CALL_KEY;
            memcpy(tape + n, "nested", 6); n += 6;
            tape[n++] = RETURN_KEY;
        }
        goto prepared;
    }
    if (!strncmp(scenario, "acid-", 5) || !strncmp(scenario, "sequential-", 11)) {
        key = UP_KEY;
        pos destination = {player.loc.x, player.loc.y - 1};
        for (int layer = 0; layer < NUMBER_TERRAIN_LAYERS; ++layer) pmapAt(destination)->layers[layer] = NOTHING;
        pmapAt(destination)->layers[DUNGEON] = FLOOR;
        pmapAt(destination)->flags |= DISCOVERED | VISIBLE | HAS_MONSTER;
        creature *target = generateMonster(MK_ACID_JELLY, false, false);
        target->loc = destination;
        target->info.flags |= MONST_DEFEND_DEGRADE_WEAPON;
        target->ticksUntilTurn = 10000;
        if (!strncmp(scenario, "sequential-", 11)) {
            target->creatureState = MONSTER_ALLY;
            target->status[STATUS_DISCORDANT] = 100;
            tape[n++] = 'y';
        }
        tape[n++] = strstr(scenario, "yes") ? 'y' : strstr(scenario, "no") ? 'n' : ESCAPE_KEY;
        goto prepared;
    }

    if (!strncmp(scenario, "food-", 5)) {
        key = APPLY_KEY;
        for (selected = packItems->nextItem; selected && selected->category != FOOD; selected = selected->nextItem) {}
        if (!selected) return 2;
        tape[n++] = selected->inventoryLetter;
        tape[n++] = !strcmp(scenario, "food-yes") ? 'y' : !strcmp(scenario, "food-no") ? 'n' : ESCAPE_KEY;
        goto prepared;
    }
    if (!strncmp(scenario, "identify-", 9) || !strncmp(scenario, "enchant-", 8)) {
        boolean identifying = !strncmp(scenario, "identify-", 9);
        boolean empty = strstr(scenario, "empty") != NULL;
        key = APPLY_KEY;
        selected = addItemToPack(generateItem(SCROLL, identifying ? SCROLL_IDENTIFY : SCROLL_ENCHANTING));
        tableForItemCategory(SCROLL)[selected->kind].identified = false;
        selected->flags &= ~ITEM_IDENTIFIED;
        if (empty) {
            if (identifying) {
                for (item *it = packItems->nextItem; it; it = it->nextItem) if (it != selected) identify(it);
            } else {
                rogue.weapon = rogue.armor = NULL;
                item *it = packItems->nextItem;
                while (it) {
                    item *next = it->nextItem;
                    if (it != selected) { removeItemFromChain(it, packItems); deleteItem(it); }
                    it = next;
                }
            }
        } else if (identifying) {
            item *ring = addItemToPack(generateItem(RING, RING_CLAIRVOYANCE));
            ring->flags &= ~ITEM_IDENTIFIED;
        }
        updateIdentifiableItems();
        tape[n++] = selected->inventoryLetter;
        tape[n++] = ACKNOWLEDGE_KEY;
        if (!empty) {
            if (strstr(scenario, "escape")) {
                tape[n++] = ESCAPE_KEY;
                if (!identifying) tape[n++] = ACKNOWLEDGE_KEY;
            }
            if (identifying) {
                for (item *it = packItems->nextItem; it; it = it->nextItem)
                    if (it->category == RING) { tape[n++] = it->inventoryLetter; break; }
            } else tape[n++] = rogue.weapon->inventoryLetter;
        }
        goto prepared;
    }
    if (!strncmp(scenario, "equip-", 6)) {
        key = EQUIP_KEY;
        if (strstr(scenario, "third-ring")) {
            item *first = addItemToPack(generateItem(RING, RING_CLAIRVOYANCE));
            item *second = addItemToPack(generateItem(RING, RING_STEALTH));
            selected = addItemToPack(generateItem(RING, RING_REGENERATION));
            first->flags &= ~ITEM_CURSED; second->flags &= ~ITEM_CURSED;
            equipItem(first, true, NULL); equipItem(second, true, NULL);
            if (strstr(scenario, "cursed")) first->flags |= ITEM_CURSED;
            tape[n++] = selected->inventoryLetter;
            tape[n++] = strstr(scenario, "cancel") ? ESCAPE_KEY : first->inventoryLetter;
        } else {
            selected = addItemToPack(generateItem(WEAPON, DAGGER));
            if (strstr(scenario, "cursed")) rogue.weapon->flags |= ITEM_CURSED;
            tape[n++] = selected->inventoryLetter;
        }
        goto prepared;
    }
    if (!strncmp(scenario, "remove-", 7) || !strncmp(scenario, "drop-", 5)) {
        key = !strncmp(scenario, "remove-", 7) ? UNEQUIP_KEY : DROP_KEY;
        if (strstr(scenario, "cursed")) selected->flags |= ITEM_CURSED;
        tape[n++] = selected->inventoryLetter;
        goto prepared;
    }
    if (!strncmp(scenario, "chasm-", 6)) {
        key = UP_KEY;
        pos destination = {player.loc.x, player.loc.y - 1};
        pmapAt(destination)->layers[DUNGEON] = FLOOR;
        pmapAt(destination)->layers[LIQUID] = CHASM;
        pmapAt(destination)->flags |= DISCOVERED;
        tape[n++] = !strcmp(scenario, "chasm-yes") ? 'y' : !strcmp(scenario, "chasm-no") ? 'n' : ESCAPE_KEY;
        if (!strcmp(scenario, "chasm-yes")) tape[n++] = ACKNOWLEDGE_KEY;
        goto prepared;
    }
    if (!strncmp(scenario, "throw-", 6) || !strncmp(scenario, "staff-", 6) || !strncmp(scenario, "wand-", 5)) {
        if (!strncmp(scenario, "throw-", 6)) {
            key = THROW_KEY;
            for (selected = packItems->nextItem; selected; selected = selected->nextItem)
                if (selected->category == WEAPON && selected->kind == DART) break;
        } else {
            key = APPLY_KEY;
            selected = addItemToPack(generateItem(!strncmp(scenario, "staff-", 6) ? STAFF : WAND,
                                                 !strncmp(scenario, "staff-", 6) ? STAFF_LIGHTNING : WAND_SLOW));
            selected->charges = 3;
        }
        tape[n++] = selected->inventoryLetter;
        if (strstr(scenario, "cycle")) tape[n++] = TAB_KEY;
        if (strstr(scenario, "cancel")) tape[n++] = ESCAPE_KEY;
        else { tape[n++] = UP_KEY; tape[n++] = RETURN_KEY; }
        goto prepared;
    }
    if (!strncmp(scenario, "kind-", 5) || !strncmp(scenario, "ring-", 5)) {
        selected = generateItem(RING, RING_CLAIRVOYANCE);
        selected->flags &= ~(ITEM_IDENTIFIED | ITEM_CURSED);
        selected->inventoryLetter = 'z';
        selected = addItemToPack(selected);
        tableForItemCategory(RING)[selected->kind].identified = false;
        updateIdentifiableItems();
    }
    tape[n++] = selected->inventoryLetter;
    if (!strncmp(scenario, "relabel-", 8)) {
        key = RELABEL_KEY;
        if (!strcmp(scenario, "relabel-uppercase")) tape[n++] = 'Z';
        else if (!strcmp(scenario, "relabel-swap")) tape[n++] = rogue.armor->inventoryLetter;
        else if (!strcmp(scenario, "relabel-unchanged")) tape[n++] = selected->inventoryLetter;
        else if (!strcmp(scenario, "relabel-cancel")) tape[n++] = ESCAPE_KEY;
        else if (!strcmp(scenario, "relabel-invalid")) tape[n++] = '1';
        else return 2;
    } else {
        if (!strcmp(scenario, "ring-inscribe")) tape[n++] = 'y';
        else if (!strcmp(scenario, "kind-no")) tape[n++] = 'n';
        else if (!strcmp(scenario, "kind-escape")) tape[n++] = ESCAPE_KEY;
        else if (!strcmp(scenario, "kind-clear")) {
            strcpy(tableForItemCategory(RING)[selected->kind].callTitle, "old title");
            tableForItemCategory(RING)[selected->kind].called = true;
            tape[n++] = 'n';
        }
        if (!strcmp(scenario, "inscribe-cancel")) tape[n++] = ESCAPE_KEY;
        else {
            if (!strcmp(scenario, "inscribe-clear") || !strcmp(scenario, "kind-clear")) {
                strcpy(selected->inscription, "old inscription");
            } else if (!strcmp(scenario, "inscribe-maximum")) {
                for (int i = 0; i < 40; ++i) tape[n++] = 'x';
            } else if (!strcmp(scenario, "inscribe-invalid")) {
                tape[n++] = 1; tape[n++] = 127; tape[n++] = 'A';
            } else if (!strcmp(scenario, "inscribe-delete")) {
                tape[n++] = 'A'; tape[n++] = 'B'; tape[n++] = DELETE_KEY; tape[n++] = 'C';
            } else if (!strcmp(scenario, "inscribe") || !strcmp(scenario, "ring-inscribe")
                       || !strcmp(scenario, "kind-no") || !strcmp(scenario, "kind-escape")) {
                memcpy(tape + n, "fixture", 7); n += 7;
            } else return 2;
            tape[n++] = RETURN_KEY;
        }
    }
prepared:
    fixtureInput = tape;
    fixtureInputIndex = 0;
    fixtureInputLength = n;
    printf("FIXTURE scenario=%s seed=%llu entry=executeKeystroke command=%d\n", scenario,
           (unsigned long long)seed, key);
    fixtureState("before");
    executeKeystroke(key, false, false);
    if (fixtureInputIndex != fixtureInputLength) {
        fprintf(stderr, "Native fixture left %llu unused responses.\n",
                (unsigned long long)(fixtureInputLength - fixtureInputIndex));
        return 3;
    }
    fixtureState("after");
    flushBufferToFile();
    if (recordingLastError()[0]) { fprintf(stderr, "%s\n", recordingLastError()); return 3; }
    /* The recorded artifact ends at the turnless command boundary. */
    if (!saveGameToPath("native-command.broguesave")) return 3;
    rogue.gameHasEnded = false;
    executeKeystroke(REST_KEY, false, false);
    fixtureState("wait");
    printf("CONTINUATION random=%ld\n", rand_range(0, 1000000));
    freeEverything();
    currentFilePath[0] = 0;
    return 0;
}
