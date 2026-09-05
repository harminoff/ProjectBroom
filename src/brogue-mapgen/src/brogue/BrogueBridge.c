/*
 * Brogue CE -> frontend runtime adapter.
 *
 * The adapter is intentionally the only file that knows Brogue's internal
 * pcell/creature layout.  Every public result is a copied value object from
 * BrogueBridge.h.  Movement and turn processing call Brogue's existing
 * playerMoves() and playerTurnEnded() paths; there is no second rules engine
 * here.
 */
#include "Rogue.h"
#include "GlobalsBase.h"
#include "Globals.h"
#include "BrogueBridge.h"
#include "BrogueBridgeInternal.h"
#include "platform.h"

#include <stdio.h>
#include <string.h>

typedef struct bridgeCreatureIdentity {
    creature *pointer;
    uint64_t id;
    boolean seen;
} bridgeCreatureIdentity;

typedef struct bridgeItemIdentity {
    item *pointer;
    uint64_t id;
    boolean seen;
} bridgeItemIdentity;

static boolean bridgeInitialized = false;
static boolean bridgeGameStarted = false;
static uint64_t bridgeRevision = 0;
static uint64_t bridgeNextEntityId = 2;
static BrogueBridgeState bridgeState;
static BrogueBridgeState bridgePreviousState;
static bridgeCreatureIdentity creatureIdentities[BROGUE_BRIDGE_MAX_CREATURES];
static size_t creatureIdentityCount = 0;
static bridgeItemIdentity itemIdentities[BROGUE_BRIDGE_MAX_ITEMS];
static size_t itemIdentityCount = 0;
static uint64_t eventSequence = 0;
static boolean recordingActionEvents = false;
static boolean recordedEventsTruncated = false;
static BrogueBridgeEvent recordedEvents[BROGUE_BRIDGE_MAX_EVENTS];
static size_t recordedEventCount = 0;
static boolean recordedPlayerFall = false;
static pos recordedPlayerFallSource = INVALID_POS;
static boolean confirmationBrokerActive = false;
static uint8_t confirmationApprovalsRemaining = 0;
static boolean confirmationWasRequested = false;
static char confirmationPrompt[BROGUE_BRIDGE_MESSAGE_LENGTH];
static BrogueBridgeGameResult bridgeGameResult;

static uint64_t stateHash(const BrogueBridgeState *state);
static uint64_t presentationHash(const BrogueBridgeState *state);
static uint64_t identityForItem(item *pointer);
static void copyText(char *destination, size_t destinationSize, const char *source);

boolean brogue_bridge_intercept_confirmation(const char *prompt, boolean *answer) {
    if (!confirmationBrokerActive || answer == NULL) return false;
    if (confirmationApprovalsRemaining > 0) {
        confirmationApprovalsRemaining--;
        *answer = true;
        return true;
    }
    confirmationWasRequested = true;
    copyText(confirmationPrompt, sizeof(confirmationPrompt), prompt);
    *answer = false;
    return true;
}

void brogue_bridge_note_game_over(const char *cause,
                                  const char *summary,
                                  signed long score,
                                  boolean playerQuit) {
    if (!bridgeGameStarted) return;
    memset(&bridgeGameResult, 0, sizeof(bridgeGameResult));
    bridgeGameResult.outcome = playerQuit ? BROGUE_GAME_OUTCOME_QUIT : BROGUE_GAME_OUTCOME_DEATH;
    bridgeGameResult.score = score;
    bridgeGameResult.depth = rogue.depthLevel;
    bridgeGameResult.deepestDepth = rogue.deepestLevel;
    bridgeGameResult.turn = rogue.absoluteTurnNumber;
    copyText(bridgeGameResult.cause, sizeof(bridgeGameResult.cause), cause);
    copyText(bridgeGameResult.summary, sizeof(bridgeGameResult.summary), summary);
}

static void beginConfirmationBroker(uint8_t approvedPromptCount) {
    confirmationBrokerActive = true;
    confirmationApprovalsRemaining = approvedPromptCount;
    confirmationWasRequested = false;
    confirmationPrompt[0] = '\0';
}

static void endConfirmationBroker(void) {
    confirmationBrokerActive = false;
    confirmationApprovalsRemaining = 0;
}

static const char *monsterSymbols[NUMBER_MONSTER_KINDS] = {
    "MK_YOU", "MK_RAT", "MK_KOBOLD", "MK_JACKAL", "MK_EEL", "MK_MONKEY",
    "MK_BLOAT", "MK_PIT_BLOAT", "MK_GOBLIN", "MK_GOBLIN_CONJURER",
    "MK_GOBLIN_MYSTIC", "MK_GOBLIN_TOTEM", "MK_PINK_JELLY", "MK_TOAD",
    "MK_VAMPIRE_BAT", "MK_ARROW_TURRET", "MK_ACID_MOUND", "MK_CENTIPEDE",
    "MK_OGRE", "MK_BOG_MONSTER", "MK_OGRE_TOTEM", "MK_SPIDER",
    "MK_SPARK_TURRET", "MK_WILL_O_THE_WISP", "MK_WRAITH", "MK_ZOMBIE",
    "MK_TROLL", "MK_OGRE_SHAMAN", "MK_NAGA", "MK_SALAMANDER",
    "MK_EXPLOSIVE_BLOAT", "MK_DAR_BLADEMASTER", "MK_DAR_PRIESTESS",
    "MK_DAR_BATTLEMAGE", "MK_ACID_JELLY", "MK_CENTAUR", "MK_UNDERWORM",
    "MK_SENTINEL", "MK_DART_TURRET", "MK_KRAKEN", "MK_LICH",
    "MK_PHYLACTERY", "MK_PIXIE", "MK_PHANTOM", "MK_FLAME_TURRET", "MK_IMP",
    "MK_FURY", "MK_REVENANT", "MK_TENTACLE_HORROR", "MK_GOLEM", "MK_DRAGON",
    "MK_GOBLIN_CHIEFTAN", "MK_BLACK_JELLY", "MK_VAMPIRE", "MK_FLAMEDANCER",
    "MK_SPECTRAL_BLADE", "MK_SPECTRAL_IMAGE", "MK_GUARDIAN",
    "MK_WINGED_GUARDIAN", "MK_CHARM_GUARDIAN", "MK_WARDEN_OF_YENDOR",
    "MK_ELDRITCH_TOTEM", "MK_MIRRORED_TOTEM", "MK_UNICORN", "MK_IFRIT",
    "MK_PHOENIX", "MK_PHOENIX_EGG", "MK_ANCIENT_SPIRIT"
};

static void copyText(char *destination, size_t destinationSize, const char *source) {
    if (destinationSize == 0) {
        return;
    }
    if (source == NULL) {
        destination[0] = '\0';
        return;
    }
    strncpy(destination, source, destinationSize - 1);
    destination[destinationSize - 1] = '\0';
}

static void copyPlainText(char *destination, size_t destinationSize, const char *source) {
    size_t written = 0;
    if (destinationSize == 0) return;
    while (source != NULL && *source != '\0' && written + 1 < destinationSize) {
        if ((unsigned char) *source == COLOR_ESCAPE) {
            source += source[1] != '\0' && source[2] != '\0' && source[3] != '\0' ? 4 : 1;
            continue;
        }
        destination[written++] = *source++;
    }
    destination[written] = '\0';
}

static void copyStyledLookText(BrogueBridgeLookResult *result, const char *source) {
    size_t written = 0;
    uint8_t red = 100, green = 100, blue = 100;
    uint32_t spanStart = 0;

    while (source != NULL && *source != '\0'
           && written + 1 < sizeof(result->detail)) {
        if ((unsigned char) *source == COLOR_ESCAPE
            && source[1] != '\0' && source[2] != '\0' && source[3] != '\0') {
            if (written > spanStart
                && result->detailColorSpanCount < BROGUE_BRIDGE_MAX_LOOK_COLOR_SPANS) {
                BrogueBridgeTextColorSpan *span =
                    &result->detailColorSpans[result->detailColorSpanCount++];
                span->offset = spanStart;
                span->length = (uint32_t) written - spanStart;
                span->red = red;
                span->green = green;
                span->blue = blue;
            }
            red = (uint8_t) clamp((int) ((unsigned char) source[1]) - COLOR_VALUE_INTERCEPT, 0, 100);
            green = (uint8_t) clamp((int) ((unsigned char) source[2]) - COLOR_VALUE_INTERCEPT, 0, 100);
            blue = (uint8_t) clamp((int) ((unsigned char) source[3]) - COLOR_VALUE_INTERCEPT, 0, 100);
            source += 4;
            spanStart = (uint32_t) written;
            continue;
        }
        result->detail[written++] = *source++;
    }
    result->detail[written] = '\0';
    if (written > spanStart
        && result->detailColorSpanCount < BROGUE_BRIDGE_MAX_LOOK_COLOR_SPANS) {
        BrogueBridgeTextColorSpan *span =
            &result->detailColorSpans[result->detailColorSpanCount++];
        span->offset = spanStart;
        span->length = (uint32_t) written - spanStart;
        span->red = red;
        span->green = green;
        span->blue = blue;
    }
}

static uint64_t statusFlagsFor(const creature *monst) {
    uint64_t flags = 0;
    int i;

    for (i = 0; i < NUMBER_OF_STATUS_EFFECTS && i < 64; i++) {
        if (monst->status[i] != 0) {
            flags |= ((uint64_t) 1 << i);
        }
    }
    return flags;
}

static uint64_t hashBytes(uint64_t hash, const void *data, size_t length) {
    const unsigned char *bytes = (const unsigned char *) data;
    size_t i;

    for (i = 0; i < length; i++) {
        hash ^= bytes[i];
        hash *= UINT64_C(1099511628211);
    }
    return hash;
}

static uint64_t hashU64(uint64_t hash, uint64_t value) {
    unsigned char bytes[8];
    int i;

    for (i = 0; i < 8; i++) {
        bytes[i] = (unsigned char) (value >> (i * 8));
    }
    return hashBytes(hash, bytes, sizeof(bytes));
}

static uint64_t hashU32(uint64_t hash, uint32_t value) {
    unsigned char bytes[4];
    int i;

    for (i = 0; i < 4; i++) {
        bytes[i] = (unsigned char) (value >> (i * 8));
    }
    return hashBytes(hash, bytes, sizeof(bytes));
}

static uint64_t hashSigned(uint64_t hash, int64_t value) {
    return hashU64(hash, (uint64_t) value);
}

static boolean validTile(enum tileType tile) {
    return tile >= 0 && tile < NUMBER_TILETYPES;
}

static boolean tileIsDoor(enum tileType tile) {
    switch (tile) {
        case DOOR:
        case OPEN_DOOR:
        case SECRET_DOOR:
        case LOCKED_DOOR:
        case OPEN_IRON_DOOR_INERT:
        case PORTCULLIS_CLOSED:
        case PORTCULLIS_DORMANT:
        case WOODEN_BARRICADE:
        case MUD_DOORWAY:
        case STATUE_INERT_DOORWAY:
        case STATUE_DORMANT_DOORWAY:
            return true;
        default:
            return false;
    }
}

