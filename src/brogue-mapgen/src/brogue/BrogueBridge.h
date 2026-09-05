/*
 * Brogue CE -> frontend bridge contract.
 *
 * This header deliberately contains no Brogue implementation types.  The
 * implementation may use pcell/creature internally, but consumers receive
 * copied, fixed-width state only.
 */
#ifndef BROGUE_BRIDGE_H
#define BROGUE_BRIDGE_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define BROGUE_BRIDGE_API_VERSION 15u
#define BROGUE_BRIDGE_MAX_CELLS 2291u
#define BROGUE_BRIDGE_MAX_CREATURES 1024u
#define BROGUE_BRIDGE_MAX_ITEMS 1024u
#define BROGUE_BRIDGE_MAX_EVENTS 256u
#define BROGUE_BRIDGE_MAX_MESSAGES 8u
#define BROGUE_BRIDGE_MESSAGE_LENGTH 256u
#define BROGUE_BRIDGE_MONSTER_NAME_LENGTH 64u
#define BROGUE_BRIDGE_MONSTER_SYMBOL_LENGTH 48u
#define BROGUE_BRIDGE_ITEM_NAME_LENGTH 96u
#define BROGUE_BRIDGE_ITEM_DETAIL_LENGTH 384u
#define BROGUE_BRIDGE_LOOK_TITLE_LENGTH 128u
#define BROGUE_BRIDGE_LOOK_DETAIL_LENGTH 8192u
#define BROGUE_BRIDGE_MAX_LOOK_COLOR_SPANS 128u
#define BROGUE_BRIDGE_MAX_PROJECTILE_PATH 128u
#define BROGUE_BRIDGE_MAX_MONSTER_KINDS 128u
#define BROGUE_BRIDGE_MAX_ITEM_CHOICES 26u
#define BROGUE_BRIDGE_GAME_OVER_CAUSE_LENGTH 128u
#define BROGUE_BRIDGE_GAME_OVER_SUMMARY_LENGTH 256u
#define BROGUE_BRIDGE_PLAYER_ENTITY_ID UINT64_C(1)

typedef enum BrogueBridgeResult {
    BROGUE_BRIDGE_OK = 0,
    BROGUE_BRIDGE_NOT_INITIALIZED,
    BROGUE_BRIDGE_GAME_NOT_STARTED,
    BROGUE_BRIDGE_GAME_ENDED,
    BROGUE_BRIDGE_INVALID_ACTION,
    BROGUE_BRIDGE_INVALID_STATE,
    BROGUE_BRIDGE_OUT_OF_RANGE,
    BROGUE_BRIDGE_UNSUPPORTED,
    BROGUE_BRIDGE_INTERNAL_BROGUE_ERROR,
    BROGUE_BRIDGE_CAPACITY_EXCEEDED,
    BROGUE_BRIDGE_STALE_REVISION,
    BROGUE_BRIDGE_ITEM_NOT_FOUND,
    BROGUE_BRIDGE_CONFIRMATION_REQUIRED,
    BROGUE_BRIDGE_SELECTION_REQUIRED
} BrogueBridgeResult;

/* These are player intents, not keyboard scan codes. */
typedef enum BrogueBridgeAction {
    BROGUE_ACTION_MOVE_N = 0,
    BROGUE_ACTION_MOVE_NE,
    BROGUE_ACTION_MOVE_E,
    BROGUE_ACTION_MOVE_SE,
    BROGUE_ACTION_MOVE_S,
    BROGUE_ACTION_MOVE_SW,
    BROGUE_ACTION_MOVE_W,
    BROGUE_ACTION_MOVE_NW,
    BROGUE_ACTION_WAIT,
    BROGUE_ACTION_COUNT
} BrogueBridgeAction;

typedef enum BrogueBridgeCommandType {
    BROGUE_COMMAND_ACTION = 0,
    BROGUE_COMMAND_EQUIP_ITEM,
    BROGUE_COMMAND_UNEQUIP_ITEM,
    BROGUE_COMMAND_THROW_ITEM,
    BROGUE_COMMAND_DROP_ITEM,
    BROGUE_COMMAND_APPLY_ITEM,
    BROGUE_COMMAND_USE_STAFF,
    BROGUE_COMMAND_USE_WAND,
    BROGUE_COMMAND_COUNT
} BrogueBridgeCommandType;

