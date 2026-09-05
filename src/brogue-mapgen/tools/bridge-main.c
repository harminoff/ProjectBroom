/*
 * Headless deterministic driver for the public Brogue bridge contract.
 *
 * Example:
 *   brogue-bridge.exe --seed 12345 --actions "N,N,E,WAIT,SE,W"
 */
#include "Rogue.h"
#include "GlobalsBase.h"
#include "Globals.h"
#include "platform.h"
#include "BrogueBridge.h"
#include "BrogueBridgeInternal.h"

#include <ctype.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "bridge-staff-smoke.h"
#include "bridge-wand-smoke.h"
#include "bridge-target-smoke.h"

static void printEvents(const BrogueBridgeTurnResult *result);

/* MainMenu.c references the normal platform parser.  The bridge driver owns
 * its command-line parser, but retains this small compatibility symbol so
 * the unchanged Brogue menu translation unit can still be linked. */
boolean tryParseUint64(char *text, uint64_t *outValue) {
    unsigned long long value;
    char normalized[100];

    if (text == NULL || *text == '\0'
        || sscanf(text, "%llu", &value) != 1
        || sprintf(normalized, "%llu", value) <= 0
        || strcmp(normalized, text) != 0) {
        return false;
    }
    *outValue = (uint64_t) value;
    return true;
}

static void printUsage(void) {
    puts("Usage: brogue-bridge --seed SEED [--actions ACTIONS] [--long-run COUNT] [--weapon-smoke] [--consumable-smoke] [--warning-smoke] [--look-smoke] [--verbose]");
    puts("       brogue-bridge --dump-monster-catalog OUTPUT.json");
    puts("       brogue-bridge --seed SEED [--staff-smoke | --wand-smoke]");
    puts("Actions: N, NE, E, SE, S, SW, W, NW, WAIT (or numpad 8,9,6,3,2,1,4,7,5)");
}

static const BrogueBridgeItemState *findCarriedCategory(const BrogueBridgeState *state, int category) {
    size_t i;
    for (i = 0; i < state->itemCount; i++) {
        if (state->items[i].carried && (state->items[i].category & category)) {
            return &state->items[i];
        }
    }
    return NULL;
}

static const BrogueBridgeItemState *findItemId(const BrogueBridgeState *state, uint64_t id) {
    size_t i;
    for (i = 0; i < state->itemCount; i++) {
        if (state->items[i].id == id) return &state->items[i];
    }
    return NULL;
}

static boolean choiceContains(const BrogueBridgeTurnResult *turn, uint64_t itemId) {
    size_t i;
    for (i = 0; i < turn->choiceCount; i++) {
        if (turn->choiceItemIds[i] == itemId) return true;
    }
    return false;
}

static const BrogueBridgeItemState *findCarriedWeapon(const BrogueBridgeState *state, int kind) {
    size_t i;
    for (i = 0; i < state->itemCount; i++) {
        if (state->items[i].carried && state->items[i].category == 2 && state->items[i].kind == kind) {
            return &state->items[i];
        }
    }
    return NULL;
}