static boolean tileIsLiquid(enum tileType tile) {
    switch (tile) {
        case DEEP_WATER:
        case SHALLOW_WATER:
        case MUD:
        case LAVA:
        case LAVA_RETRACTABLE:
        case LAVA_RETRACTING:
        case FLOOD_WATER_DEEP:
        case FLOOD_WATER_SHALLOW:
        case MACHINE_FLOOD_WATER_DORMANT:
        case MACHINE_FLOOD_WATER_SPREADING:
        case MACHINE_MUD_DORMANT:
        case ICE_DEEP:
        case ICE_DEEP_MELT:
        case ICE_SHALLOW:
        case ICE_SHALLOW_MELT:
            return true;
        default:
            return false;
    }
}

static boolean tileIsChasm(enum tileType tile) {
    switch (tile) {
        case CHASM:
        case CHASM_EDGE:
        case MACHINE_COLLAPSE_EDGE_DORMANT:
        case MACHINE_COLLAPSE_EDGE_SPREADING:
        case CHASM_WITH_HIDDEN_BRIDGE:
        case CHASM_WITH_HIDDEN_BRIDGE_ACTIVE:
        case MACHINE_CHASM_EDGE:
        case HOLE:
        case HOLE_GLOW:
        case HOLE_EDGE:
            return true;
        default:
            return false;
    }
}

static boolean tileIsLava(enum tileType tile) {
    return tile == LAVA || tile == LAVA_RETRACTABLE || tile == LAVA_RETRACTING
        || tile == SACRIFICE_LAVA;
}

static boolean tileIsBridge(enum tileType tile) {
    return tile == BRIDGE || tile == BRIDGE_FALLING || tile == BRIDGE_EDGE
        || tile == STONE_BRIDGE;
}

static BrogueBridgePlayerState playerState(void) {
    BrogueBridgePlayerState state;

    memset(&state, 0, sizeof(state));
    state.x = player.loc.x;
    state.y = player.loc.y;
    state.hp = player.currentHP;
    state.maxHp = player.info.maxHP;
    state.depth = rogue.depthLevel;
    state.turn = rogue.playerTurnNumber;
    state.absoluteTurn = rogue.absoluteTurnNumber;
    state.statusFlags = statusFlagsFor(&player);
    state.equippedWeaponId = rogue.weapon != NULL ? identityForItem(rogue.weapon) : 0;
    state.equippedArmorId = rogue.armor != NULL ? identityForItem(rogue.armor) : 0;
    state.equippedLeftRingId = rogue.ringLeft != NULL ? identityForItem(rogue.ringLeft) : 0;
    state.equippedRightRingId = rogue.ringRight != NULL ? identityForItem(rogue.ringRight) : 0;
    state.armor = displayedArmorValue();
    state.strength = rogue.strength;
    state.nutrition = player.status[STATUS_NUTRITION];
    state.maxNutrition = STOMACH_SIZE;
    state.stealthRange = currentStealthRange();
    state.gold = rogue.gold;
    state.alive = (player.bookkeepingFlags & MB_IS_DYING) == 0 && player.currentHP > 0;
    state.gameInProgress = rogue.gameInProgress;
    state.gameHasEnded = rogue.gameHasEnded;
    return state;
}

static uint64_t identityForCreature(creature *pointer) {
    size_t i;

    for (i = 0; i < creatureIdentityCount; i++) {
        if (creatureIdentities[i].pointer == pointer) {
            creatureIdentities[i].seen = true;
            return creatureIdentities[i].id;
        }
    }
    for (i = 0; i < creatureIdentityCount; i++) {
        if (creatureIdentities[i].pointer == NULL) {
            creatureIdentities[i].pointer = pointer;
            creatureIdentities[i].id = bridgeNextEntityId++;
            creatureIdentities[i].seen = true;
            return creatureIdentities[i].id;
        }
    }
    if (creatureIdentityCount >= BROGUE_BRIDGE_MAX_CREATURES) {
        return 0;
    }
    creatureIdentities[creatureIdentityCount].pointer = pointer;
    creatureIdentities[creatureIdentityCount].id = bridgeNextEntityId++;
    creatureIdentities[creatureIdentityCount].seen = true;
    creatureIdentityCount++;
    return creatureIdentities[creatureIdentityCount - 1].id;
}

static uint64_t entityIdForCreature(creature *pointer) {
    if (pointer == NULL) {
        return 0;
    }
    if (pointer == &player) {
        return BROGUE_BRIDGE_PLAYER_ENTITY_ID;
    }
    return identityForCreature(pointer);
}

static BrogueBridgeEvent *recordActionEvent(BrogueBridgeEventType type,
                                             creature *source,
                                             creature *target) {
    BrogueBridgeEvent *event;
    if (!recordingActionEvents) {
        return NULL;
    }
    if (recordedEventCount >= BROGUE_BRIDGE_MAX_EVENTS) {
        recordedEventsTruncated = true;
        return NULL;
    }
    event = &recordedEvents[recordedEventCount++];
    memset(event, 0, sizeof(*event));
    event->sequence = ++eventSequence;
    event->type = type;
    event->sourceEntityId = entityIdForCreature(source);
    event->targetEntityId = entityIdForCreature(target);
    event->entityId = event->targetEntityId != 0
        ? event->targetEntityId : event->sourceEntityId;
    return event;
}

void brogue_bridge_note_movement(creature *mover, pos from, pos to) {
    BrogueBridgeEvent *event;
    if (from.x == to.x && from.y == to.y) {
        return;
    }
    event = recordActionEvent(mover == &player
                                  ? BROGUE_EVENT_PLAYER_MOVED
                                  : BROGUE_EVENT_CREATURE_MOVED,
                              mover, NULL);
    if (event == NULL) {
        return;
    }
    event->entityId = entityIdForCreature(mover);
    event->fromX = from.x;
    event->fromY = from.y;
    event->toX = to.x;
    event->toY = to.y;
    event->x = to.x;
    event->y = to.y;
    copyText(event->text, sizeof(event->text),
             mover == &player ? "player moved" : "creature moved");
}

void brogue_bridge_note_player_fall(pos source) {
    if (!recordingActionEvents) return;
    recordedPlayerFall = true;
    recordedPlayerFallSource = source;
}

void brogue_bridge_note_attack(creature *attacker, creature *defender,
                               boolean lungeAttack) {
    BrogueBridgeEvent *event = recordActionEvent(BROGUE_EVENT_ATTACK_ATTEMPTED,
                                                  attacker, defender);
    if (event == NULL) {
        return;
    }
    if (attacker != NULL) {
        event->fromX = attacker->loc.x;
        event->fromY = attacker->loc.y;
    }
    if (defender != NULL) {
        event->toX = event->x = defender->loc.x;
        event->toY = event->y = defender->loc.y;
    }
    if (lungeAttack) {
        event->eventFlags |= BROGUE_EVENT_FLAG_LUNGE;
    }
    if (attacker == &player && rogue.weapon != NULL) {
        event->itemId = identityForItem(rogue.weapon);
        event->itemCategory = rogue.weapon->category;
        event->itemKind = rogue.weapon->kind;
        if (rogue.weapon->flags & ITEM_ATTACKS_EXTEND) event->eventFlags |= BROGUE_EVENT_FLAG_ATTACK_EXTEND;
        if (rogue.weapon->flags & ITEM_ATTACKS_PENETRATE) event->eventFlags |= BROGUE_EVENT_FLAG_ATTACK_PENETRATE;
        if (rogue.weapon->flags & ITEM_ATTACKS_ALL_ADJACENT) event->eventFlags |= BROGUE_EVENT_FLAG_ATTACK_SWEEP;
        if (rogue.weapon->flags & ITEM_ATTACKS_STAGGER) event->eventFlags |= BROGUE_EVENT_FLAG_ATTACK_STAGGER;
        if (rogue.weapon->flags & ITEM_PASS_ATTACKS) event->eventFlags |= BROGUE_EVENT_FLAG_ATTACK_PASS;
        if (rogue.weapon->flags & ITEM_ATTACKS_QUICKLY) event->eventFlags |= BROGUE_EVENT_FLAG_ATTACK_QUICK;
    }
    copyText(event->text, sizeof(event->text), "attack attempted");
}

void brogue_bridge_note_damage(creature *attacker, creature *defender,
                               short amount, boolean lethal) {
    BrogueBridgeEvent *event;
    if (amount <= 0) {
        return;
    }
    event = recordActionEvent(BROGUE_EVENT_ENTITY_DAMAGED, attacker, defender);
    if (event == NULL) {
        return;
    }
    event->amount = amount;
    if (defender != NULL) {
        event->x = defender->loc.x;
        event->y = defender->loc.y;
    }
    if (lethal) {
        event->eventFlags |= BROGUE_EVENT_FLAG_LETHAL;
    }
    copyText(event->text, sizeof(event->text), "entity damaged");
}

void brogue_bridge_note_death(creature *decedent, boolean administrativeDeath) {
    BrogueBridgeEvent *event = recordActionEvent(BROGUE_EVENT_ENTITY_DIED,
                                                  NULL, decedent);
    if (event == NULL) {
        return;
    }
    event->eventFlags |= BROGUE_EVENT_FLAG_LETHAL;
    if (administrativeDeath) {
        event->eventFlags |= BROGUE_EVENT_FLAG_ADMINISTRATIVE;
    }
    if (decedent != NULL) {
        event->x = decedent->loc.x;
        event->y = decedent->loc.y;
    }
    copyText(event->text, sizeof(event->text), "entity died");
}

static uint64_t identityForItem(item *pointer) {
    size_t i;

    for (i = 0; i < itemIdentityCount; i++) {
        if (itemIdentities[i].pointer == pointer) {
            itemIdentities[i].seen = true;
            return itemIdentities[i].id;
        }
    }
    for (i = 0; i < itemIdentityCount; i++) {
        if (itemIdentities[i].pointer == NULL) {
            itemIdentities[i].pointer = pointer;
            itemIdentities[i].id = bridgeNextEntityId++;
            itemIdentities[i].seen = true;
            return itemIdentities[i].id;
        }
    }
    if (itemIdentityCount >= BROGUE_BRIDGE_MAX_ITEMS) {
        return 0;
    }
    itemIdentities[itemIdentityCount].pointer = pointer;
    itemIdentities[itemIdentityCount].id = bridgeNextEntityId++;
    itemIdentities[itemIdentityCount].seen = true;
    itemIdentityCount++;
    return itemIdentities[itemIdentityCount - 1].id;
}

static item *itemForIdentity(uint64_t id) {
    size_t i;
    for (i = 0; i < itemIdentityCount; i++) {
        if (itemIdentities[i].id == id && itemIdentities[i].pointer != NULL) {
            return itemIdentities[i].pointer;
        }
    }
    return NULL;
}

void brogue_bridge_prepare_thrown_item(item *source, item *projectile, boolean preserveIdentity) {
    size_t i;
    if (source == NULL || projectile == NULL) return;
    if (preserveIdentity) {
        for (i = 0; i < itemIdentityCount; i++) {
            if (itemIdentities[i].pointer == source) {
                itemIdentities[i].pointer = projectile;
                itemIdentities[i].seen = true;
                return;
            }
        }
    }
    identityForItem(projectile);
}