typedef enum BrogueBridgeItemActionFlags {
    BROGUE_ITEM_ACTION_NONE = 0,
    BROGUE_ITEM_ACTION_EQUIP = 1u << 0,
    BROGUE_ITEM_ACTION_UNEQUIP = 1u << 1,
    BROGUE_ITEM_ACTION_DROP = 1u << 2,
    BROGUE_ITEM_ACTION_THROW = 1u << 3,
    BROGUE_ITEM_ACTION_APPLY = 1u << 4,
    BROGUE_ITEM_ACTION_TARGET_STAFF = 1u << 5,
    BROGUE_ITEM_ACTION_TARGET_WAND = 1u << 6
} BrogueBridgeItemActionFlags;

typedef enum BrogueBridgeSelectionType {
    BROGUE_SELECTION_NONE = 0,
    BROGUE_SELECTION_IDENTIFY_ITEM,
    BROGUE_SELECTION_ENCHANT_ITEM
} BrogueBridgeSelectionType;

typedef enum BrogueBridgeEventType {
    BROGUE_EVENT_NONE = 0,
    BROGUE_EVENT_PLAYER_MOVED,
    BROGUE_EVENT_PLAYER_ACTION_BLOCKED,
    BROGUE_EVENT_CREATURE_SPAWNED,
    BROGUE_EVENT_CREATURE_MOVED,
    BROGUE_EVENT_CREATURE_REMOVED,
    BROGUE_EVENT_CREATURE_STATE_CHANGED,
    BROGUE_EVENT_CELL_TERRAIN_CHANGED,
    BROGUE_EVENT_PLAYER_HP_CHANGED,
    BROGUE_EVENT_PLAYER_STATUS_CHANGED,
    BROGUE_EVENT_MESSAGE,
    BROGUE_EVENT_LEVEL_CHANGE_REQUESTED,
    BROGUE_EVENT_ATTACK_ATTEMPTED,
    BROGUE_EVENT_ENTITY_DAMAGED,
    BROGUE_EVENT_ENTITY_DIED,
    BROGUE_EVENT_WEAPON_EQUIPPED,
    BROGUE_EVENT_WEAPON_UNEQUIPPED,
    BROGUE_EVENT_PROJECTILE_MOVED,
    BROGUE_EVENT_PROJECTILE_IMPACT,
    BROGUE_EVENT_ITEM_LANDED
} BrogueBridgeEventType;

typedef enum BrogueBridgeVisibility {
    BROGUE_VISIBILITY_HIDDEN = 0,
    BROGUE_VISIBILITY_SENSED,
    BROGUE_VISIBILITY_DIRECT
} BrogueBridgeVisibility;

typedef enum BrogueBridgeGameOutcome {
    BROGUE_GAME_OUTCOME_NONE = 0,
    BROGUE_GAME_OUTCOME_DEATH,
    BROGUE_GAME_OUTCOME_QUIT,
    BROGUE_GAME_OUTCOME_VICTORY,
    BROGUE_GAME_OUTCOME_SUPER_VICTORY
} BrogueBridgeGameOutcome;

typedef struct BrogueBridgeGameResult {
    BrogueBridgeGameOutcome outcome;
    int64_t score;
    int32_t depth;
    int32_t deepestDepth;
    uint64_t turn;
    char cause[BROGUE_BRIDGE_GAME_OVER_CAUSE_LENGTH];
    char summary[BROGUE_BRIDGE_GAME_OVER_SUMMARY_LENGTH];
} BrogueBridgeGameResult;

typedef enum BrogueBridgeEventFlags {
    BROGUE_EVENT_FLAG_NONE = 0,
    BROGUE_EVENT_FLAG_LUNGE = 1u << 0,
    BROGUE_EVENT_FLAG_LETHAL = 1u << 1,
    BROGUE_EVENT_FLAG_ADMINISTRATIVE = 1u << 2,
    BROGUE_EVENT_FLAG_ATTACK_EXTEND = 1u << 3,
    BROGUE_EVENT_FLAG_ATTACK_PENETRATE = 1u << 4,
    BROGUE_EVENT_FLAG_ATTACK_SWEEP = 1u << 5,
    BROGUE_EVENT_FLAG_ATTACK_STAGGER = 1u << 6,
    BROGUE_EVENT_FLAG_ATTACK_PASS = 1u << 7,
    BROGUE_EVENT_FLAG_ATTACK_QUICK = 1u << 8,
    /* The level change was caused by entering T_AUTO_DESCENT terrain. For
     * this event, fromX/fromY identify the source hole and toX/toY identify
     * Brogue's authoritative landing cell on the destination depth. */
    BROGUE_EVENT_FLAG_LEVEL_FALL = 1u << 9
} BrogueBridgeEventFlags;