static int runWeaponSmoke(BrogueBridgeState *state, boolean verbose) {
    const BrogueBridgeItemState *dagger = findCarriedWeapon(state, 0);
    const BrogueBridgeItemState *dart = findCarriedWeapon(state, 12);
    BrogueBridgeCommand command;
    BrogueBridgeTurnResult turn;
    BrogueBridgeThrowPreview preview;
    BrogueBridgeResult result;
    int targetY;

    if (dagger == NULL || dart == NULL || state->player.equippedWeaponId != dagger->id) {
        fputs("Weapon smoke requires Brogue's starting dagger and darts.\n", stderr);
        return 1;
    }
    printf("WEAPON phase=initial equipped=%llu kind=%d name=%s dartQuantity=%d\n",
           (unsigned long long) state->player.equippedWeaponId, dagger->kind,
           dagger->displayName, dart->quantity);

    memset(&command, 0, sizeof(command));
    command.apiVersion = BROGUE_BRIDGE_API_VERSION;
    command.type = BROGUE_COMMAND_UNEQUIP_ITEM;
    command.expectedRevision = state->revision;
    command.itemId = dagger->id;
    result = brogue_bridge_perform_command(&command, &turn);
    if (result != BROGUE_BRIDGE_OK || !turn.actionAccepted
        || brogue_bridge_get_state(state) != BROGUE_BRIDGE_OK) return 1;
    printf("WEAPON phase=unequip revision=%llu accepted=%s consumedTurn=%s equipped=%llu\n",
           (unsigned long long) turn.revision, turn.actionAccepted ? "true" : "false",
           turn.consumedTurn ? "true" : "false",
           (unsigned long long) state->player.equippedWeaponId);

    dagger = findCarriedWeapon(state, 0);
    memset(&command, 0, sizeof(command));
    command.apiVersion = BROGUE_BRIDGE_API_VERSION;
    command.type = BROGUE_COMMAND_EQUIP_ITEM;
    command.expectedRevision = state->revision;
    command.itemId = dagger->id;
    result = brogue_bridge_perform_command(&command, &turn);
    if (result != BROGUE_BRIDGE_OK || !turn.actionAccepted
        || brogue_bridge_get_state(state) != BROGUE_BRIDGE_OK) return 1;
    printf("WEAPON phase=equip revision=%llu accepted=%s consumedTurn=%s equipped=%llu\n",
           (unsigned long long) turn.revision, turn.actionAccepted ? "true" : "false",
           turn.consumedTurn ? "true" : "false",
           (unsigned long long) state->player.equippedWeaponId);

    dart = findCarriedWeapon(state, 12);
    targetY = state->player.y >= 3 ? state->player.y - 3 : state->player.y + 3;
    result = brogue_bridge_preview_throw(dart->id, state->player.x, targetY, &preview);
    if (result != BROGUE_BRIDGE_OK || !preview.valid) return 1;
    printf("WEAPON phase=preview item=%llu target=%d,%d range=%d path=%u confirm=%s\n",
           (unsigned long long) dart->id, preview.targetX, preview.targetY,
           preview.maxDistance, preview.pathCount,
           preview.requiresConfirmation ? "true" : "false");

    memset(&command, 0, sizeof(command));
    command.apiVersion = BROGUE_BRIDGE_API_VERSION;
    command.type = BROGUE_COMMAND_THROW_ITEM;
    command.expectedRevision = state->revision;
    command.itemId = dart->id;
    command.targetX = preview.targetX;
    command.targetY = preview.targetY;
    command.confirmed = true;
    result = brogue_bridge_perform_command(&command, &turn);
    if (result != BROGUE_BRIDGE_OK || !turn.actionAccepted
        || brogue_bridge_get_state(state) != BROGUE_BRIDGE_OK) return 1;
    dart = findCarriedWeapon(state, 12);
    printf("WEAPON phase=throw revision=%llu accepted=%s consumedTurn=%s dartQuantity=%d hash=%016llx\n",
           (unsigned long long) turn.revision, turn.actionAccepted ? "true" : "false",
           turn.consumedTurn ? "true" : "false", dart == NULL ? 0 : dart->quantity,
           (unsigned long long) state->stateHash);
    if (verbose) printEvents(&turn);
    return 0;
}

static int runLookSmoke(BrogueBridgeState *state) {
    BrogueBridgeLookResult look;
    BrogueBridgeState after;
    BrogueBridgeResult result;

    result = brogue_bridge_inspect_cell(state->player.x, state->player.y, &look);
    if (result != BROGUE_BRIDGE_OK || look.errorCode != BROGUE_BRIDGE_OK
        || look.kind != BROGUE_LOOK_PLAYER || !look.known) {
        fputs("Look smoke could not inspect the authoritative player cell.\n", stderr);
        return 1;
    }
    if (brogue_bridge_get_state(&after) != BROGUE_BRIDGE_OK
        || after.revision != state->revision
        || after.absoluteTurn != state->absoluteTurn
        || after.stateHash != state->stateHash) {
        fputs("Look smoke mutated authoritative Brogue state.\n", stderr);
        return 1;
    }
    printf("LOOK revision=%llu turn=%llu cell=%d,%d kind=%d known=%s title=%s summary=%s hash=%016llx\n",
           (unsigned long long) after.revision,
           (unsigned long long) after.absoluteTurn,
           look.x, look.y, (int) look.kind, look.known ? "true" : "false",
           look.title, look.summary, (unsigned long long) after.stateHash);
    return 0;
}