static BrogueBridgeEvent *recordItemEvent(BrogueBridgeEventType type, item *theItem) {
    BrogueBridgeEvent *event = recordActionEvent(type, &player, NULL);
    if (event != NULL && theItem != NULL) {
        event->itemId = identityForItem(theItem);
        event->itemCategory = theItem->category;
        event->itemKind = theItem->kind;
    }
    return event;
}

void brogue_bridge_note_projectile_step(item *projectile, pos from, pos to) {
    BrogueBridgeEvent *event = recordItemEvent(BROGUE_EVENT_PROJECTILE_MOVED, projectile);
    if (event == NULL) return;
    event->fromX = from.x;
    event->fromY = from.y;
    event->toX = event->x = to.x;
    event->toY = event->y = to.y;
    copyText(event->text, sizeof(event->text), "projectile moved");
}

void brogue_bridge_note_projectile_impact(item *projectile, pos loc) {
    BrogueBridgeEvent *event = recordItemEvent(BROGUE_EVENT_PROJECTILE_IMPACT, projectile);
    if (event == NULL) return;
    event->x = event->toX = loc.x;
    event->y = event->toY = loc.y;
    copyText(event->text, sizeof(event->text), "projectile impact");
}

void brogue_bridge_note_item_landed(item *projectile, pos loc) {
    BrogueBridgeEvent *event = recordItemEvent(BROGUE_EVENT_ITEM_LANDED, projectile);
    if (event == NULL) return;
    event->x = event->toX = loc.x;
    event->y = event->toY = loc.y;
    copyText(event->text, sizeof(event->text), "item landed");
}

static void beginIdentityCapture(void) {
    size_t i;
    for (i = 0; i < creatureIdentityCount; i++) {
        creatureIdentities[i].seen = false;
    }
    for (i = 0; i < itemIdentityCount; i++) {
        itemIdentities[i].seen = false;
    }
}

static void pruneIdentities(void) {
    size_t i;
    for (i = 0; i < creatureIdentityCount; i++) {
        if (!creatureIdentities[i].seen) {
            creatureIdentities[i].pointer = NULL;
        }
    }
    for (i = 0; i < itemIdentityCount; i++) {
        if (!itemIdentities[i].seen) {
            itemIdentities[i].pointer = NULL;
        }
    }
}

static void captureCell(BrogueBridgeCellState *outCell, int x, int y) {
    pcell *cell = &pmap[x][y];
    enum displayGlyph displayGlyph;
    color foreground;
    color background;
    uint64_t terrainFlags = 0;
    uint64_t mechanicalFlags = 0;
    boolean isDoor = false;
    boolean isLiquid = false;
    boolean isChasm = false;
    boolean isLava = false;
    boolean isFire = false;
    boolean isGas = false;
    boolean isBridge = false;
    int layer;

    memset(outCell, 0, sizeof(*outCell));
    outCell->x = x;
    outCell->y = y;
    outCell->cellFlags = (uint64_t) cell->flags;
    outCell->volume = cell->volume;
    outCell->machineNumber = cell->machineNumber;
    outCell->exposedToFire = cell->exposedToFire;

    for (layer = 0; layer < NUMBER_TERRAIN_LAYERS; layer++) {
        enum tileType tile = cell->layers[layer];
        outCell->layers[layer] = (int16_t) tile;
        if (validTile(tile)) {
            terrainFlags |= (uint64_t) tileCatalog[tile].flags;
            mechanicalFlags |= (uint64_t) tileCatalog[tile].mechFlags;
            isDoor = isDoor || tileIsDoor(tile);
            isLiquid = isLiquid || (layer == LIQUID && tileIsLiquid(tile));
            isChasm = isChasm || tileIsChasm(tile);
            isLava = isLava || tileIsLava(tile);
            isFire = isFire || (tileCatalog[tile].flags & T_IS_FIRE) != 0;
            isGas = isGas || (layer == GAS && tile != NOTHING);
            isBridge = isBridge || tileIsBridge(tile);
        }
    }

    outCell->terrainFlags = terrainFlags;
    outCell->mechanicalFlags = mechanicalFlags;
    outCell->isSolid = (terrainFlags & T_OBSTRUCTS_PASSABILITY) != 0;
    outCell->isWalkable = !outCell->isSolid;
    outCell->blocksVision = (terrainFlags & T_OBSTRUCTS_VISION) != 0;
    outCell->blocksDiagonalMovement = (terrainFlags & T_OBSTRUCTS_DIAGONAL_MOVEMENT) != 0;
    outCell->isDoor = isDoor;
    outCell->isSecret = (mechanicalFlags & TM_IS_SECRET) != 0;
    outCell->isLiquid = isLiquid;
    outCell->isDeepWater = (terrainFlags & T_IS_DEEP_WATER) != 0;
    outCell->isMud = cell->layers[LIQUID] == MUD;
    outCell->isLava = isLava;
    outCell->isFire = isFire;
    outCell->isGas = isGas;
    outCell->isChasm = isChasm;
    outCell->isBridge = isBridge;
    outCell->isStairsUp = (x == rogue.upLoc.x && y == rogue.upLoc.y);
    outCell->isStairsDown = (x == rogue.downLoc.x && y == rogue.downLoc.y);
    outCell->discovered = (cell->flags & (DISCOVERED | MAGIC_MAPPED)) != 0;
    outCell->currentlyVisible = (cell->flags & ANY_KIND_OF_VISIBLE) != 0;
    outCell->magicMapped = (cell->flags & MAGIC_MAPPED) != 0;

    /* Use Brogue's renderer-facing appearance resolver so the frontend map
     * sees the same remembered terrain, visibility, creature/item glyph and
     * lighting colors as the original terminal UI. This function uses only
     * Brogue's cosmetic RNG stream and restores the substantive stream. */
    getCellAppearance((pos) {x, y}, &displayGlyph, &foreground, &background);
    outCell->displayCodepoint = glyphToUnicode(displayGlyph);
    outCell->foregroundRed = (uint8_t) (clamp(foreground.red, 0, 100) * 255 / 100);
    outCell->foregroundGreen = (uint8_t) (clamp(foreground.green, 0, 100) * 255 / 100);
    outCell->foregroundBlue = (uint8_t) (clamp(foreground.blue, 0, 100) * 255 / 100);
    outCell->backgroundRed = (uint8_t) (clamp(background.red, 0, 100) * 255 / 100);
    outCell->backgroundGreen = (uint8_t) (clamp(background.green, 0, 100) * 255 / 100);
    outCell->backgroundBlue = (uint8_t) (clamp(background.blue, 0, 100) * 255 / 100);
}

static BrogueBridgeResult captureCreature(BrogueBridgeCreatureState *outCreature,
                                          creature *monst) {
    uint64_t id;
    boolean hallucinated;

    id = identityForCreature(monst);
    if (id == 0) {
        return BROGUE_BRIDGE_CAPACITY_EXCEEDED;
    }
    memset(outCreature, 0, sizeof(*outCreature));
    outCreature->id = id;
    outCreature->kind = monst->info.monsterID;
    hallucinated = player.status[STATUS_HALLUCINATING]
        && !rogue.playbackOmniscience
        && !monsterRevealed(monst);
    outCreature->presentationKind = monst->info.monsterID;
    if (hallucinated) {
        /* Brogue's renderer draws hallucinated forms from its cosmetic RNG.
         * Preserve that exact catalog selection without ever advancing the
         * substantive gameplay stream while taking a bridge snapshot. */
        assureCosmeticRNG;
        outCreature->presentationKind = randomAnimateMonster();
        restoreRNG;
    }
    outCreature->x = monst->loc.x;
    outCreature->y = monst->loc.y;
    outCreature->hp = monst->currentHP;
    outCreature->maxHp = monst->info.maxHP;
    outCreature->state = monst->creatureState;
    outCreature->mode = monst->creatureMode;
    outCreature->behaviorFlags = (uint64_t) monst->info.flags;
    outCreature->abilityFlags = (uint64_t) monst->info.abilityFlags;
    outCreature->bookkeepingFlags = (uint64_t) monst->bookkeepingFlags;
    outCreature->statusFlags = statusFlagsFor(monst);
    outCreature->mutationIndex = monst->mutationIndex;
    outCreature->wasNegated = monst->wasNegated;
    if (canDirectlySeeMonster(monst)) {
        outCreature->visibility = BROGUE_VISIBILITY_DIRECT;
    } else if (canSeeMonster(monst)) {
        outCreature->visibility = BROGUE_VISIBILITY_SENSED;
    } else {
        outCreature->visibility = BROGUE_VISIBILITY_HIDDEN;
        outCreature->presentationKind = -1;
    }
    outCreature->isAlly = monst->creatureState == MONSTER_ALLY;
    outCreature->isLarge = monst->info.isLarge;
    outCreature->visible = outCreature->visibility != BROGUE_VISIBILITY_HIDDEN;
    outCreature->alive = (monst->bookkeepingFlags & (MB_IS_DYING | MB_HAS_DIED)) == 0
                      && monst->currentHP > 0;
    return BROGUE_BRIDGE_OK;
}

static BrogueBridgeResult appendItem(BrogueBridgeState *state,
                                     item *theItem,
                                     boolean carried) {
    BrogueBridgeItemState *outItem;
    itemTable *kindTable;
    uint64_t id;
    char itemNameBuffer[COLS * 3];
    char itemDetailBuffer[1000];

    if (state->itemCount >= BROGUE_BRIDGE_MAX_ITEMS) {
        return BROGUE_BRIDGE_CAPACITY_EXCEEDED;
    }
    id = identityForItem(theItem);
    if (id == 0) {
        return BROGUE_BRIDGE_CAPACITY_EXCEEDED;
    }
    outItem = &state->items[state->itemCount++];
    memset(outItem, 0, sizeof(*outItem));
    outItem->id = id;
    outItem->category = theItem->category;
    outItem->kind = theItem->kind;
    outItem->x = theItem->loc.x;
    outItem->y = theItem->loc.y;
    outItem->quantity = theItem->quantity;
    outItem->flags = (uint64_t) theItem->flags;
    outItem->damageLower = theItem->damage.lowerBound;
    outItem->damageUpper = theItem->damage.upperBound;
    outItem->damageClump = theItem->damage.clumpFactor;
    outItem->strengthRequired = theItem->strengthRequired;
    outItem->enchantment = theItem->enchant1;
    outItem->carried = carried;
    outItem->visible = !carried
        && coordinatesAreInMap(theItem->loc.x, theItem->loc.y)
        && playerCanSeeOrSense(theItem->loc.x, theItem->loc.y);
    kindTable = tableForItemCategory(theItem->category);
    outItem->kindKnown = (theItem->flags & ITEM_IDENTIFIED) != 0
        || (theItem->category & NEVER_IDENTIFIABLE) != 0
        || (kindTable != NULL && kindTable[theItem->kind].identified);
    outItem->equipped = (theItem->flags & ITEM_EQUIPPED) != 0;
    outItem->enchantmentKnown = (theItem->flags & ITEM_IDENTIFIED) != 0;
    outItem->runicKnown = (theItem->flags & ITEM_RUNIC_IDENTIFIED) != 0;
    outItem->cursedKnown = (theItem->flags & ITEM_IDENTIFIED) != 0;
    outItem->inventoryLetter = carried ? theItem->inventoryLetter : 0;
    outItem->equipmentSlot = rogue.weapon == theItem ? 1
        : rogue.armor == theItem ? 2
        : rogue.ringLeft == theItem ? 3
        : rogue.ringRight == theItem ? 4 : 0;
    outItem->actionFlags = carried ? (BROGUE_ITEM_ACTION_DROP | BROGUE_ITEM_ACTION_THROW) : 0;
    if (carried && theItem->category == STAFF) outItem->actionFlags |= BROGUE_ITEM_ACTION_TARGET_STAFF;
    if (carried && theItem->category == WAND) outItem->actionFlags |= BROGUE_ITEM_ACTION_TARGET_WAND;
    if (carried && (theItem->category & (FOOD | POTION | SCROLL | CHARM))) {
        outItem->actionFlags |= BROGUE_ITEM_ACTION_APPLY;
    }
    if (carried && (theItem->category & (WEAPON | ARMOR | RING))) {
        outItem->actionFlags |= outItem->equipped
            ? BROGUE_ITEM_ACTION_UNEQUIP : BROGUE_ITEM_ACTION_EQUIP;
    }
    itemName(theItem, itemNameBuffer, false, false, NULL);
    copyPlainText(outItem->displayName, sizeof(outItem->displayName), itemNameBuffer);
    itemDetails(itemDetailBuffer, theItem);
    copyPlainText(outItem->detailText, sizeof(outItem->detailText), itemDetailBuffer);
    return BROGUE_BRIDGE_OK;
}

