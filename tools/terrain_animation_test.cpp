#include "../src/gzdoom-bridge/terrain_animation.h"
#include <cassert>
int main() {
    TerrainTween t;
    t.Settle(0); t.Retarget(24,100,21);
    assert(t.Value(100)==0 && t.Value(121)==24 && !t.Active(121));
    const double pose=t.Value(107);
    t.Retarget(-8,107,21);
    assert(t.Value(107)==pose && t.Value(128)==-8);
    const auto start=t.start;
    t.Retarget(-8,110,21); // repeated target does not restart
    assert(t.start==start);
    t.Settle(8); assert(t.Value(0)==8 && !t.Active(0)); // Basic / attachment
    for (int i=0;i<1000;++i) {
        const double before=t.Value(i);
        t.Retarget(i%2 ? 1 : -1,i,12);
        assert(std::abs(t.Value(i)-before)<1e-12);
    }
    TerrainMotion m; m.liquidAlpha.Retarget(1,5,21);
    assert(m.Active(10) && !m.Active(26));
    m.sampledAt=11;
    // A skipped frame must still flush the final pose, even after all curves expire.
    assert(!m.Active(40) && m.Active(m.sampledAt));
    assert(m.liquidAlpha.Value(40)==1);
    m.sampledAt=40; assert(!m.Active(m.sampledAt));
}
