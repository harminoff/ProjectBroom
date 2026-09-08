/*
 * Deterministic Brogue terrain export for the Brogue-to-GZDoom pipeline.
 *
 * This file intentionally consumes the existing initialized pmap/levels state
 * after startLevel(). It does not implement a second dungeon generator.
 */

#include "Rogue.h"
#include "GlobalsBase.h"
#include "Globals.h"
#include "TileTypeNames.generated.h"

#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define BROGUE_SOURCE_COMMIT "7f52dd93b7fa553dd6e354ccd44229a3c22d8a76"
#define BROGUE_SOURCE_REPOSITORY "https://github.com/tmewett/BrogueCE"

typedef struct sha256Context {
    uint32_t state[8];
    uint64_t bitLength;
    unsigned char buffer[64];
    size_t bufferLength;
} sha256Context;

static const uint32_t sha256RoundConstants[64] = {
    0x428a2f98u, 0x71374491u, 0xb5c0fbcfu, 0xe9b5dba5u,
    0x3956c25bu, 0x59f111f1u, 0x923f82a4u, 0xab1c5ed5u,
    0xd807aa98u, 0x12835b01u, 0x243185beu, 0x550c7dc3u,
    0x72be5d74u, 0x80deb1feu, 0x9bdc06a7u, 0xc19bf174u,
    0xe49b69c1u, 0xefbe4786u, 0x0fc19dc6u, 0x240ca1ccu,
    0x2de92c6fu, 0x4a7484aau, 0x5cb0a9dcu, 0x76f988dau,
    0x983e5152u, 0xa831c66du, 0xb00327c8u, 0xbf597fc7u,
    0xc6e00bf3u, 0xd5a79147u, 0x06ca6351u, 0x14292967u,
    0x27b70a85u, 0x2e1b2138u, 0x4d2c6dfcu, 0x53380d13u,
    0x650a7354u, 0x766a0abbu, 0x81c2c92eu, 0x92722c85u,
    0xa2bfe8a1u, 0xa81a664bu, 0xc24b8b70u, 0xc76c51a3u,
    0xd192e819u, 0xd6990624u, 0xf40e3585u, 0x106aa070u,
    0x19a4c116u, 0x1e376c08u, 0x2748774cu, 0x34b0bcb5u,
    0x391c0cb3u, 0x4ed8aa4au, 0x5b9cca4fu, 0x682e6ff3u,
    0x748f82eeu, 0x78a5636fu, 0x84c87814u, 0x8cc70208u,
    0x90befffau, 0xa4506cebu, 0xbef9a3f7u, 0xc67178f2u
};

static uint32_t sha256RotateRight(uint32_t value, unsigned int amount) {
    return (value >> amount) | (value << (32 - amount));
}

static void sha256Transform(sha256Context *context, const unsigned char block[64]) {
    uint32_t words[64];
    uint32_t a, b, c, d, e, f, g, h;
    uint32_t t1, t2;
    unsigned int i;

    for (i = 0; i < 16; i++) {
        words[i] = ((uint32_t) block[i * 4] << 24)
                 | ((uint32_t) block[i * 4 + 1] << 16)
                 | ((uint32_t) block[i * 4 + 2] << 8)
                 | (uint32_t) block[i * 4 + 3];
    }
    for (i = 16; i < 64; i++) {
        uint32_t s0 = sha256RotateRight(words[i - 15], 7)
                     ^ sha256RotateRight(words[i - 15], 18)
                     ^ (words[i - 15] >> 3);
        uint32_t s1 = sha256RotateRight(words[i - 2], 17)
                     ^ sha256RotateRight(words[i - 2], 19)
                     ^ (words[i - 2] >> 10);
        words[i] = words[i - 16] + s0 + words[i - 7] + s1;
    }

    a = context->state[0];
    b = context->state[1];
    c = context->state[2];
    d = context->state[3];
    e = context->state[4];
    f = context->state[5];
    g = context->state[6];
    h = context->state[7];

    for (i = 0; i < 64; i++) {
        uint32_t sigma1 = sha256RotateRight(e, 6) ^ sha256RotateRight(e, 11) ^ sha256RotateRight(e, 25);
        uint32_t choose = (e & f) ^ ((~e) & g);
        uint32_t sigma0 = sha256RotateRight(a, 2) ^ sha256RotateRight(a, 13) ^ sha256RotateRight(a, 22);
        uint32_t majority = (a & b) ^ (a & c) ^ (b & c);

        t1 = h + sigma1 + choose + sha256RoundConstants[i] + words[i];
        t2 = sigma0 + majority;
        h = g;
        g = f;
        f = e;
        e = d + t1;
        d = c;
        c = b;
        b = a;
        a = t1 + t2;
    }

    context->state[0] += a;
    context->state[1] += b;
    context->state[2] += c;
    context->state[3] += d;
    context->state[4] += e;
    context->state[5] += f;
    context->state[6] += g;
    context->state[7] += h;
}

