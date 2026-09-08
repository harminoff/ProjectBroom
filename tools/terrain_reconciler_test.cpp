#include "../src/gzdoom-bridge/terrain_reconciler.h"
#include <cassert>
#include <iostream>
#include <cstddef>
static_assert(BROGUE_BRIDGE_API_VERSION == 20);
static_assert(sizeof(BrogueBridgeTerrainAppearance) == 28);
static_assert(offsetof(BrogueBridgeCellState, appearance) == 84);
static_assert(sizeof(BrogueBridgeCellState) == 112);
int main() {
    static BrogueBridgeState state{};
    state.apiVersion = BROGUE_BRIDGE_API_VERSION;
    state.session = 2; state.revision = 10; state.depth = 1;
    state.width = 79; state.height = 29; state.cellCount = 2291;
    for (int i=0; i<2291; ++i) { state.cells[i].x = i%79; state.cells[i].y = i/79; }
    TerrainReconciler reconciler;
    TerrainReconciler::Batch batch;
    assert(reconciler.Prepare(state, 1, batch) == TerrainReconciler::Ready);
    assert(batch.initial && batch.changed.size() == 2291);
    reconciler.Commit(state);
    assert(reconciler.Prepare(state, 1, batch) == TerrainReconciler::Unchanged);
    state.revision = 20; // missed revisions, no events at all
    state.cells[80].appearance.flags = BROGUE_APPEARANCE_HOLE;
    assert(reconciler.Prepare(state, 1, batch) == TerrainReconciler::Ready);
    assert(batch.changed.size() == 1 && batch.boundaries.size() == 5);
    assert(reconciler.applied[80].flags == 0); // prepare is not commit
    reconciler.Commit(state);
    state.revision = 19;
    assert(reconciler.Prepare(state, 1, batch) == TerrainReconciler::Rejected);
    assert(reconciler.applied[80].flags == BROGUE_APPEARANCE_HOLE);
    state.revision = 21; state.cells[81].x = 0;
    assert(reconciler.Prepare(state, 1, batch) == TerrainReconciler::Rejected);
    state.cells[81].x = 2; state.cellCount = 1;
    assert(reconciler.Prepare(state, 1, batch) == TerrainReconciler::Rejected);
    state.cellCount = 2291; state.session = 1;
    assert(reconciler.Prepare(state, 1, batch) == TerrainReconciler::Rejected);
    state.session = 3;
    assert(reconciler.Prepare(state, 1, batch) == TerrainReconciler::Ready && batch.initial);
    reconciler.Commit(state);
    state.depth = 2;
    assert(reconciler.Prepare(state, 1, batch) == TerrainReconciler::Rejected);
    assert(reconciler.Prepare(state, 2, batch) == TerrainReconciler::Rejected);
    reconciler.Clear();
    assert(reconciler.Prepare(state, 2, batch) == TerrainReconciler::Ready && batch.initial);
    std::cout << "TERRAIN planner identity revision recovery atomicity passed\n";
}