static int runConsumableSmoke(BrogueBridgeState *state, boolean verbose) {
    const BrogueBridgeItemState *food = findCarriedCategory(state, FOOD);
    BrogueBridgeCommand command;
    BrogueBridgeTurnResult turn;
    BrogueBridgeState unchanged;
    BrogueBridgeResult result;
    uint64_t initialRevision;
    uint64_t initialHash;
    uint64_t foodId;
    int initialQuantity;
    const BrogueBridgeItemState *remaining;
    item *identifyScroll;
    item *unknownRing;
    const BrogueBridgeItemState *scrollState;
    const BrogueBridgeItemState *ringState;
    uint64_t selectionRevision;
    uint64_t selectionHash;
    uint64_t scrollId;
    uint64_t ringId;

    if (food == NULL || !(food->actionFlags & BROGUE_ITEM_ACTION_APPLY)) {
        fputs("Consumable smoke requires Brogue's starting food ration.\n", stderr);
        return 1;
    }
    initialRevision = state->revision;
    initialHash = state->stateHash;
    foodId = food->id;
    initialQuantity = food->quantity;

    memset(&command, 0, sizeof(command));
    command.apiVersion = BROGUE_BRIDGE_API_VERSION;
    command.type = BROGUE_COMMAND_APPLY_ITEM;
    command.expectedRevision = state->revision;
    command.itemId = foodId;
    result = brogue_bridge_perform_command(&command, &turn);
    if (result != BROGUE_BRIDGE_CONFIRMATION_REQUIRED
        || turn.errorCode != BROGUE_BRIDGE_CONFIRMATION_REQUIRED
        || turn.prompt[0] == '\0'
        || brogue_bridge_get_state(&unchanged) != BROGUE_BRIDGE_OK
        || unchanged.revision != initialRevision
        || unchanged.stateHash != initialHash) {
        fputs("Consumable smoke confirmation preflight failed or mutated state.\n", stderr);
        return 1;
    }
    printf("CONSUMABLE phase=confirm revision=%llu result=%s prompt=%s\n",
           (unsigned long long) unchanged.revision,
           brogue_bridge_result_name(result), turn.prompt);

    command.confirmed = true;
    result = brogue_bridge_perform_command(&command, &turn);
    if (result != BROGUE_BRIDGE_OK || !turn.actionAccepted || !turn.consumedTurn
        || brogue_bridge_get_state(state) != BROGUE_BRIDGE_OK
        || state->revision <= initialRevision) {
        fputs("Consumable smoke could not consume food through Brogue.\n", stderr);
        return 1;
    }
    remaining = findItemId(state, foodId);
    if (remaining != NULL && remaining->quantity >= initialQuantity) {
        fputs("Consumable smoke did not reduce the authoritative food stack.\n", stderr);
        return 1;
    }
    printf("CONSUMABLE phase=apply revision=%llu accepted=true consumedTurn=true quantity=%d hash=%016llx\n",
           (unsigned long long) turn.revision,
           remaining == NULL ? 0 : remaining->quantity,
           (unsigned long long) state->stateHash);
    if (verbose) printEvents(&turn);

    // A deterministic harness-only fixture exercises Brogue's mandatory
    // secondary selection without adding debug behavior to the public API.
    identifyScroll = generateItem(SCROLL, SCROLL_IDENTIFY);
    unknownRing = generateItem(RING, RING_CLAIRVOYANCE);
    if (identifyScroll == NULL || unknownRing == NULL) return 1;
    addItemToPack(identifyScroll);
    addItemToPack(unknownRing);
    if (brogue_bridge_perform_action(BROGUE_ACTION_WAIT, &turn) != BROGUE_BRIDGE_OK
        || brogue_bridge_get_state(state) != BROGUE_BRIDGE_OK) return 1;
    scrollState = findCarriedCategory(state, SCROLL);
    ringState = findCarriedCategory(state, RING);
    if (scrollState == NULL || ringState == NULL) return 1;
    scrollId = scrollState->id;
    ringId = ringState->id;
    selectionRevision = state->revision;
    selectionHash = state->stateHash;

    memset(&command, 0, sizeof(command));
    command.apiVersion = BROGUE_BRIDGE_API_VERSION;
    command.type = BROGUE_COMMAND_APPLY_ITEM;
    command.expectedRevision = selectionRevision;
    command.itemId = scrollId;
    result = brogue_bridge_perform_command(&command, &turn);
    if (result != BROGUE_BRIDGE_SELECTION_REQUIRED
        || turn.selectionType != BROGUE_SELECTION_IDENTIFY_ITEM
        || !choiceContains(&turn, ringId)
        || brogue_bridge_get_state(&unchanged) != BROGUE_BRIDGE_OK
        || unchanged.revision != selectionRevision
        || unchanged.stateHash != selectionHash) {
        fputs("Consumable smoke identify selection preflight failed or mutated state.\n", stderr);
        return 1;
    }
    printf("CONSUMABLE phase=selection revision=%llu result=%s type=%d choices=%u prompt=%s\n",
           (unsigned long long) unchanged.revision,
           brogue_bridge_result_name(result), (int) turn.selectionType,
           turn.choiceCount, turn.prompt);

    command.secondaryItemId = ringId;
    result = brogue_bridge_perform_command(&command, &turn);
    if (result != BROGUE_BRIDGE_OK || !turn.actionAccepted || !turn.consumedTurn
        || brogue_bridge_get_state(state) != BROGUE_BRIDGE_OK
        || findItemId(state, scrollId) != NULL) {
        fputs("Consumable smoke could not apply identify through Brogue.\n", stderr);
        return 1;
    }
    ringState = findItemId(state, ringId);
    if (ringState == NULL || (ringState->flags & ITEM_CAN_BE_IDENTIFIED)) {
        fputs("Consumable smoke did not identify the selected item.\n", stderr);
        return 1;
    }
    printf("CONSUMABLE phase=identify revision=%llu accepted=true consumedTurn=true target=%llu identifiable=false hash=%016llx\n",
           (unsigned long long) turn.revision, (unsigned long long) ringId,
           (unsigned long long) state->stateHash);
    return 0;
}