static void sha256Initialize(sha256Context *context) {
    context->state[0] = 0x6a09e667u;
    context->state[1] = 0xbb67ae85u;
    context->state[2] = 0x3c6ef372u;
    context->state[3] = 0xa54ff53au;
    context->state[4] = 0x510e527fu;
    context->state[5] = 0x9b05688cu;
    context->state[6] = 0x1f83d9abu;
    context->state[7] = 0x5be0cd19u;
    context->bitLength = 0;
    context->bufferLength = 0;
}

static void sha256Update(sha256Context *context, const unsigned char *data, size_t length) {
    size_t index = 0;
    while (index < length) {
        size_t copyLength = min(sizeof(context->buffer) - context->bufferLength, length - index);
        memcpy(context->buffer + context->bufferLength, data + index, copyLength);
        context->bufferLength += copyLength;
        index += copyLength;
        if (context->bufferLength == sizeof(context->buffer)) {
            sha256Transform(context, context->buffer);
            context->bitLength += 512;
            context->bufferLength = 0;
        }
    }
}

static void sha256Finalize(sha256Context *context, unsigned char digest[32]) {
    unsigned int i;
    uint64_t totalBits = context->bitLength + ((uint64_t) context->bufferLength * 8);

    context->buffer[context->bufferLength++] = 0x80;
    while (context->bufferLength != 56) {
        if (context->bufferLength == 64) {
            sha256Transform(context, context->buffer);
            context->bufferLength = 0;
        }
        context->buffer[context->bufferLength++] = 0;
    }
    for (i = 0; i < 8; i++) {
        context->buffer[56 + i] = (unsigned char) (totalBits >> (56 - i * 8));
    }
    sha256Transform(context, context->buffer);

    for (i = 0; i < 8; i++) {
        digest[i * 4] = (unsigned char) (context->state[i] >> 24);
        digest[i * 4 + 1] = (unsigned char) (context->state[i] >> 16);
        digest[i * 4 + 2] = (unsigned char) (context->state[i] >> 8);
        digest[i * 4 + 3] = (unsigned char) context->state[i];
    }
}

typedef struct dungeonWriter {
    FILE *file;
    sha256Context hash;
    boolean hashingEnabled;
    boolean currentLevel;
} dungeonWriter;

static boolean writerBytes(dungeonWriter *writer, const char *bytes, size_t length) {
    if (fwrite(bytes, 1, length, writer->file) != length) {
        return false;
    }
    if (writer->hashingEnabled) {
        sha256Update(&writer->hash, (const unsigned char *) bytes, length);
    }
    return true;
}

static boolean writerPrintf(dungeonWriter *writer, const char *format, ...) {
    char buffer[8192];
    va_list arguments;
    int length;

    va_start(arguments, format);
    length = vsnprintf(buffer, sizeof(buffer), format, arguments);
    va_end(arguments);
    if (length < 0 || (size_t) length >= sizeof(buffer)) {
        return false;
    }
    return writerBytes(writer, buffer, (size_t) length);
}

static void setExportError(char *errorMessage, const char *message) {
    if (errorMessage) {
        strncpy(errorMessage, message, ERROR_MESSAGE_LENGTH);
        errorMessage[ERROR_MESSAGE_LENGTH - 1] = '\0';
    }
}

static boolean writeTileValue(dungeonWriter *writer, enum tileType tile) {
    if (tile < 0 || tile >= NUMBER_TILETYPES) {
        return false;
    }
    return writerPrintf(writer, "{\"id\":%d,\"symbol\":\"%s\"}",
                        (int) tile, brogueTileTypeNames[tile]);
}

static boolean writeCellLayer(dungeonWriter *writer, enum tileType tile) {
    if (!writeTileValue(writer, tile)) {
        return false;
    }
    return true;
}

static const char *jsonBoolean(boolean value) {
    return value ? "true" : "false";
}