static void sortCreatures(BrogueBridgeState *state) {
    size_t i;
    for (i = 1; i < state->creatureCount; i++) {
        BrogueBridgeCreatureState value = state->creatures[i];
        size_t j = i;
        while (j > 0 && state->creatures[j - 1].id > value.id) {
            state->creatures[j] = state->creatures[j - 1];
            j--;
        }
        state->creatures[j] = value;
    }
}

static void sortItems(BrogueBridgeState *state) {
    size_t i;
    for (i = 1; i < state->itemCount; i++) {
        BrogueBridgeItemState value = state->items[i];
        size_t j = i;
        while (j > 0 && state->items[j - 1].id > value.id) {
            state->items[j] = state->items[j - 1];
            j--;
        }
        state->items[j] = value;
    }
}

static BrogueBridgeResult captureState(BrogueBridgeState *outState) {
    creatureIterator iterator;
    creature *monst;
    item *theItem;
    int x, y;
    int i;
    BrogueBridgeResult result;

    if (levels == NULL || gameConst == NULL) {
        return BROGUE_BRIDGE_INVALID_STATE;
    }
    memset(outState, 0, sizeof(*outState));
    outState->apiVersion = BROGUE_BRIDGE_API_VERSION;
    outState->revision = bridgeRevision;
    outState->gameSeed = rogue.seed;
    outState->depth = rogue.depthLevel;
    outState->width = DCOLS;
    outState->height = DROWS;
    outState->turn = rogue.playerTurnNumber;
    outState->absoluteTurn = rogue.absoluteTurnNumber;
    outState->levelSeed = levels[rogue.depthLevel - 1].levelSeed;
    outState->player = playerState();
    outState->gameResult = bridgeGameResult;
    outState->upStairsX = rogue.upLoc.x;
    outState->upStairsY = rogue.upLoc.y;
    outState->downStairsX = rogue.downLoc.x;
    outState->downStairsY = rogue.downLoc.y;

    for (y = 0; y < DROWS; y++) {
        for (x = 0; x < DCOLS; x++) {
            captureCell(&outState->cells[outState->cellCount++], x, y);
        }
    }

    iterator = iterateCreatures(monsters);
    while (hasNextCreature(iterator)) {
        monst = nextCreature(&iterator);
        if (outState->creatureCount >= BROGUE_BRIDGE_MAX_CREATURES) {
            return BROGUE_BRIDGE_CAPACITY_EXCEEDED;
        }
        result = captureCreature(&outState->creatures[outState->creatureCount++], monst);
        if (result != BROGUE_BRIDGE_OK) {
            return result;
        }
    }
    sortCreatures(outState);

    // floorItems and packItems are sentinel list heads, not gameplay items.
    // Starting at the heads exported category-zero placeholders and made the
    // frontend retry an impossible proxy spawn every tic.
    theItem = floorItems->nextItem;
    while (theItem != NULL) {
        result = appendItem(outState, theItem, false);
        if (result != BROGUE_BRIDGE_OK) {
            return result;
        }
        theItem = theItem->nextItem;
    }
    theItem = packItems->nextItem;
    i = 4;
    while (theItem != NULL) {
        result = appendItem(outState, theItem, true);
        if (result != BROGUE_BRIDGE_OK) {
            return result;
        }
        if (outState->items[outState->itemCount - 1].equipmentSlot != 0) {
            outState->items[outState->itemCount - 1].inventoryOrder
                = outState->items[outState->itemCount - 1].equipmentSlot - 1;
        } else {
            outState->items[outState->itemCount - 1].inventoryOrder = (uint8_t) i++;
        }
        theItem = theItem->nextItem;
    }
    sortItems(outState);

    for (i = 0; i < MESSAGE_LINES && i < BROGUE_BRIDGE_MAX_MESSAGES; i++) {
        if (displayedMessage[i][0] != '\0') {
            // Brogue embeds COLOR_ESCAPE plus RGB bytes in displayed text.
            // GZDoom interprets those control bytes as font/control glyphs,
            // so expose the same readable message without the terminal-only
            // formatting payload.
            copyPlainText(outState->messages[outState->messageCount++],
                          BROGUE_BRIDGE_MESSAGE_LENGTH,
                          displayedMessage[i]);
        }
    }

    outState->stateHash = stateHash(outState);
    outState->presentationHash = presentationHash(outState);
    return BROGUE_BRIDGE_OK;
}

static uint64_t hashPlayer(uint64_t hash, const BrogueBridgePlayerState *playerStateValue) {
    hash = hashSigned(hash, playerStateValue->x);
    hash = hashSigned(hash, playerStateValue->y);
    hash = hashSigned(hash, playerStateValue->hp);
    hash = hashSigned(hash, playerStateValue->maxHp);
    hash = hashSigned(hash, playerStateValue->depth);
    hash = hashU64(hash, playerStateValue->turn);
    hash = hashU64(hash, playerStateValue->absoluteTurn);
    hash = hashU64(hash, playerStateValue->statusFlags);
    hash = hashU64(hash, playerStateValue->equippedWeaponId);
    hash = hashU64(hash, playerStateValue->equippedArmorId);
    hash = hashU64(hash, playerStateValue->equippedLeftRingId);
    hash = hashU64(hash, playerStateValue->equippedRightRingId);
    hash = hashSigned(hash, playerStateValue->armor);
    hash = hashSigned(hash, playerStateValue->strength);
    hash = hashSigned(hash, playerStateValue->nutrition);
    hash = hashSigned(hash, playerStateValue->maxNutrition);
    hash = hashSigned(hash, playerStateValue->stealthRange);
    hash = hashU64(hash, playerStateValue->gold);
    hash = hashU32(hash, playerStateValue->alive);
    hash = hashU32(hash, playerStateValue->gameInProgress);
    return hashU32(hash, playerStateValue->gameHasEnded);
}

static uint64_t stateHash(const BrogueBridgeState *state) {
    uint64_t hash = UINT64_C(1469598103934665603);
    size_t i;
    int layer;

    hash = hashU64(hash, state->gameSeed);
    hash = hashU64(hash, state->levelSeed);
    hash = hashSigned(hash, state->depth);
    hash = hashSigned(hash, state->width);
    hash = hashSigned(hash, state->height);
    hash = hashU64(hash, state->turn);
    hash = hashU64(hash, state->absoluteTurn);
    hash = hashPlayer(hash, &state->player);
    hash = hashU32(hash, state->gameResult.outcome);
    hash = hashSigned(hash, state->gameResult.score);
    hash = hashSigned(hash, state->gameResult.depth);
    hash = hashSigned(hash, state->gameResult.deepestDepth);
    hash = hashU64(hash, state->gameResult.turn);
    hash = hashBytes(hash, state->gameResult.cause, strlen(state->gameResult.cause) + 1);
    hash = hashBytes(hash, state->gameResult.summary, strlen(state->gameResult.summary) + 1);
    hash = hashSigned(hash, state->upStairsX);
    hash = hashSigned(hash, state->upStairsY);
    hash = hashSigned(hash, state->downStairsX);
    hash = hashSigned(hash, state->downStairsY);

    for (i = 0; i < state->cellCount; i++) {
        const BrogueBridgeCellState *cell = &state->cells[i];
        hash = hashSigned(hash, cell->x);
        hash = hashSigned(hash, cell->y);
        for (layer = 0; layer < 4; layer++) {
            hash = hashSigned(hash, cell->layers[layer]);
        }
        hash = hashU64(hash, cell->cellFlags);
        hash = hashU64(hash, cell->terrainFlags);
        hash = hashU64(hash, cell->mechanicalFlags);
        hash = hashU32(hash, cell->volume);
        hash = hashU32(hash, cell->machineNumber);
        hash = hashSigned(hash, cell->exposedToFire);
        hash = hashU32(hash, cell->isSolid);
        hash = hashU32(hash, cell->isWalkable);
        hash = hashU32(hash, cell->blocksVision);
        hash = hashU32(hash, cell->blocksDiagonalMovement);
        hash = hashU32(hash, cell->isDoor);
        hash = hashU32(hash, cell->isSecret);
        hash = hashU32(hash, cell->isLiquid);
        hash = hashU32(hash, cell->isDeepWater);
        hash = hashU32(hash, cell->isMud);
        hash = hashU32(hash, cell->isLava);
        hash = hashU32(hash, cell->isFire);
        hash = hashU32(hash, cell->isGas);
        hash = hashU32(hash, cell->isChasm);
        hash = hashU32(hash, cell->isBridge);
        hash = hashU32(hash, cell->isStairsUp);
        hash = hashU32(hash, cell->isStairsDown);
    }

    for (i = 0; i < state->creatureCount; i++) {
        const BrogueBridgeCreatureState *creatureState = &state->creatures[i];
        hash = hashU64(hash, creatureState->id);
        hash = hashSigned(hash, creatureState->kind);
        hash = hashSigned(hash, creatureState->x);
        hash = hashSigned(hash, creatureState->y);
        hash = hashSigned(hash, creatureState->hp);
        hash = hashSigned(hash, creatureState->maxHp);
        hash = hashSigned(hash, creatureState->state);
        hash = hashSigned(hash, creatureState->mode);
        hash = hashU64(hash, creatureState->behaviorFlags);
        hash = hashU64(hash, creatureState->abilityFlags);
        hash = hashU64(hash, creatureState->bookkeepingFlags);
        hash = hashU64(hash, creatureState->statusFlags);
        hash = hashSigned(hash, creatureState->mutationIndex);
        hash = hashU32(hash, creatureState->wasNegated);
        hash = hashU32(hash, creatureState->isAlly);
        hash = hashU32(hash, creatureState->isLarge);
        hash = hashU32(hash, creatureState->alive);
    }

    for (i = 0; i < state->itemCount; i++) {
        const BrogueBridgeItemState *itemState = &state->items[i];
        hash = hashU64(hash, itemState->id);
        hash = hashSigned(hash, itemState->category);
        hash = hashSigned(hash, itemState->kind);
        hash = hashSigned(hash, itemState->x);
        hash = hashSigned(hash, itemState->y);
        hash = hashSigned(hash, itemState->quantity);
        hash = hashU64(hash, itemState->flags);
        hash = hashSigned(hash, itemState->damageLower);
        hash = hashSigned(hash, itemState->damageUpper);
        hash = hashSigned(hash, itemState->damageClump);
        hash = hashSigned(hash, itemState->strengthRequired);
        hash = hashSigned(hash, itemState->enchantment);
        hash = hashU32(hash, itemState->carried);
        hash = hashU32(hash, itemState->visible);
        hash = hashU32(hash, itemState->kindKnown);
        hash = hashU32(hash, itemState->equipped);
        hash = hashU32(hash, itemState->enchantmentKnown);
        hash = hashU32(hash, itemState->runicKnown);
        hash = hashU32(hash, itemState->cursedKnown);
        hash = hashBytes(hash, itemState->displayName, strlen(itemState->displayName) + 1);
    }

    for (i = 0; i < state->messageCount; i++) {
        hash = hashBytes(hash, state->messages[i], strlen(state->messages[i]) + 1);
    }
    return hash;
}