typedef struct BrogueBridgePlayerState {
    int32_t x;
    int32_t y;
    int32_t hp;
    int32_t maxHp;
    int32_t depth;
    uint64_t turn;
    uint64_t absoluteTurn;
    uint64_t statusFlags;
    uint64_t equippedWeaponId;
    uint64_t equippedArmorId;
    uint64_t equippedLeftRingId;
    uint64_t equippedRightRingId;
    int32_t armor;
    int32_t strength;
    int32_t nutrition;
    int32_t maxNutrition;
    int32_t stealthRange;
    uint64_t gold;
    uint8_t alive;
    uint8_t gameInProgress;
    uint8_t gameHasEnded;
} BrogueBridgePlayerState;

typedef struct BrogueBridgeCreatureState {
    uint64_t id;
    int32_t kind;
    int32_t presentationKind;
    int32_t x;
    int32_t y;
    int32_t hp;
    int32_t maxHp;
    int32_t state;
    int32_t mode;
    uint64_t behaviorFlags;
    uint64_t abilityFlags;
    uint64_t bookkeepingFlags;
    uint64_t statusFlags;
    int32_t mutationIndex;
    uint8_t wasNegated;
    BrogueBridgeVisibility visibility;
    uint8_t isAlly;
    uint8_t isLarge;
    uint8_t visible;
    uint8_t alive;
} BrogueBridgeCreatureState;

typedef struct BrogueBridgeMonsterKindInfo {
    int32_t kind;
    char symbol[BROGUE_BRIDGE_MONSTER_SYMBOL_LENGTH];
    char name[BROGUE_BRIDGE_MONSTER_NAME_LENGTH];
    int32_t displayGlyph;
    int32_t colorRed;
    int32_t colorGreen;
    int32_t colorBlue;
    int32_t colorRedRand;
    int32_t colorGreenRand;
    int32_t colorBlueRand;
    int32_t colorRand;
    uint8_t colorDances;
    int32_t maxHp;
    int32_t intrinsicLightType;
    uint8_t isLarge;
    uint64_t behaviorFlags;
    uint64_t abilityFlags;
} BrogueBridgeMonsterKindInfo;

typedef struct BrogueBridgeMonsterCatalog {
    uint32_t apiVersion;
    uint32_t count;
    BrogueBridgeMonsterKindInfo kinds[BROGUE_BRIDGE_MAX_MONSTER_KINDS];
} BrogueBridgeMonsterCatalog;

typedef struct BrogueBridgeItemState {
    uint64_t id;
    int32_t category;
    int32_t kind;
    int32_t x;
    int32_t y;
    int32_t quantity;
    uint64_t flags;
    int32_t damageLower;
    int32_t damageUpper;
    int32_t damageClump;
    int32_t strengthRequired;
    int32_t enchantment;
    uint8_t carried;
    uint8_t visible;
    uint8_t kindKnown;
    uint8_t equipped;
    uint8_t enchantmentKnown;
    uint8_t runicKnown;
    uint8_t cursedKnown;
    uint8_t inventoryLetter;
    uint8_t inventoryOrder;
    uint8_t equipmentSlot;
    uint32_t actionFlags;
    char displayName[BROGUE_BRIDGE_ITEM_NAME_LENGTH];
    char detailText[BROGUE_BRIDGE_ITEM_DETAIL_LENGTH];
} BrogueBridgeItemState;

typedef struct BrogueBridgePoint {
    int32_t x;
    int32_t y;
} BrogueBridgePoint;

typedef struct BrogueBridgeCommand {
    uint32_t apiVersion;
    BrogueBridgeCommandType type;
    BrogueBridgeAction action;
    uint64_t expectedRevision;
    uint64_t itemId;
    uint64_t secondaryItemId;
    int32_t targetX;
    int32_t targetY;
    /* Number of sequential Brogue confirmation prompts already approved for
     * this exact command/revision. Most commands need zero or one. */
    uint8_t confirmed;
} BrogueBridgeCommand;