static boolean writeRememberedAppearance(dungeonWriter *writer, const cellDisplayBuffer *appearance) {
    return writerPrintf(writer,
                        "{\"character\":%d,\"foreColorComponents\":[%d,%d,%d],\"backColorComponents\":[%d,%d,%d],\"opacity\":%d}",
                        (int) appearance->character,
                        (int) (unsigned char) appearance->foreColorComponents[0],
                        (int) (unsigned char) appearance->foreColorComponents[1],
                        (int) (unsigned char) appearance->foreColorComponents[2],
                        (int) (unsigned char) appearance->backColorComponents[0],
                        (int) (unsigned char) appearance->backColorComponents[1],
                        (int) (unsigned char) appearance->backColorComponents[2],
                        (int) (unsigned char) appearance->opacity);
}

static boolean writeCellSemantic(dungeonWriter *writer, const pcell *cell, pos loc) {
    unsigned long flags = terrainFlags(loc);
    unsigned long mechFlags = terrainMechFlags(loc);
    enum tileType dungeon = cell->layers[DUNGEON];
    enum tileType liquid = cell->layers[LIQUID];
    enum tileType surface = cell->layers[SURFACE];
    boolean isDoor = (dungeon == DOOR
                      || dungeon == SECRET_DOOR
                      || dungeon == LOCKED_DOOR
                      || dungeon == OPEN_IRON_DOOR_INERT
                      || dungeon == PORTCULLIS_CLOSED
                      || dungeon == PORTCULLIS_DORMANT
                      || dungeon == WOODEN_BARRICADE);
    boolean isChasm = (liquid == CHASM
                       || liquid == CHASM_EDGE
                       || liquid == MACHINE_COLLAPSE_EDGE_DORMANT
                       || liquid == MACHINE_COLLAPSE_EDGE_SPREADING
                       || liquid == CHASM_WITH_HIDDEN_BRIDGE
                       || liquid == CHASM_WITH_HIDDEN_BRIDGE_ACTIVE
                       || liquid == MACHINE_CHASM_EDGE);
    boolean isBridge = (liquid == BRIDGE
                        || liquid == BRIDGE_FALLING
                        || surface == BRIDGE_EDGE
                        || surface == STONE_BRIDGE);

    return writerPrintf(writer,
                        "{\"isSolid\":%s,\"isWalkable\":%s,\"isPathingBlocked\":%s,\"blocksVision\":%s,\"blocksDiagonalMovement\":%s,\"isDoor\":%s,\"isSecret\":%s,\"isLiquid\":%s,\"isDeepWater\":%s,\"isLava\":%s,\"isChasm\":%s,\"isBridge\":%s,\"isStairsUp\":%s,\"isStairsDown\":%s,\"isMachineTerrain\":%s}",
                        jsonBoolean((flags & T_OBSTRUCTS_PASSABILITY) != 0),
                        jsonBoolean((flags & T_OBSTRUCTS_PASSABILITY) == 0),
                        jsonBoolean((flags & T_PATHING_BLOCKER) != 0),
                        jsonBoolean((flags & T_OBSTRUCTS_VISION) != 0),
                        jsonBoolean((flags & T_OBSTRUCTS_DIAGONAL_MOVEMENT) != 0),
                        jsonBoolean(isDoor),
                        jsonBoolean((mechFlags & TM_IS_SECRET) != 0),
                        jsonBoolean(liquid != NOTHING),
                        jsonBoolean((flags & T_IS_DEEP_WATER) != 0),
                        jsonBoolean((flags & T_LAVA_INSTA_DEATH) != 0),
                        jsonBoolean(isChasm),
                        jsonBoolean(isBridge),
                        jsonBoolean(dungeon == UP_STAIRS || dungeon == DUNGEON_EXIT),
                        jsonBoolean(dungeon == DOWN_STAIRS || dungeon == DUNGEON_PORTAL),
                        jsonBoolean(cell->machineNumber != 0 || (cell->flags & IS_IN_MACHINE) != 0));
}

static boolean writeTerrainCatalog(dungeonWriter *writer) {
    int tile;
    if (!writerPrintf(writer, "\"terrainCatalog\":[")) {
        return false;
    }
    for (tile = 0; tile < NUMBER_TILETYPES; tile++) {
        if (tile > 0 && !writerPrintf(writer, ",")) {
            return false;
        }
        if (!writerPrintf(writer,
                         "{\"id\":%d,\"symbol\":\"%s\",\"drawPriority\":%d,\"flags\":%lu,\"mechFlags\":%lu,\"layerApplicability\":\"runtime\"}",
                         tile,
                         brogueTileTypeNames[tile],
                         tileCatalog[tile].drawPriority,
                         (unsigned long) tileCatalog[tile].flags,
                         (unsigned long) tileCatalog[tile].mechFlags)) {
            return false;
        }
    }
    return writerPrintf(writer, "],");
}