static uint64_t presentationHash(const BrogueBridgeState *state) {
    uint64_t hash = UINT64_C(1469598103934665603);
    size_t i;
    hash = hashU64(hash, state->revision);
    for (i = 0; i < state->creatureCount; i++) {
        const BrogueBridgeCreatureState *creatureState = &state->creatures[i];
        hash = hashU64(hash, creatureState->id);
        hash = hashSigned(hash, creatureState->presentationKind);
        hash = hashU32(hash, creatureState->visibility);
        hash = hashU32(hash, creatureState->visible);
    }
    return hash;
}

static boolean creatureStateEqual(const BrogueBridgeCreatureState *first,
                                  const BrogueBridgeCreatureState *second) {
    return memcmp(first, second, sizeof(*first)) == 0;
}

/* Visibility/discovery flags change as Brogue refreshes FOV.  They are part
 * of the snapshot, but are not terrain deltas and must not flood the event
 * stream after every movement. */
static boolean cellGameplayEqual(const BrogueBridgeCellState *first,
                                 const BrogueBridgeCellState *second) {
    int layer;
    if (first->volume != second->volume
        || first->machineNumber != second->machineNumber
        || first->exposedToFire != second->exposedToFire
        || first->terrainFlags != second->terrainFlags
        || first->mechanicalFlags != second->mechanicalFlags) {
        return false;
    }
    for (layer = 0; layer < 4; layer++) {
        if (first->layers[layer] != second->layers[layer]) {
            return false;
        }
    }
    return true;
}

static const BrogueBridgeCreatureState *findCreatureState(const BrogueBridgeState *state,
                                                           uint64_t id) {
    size_t i;
    for (i = 0; i < state->creatureCount; i++) {
        if (state->creatures[i].id == id) {
            return &state->creatures[i];
        }
    }
    return NULL;
}

static const BrogueBridgeCellState *findCellState(const BrogueBridgeState *state,
                                                  int x,
                                                  int y) {
    size_t index;
    if (x < 0 || y < 0 || x >= state->width || y >= state->height) {
        return NULL;
    }
    index = (size_t) y * (size_t) state->width + (size_t) x;
    if (index >= state->cellCount) {
        return NULL;
    }
    return &state->cells[index];
}

static const BrogueBridgeItemState *findItemState(const BrogueBridgeState *state,
                                                   uint64_t id) {
    size_t i;
    for (i = 0; i < state->itemCount; i++) {
        if (state->items[i].id == id) return &state->items[i];
    }
    return NULL;
}

static BrogueBridgeEvent *addEvent(BrogueBridgeTurnResult *result,
                                    BrogueBridgeEventType type,
                                    int x,
                                    int y,
                                    const char *text) {
    BrogueBridgeEvent *event;
    if (result->eventCount >= BROGUE_BRIDGE_MAX_EVENTS) {
        result->eventsTruncated = 1;
        return NULL;
    }
    event = &result->events[result->eventCount++];
    memset(event, 0, sizeof(*event));
    event->sequence = ++eventSequence;
    event->type = type;
    event->x = x;
    event->y = y;
    copyText(event->text, sizeof(event->text), text);
    return event;
}

static boolean resultHasEntityEvent(const BrogueBridgeTurnResult *result,
                                    BrogueBridgeEventType type,
                                    uint64_t entityId) {
    size_t i;
    for (i = 0; i < result->eventCount; i++) {
        if (result->events[i].type == type
            && result->events[i].entityId == entityId) {
            return true;
        }
    }
    return false;
}

static void appendRecordedEvents(BrogueBridgeTurnResult *result) {
    size_t i;
    for (i = 0; i < recordedEventCount; i++) {
        if (result->eventCount >= BROGUE_BRIDGE_MAX_EVENTS) {
            result->eventsTruncated = 1;
            break;
        }
        result->events[result->eventCount++] = recordedEvents[i];
    }
    if (recordedEventsTruncated) {
        result->eventsTruncated = 1;
    }
}

static void buildEvents(const BrogueBridgeState *before,
                        const BrogueBridgeState *after,
                        BrogueBridgeTurnResult *result) {
    size_t i;
    size_t j;
    const BrogueBridgeCreatureState *oldCreature;
    const BrogueBridgeCellState *oldCell;
    BrogueBridgeEvent *event;
    boolean foundMessage;

    /* A depth change replaces the addressed map. It must never be displaced
     * by thousands of cross-level cell/creature differences in the bounded
     * event buffer; the new full snapshot is the authoritative level state. */
    if (before->depth != after->depth) {
        int sourceX = before->player.x;
        int sourceY = before->player.y;
        boolean fell = false;

        /* Stairs change depth without recording ordinary player movement.
         * Auto-descent first records movement into the hole/chasm and then
         * changes levels at the end of Brogue's turn. Preserve that final
         * source-floor coordinate before the source pmap is replaced. */
        if (recordedPlayerFall && after->depth > before->depth) {
            sourceX = recordedPlayerFallSource.x;
            sourceY = recordedPlayerFallSource.y;
            fell = true;
        }

        event = addEvent(result, BROGUE_EVENT_LEVEL_CHANGE_REQUESTED,
                         after->player.x, after->player.y, "level change requested");
        if (event != NULL) {
            event->fromX = sourceX;
            event->fromY = sourceY;
            event->toX = after->player.x;
            event->toY = after->player.y;
            event->amount = after->depth - before->depth;
            if (fell) event->eventFlags |= BROGUE_EVENT_FLAG_LEVEL_FALL;
        }
        return;
    }

    if (before->player.x != after->player.x || before->player.y != after->player.y) {
        if (!resultHasEntityEvent(result, BROGUE_EVENT_PLAYER_MOVED,
                                  BROGUE_BRIDGE_PLAYER_ENTITY_ID)) {
            event = addEvent(result, BROGUE_EVENT_PLAYER_MOVED,
                             after->player.x, after->player.y, "player moved");
            if (event != NULL) {
                event->entityId = BROGUE_BRIDGE_PLAYER_ENTITY_ID;
            }
        }
    }
    if (!result->actionAccepted) {
        addEvent(result, BROGUE_EVENT_PLAYER_ACTION_BLOCKED,
                 after->player.x, after->player.y, "action blocked by Brogue");
    }
    if (before->player.hp != after->player.hp) {
        addEvent(result, BROGUE_EVENT_PLAYER_HP_CHANGED,
                 after->player.x, after->player.y, "player HP changed");
    }
    if (before->player.statusFlags != after->player.statusFlags) {
        addEvent(result, BROGUE_EVENT_PLAYER_STATUS_CHANGED,
                 after->player.x, after->player.y, "player status changed");
    }
    if (before->player.equippedWeaponId != after->player.equippedWeaponId) {
        if (before->player.equippedWeaponId != 0) {
            const BrogueBridgeItemState *oldWeapon = findItemState(before, before->player.equippedWeaponId);
            event = addEvent(result, BROGUE_EVENT_WEAPON_UNEQUIPPED,
                             after->player.x, after->player.y, "weapon unequipped");
            if (event != NULL) {
                event->itemId = before->player.equippedWeaponId;
                if (oldWeapon != NULL) {
                    event->itemCategory = oldWeapon->category;
                    event->itemKind = oldWeapon->kind;
                }
            }
        }
        if (after->player.equippedWeaponId != 0) {
            const BrogueBridgeItemState *newWeapon = findItemState(after, after->player.equippedWeaponId);
            event = addEvent(result, BROGUE_EVENT_WEAPON_EQUIPPED,
                             after->player.x, after->player.y, "weapon equipped");
            if (event != NULL) {
                event->itemId = after->player.equippedWeaponId;
                if (newWeapon != NULL) {
                    event->itemCategory = newWeapon->category;
                    event->itemKind = newWeapon->kind;
                }
            }
        }
    }

    for (i = 0; i < after->creatureCount; i++) {
        const BrogueBridgeCreatureState *creatureState = &after->creatures[i];
        oldCreature = findCreatureState(before, creatureState->id);
        if (oldCreature == NULL) {
            event = addEvent(result, BROGUE_EVENT_CREATURE_SPAWNED,
                             creatureState->x, creatureState->y, "creature spawned");
            if (event != NULL) {
                event->entityId = creatureState->id;
            }
        } else if (oldCreature->x != creatureState->x || oldCreature->y != creatureState->y) {
            if (!resultHasEntityEvent(result, BROGUE_EVENT_CREATURE_MOVED,
                                      creatureState->id)) {
                event = addEvent(result, BROGUE_EVENT_CREATURE_MOVED,
                                 creatureState->x, creatureState->y, "creature moved");
                if (event != NULL) {
                    event->entityId = creatureState->id;
                    event->fromX = oldCreature->x;
                    event->fromY = oldCreature->y;
                    event->toX = creatureState->x;
                    event->toY = creatureState->y;
                }
            }
        } else if (!creatureStateEqual(oldCreature, creatureState)) {
            event = addEvent(result, BROGUE_EVENT_CREATURE_STATE_CHANGED,
                             creatureState->x, creatureState->y, "creature state changed");
            if (event != NULL) {
                event->entityId = creatureState->id;
            }
        }
    }
    for (i = 0; i < before->creatureCount; i++) {
        if (findCreatureState(after, before->creatures[i].id) == NULL) {
            event = addEvent(result, BROGUE_EVENT_CREATURE_REMOVED,
                             before->creatures[i].x, before->creatures[i].y, "creature removed");
            if (event != NULL) {
                event->entityId = before->creatures[i].id;
            }
        }
    }

    for (i = 0; i < after->cellCount; i++) {
        const BrogueBridgeCellState *cell = &after->cells[i];
        oldCell = findCellState(before, cell->x, cell->y);
        if (oldCell != NULL && !cellGameplayEqual(oldCell, cell)) {
            event = addEvent(result, BROGUE_EVENT_CELL_TERRAIN_CHANGED,
                             cell->x, cell->y, "cell terrain changed");
            if (event != NULL) {
                event->beforeDungeon = oldCell->layers[DUNGEON];
                event->afterDungeon = cell->layers[DUNGEON];
                event->beforeCellFlags = oldCell->cellFlags;
                event->afterCellFlags = cell->cellFlags;
                event->beforeTerrainFlags = oldCell->terrainFlags;
                event->afterTerrainFlags = cell->terrainFlags;
                event->beforeMechanicalFlags = oldCell->mechanicalFlags;
                event->afterMechanicalFlags = cell->mechanicalFlags;
            }
        }
    }

    for (i = 0; i < after->messageCount; i++) {
        foundMessage = false;
        for (j = 0; j < before->messageCount; j++) {
            if (strcmp(after->messages[i], before->messages[j]) == 0) {
                foundMessage = true;
                break;
            }
        }
        if (!foundMessage) {
            addEvent(result, BROGUE_EVENT_MESSAGE,
                     after->player.x, after->player.y, after->messages[i]);
        }
    }
}