typedef struct BrogueBridgeThrowPreview {
    uint32_t apiVersion;
    uint64_t revision;
    uint64_t itemId;
    int32_t targetX;
    int32_t targetY;
    int32_t maxDistance;
    uint8_t valid;
    uint8_t requiresConfirmation;
    uint32_t pathCount;
    BrogueBridgePoint path[BROGUE_BRIDGE_MAX_PROJECTILE_PATH];
    char message[BROGUE_BRIDGE_MESSAGE_LENGTH];
    BrogueBridgeResult errorCode;
} BrogueBridgeThrowPreview;

/* A knowledge-limited aiming guide, not a prediction of bolt outcomes or
 * reflections. Confirmations are returned by perform_command, before use. */
typedef struct BrogueBridgeStaffPreview {
    BrogueBridgeThrowPreview aim;
    uint8_t hasNextTarget;
    BrogueBridgePoint nextTarget;
} BrogueBridgeStaffPreview;

/* Wands share the device aiming layout; their range remains Brogue-owned. */
typedef BrogueBridgeStaffPreview BrogueBridgeWandPreview;

typedef enum BrogueBridgeLookKind {
    BROGUE_LOOK_UNEXPLORED = 0,
    BROGUE_LOOK_TERRAIN,
    BROGUE_LOOK_PLAYER,
    BROGUE_LOOK_CREATURE,
    BROGUE_LOOK_ITEM
} BrogueBridgeLookKind;

typedef struct BrogueBridgeTextColorSpan {
    uint32_t offset;
    uint32_t length;
    uint8_t red;
    uint8_t green;
    uint8_t blue;
} BrogueBridgeTextColorSpan;

typedef struct BrogueBridgeLookResult {
    uint32_t apiVersion;
    uint64_t revision;
    int32_t x;
    int32_t y;
    BrogueBridgeLookKind kind;
    uint64_t creatureId;
    uint64_t itemId;
    uint8_t known;
    uint8_t currentlyVisible;
    char title[BROGUE_BRIDGE_LOOK_TITLE_LENGTH];
    char summary[BROGUE_BRIDGE_MESSAGE_LENGTH];
    char detail[BROGUE_BRIDGE_LOOK_DETAIL_LENGTH];
    uint32_t detailColorSpanCount;
    BrogueBridgeTextColorSpan detailColorSpans[BROGUE_BRIDGE_MAX_LOOK_COLOR_SPANS];
    BrogueBridgeResult errorCode;
} BrogueBridgeLookResult;

typedef struct BrogueBridgeCellState {
    int32_t x;
    int32_t y;
    int16_t layers[4];
    uint64_t cellFlags;
    uint64_t terrainFlags;
    uint64_t mechanicalFlags;
    uint16_t volume;
    uint8_t machineNumber;
    int16_t exposedToFire;
    uint8_t isSolid;
    uint8_t isWalkable;
    uint8_t blocksVision;
    uint8_t blocksDiagonalMovement;
    uint8_t isDoor;
    uint8_t isSecret;
    uint8_t isLiquid;
    uint8_t isDeepWater;
    uint8_t isMud;
    uint8_t isLava;
    uint8_t isFire;
    uint8_t isGas;
    uint8_t isChasm;
    uint8_t isBridge;
    uint8_t isStairsUp;
    uint8_t isStairsDown;
    uint8_t discovered;
    uint8_t currentlyVisible;
    uint8_t magicMapped;
    uint32_t displayCodepoint;
    uint8_t foregroundRed;
    uint8_t foregroundGreen;
    uint8_t foregroundBlue;
    uint8_t backgroundRed;
    uint8_t backgroundGreen;
    uint8_t backgroundBlue;
} BrogueBridgeCellState;

typedef struct BrogueBridgeEvent {
    uint64_t sequence;
    BrogueBridgeEventType type;
    int32_t x;
    int32_t y;
    int32_t fromX;
    int32_t fromY;
    int32_t toX;
    int32_t toY;
    uint64_t entityId;
    uint64_t sourceEntityId;
    uint64_t targetEntityId;
    uint64_t itemId;
    int32_t itemCategory;
    int32_t itemKind;
    int32_t amount;
    uint32_t eventFlags;
    int32_t beforeDungeon;
    int32_t afterDungeon;
    uint64_t beforeCellFlags;
    uint64_t afterCellFlags;
    uint64_t beforeTerrainFlags;
    uint64_t afterTerrainFlags;
    uint64_t beforeMechanicalFlags;
    uint64_t afterMechanicalFlags;
    char text[BROGUE_BRIDGE_MESSAGE_LENGTH];
} BrogueBridgeEvent;