static int runWarningSmoke(BrogueBridgeState *state) {
    BrogueBridgeCommand command;
    BrogueBridgeTurnResult turn;
    BrogueBridgeState unchanged;
    BrogueBridgeResult result;
    const BrogueBridgeEvent *levelEvent = NULL;
    size_t eventIndex;
    pos destination = { (short) state->player.x, (short) (state->player.y - 1) };
    uint64_t initialRevision = state->revision;
    uint64_t initialHash = state->stateHash;

    if (!isPosInMap(destination)) return 1;
    /* Harness-only terrain fixture. The action still enters Brogue through
     * playerMoves(), which owns the warning and the resulting fall. */
    pmap[destination.x][destination.y].layers[LIQUID] = CHASM;
    pmap[destination.x][destination.y].flags |= DISCOVERED;

    memset(&command, 0, sizeof(command));
    command.apiVersion = BROGUE_BRIDGE_API_VERSION;
    command.type = BROGUE_COMMAND_ACTION;
    command.action = BROGUE_ACTION_MOVE_N;
    command.expectedRevision = initialRevision;
    result = brogue_bridge_perform_command(&command, &turn);
    if (result != BROGUE_BRIDGE_CONFIRMATION_REQUIRED
        || strcmp(turn.prompt, "Dive into the depths?") != 0
        || brogue_bridge_get_state(&unchanged) != BROGUE_BRIDGE_OK
        || unchanged.revision != initialRevision
        || unchanged.stateHash != initialHash
        || unchanged.player.x != state->player.x
        || unchanged.player.y != state->player.y) {
        fputs("Warning smoke did not pause safely at Brogue's chasm confirmation.\n", stderr);
        return 1;
    }
    printf("WARNING phase=prompt revision=%llu result=%s prompt=%s player=%d,%d hash=%016llx\n",
           (unsigned long long) unchanged.revision, brogue_bridge_result_name(result),
           turn.prompt, unchanged.player.x, unchanged.player.y,
           (unsigned long long) unchanged.stateHash);

    command.confirmed = 1;
    result = brogue_bridge_perform_command(&command, &turn);
    if (result != BROGUE_BRIDGE_OK || !turn.actionAccepted
        || brogue_bridge_get_state(state) != BROGUE_BRIDGE_OK
        || state->revision <= initialRevision) {
        fputs("Warning smoke could not resume the confirmed Brogue movement.\n", stderr);
        return 1;
    }
    for (eventIndex = 0; eventIndex < turn.eventCount; eventIndex++) {
        if (turn.events[eventIndex].type == BROGUE_EVENT_LEVEL_CHANGE_REQUESTED) {
            levelEvent = &turn.events[eventIndex];
            break;
        }
    }
    if (levelEvent == NULL
        || !(levelEvent->eventFlags & BROGUE_EVENT_FLAG_LEVEL_FALL)
        || levelEvent->fromX != destination.x
        || levelEvent->fromY != destination.y
        || levelEvent->toX != state->player.x
        || levelEvent->toY != state->player.y) {
        fputs("Warning smoke did not preserve fall source and landing coordinates.\n", stderr);
        return 1;
    }
    printf("WARNING phase=confirmed revision=%llu accepted=true consumedTurn=%s depth=%d player=%d,%d hash=%016llx transition=fall source=%d,%d landing=%d,%d\n",
           (unsigned long long) turn.revision,
           turn.consumedTurn ? "true" : "false", state->depth,
           state->player.x, state->player.y, (unsigned long long) state->stateHash,
           levelEvent->fromX, levelEvent->fromY, levelEvent->toX, levelEvent->toY);
    return 0;
}

