#pragma once
#include "../brogue-mapgen/src/brogue/BrogueBridge.h"
#include <array>
#include <cstring>
#include <vector>

// Engine-independent transaction planner, shared by runtime and headless tests.
// Events never enter the correctness path. Commit only after renderer success.
class TerrainReconciler {
public:
    enum Result { Rejected, Unchanged, Ready };
    struct Batch {
        bool initial = false;
        std::vector<int> changed, boundaries;
    };
    uint64_t session = 0, revision = 0;
    int depth = 0;
    std::array<BrogueBridgeTerrainAppearance, BROGUE_BRIDGE_MAX_CELLS> applied{};
    void Clear() { session = revision = 0; depth = 0; applied = {}; }
    Result Prepare(const BrogueBridgeState &state, int levelDepth, Batch &batch) const {
        batch = {};
        if (state.apiVersion != BROGUE_BRIDGE_API_VERSION || !state.session || !state.revision
            || state.depth != levelDepth || state.width != 79 || state.height != 29
            || state.cellCount != BROGUE_BRIDGE_MAX_CELLS) return Rejected;
        if (session && (state.session < session || (state.session == session && state.revision < revision))) return Rejected;
        if (session == state.session && depth && depth != state.depth) return Rejected; // detach/bind required
        for (int i = 0; i < BROGUE_BRIDGE_MAX_CELLS; ++i)
            if (state.cells[i].x != i % 79 || state.cells[i].y != i / 79) return Rejected;
        if (state.session == session && state.revision == revision) return Unchanged;
        batch.initial = state.session != session || !depth;
        std::array<bool, BROGUE_BRIDGE_MAX_CELLS> affected{};
        for (int i = 0; i < BROGUE_BRIDGE_MAX_CELLS; ++i) {
            if (batch.initial || std::memcmp(&applied[i], &state.cells[i].appearance, sizeof(applied[i]))) {
                batch.changed.push_back(i);
                affected[i] = true;
                if (i % 79) affected[i-1] = true;
                if (i % 79 < 78) affected[i+1] = true;
                if (i >= 79) affected[i-79] = true;
                if (i < 2291-79) affected[i+79] = true;
            }
        }
        for (int i = 0; i < 2291; ++i) if (affected[i]) batch.boundaries.push_back(i);
        return Ready;
    }
    void Commit(const BrogueBridgeState &state) {
        session = state.session; revision = state.revision; depth = state.depth;
        for (int i = 0; i < 2291; ++i) applied[i] = state.cells[i].appearance;
    }
};