static enum directions actionDirection(BrogueBridgeAction action) {
    switch (action) {
        case BROGUE_ACTION_MOVE_N: return UP;
        case BROGUE_ACTION_MOVE_NE: return UPRIGHT;
        case BROGUE_ACTION_MOVE_E: return RIGHT;
        case BROGUE_ACTION_MOVE_SE: return DOWNRIGHT;
        case BROGUE_ACTION_MOVE_S: return DOWN;
        case BROGUE_ACTION_MOVE_SW: return DOWNLEFT;
        case BROGUE_ACTION_MOVE_W: return LEFT;
        case BROGUE_ACTION_MOVE_NW: return UPLEFT;
        default: return NO_DIRECTION;
    }
}

BrogueBridgeResult brogue_bridge_initialize(void) {
    if (!bridgeInitialized) {
        gameVariant = VARIANT_BROGUE;
        initializeGameVariant();
        bridgeInitialized = true;
    }
    return BROGUE_BRIDGE_OK;
}

BrogueBridgeResult brogue_bridge_start_game(uint64_t gameSeed) {
    BrogueBridgeResult result;

    if (!bridgeInitialized) {
        result = brogue_bridge_initialize();
        if (result != BROGUE_BRIDGE_OK) {
            return result;
        }
    }
    if (bridgeGameStarted) {
        brogue_bridge_shutdown();
    }

    currentConsole = nullConsole;
    /* Keep Brogue's normal rules, but route terminal death/victory cleanup
     * through its non-interactive/server-safe branch. RogueMain skips only
     * the blocking acknowledgement in server mode, preserving the real death
     * outcome instead of disguising it as a player quit. */
    serverMode = true;
    nonInteractivePlayback = true;
    hasGraphics = false;
    graphicsMode = TEXT_GRAPHICS;
    rogue.mode = GAME_MODE_NORMAL;
    rogue.playbackMode = false;
    rogue.playbackFastForward = true;
    rogue.playbackPaused = false;
    rogue.quit = false;
    rogue.nextGame = NG_NOTHING;

    initializeRogue(gameSeed);
    /* Server mode bypasses terminal-only death acknowledgement while leaving
     * Brogue's real quit/death outcome untouched. */
    rogue.quit = false;
    startLevel(rogue.depthLevel, 1);
    rogue.automationActive = true;

    memset(creatureIdentities, 0, sizeof(creatureIdentities));
    memset(itemIdentities, 0, sizeof(itemIdentities));
    creatureIdentityCount = 0;
    itemIdentityCount = 0;
    bridgeNextEntityId = 2;
    bridgeRevision = 1;
    eventSequence = 0;
    endConfirmationBroker();
    confirmationWasRequested = false;
    confirmationPrompt[0] = '\0';
    memset(&bridgeGameResult, 0, sizeof(bridgeGameResult));
    bridgeGameStarted = true;

    beginIdentityCapture();
    result = captureState(&bridgeState);
    pruneIdentities();
    if (result != BROGUE_BRIDGE_OK) {
        bridgeGameStarted = false;
        freeEverything();
        return result;
    }
    return BROGUE_BRIDGE_OK;
}

BrogueBridgeResult brogue_bridge_get_state(BrogueBridgeState *outState) {
    if (outState == NULL) {
        return BROGUE_BRIDGE_INVALID_STATE;
    }
    if (!bridgeInitialized) {
        return BROGUE_BRIDGE_NOT_INITIALIZED;
    }
    if (!bridgeGameStarted) {
        return BROGUE_BRIDGE_GAME_NOT_STARTED;
    }
    memcpy(outState, &bridgeState, sizeof(*outState));
    return BROGUE_BRIDGE_OK;
}

BrogueBridgeResult brogue_bridge_get_monster_catalog(BrogueBridgeMonsterCatalog *outCatalog) {
    int i;
    if (outCatalog == NULL) {
        return BROGUE_BRIDGE_INVALID_STATE;
    }
    if (!bridgeInitialized) {
        return BROGUE_BRIDGE_NOT_INITIALIZED;
    }
    if (NUMBER_MONSTER_KINDS > BROGUE_BRIDGE_MAX_MONSTER_KINDS) {
        return BROGUE_BRIDGE_CAPACITY_EXCEEDED;
    }
    memset(outCatalog, 0, sizeof(*outCatalog));
    outCatalog->apiVersion = BROGUE_BRIDGE_API_VERSION;
    outCatalog->count = NUMBER_MONSTER_KINDS;
    for (i = 0; i < NUMBER_MONSTER_KINDS; i++) {
        const creatureType *source = &monsterCatalog[i];
        const color *foreColor = source->foreColor;
        BrogueBridgeMonsterKindInfo *target = &outCatalog->kinds[i];
        target->kind = i;
        copyText(target->symbol, sizeof(target->symbol), monsterSymbols[i]);
        copyText(target->name, sizeof(target->name), source->monsterName);
        target->displayGlyph = source->displayChar;
        if (foreColor != NULL) {
            target->colorRed = foreColor->red;
            target->colorGreen = foreColor->green;
            target->colorBlue = foreColor->blue;
            target->colorRedRand = foreColor->redRand;
            target->colorGreenRand = foreColor->greenRand;
            target->colorBlueRand = foreColor->blueRand;
            target->colorRand = foreColor->rand;
            target->colorDances = foreColor->colorDances;
        }
        target->maxHp = source->maxHP;
        target->intrinsicLightType = source->intrinsicLightType;
        target->isLarge = source->isLarge;
        target->behaviorFlags = (uint64_t) source->flags;
        target->abilityFlags = (uint64_t) source->abilityFlags;
    }
    return BROGUE_BRIDGE_OK;
}

static BrogueBridgeSelectionType applySelectionType(const item *source) {
    if (source == NULL || !(source->category & SCROLL)) {
        return BROGUE_SELECTION_NONE;
    }
    if (source->kind == SCROLL_IDENTIFY) {
        return BROGUE_SELECTION_IDENTIFY_ITEM;
    }
    if (source->kind == SCROLL_ENCHANTING) {
        return BROGUE_SELECTION_ENCHANT_ITEM;
    }
    return BROGUE_SELECTION_NONE;
}

static boolean validApplySelection(const item *source, const item *candidate) {
    BrogueBridgeSelectionType type = applySelectionType(source);
    if (source == NULL || candidate == NULL || source == candidate || !itemIsCarried((item *) candidate)) {
        return false;
    }
    if (type == BROGUE_SELECTION_IDENTIFY_ITEM) {
        return (candidate->flags & ITEM_CAN_BE_IDENTIFIED) != 0;
    }
    if (type == BROGUE_SELECTION_ENCHANT_ITEM) {
        return (candidate->category & (WEAPON | ARMOR | RING | STAFF | WAND | CHARM)) != 0;
    }
    return false;
}

static void populateApplyChoices(const item *source, BrogueBridgeTurnResult *outResult) {
    item *candidate;
    outResult->selectionType = applySelectionType(source);
    copyText(outResult->prompt, sizeof(outResult->prompt),
             outResult->selectionType == BROGUE_SELECTION_IDENTIFY_ITEM
                 ? "Identify what?" : "Enchant what?");
    for (candidate = packItems->nextItem;
         candidate != NULL && outResult->choiceCount < BROGUE_BRIDGE_MAX_ITEM_CHOICES;
         candidate = candidate->nextItem) {
        if (validApplySelection(source, candidate)) {
            outResult->choiceItemIds[outResult->choiceCount++] = identityForItem(candidate);
        }
    }
}