static void printStateLine(const char *prefix, const BrogueBridgeState *state) {
    printf("%s revision=%llu turn=%llu depth=%d player=%d,%d hp=%d/%d "
           "creatures=%llu items=%llu hash=%016llx presentation=%016llx\n",
           prefix,
           (unsigned long long) state->revision,
           (unsigned long long) state->absoluteTurn,
           state->depth,
           state->player.x,
           state->player.y,
           state->player.hp,
           state->player.maxHp,
           (unsigned long long) state->creatureCount,
           (unsigned long long) state->itemCount,
           (unsigned long long) state->stateHash,
           (unsigned long long) state->presentationHash);
    if (state->gameResult.outcome != BROGUE_GAME_OUTCOME_NONE) {
        printf("RESULT outcome=%d score=%lld depth=%d deepest=%d turn=%llu cause=\"%s\" summary=\"%s\"\n",
               (int) state->gameResult.outcome,
               (long long) state->gameResult.score,
               state->gameResult.depth,
               state->gameResult.deepestDepth,
               (unsigned long long) state->gameResult.turn,
               state->gameResult.cause,
               state->gameResult.summary);
    }
}

static void writeJsonString(FILE *file, const char *text) {
    const unsigned char *cursor = (const unsigned char *) text;
    fputc('"', file);
    while (*cursor != '\0') {
        if (*cursor == '"' || *cursor == '\\') {
            fputc('\\', file);
            fputc(*cursor, file);
        } else if (*cursor < 32) {
            fprintf(file, "\\u%04x", *cursor);
        } else {
            fputc(*cursor, file);
        }
        cursor++;
    }
    fputc('"', file);
}

static int dumpMonsterCatalog(const char *path) {
    BrogueBridgeMonsterCatalog catalog;
    BrogueBridgeResult result;
    FILE *file;
    size_t i;

    result = brogue_bridge_initialize();
    if (result != BROGUE_BRIDGE_OK) {
        fprintf(stderr, "Bridge initialize failed: %s\n", brogue_bridge_result_name(result));
        return 1;
    }
    result = brogue_bridge_get_monster_catalog(&catalog);
    if (result != BROGUE_BRIDGE_OK) {
        fprintf(stderr, "Catalog query failed: %s\n", brogue_bridge_result_name(result));
        return 1;
    }
    file = fopen(path, "wb");
    if (file == NULL) {
        fprintf(stderr, "Could not open catalog output: %s\n", path);
        return 1;
    }
    fprintf(file, "{\n  \"schemaVersion\": 1,\n  \"bridgeApiVersion\": %u,\n  \"count\": %u,\n  \"kinds\": [\n",
            catalog.apiVersion, catalog.count);
    for (i = 0; i < catalog.count; i++) {
        const BrogueBridgeMonsterKindInfo *kind = &catalog.kinds[i];
        fprintf(file, "    {\"kind\": %d, \"symbol\": ", kind->kind);
        writeJsonString(file, kind->symbol);
        fputs(", \"name\": ", file);
        writeJsonString(file, kind->name);
        fprintf(file, ", \"displayGlyph\": %d, \"color\": {\"red\": %d, \"green\": %d, \"blue\": %d, \"redRand\": %d, \"greenRand\": %d, \"blueRand\": %d, \"rand\": %d, \"dances\": %s}, \"maxHp\": %d, \"intrinsicLightType\": %d, \"isLarge\": %s, \"behaviorFlags\": \"%llu\", \"abilityFlags\": \"%llu\"}%s\n",
                kind->displayGlyph, kind->colorRed, kind->colorGreen, kind->colorBlue,
                kind->colorRedRand, kind->colorGreenRand, kind->colorBlueRand,
                kind->colorRand, kind->colorDances ? "true" : "false", kind->maxHp,
                kind->intrinsicLightType, kind->isLarge ? "true" : "false",
                (unsigned long long) kind->behaviorFlags,
                (unsigned long long) kind->abilityFlags,
                i + 1 == catalog.count ? "" : ",");
    }
    fputs("  ]\n}\n", file);
    if (fclose(file) != 0) {
        fprintf(stderr, "Could not finish catalog output: %s\n", path);
        return 1;
    }
    return 0;
}