static boolean writeCell(dungeonWriter *writer, int x, int y) {
    pcell *cell = &pmap[x][y];
    pos loc = (pos) { .x = x, .y = y };

    if (writer->currentLevel && !writerPrintf(writer,
        "{\"currentlyVisible\":%s,\"discovered\":%s,",
        jsonBoolean((cell->flags & ANY_KIND_OF_VISIBLE) != 0), jsonBoolean((cell->flags & DISCOVERED) != 0))) return false;
    if (!writerPrintf(writer,
                      writer->currentLevel ? "\"x\":%d,\"y\":%d,\"layers\":{\"dungeon\":" : "{\"x\":%d,\"y\":%d,\"layers\":{\"dungeon\":",
                      x, y)
        || !writeCellLayer(writer, cell->layers[DUNGEON])
        || !writerPrintf(writer, ",\"liquid\":")
        || !writeCellLayer(writer, cell->layers[LIQUID])
        || !writerPrintf(writer, ",\"gas\":")
        || !writeCellLayer(writer, cell->layers[GAS])
        || !writerPrintf(writer, ",\"surface\":")
        || !writeCellLayer(writer, cell->layers[SURFACE])
        || !writerPrintf(writer,
                         "},\"flags\":%lu,\"terrainFlags\":%lu,\"terrainMechFlags\":%lu,\"volume\":%u,\"machine\":%u,\"exposedToFire\":%d,\"remembered\":{\"appearance\":",
                         (unsigned long) cell->flags,
                         (unsigned long) terrainFlags(loc),
                         (unsigned long) terrainMechFlags(loc),
                         (unsigned int) cell->volume,
                         (unsigned int) cell->machineNumber,
                         (int) cell->exposedToFire)
        || !writeRememberedAppearance(writer, &cell->rememberedAppearance)
        || !writerPrintf(writer,
                         ",\"itemCategory\":%d,\"itemKind\":%d,\"itemQuantity\":%d,\"itemOriginDepth\":%d,\"terrain\":%d,\"cellFlags\":%lu,\"terrainFlags\":%lu,\"tmFlags\":%lu},\"semantic\":",
                         (int) cell->rememberedItemCategory,
                         (int) cell->rememberedItemKind,
                         (int) cell->rememberedItemQuantity,
                         (int) cell->rememberedItemOriginDepth,
                         (int) cell->rememberedTerrain,
                         (unsigned long) cell->rememberedCellFlags,
                         (unsigned long) cell->rememberedTerrainFlags,
                         (unsigned long) cell->rememberedTMFlags)
        || !writeCellSemantic(writer, cell, loc)
        || !writerPrintf(writer, "}")) {
        return false;
    }
    return true;
}

static boolean writeLevel(dungeonWriter *writer, int depth) {
    int x, y;
    pos up = levels[depth - 1].upStairsLoc;
    pos down = levels[depth - 1].downStairsLoc;

    if (!writerPrintf(writer,
                     "{\"depth\":%d,\"levelSeed\":\"%llu\",\"upStairs\":{\"x\":%d,\"y\":%d},\"downStairs\":{\"x\":%d,\"y\":%d},\"cells\":[",
                     depth,
                     (unsigned long long) levels[depth - 1].levelSeed,
                     (int) up.x, (int) up.y, (int) down.x, (int) down.y)) {
        return false;
    }

    for (y = 0; y < DROWS; y++) {
        for (x = 0; x < DCOLS; x++) {
            if ((x != 0 || y != 0) && !writerPrintf(writer, ",")) {
                return false;
            }
            if (!writeCell(writer, x, y)) {
                return false;
            }
        }
    }
    return writerPrintf(writer, "],\"entities\":{\"items\":[],\"monsters\":[]}}");
}