typedef struct BrogueBridgeState {
    uint32_t apiVersion;
    uint64_t revision;
    uint64_t gameSeed;
    uint64_t levelSeed;
    uint64_t stateHash;
    uint64_t presentationHash;
    int32_t depth;
    int32_t width;
    int32_t height;
    uint64_t turn;
    uint64_t absoluteTurn;
    BrogueBridgePlayerState player;
    BrogueBridgeGameResult gameResult;
    int32_t upStairsX;
    int32_t upStairsY;
    int32_t downStairsX;
    int32_t downStairsY;
    uint32_t cellCount;
    BrogueBridgeCellState cells[BROGUE_BRIDGE_MAX_CELLS];
    uint32_t creatureCount;
    BrogueBridgeCreatureState creatures[BROGUE_BRIDGE_MAX_CREATURES];
    uint32_t itemCount;
    BrogueBridgeItemState items[BROGUE_BRIDGE_MAX_ITEMS];
    uint32_t messageCount;
    char messages[BROGUE_BRIDGE_MAX_MESSAGES][BROGUE_BRIDGE_MESSAGE_LENGTH];
} BrogueBridgeState;

typedef struct BrogueBridgeTurnResult {
    uint32_t apiVersion;
    uint8_t success;
    uint8_t actionAccepted;
    uint8_t consumedTurn;
    BrogueBridgeAction action;
    BrogueBridgeCommandType commandType;
    uint64_t itemId;
    uint64_t previousTurn;
    uint64_t currentTurn;
    uint64_t revision;
    BrogueBridgePlayerState playerBefore;
    BrogueBridgePlayerState playerAfter;
    uint32_t eventCount;
    uint8_t eventsTruncated;
    BrogueBridgeEvent events[BROGUE_BRIDGE_MAX_EVENTS];
    BrogueBridgeSelectionType selectionType;
    uint32_t choiceCount;
    uint64_t choiceItemIds[BROGUE_BRIDGE_MAX_ITEM_CHOICES];
    char prompt[BROGUE_BRIDGE_MESSAGE_LENGTH];
    BrogueBridgeResult errorCode;
} BrogueBridgeTurnResult;

BrogueBridgeResult brogue_bridge_initialize(void);
BrogueBridgeResult brogue_bridge_start_game(uint64_t gameSeed);
BrogueBridgeResult brogue_bridge_get_state(BrogueBridgeState *outState);
BrogueBridgeResult brogue_bridge_get_monster_catalog(BrogueBridgeMonsterCatalog *outCatalog);
BrogueBridgeResult brogue_bridge_perform_action(BrogueBridgeAction action,
                                                 BrogueBridgeTurnResult *outResult);
BrogueBridgeResult brogue_bridge_perform_command(const BrogueBridgeCommand *command,
                                                  BrogueBridgeTurnResult *outResult);
BrogueBridgeResult brogue_bridge_preview_throw(uint64_t itemId,
                                                int32_t targetX,
                                                int32_t targetY,
                                                BrogueBridgeThrowPreview *outPreview);
BrogueBridgeResult brogue_bridge_inspect_cell(int32_t x,
                                               int32_t y,
                                               BrogueBridgeLookResult *outResult);
BrogueBridgeResult brogue_bridge_preview_staff(uint64_t itemId, int32_t targetX,
                                                int32_t targetY, BrogueBridgeStaffPreview *outPreview);
BrogueBridgeResult brogue_bridge_preview_wand(uint64_t itemId, int32_t targetX,
                                               int32_t targetY, BrogueBridgeWandPreview *outPreview);
void brogue_bridge_shutdown(void);

const char *brogue_bridge_result_name(BrogueBridgeResult result);
const char *brogue_bridge_action_name(BrogueBridgeAction action);
const char *brogue_bridge_event_name(BrogueBridgeEventType type);
const char *brogue_bridge_command_name(BrogueBridgeCommandType type);

#ifdef __cplusplus
}
#endif

#endif