static int equalsIgnoreCase(const char *first, const char *second) {
    while (*first != '\0' && *second != '\0') {
        if (toupper((unsigned char) *first) != toupper((unsigned char) *second)) {
            return 0;
        }
        first++;
        second++;
    }
    return *first == '\0' && *second == '\0';
}

static int parseAction(const char *token, BrogueBridgeAction *outAction) {
    static const char *names[BROGUE_ACTION_COUNT] = {
        "N", "NE", "E", "SE", "S", "SW", "W", "NW", "WAIT"
    };
    static const char *numpad[BROGUE_ACTION_COUNT] = {
        "8", "9", "6", "3", "2", "1", "4", "7", "5"
    };
    int i;

    for (i = 0; i < BROGUE_ACTION_COUNT; i++) {
        if (equalsIgnoreCase(token, names[i]) || strcmp(token, numpad[i]) == 0) {
            *outAction = (BrogueBridgeAction) i;
            return 1;
        }
    }
    return 0;
}

static int parseUnsigned64(const char *text, uint64_t *outValue) {
    char *end;
    unsigned long long value;

    errno = 0;
    end = NULL;
    value = strtoull(text, &end, 10);
    if (errno != 0 || end == text || *end != '\0') {
        return 0;
    }
    *outValue = (uint64_t) value;
    return 1;
}

static void printEvents(const BrogueBridgeTurnResult *result) {
    size_t i;
    for (i = 0; i < result->eventCount; i++) {
        const BrogueBridgeEvent *event = &result->events[i];
        printf("EVENT sequence=%llu type=%s x=%d y=%d entity=%llu source=%llu target=%llu amount=%d flags=%u beforeDungeon=%d afterDungeon=%d text=%s\n",
               (unsigned long long) event->sequence,
               brogue_bridge_event_name(event->type),
               event->x,
               event->y,
               (unsigned long long) event->entityId,
               (unsigned long long) event->sourceEntityId,
               (unsigned long long) event->targetEntityId,
               event->amount,
               event->eventFlags,
               event->beforeDungeon,
               event->afterDungeon,
               event->text);
    }
}