BrogueBridgeResult brogue_bridge_perform_command(const BrogueBridgeCommand *command,
                                                  BrogueBridgeTurnResult *outResult) {
    enum directions direction;
    uint64_t oldAbsoluteTurn;
    boolean accepted = false;
    BrogueBridgeResult result;
    item *commandItem = NULL;
    item *secondaryItem = NULL;
    BrogueBridgeAction action = BROGUE_ACTION_WAIT;

    if (command == NULL || outResult == NULL) {
        return BROGUE_BRIDGE_INVALID_STATE;
    }
    memset(outResult, 0, sizeof(*outResult));
    outResult->apiVersion = BROGUE_BRIDGE_API_VERSION;
    outResult->commandType = command->type;
    outResult->action = command->action;
    outResult->itemId = command->itemId;
    outResult->errorCode = BROGUE_BRIDGE_OK;
    if (!bridgeInitialized) {
        outResult->errorCode = BROGUE_BRIDGE_NOT_INITIALIZED;
        return outResult->errorCode;
    }
    if (!bridgeGameStarted) {
        outResult->errorCode = BROGUE_BRIDGE_GAME_NOT_STARTED;
        return outResult->errorCode;
    }
    if (rogue.gameHasEnded) {
        outResult->errorCode = BROGUE_BRIDGE_GAME_ENDED;
        return outResult->errorCode;
    }
    if (command->apiVersion != BROGUE_BRIDGE_API_VERSION
        || command->type < 0 || command->type >= BROGUE_COMMAND_COUNT) {
        outResult->errorCode = BROGUE_BRIDGE_INVALID_ACTION;
        return outResult->errorCode;
    }
    if (command->expectedRevision != 0 && command->expectedRevision != bridgeRevision) {
        outResult->errorCode = BROGUE_BRIDGE_STALE_REVISION;
        return outResult->errorCode;
    }
    if (command->type == BROGUE_COMMAND_ACTION) {
        action = command->action;
        if (action < 0 || action >= BROGUE_ACTION_COUNT) {
            outResult->errorCode = BROGUE_BRIDGE_INVALID_ACTION;
            return outResult->errorCode;
        }
    } else {
        commandItem = itemForIdentity(command->itemId);
        if (commandItem == NULL || !itemIsCarried(commandItem)) {
            outResult->errorCode = BROGUE_BRIDGE_ITEM_NOT_FOUND;
            return outResult->errorCode;
        }
        if ((command->type == BROGUE_COMMAND_EQUIP_ITEM
             || command->type == BROGUE_COMMAND_UNEQUIP_ITEM)
            && !(commandItem->category & (WEAPON | ARMOR | RING))) {
            outResult->errorCode = BROGUE_BRIDGE_INVALID_ACTION;
            return outResult->errorCode;
        }
        if (command->type == BROGUE_COMMAND_USE_STAFF || command->type == BROGUE_COMMAND_USE_WAND) {
            if (commandItem->category != (command->type == BROGUE_COMMAND_USE_STAFF ? STAFF : WAND)) {
                return outResult->errorCode = BROGUE_BRIDGE_INVALID_ACTION;
            }
            if (!coordinatesAreInMap(command->targetX, command->targetY)
                || (command->targetX == player.loc.x && command->targetY == player.loc.y)) {
                return outResult->errorCode = BROGUE_BRIDGE_OUT_OF_RANGE;
            }
        }
        if (command->type == BROGUE_COMMAND_THROW_ITEM
            && itemRequiresThrowConfirmation(commandItem)
            && !command->confirmed) {
            itemThrowConfirmationPrompt(commandItem, outResult->prompt, sizeof(outResult->prompt));
            outResult->errorCode = BROGUE_BRIDGE_CONFIRMATION_REQUIRED;
            return outResult->errorCode;
        }
        if (command->type == BROGUE_COMMAND_APPLY_ITEM) {
            char prompt[BROGUE_BRIDGE_MESSAGE_LENGTH];
            if (!(commandItem->category & (FOOD | POTION | SCROLL | CHARM))) {
                outResult->errorCode = BROGUE_BRIDGE_INVALID_ACTION;
                return outResult->errorCode;
            }
            if (itemApplyConfirmationPrompt(commandItem, prompt, sizeof(prompt))
                && !command->confirmed) {
                copyText(outResult->prompt, sizeof(outResult->prompt), prompt);
                outResult->errorCode = BROGUE_BRIDGE_CONFIRMATION_REQUIRED;
                return outResult->errorCode;
            }
            if (applySelectionType(commandItem) != BROGUE_SELECTION_NONE) {
                BrogueBridgeTurnResult choices = *outResult;
                populateApplyChoices(commandItem, &choices);
                if (choices.choiceCount > 0 && command->secondaryItemId == 0) {
                    *outResult = choices;
                    outResult->errorCode = BROGUE_BRIDGE_SELECTION_REQUIRED;
                    return outResult->errorCode;
                }
                if (command->secondaryItemId != 0) {
                    secondaryItem = itemForIdentity(command->secondaryItemId);
                    if (!validApplySelection(commandItem, secondaryItem)) {
                        outResult->errorCode = BROGUE_BRIDGE_INVALID_ACTION;
                        return outResult->errorCode;
                    }
                }
            }
        }
        if (command->type == BROGUE_COMMAND_THROW_ITEM
            && !coordinatesAreInMap(command->targetX, command->targetY)) {
            outResult->errorCode = BROGUE_BRIDGE_OUT_OF_RANGE;
            return outResult->errorCode;
        }
    }

    memcpy(&bridgePreviousState, &bridgeState, sizeof(bridgeState));
    outResult->playerBefore = bridgePreviousState.player;
    outResult->previousTurn = rogue.absoluteTurnNumber;
    oldAbsoluteTurn = rogue.absoluteTurnNumber;
    recordedEventCount = 0;
    recordedEventsTruncated = false;
    recordedPlayerFall = false;
    recordedPlayerFallSource = INVALID_POS;
    recordingActionEvents = true;
    beginConfirmationBroker(command->confirmed);

    switch (command->type) {
        case BROGUE_COMMAND_ACTION:
            if (action == BROGUE_ACTION_WAIT) {
                rogue.justRested = true;
                playerTurnEnded();
                accepted = true;
            } else {
                direction = actionDirection(action);
                if (direction == NO_DIRECTION) {
                    endConfirmationBroker();
                    recordingActionEvents = false;
                    outResult->errorCode = BROGUE_BRIDGE_INVALID_ACTION;
                    return outResult->errorCode;
                }
                accepted = playerMoves(direction);
            }
            break;
        case BROGUE_COMMAND_EQUIP_ITEM:
            equip(commandItem);
            accepted = rogue.weapon == commandItem
                && bridgePreviousState.player.equippedWeaponId != command->itemId;
            break;
        case BROGUE_COMMAND_UNEQUIP_ITEM:
            if (!(commandItem->flags & ITEM_EQUIPPED)) {
                accepted = false;
            } else {
                unequip(commandItem);
                accepted = !(commandItem->flags & ITEM_EQUIPPED);
            }
            break;
        case BROGUE_COMMAND_THROW_ITEM:
            accepted = throwItemAtTarget(commandItem,
                                         (pos){ (short) command->targetX, (short) command->targetY },
                                         false);
            break;
        case BROGUE_COMMAND_DROP_ITEM:
            drop(commandItem);
            accepted = !itemIsCarried(commandItem);
            break;
        case BROGUE_COMMAND_APPLY_ITEM:
            applyItemWithSelection(commandItem, secondaryItem);
            accepted = rogue.absoluteTurnNumber != oldAbsoluteTurn;
            break;
        case BROGUE_COMMAND_USE_STAFF:
        case BROGUE_COMMAND_USE_WAND:
            applyDeviceAtTarget(commandItem, (pos){ (short) command->targetX, (short) command->targetY });
            accepted = rogue.absoluteTurnNumber != oldAbsoluteTurn;
            break;
        default:
            endConfirmationBroker();
            recordingActionEvents = false;
            outResult->errorCode = BROGUE_BRIDGE_INVALID_ACTION;
            return outResult->errorCode;
    }

    endConfirmationBroker();
    recordingActionEvents = false;
    if (confirmationWasRequested) {
        /* Brogue's negative response path has cancelled the command without
         * consuming a turn. Do not advance the bridge revision or publish
         * transient cancellation messages; the frontend now owns the prompt. */
        copyText(outResult->prompt, sizeof(outResult->prompt), confirmationPrompt);
        outResult->errorCode = BROGUE_BRIDGE_CONFIRMATION_REQUIRED;
        return outResult->errorCode;
    }
    bridgeRevision++;
    beginIdentityCapture();
    result = captureState(&bridgeState);
    pruneIdentities();
    if (result != BROGUE_BRIDGE_OK) {
        outResult->errorCode = result;
        return result;
    }

    outResult->success = 1;
    /* playerMoves() reports physical tile displacement. Taking stairs is a
     * committed action that changes depth without setting playerMoved, so the
     * bridge must also recognize Brogue's authoritative depth transition. */
    outResult->actionAccepted = (accepted || bridgePreviousState.depth != bridgeState.depth) ? 1 : 0;
    outResult->consumedTurn = (rogue.absoluteTurnNumber != oldAbsoluteTurn) ? 1 : 0;
    outResult->currentTurn = rogue.absoluteTurnNumber;
    outResult->revision = bridgeRevision;
    outResult->playerAfter = bridgeState.player;
    if (bridgePreviousState.depth != bridgeState.depth) {
        buildEvents(&bridgePreviousState, &bridgeState, outResult);
    } else {
        appendRecordedEvents(outResult);
        buildEvents(&bridgePreviousState, &bridgeState, outResult);
    }
    return BROGUE_BRIDGE_OK;
}

BrogueBridgeResult brogue_bridge_perform_action(BrogueBridgeAction action,
                                                 BrogueBridgeTurnResult *outResult) {
    BrogueBridgeCommand command;
    memset(&command, 0, sizeof(command));
    command.apiVersion = BROGUE_BRIDGE_API_VERSION;
    command.type = BROGUE_COMMAND_ACTION;
    command.action = action;
    return brogue_bridge_perform_command(&command, outResult);
}

BrogueBridgeResult brogue_bridge_inspect_cell(int32_t x,
                                               int32_t y,
                                               BrogueBridgeLookResult *outResult) {
    pos target;
    creature *monst;
    item *theItem;
    char buffer[COLS * 100];
    char nameBuffer[COLS * 3];

    if (outResult == NULL) return BROGUE_BRIDGE_INVALID_STATE;
    memset(outResult, 0, sizeof(*outResult));
    outResult->apiVersion = BROGUE_BRIDGE_API_VERSION;
    outResult->revision = bridgeRevision;
    outResult->x = x;
    outResult->y = y;
    outResult->errorCode = BROGUE_BRIDGE_OK;
    if (!bridgeInitialized) return outResult->errorCode = BROGUE_BRIDGE_NOT_INITIALIZED;
    if (!bridgeGameStarted) return outResult->errorCode = BROGUE_BRIDGE_GAME_NOT_STARTED;
    if (!coordinatesAreInMap(x, y)) return outResult->errorCode = BROGUE_BRIDGE_OUT_OF_RANGE;

    target = (pos){ (short) x, (short) y };
    outResult->currentlyVisible = (pmapAt(target)->flags & ANY_KIND_OF_VISIBLE) != 0;
    outResult->known = (pmapAt(target)->flags & (DISCOVERED | MAGIC_MAPPED | ANY_KIND_OF_VISIBLE)) != 0;
    if (!outResult->known) {
        outResult->kind = BROGUE_LOOK_UNEXPLORED;
        copyText(outResult->title, sizeof(outResult->title), "Unexplored");
        copyText(outResult->summary, sizeof(outResult->summary), "You have not explored this location.");
        return BROGUE_BRIDGE_OK;
    }

    describeLocation(buffer, (short) x, (short) y);
    copyPlainText(outResult->summary, sizeof(outResult->summary), buffer);
    if (posEq(player.loc, target)) {
        outResult->kind = BROGUE_LOOK_PLAYER;
        copyText(outResult->title, sizeof(outResult->title), "You");
        return BROGUE_BRIDGE_OK;
    }

    monst = monsterAtLoc(target);
    if (monst != NULL && canSeeMonster(monst)) {
        outResult->kind = BROGUE_LOOK_CREATURE;
        outResult->creatureId = identityForCreature(monst);
        if (player.status[STATUS_HALLUCINATING] && !player.status[STATUS_TELEPATHIC]) {
            copyText(outResult->title, sizeof(outResult->title), "Something");
        } else {
            monsterName(nameBuffer, monst, true);
            copyPlainText(outResult->title, sizeof(outResult->title), nameBuffer);
            monsterDetails(buffer, monst);
            copyStyledLookText(outResult, buffer);
        }
        return BROGUE_BRIDGE_OK;
    }

    theItem = itemAtLoc(target);
    if (theItem != NULL && playerCanSeeOrSense(x, y)) {
        outResult->kind = BROGUE_LOOK_ITEM;
        outResult->itemId = identityForItem(theItem);
        if (player.status[STATUS_HALLUCINATING]) {
            copyText(outResult->title, sizeof(outResult->title), "Something");
        } else {
            itemName(theItem, nameBuffer, false, false, NULL);
            copyPlainText(outResult->title, sizeof(outResult->title), nameBuffer);
            itemDetails(buffer, theItem);
            copyStyledLookText(outResult, buffer);
        }
        return BROGUE_BRIDGE_OK;
    }

    outResult->kind = BROGUE_LOOK_TERRAIN;
    copyText(outResult->title, sizeof(outResult->title), "Terrain");
    return BROGUE_BRIDGE_OK;
}