int exportDungeonJson(uint64_t seed, unsigned int depthCount, const char *outputPath, char *errorMessage) {
    dungeonWriter writer;
    unsigned char digest[32];
    char digestHex[65];
    int depth;
    int i;
    boolean success = false;

    if (!outputPath || !outputPath[0]) {
        setExportError(errorMessage, "output path is empty");
        return 1;
    }
    if (seed == 0 || depthCount == 0 || depthCount > 40) {
        setExportError(errorMessage, "seed must be positive and depth count must be 1..40");
        return 1;
    }

    writer.file = fopen(outputPath, "wb");
    if (!writer.file) {
        setExportError(errorMessage, "could not open output path");
        return 1;
    }
    sha256Initialize(&writer.hash);
    writer.hashingEnabled = true;
    writer.currentLevel = false;

    initializeGameVariant();
    rogue.nextGame = NG_NOTHING;
    rogue.nextGamePath[0] = '\0';
    currentFilePath[0] = '\0';
    randomNumbersGenerated = 0;
    rogue.playbackMode = false;
    rogue.playbackFastForward = false;
    rogue.playbackBetweenTurns = false;
    rogue.playbackOmniscience = true;
    initializeRogue(seed);

    success = writerPrintf(&writer,
                           "{\"schemaVersion\":1,\"source\":{\"repository\":\"%s\",\"commit\":\"%s\",\"variant\":\"Brogue\",\"version\":\"%s\",\"dungeonVersion\":\"%s\"},\"seed\":\"%llu\",\"dimensions\":{\"width\":%d,\"height\":%d},",
                           BROGUE_SOURCE_REPOSITORY,
                           BROGUE_SOURCE_COMMIT,
                           gameConst->versionString,
                           gameConst->dungeonVersionString,
                           (unsigned long long) seed,
                           DCOLS,
                           DROWS)
          && writeTerrainCatalog(&writer)
          && writerPrintf(&writer, "\"levels\":[");

    if (success) {
        for (depth = 1; depth <= (int) depthCount; depth++) {
            rogue.depthLevel = depth;
            startLevel(depth == 1 ? 1 : depth - 1, 1);
            if (depth > 1 && !writerPrintf(&writer, ",")) {
                success = false;
                break;
            }
            if (!writeLevel(&writer, depth)) {
                success = false;
                break;
            }
        }
    }

    if (success) {
        if (!writerPrintf(&writer, "],\"sha256\":\"")) {
            success = false;
        } else {
            writer.hashingEnabled = false;
            sha256Finalize(&writer.hash, digest);
            for (i = 0; i < 32; i++) {
                sprintf(digestHex + i * 2, "%02x", digest[i]);
            }
            digestHex[64] = '\0';
            if (!writerPrintf(&writer, "%s\"}\n", digestHex)) {
                success = false;
            }
        }
    }

    if (fclose(writer.file) != 0) {
        success = false;
    }
    freeEverything();

    if (!success) {
        remove(outputPath);
        setExportError(errorMessage, "failed while writing deterministic JSON");
        return 1;
    }
    return 0;
}

/* Pure projection of the active level. Never initialize, move or simulate here. */
int exportCurrentLevelJson(const char *outputPath, char *errorMessage) {
    dungeonWriter writer;
    unsigned char digest[32];
    char digestHex[65];
    int i;
    boolean success;
    if (!levels || !outputPath || !outputPath[0]) {
        setExportError(errorMessage, "no active level or empty output path");
        return 1;
    }
    writer.file = openBrogueFile(outputPath, "wb");
    if (!writer.file) {
        setExportError(errorMessage, "could not open current level output");
        return 1;
    }
    sha256Initialize(&writer.hash);
    writer.hashingEnabled = true;
    writer.currentLevel = true;
    success = writerPrintf(&writer,
                           "{\"schemaVersion\":1,\"currentLevel\":true,\"source\":{\"repository\":\"%s\",\"commit\":\"%s\",\"variant\":\"Brogue\",\"version\":\"%s\",\"dungeonVersion\":\"%s\"},\"seed\":\"%llu\",\"dimensions\":{\"width\":%d,\"height\":%d},",
                           BROGUE_SOURCE_REPOSITORY,
                           BROGUE_SOURCE_COMMIT,
                           gameConst->versionString,
                           gameConst->dungeonVersionString,
                           (unsigned long long) rogue.seed,
                           DCOLS,
                           DROWS)
          && writeTerrainCatalog(&writer)
          && writerPrintf(&writer, "\"levels\":[");

    if (success) success = writeLevel(&writer, rogue.depthLevel);
    if (success) {
        if (!writerPrintf(&writer, "],\"sha256\":\"")) {
            success = false;
        } else {
            writer.hashingEnabled = false;
            sha256Finalize(&writer.hash, digest);
            for (i = 0; i < 32; i++) {
                sprintf(digestHex + i * 2, "%02x", digest[i]);
            }
            digestHex[64] = '\0';
            if (!writerPrintf(&writer, "%s\"}\n", digestHex)) {
                success = false;
            }
        }
    }

    if (fclose(writer.file) != 0) {
        success = false;
    }

    if (!success) setExportError(errorMessage, "failed to write current level");
    return success ? 0 : 1;
}