#ifndef BROGUE_BRIDGE_DLL
int main(int argc, char **argv) {
    uint64_t seed = 0;
    uint64_t longRun = 0;
    const char *actionsText = NULL;
    boolean haveSeed = false;
    boolean verbose = false;
    boolean weaponSmoke = false;
    boolean consumableSmoke = false;
    boolean staffSmoke = false;
    boolean wandSmoke = false;
    boolean targetSmoke = false;
    boolean warningSmoke = false;
    boolean lookSmoke = false;
    const char *catalogOutput = NULL;
    int i;
    int exitCode = 0;
    BrogueBridgeResult bridgeResult;
    BrogueBridgeState state;
    char *actionBuffer = NULL;
    char *token;
    BrogueBridgeAction action;
    static const BrogueBridgeAction longRunPattern[] = {
        BROGUE_ACTION_MOVE_N,
        BROGUE_ACTION_MOVE_NE,
        BROGUE_ACTION_MOVE_E,
        BROGUE_ACTION_MOVE_SE,
        BROGUE_ACTION_MOVE_S,
        BROGUE_ACTION_MOVE_SW,
        BROGUE_ACTION_MOVE_W,
        BROGUE_ACTION_MOVE_NW,
        BROGUE_ACTION_WAIT
    };

    for (i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--help") == 0 || strcmp(argv[i], "-h") == 0) {
            printUsage();
            return 0;
        } else if (strcmp(argv[i], "--seed") == 0 && i + 1 < argc) {
            if (!parseUnsigned64(argv[++i], &seed)) {
                fprintf(stderr, "Invalid --seed value.\n");
                return 2;
            }
            haveSeed = true;
        } else if (strcmp(argv[i], "--actions") == 0 && i + 1 < argc) {
            actionsText = argv[++i];
        } else if (strcmp(argv[i], "--long-run") == 0 && i + 1 < argc) {
            if (!parseUnsigned64(argv[++i], &longRun)) {
                fprintf(stderr, "Invalid --long-run value.\n");
                return 2;
            }
        } else if (strcmp(argv[i], "--verbose") == 0) {
            verbose = true;
        } else if (strcmp(argv[i], "--weapon-smoke") == 0) {
            weaponSmoke = true;
        } else if (strcmp(argv[i], "--consumable-smoke") == 0) {
            consumableSmoke = true;
        } else if (strcmp(argv[i], "--staff-smoke") == 0) {
            staffSmoke = true;
        } else if (strcmp(argv[i], "--target-smoke") == 0) {
            targetSmoke = true;
        } else if (strcmp(argv[i], "--wand-smoke") == 0) {
            wandSmoke = true;
        } else if (strcmp(argv[i], "--warning-smoke") == 0) {
            warningSmoke = true;
        } else if (strcmp(argv[i], "--look-smoke") == 0) {
            lookSmoke = true;
        } else if (strcmp(argv[i], "--dump-monster-catalog") == 0 && i + 1 < argc) {
            catalogOutput = argv[++i];
        } else {
            fprintf(stderr, "Unknown or incomplete argument: %s\n", argv[i]);
            printUsage();
            return 2;
        }
    }
    if (catalogOutput != NULL) {
        if (haveSeed || actionsText != NULL || longRun != 0) {
            fprintf(stderr, "--dump-monster-catalog must be used alone.\n");
            return 2;
        }
        currentConsole = nullConsole;
        exitCode = dumpMonsterCatalog(catalogOutput);
        brogue_bridge_shutdown();
        return exitCode;
    }
    if (!haveSeed || (actionsText != NULL && longRun != 0)) {
        if (!haveSeed) {
            fprintf(stderr, "--seed is required.\n");
        } else {
            fprintf(stderr, "Choose either --actions or --long-run.\n");
        }
        return 2;
    }

    currentConsole = nullConsole;
    bridgeResult = brogue_bridge_initialize();
    if (bridgeResult != BROGUE_BRIDGE_OK) {
        fprintf(stderr, "Bridge initialize failed: %s\n", brogue_bridge_result_name(bridgeResult));
        return 1;
    }
    bridgeResult = brogue_bridge_start_game(seed);
    if (bridgeResult != BROGUE_BRIDGE_OK) {
        fprintf(stderr, "Bridge start failed: %s\n", brogue_bridge_result_name(bridgeResult));
        brogue_bridge_shutdown();
        return 1;
    }
    bridgeResult = brogue_bridge_get_state(&state);
    if (bridgeResult != BROGUE_BRIDGE_OK) {
        fprintf(stderr, "Initial state failed: %s\n", brogue_bridge_result_name(bridgeResult));
        brogue_bridge_shutdown();
        return 1;
    }
    printStateLine("INITIAL", &state);

    if (weaponSmoke) {
        exitCode = runWeaponSmoke(&state, verbose);
        brogue_bridge_shutdown();
        return exitCode;
    }
    if (consumableSmoke) {
        exitCode = runConsumableSmoke(&state, verbose);
        brogue_bridge_shutdown();
        return exitCode;
    }
    if (staffSmoke) {
        exitCode = runStaffSmoke(&state);
        brogue_bridge_shutdown();
        return exitCode;
    }
    if (targetSmoke) {
        exitCode = runTargetSmoke(&state);
        if (!exitCode) exitCode = runTargetActionSmoke(&state);
        brogue_bridge_shutdown();
        return exitCode;
    }
    if (wandSmoke) {
        exitCode = runWandSmoke(&state);
        brogue_bridge_shutdown();
        return exitCode;
    }
    if (warningSmoke) {
        exitCode = runWarningSmoke(&state);
        brogue_bridge_shutdown();
        return exitCode;
    }
    if (lookSmoke) {
        exitCode = runLookSmoke(&state);
        brogue_bridge_shutdown();
        return exitCode;
    }

    if (actionsText != NULL) {
        actionBuffer = malloc(strlen(actionsText) + 1);
        if (actionBuffer == NULL) {
            fprintf(stderr, "Could not allocate action buffer.\n");
            brogue_bridge_shutdown();
            return 1;
        }
        strcpy(actionBuffer, actionsText);
        token = strtok(actionBuffer, ",; \t\r\n");
        i = 0;
        while (token != NULL) {
            BrogueBridgeTurnResult turnResult;
            if (!parseAction(token, &action)) {
                fprintf(stderr, "Invalid action token: %s\n", token);
                exitCode = 2;
                break;
            }
            bridgeResult = brogue_bridge_perform_action(action, &turnResult);
            if (bridgeResult != BROGUE_BRIDGE_OK) {
                fprintf(stderr, "Action %d failed: %s\n", i, brogue_bridge_result_name(bridgeResult));
                exitCode = 1;
                break;
            }
            if (brogue_bridge_get_state(&state) != BROGUE_BRIDGE_OK) {
                fprintf(stderr, "State after action %d could not be read.\n", i);
                exitCode = 1;
                break;
            }
            printf("ACTION index=%d revision=%llu type=%s accepted=%s consumedTurn=%s "
                   "turn=%llu player=%d,%d hash=%016llx\n",
                   i,
                   (unsigned long long) turnResult.revision,
                   brogue_bridge_action_name(action),
                   turnResult.actionAccepted ? "true" : "false",
                   turnResult.consumedTurn ? "true" : "false",
                   (unsigned long long) turnResult.currentTurn,
                   turnResult.playerAfter.x,
                   turnResult.playerAfter.y,
                   (unsigned long long) state.stateHash);
            printf("STATE revision=%llu turn=%llu player=%d,%d hp=%d/%d creatures=%llu hash=%016llx\n",
                   (unsigned long long) state.revision,
                   (unsigned long long) state.absoluteTurn,
                   state.player.x,
                   state.player.y,
                   state.player.hp,
                   state.player.maxHp,
                   (unsigned long long) state.creatureCount,
                   (unsigned long long) state.stateHash);
            if (verbose) {
                printEvents(&turnResult);
            }
            i++;
            token = strtok(NULL, ",; \t\r\n");
        }
    } else {
        uint64_t actionIndex;
        for (actionIndex = 0; actionIndex < longRun; actionIndex++) {
            BrogueBridgeTurnResult turnResult;
            action = longRunPattern[actionIndex % (sizeof(longRunPattern) / sizeof(longRunPattern[0]))];
            if (verbose) {
                fprintf(stderr, "BEGIN action=%llu type=%s\n",
                        (unsigned long long) actionIndex,
                        brogue_bridge_action_name(action));
                fflush(stderr);
            }
            bridgeResult = brogue_bridge_perform_action(action, &turnResult);
            if (bridgeResult != BROGUE_BRIDGE_OK) {
                if (bridgeResult == BROGUE_BRIDGE_GAME_ENDED) {
                    break;
                }
                fprintf(stderr, "Long-run action %llu failed: %s\n",
                        (unsigned long long) actionIndex,
                        brogue_bridge_result_name(bridgeResult));
                exitCode = 1;
                break;
            }
            if (verbose) {
                fprintf(stderr, "END action=%llu\n", (unsigned long long) actionIndex);
                printf("ACTION index=%llu revision=%llu type=%s accepted=%s consumedTurn=%s turn=%llu player=%d,%d\n",
                       (unsigned long long) actionIndex,
                       (unsigned long long) turnResult.revision,
                       brogue_bridge_action_name(action),
                       turnResult.actionAccepted ? "true" : "false",
                       turnResult.consumedTurn ? "true" : "false",
                       (unsigned long long) turnResult.currentTurn,
                       turnResult.playerAfter.x,
                       turnResult.playerAfter.y);
                fflush(stdout);
            }
        }
        if (brogue_bridge_get_state(&state) == BROGUE_BRIDGE_OK) {
            printStateLine("FINAL", &state);
        }
    }

    free(actionBuffer);
    brogue_bridge_shutdown();
    return exitCode;
}
#endif