BrogueBridgeResult brogue_bridge_preview_target(const BrogueBridgeTargetRequest *request,
                                               BrogueBridgeTargetPreview *outPreview) {
    item *theItem;
    pos path[MAX_BOLT_LENGTH];
    creature *targets[BROGUE_BRIDGE_MAX_CREATURES];
    short count, maxDistance;
    boolean truncated;
    int hazard;
    BrogueBridgeThrowPreview *aim;
    if (!outPreview) return BROGUE_BRIDGE_INVALID_STATE;
    memset(outPreview, 0, sizeof(*outPreview));
    aim = &outPreview->aim;
    aim->apiVersion = BROGUE_BRIDGE_API_VERSION;
    aim->revision = bridgeRevision;
    if (!request) return aim->errorCode = BROGUE_BRIDGE_INVALID_STATE;
    aim->itemId = request->itemId;
    aim->targetX = request->targetX;
    aim->targetY = request->targetY;
    outPreview->type = request->type;
    if (!bridgeInitialized) return aim->errorCode = BROGUE_BRIDGE_NOT_INITIALIZED;
    if (!bridgeGameStarted) return aim->errorCode = BROGUE_BRIDGE_GAME_NOT_STARTED;
    if (rogue.gameHasEnded) return aim->errorCode = BROGUE_BRIDGE_GAME_ENDED;
    if (request->apiVersion != BROGUE_BRIDGE_API_VERSION
        || (request->type != BROGUE_COMMAND_THROW_ITEM && request->type != BROGUE_COMMAND_USE_STAFF
            && request->type != BROGUE_COMMAND_USE_WAND)) return aim->errorCode = BROGUE_BRIDGE_INVALID_ACTION;
    if (request->expectedRevision && request->expectedRevision != bridgeRevision) return aim->errorCode = BROGUE_BRIDGE_STALE_REVISION;
    theItem = itemForIdentity(request->itemId);
    if (!theItem || !itemIsCarried(theItem)) return aim->errorCode = BROGUE_BRIDGE_ITEM_NOT_FOUND;
    boolean throwing = request->type == BROGUE_COMMAND_THROW_ITEM;
    if (!throwing && theItem->category != (request->type == BROGUE_COMMAND_USE_STAFF ? STAFF : WAND))
        return aim->errorCode = BROGUE_BRIDGE_INVALID_ACTION;
    outPreview->depth = rogue.depthLevel;
    outPreview->origin = (BrogueBridgePoint){player.loc.x, player.loc.y};
    if (!coordinatesAreInMap(request->targetX, request->targetY)) return aim->errorCode = BROGUE_BRIDGE_OUT_OF_RANGE;
    pos target = {(short)request->targetX, (short)request->targetY};
    aim->valid = !posEq(player.loc, target);
    count = previewItemTarget(theItem, throwing, target, path, &maxDistance, &outPreview->termination, &hazard);
    aim->maxDistance = maxDistance;
    outPreview->hasRange = maxDistance > 0;
    aim->pathCount = min(count, BROGUE_BRIDGE_MAX_PROJECTILE_PATH);
    outPreview->pathTruncated = count > BROGUE_BRIDGE_MAX_PROJECTILE_PATH;
    for (uint32_t i = 0; i < aim->pathCount; ++i) {
        aim->path[i] = (BrogueBridgePoint){path[i].x, path[i].y};
        if (posEq(path[i], target)) outPreview->reachesTarget = true;
    }
    if (throwing) itemThrowConfirmationPrompt(theItem, aim->message, sizeof(aim->message));
    else copyText(aim->message, sizeof(aim->message), targetHazardWarning(hazard));
    aim->requiresConfirmation = throwing ? itemRequiresThrowConfirmation(theItem) : hazard == 1;
    outPreview->certainDeath = hazard == 2;
    count = collectTargetCreatures(theItem, throwing, targets, BROGUE_BRIDGE_MAX_CREATURES, &truncated);
    outPreview->targetsTruncated = truncated;
    for (short i = 0; i < count; ++i) {
        uint64_t id = 0;
        // Lookup only: preview must never allocate an identity or mark it seen.
        for (uint32_t j = 0; j < creatureIdentityCount; ++j)
            if (creatureIdentities[j].pointer == targets[i]) { id = creatureIdentities[j].id; break; }
        if (!id) { outPreview->targetsTruncated = true; continue; }
        BrogueBridgeTargetCandidate *entry = &outPreview->targets[outPreview->targetCount++];
        entry->id = id;
        entry->location = (BrogueBridgePoint){targets[i]->loc.x, targets[i]->loc.y};
    }
    if (outPreview->targetCount) {
        uint32_t next = 0;
        for (uint32_t i = 0; i < outPreview->targetCount; ++i)
            if (outPreview->targets[i].location.x == target.x && outPreview->targets[i].location.y == target.y)
                { next = (i + 1) % outPreview->targetCount; break; }
        outPreview->nextTarget = outPreview->targets[next];
        outPreview->hasNextTarget = outPreview->nextTarget.location.x != target.x || outPreview->nextTarget.location.y != target.y;
    }
    return BROGUE_BRIDGE_OK;
}

/* Deprecated compatibility layouts; validation/calculation lives above. */
BrogueBridgeResult brogue_bridge_preview_throw(uint64_t itemId, int32_t x, int32_t y, BrogueBridgeThrowPreview *out) {
    BrogueBridgeTargetRequest request = {BROGUE_BRIDGE_API_VERSION, BROGUE_COMMAND_THROW_ITEM, 0, itemId, x, y};
    BrogueBridgeTargetPreview preview;
    if (!out) return BROGUE_BRIDGE_INVALID_STATE;
    BrogueBridgeResult result = brogue_bridge_preview_target(&request, &preview);
    *out = preview.aim;
    return result;
}
static BrogueBridgeResult previewLegacyDevice(uint64_t itemId, int32_t x, int32_t y,
                                             BrogueBridgeStaffPreview *out, BrogueBridgeCommandType type) {
    BrogueBridgeTargetRequest request = {BROGUE_BRIDGE_API_VERSION, type, 0, itemId, x, y};
    BrogueBridgeTargetPreview preview;
    if (!out) return BROGUE_BRIDGE_INVALID_STATE;
    memset(out, 0, sizeof(*out));
    BrogueBridgeResult result = brogue_bridge_preview_target(&request, &preview);
    out->aim = preview.aim;
    out->hasNextTarget = preview.hasNextTarget;
    out->nextTarget = preview.nextTarget.location;
    return result;
}
BrogueBridgeResult brogue_bridge_preview_staff(uint64_t itemId, int32_t x, int32_t y, BrogueBridgeStaffPreview *out) {
    return previewLegacyDevice(itemId, x, y, out, BROGUE_COMMAND_USE_STAFF);
}
BrogueBridgeResult brogue_bridge_preview_wand(uint64_t itemId, int32_t x, int32_t y, BrogueBridgeWandPreview *out) {
    return previewLegacyDevice(itemId, x, y, out, BROGUE_COMMAND_USE_WAND);
}

void brogue_bridge_shutdown(void) {
    if (bridgeGameStarted) {
        freeEverything();
        bridgeGameStarted = false;
    }
    memset(&bridgeState, 0, sizeof(bridgeState));
    memset(&bridgePreviousState, 0, sizeof(bridgePreviousState));
    memset(creatureIdentities, 0, sizeof(creatureIdentities));
    memset(itemIdentities, 0, sizeof(itemIdentities));
    creatureIdentityCount = 0;
    itemIdentityCount = 0;
    bridgeRevision = 0;
    bridgeNextEntityId = 2;
    eventSequence = 0;
    recordingActionEvents = false;
    recordedEventCount = 0;
    recordedEventsTruncated = false;
    endConfirmationBroker();
    confirmationWasRequested = false;
    confirmationPrompt[0] = '\0';
}

const char *brogue_bridge_result_name(BrogueBridgeResult result) {
    switch (result) {
        case BROGUE_BRIDGE_OK: return "OK";
        case BROGUE_BRIDGE_NOT_INITIALIZED: return "NOT_INITIALIZED";
        case BROGUE_BRIDGE_GAME_NOT_STARTED: return "GAME_NOT_STARTED";
        case BROGUE_BRIDGE_GAME_ENDED: return "GAME_ENDED";
        case BROGUE_BRIDGE_INVALID_ACTION: return "INVALID_ACTION";
        case BROGUE_BRIDGE_INVALID_STATE: return "INVALID_STATE";
        case BROGUE_BRIDGE_OUT_OF_RANGE: return "OUT_OF_RANGE";
        case BROGUE_BRIDGE_UNSUPPORTED: return "UNSUPPORTED";
        case BROGUE_BRIDGE_INTERNAL_BROGUE_ERROR: return "INTERNAL_BROGUE_ERROR";
        case BROGUE_BRIDGE_CAPACITY_EXCEEDED: return "CAPACITY_EXCEEDED";
        case BROGUE_BRIDGE_STALE_REVISION: return "STALE_REVISION";
        case BROGUE_BRIDGE_ITEM_NOT_FOUND: return "ITEM_NOT_FOUND";
        case BROGUE_BRIDGE_CONFIRMATION_REQUIRED: return "CONFIRMATION_REQUIRED";
        case BROGUE_BRIDGE_SELECTION_REQUIRED: return "SELECTION_REQUIRED";
        default: return "UNKNOWN";
    }
}

const char *brogue_bridge_action_name(BrogueBridgeAction action) {
    static const char *names[BROGUE_ACTION_COUNT] = {
        "MOVE_N", "MOVE_NE", "MOVE_E", "MOVE_SE", "MOVE_S", "MOVE_SW", "MOVE_W", "MOVE_NW", "WAIT"
    };
    if (action < 0 || action >= BROGUE_ACTION_COUNT) {
        return "INVALID_ACTION";
    }
    return names[action];
}

const char *brogue_bridge_event_name(BrogueBridgeEventType type) {
    static const char *names[] = {
        "NONE", "PLAYER_MOVED", "PLAYER_ACTION_BLOCKED", "CREATURE_SPAWNED",
        "CREATURE_MOVED", "CREATURE_REMOVED", "CREATURE_STATE_CHANGED",
        "CELL_TERRAIN_CHANGED", "PLAYER_HP_CHANGED", "PLAYER_STATUS_CHANGED",
        "MESSAGE", "LEVEL_CHANGE_REQUESTED", "ATTACK_ATTEMPTED",
        "ENTITY_DAMAGED", "ENTITY_DIED", "WEAPON_EQUIPPED", "WEAPON_UNEQUIPPED",
        "PROJECTILE_MOVED", "PROJECTILE_IMPACT", "ITEM_LANDED"
    };
    if (type < 0 || type > BROGUE_EVENT_ITEM_LANDED) {
        return "UNKNOWN";
    }
    return names[type];
}

const char *brogue_bridge_command_name(BrogueBridgeCommandType type) {
    static const char *names[BROGUE_COMMAND_COUNT] = {
        "ACTION", "EQUIP_ITEM", "UNEQUIP_ITEM", "THROW_ITEM", "DROP_ITEM", "APPLY_ITEM", "USE_STAFF", "USE_WAND"
    };
    if (type < 0 || type >= BROGUE_COMMAND_COUNT) return "INVALID_COMMAND";
    return names[type];
}
