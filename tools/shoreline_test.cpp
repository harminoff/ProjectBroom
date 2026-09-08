#include "../src/gzdoom-bridge/shoreline.h"
#include <cassert>
#include <cstring>
#include <iostream>
#include <set>
#include <algorithm>
#include <cmath>
using Appearance=BrogueBridgeTerrainAppearance;
int main() {
    std::array<Appearance,2291> cells{};
    Appearance land{}; land.knowledge=BROGUE_TERRAIN_VISIBLE; land.structure=1;
    Appearance water=land; water.liquid=1; water.liquidKind=water.bedKind=BROGUE_LIQUID_SHALLOW_WATER;
    constexpr int key=10*79+10;
    std::set<unsigned> variants;
    for(unsigned mask=0;mask<256;++mask) {
        cells={}; cells[key]=water;
        for(int i=0;i<8;++i) if(mask&(1<<i)) cells[key+Shoreline::DY[i]*79+Shoreline::DX[i]]=land;
        const auto before=cells;
        const auto resolved=Shoreline::Resolve(cells,key);
        assert(std::memcmp(before.data(),cells.data(),sizeof(cells))==0);
        assert(resolved.water==Shoreline::Normalize(mask) && !resolved.ground);
        variants.insert(resolved.water);
        // Normalization preserves the distance to the union of wet/dry cells.
        for(int y=1;y<64;y+=5) for(int x=1;x<64;x+=5) {
            const double distances[]={double(y),64.-x,64.-y,double(x),
                std::hypot(64.-x,y),std::hypot(64.-x,64.-y),std::hypot(x,64.-y),std::hypot(x,y)};
            double expected=128,actual=128;
            for(int i=0;i<8;++i) { if(mask&(1<<i)) expected=std::min(expected,distances[i]);
                if(resolved.water&(1<<i)) actual=std::min(actual,distances[i]); }
            assert(expected==actual);
        }
    }
    assert(variants.size()==47);
    cells={}; cells[key]=water;
    cells[key+1]=land;
    assert(Shoreline::Resolve(cells,key).water==2);
    assert(Shoreline::Resolve(cells,key+1).ground==8);
    cells[key+1].knowledge=BROGUE_TERRAIN_UNKNOWN;
    assert(!Shoreline::Resolve(cells,key).water);
    cells[key+1]=land; cells[key].knowledge=BROGUE_TERRAIN_REMEMBERED;
    assert(Shoreline::Resolve(cells,key).water==2);
    cells[key].knowledge=BROGUE_TERRAIN_UNKNOWN;
    assert(!Shoreline::Resolve(cells,key+1).ground);
    cells[key]=water; cells[key].flags=BROGUE_APPEARANCE_FLOOD;
    assert(!Shoreline::Resolve(cells,key).water && !Shoreline::Resolve(cells,key+1).ground);
    cells[key+1].flags=BROGUE_APPEARANCE_WALL;
    assert(Shoreline::Resolve(cells,key).water==2);
    cells[key]=water; cells[key+1]=land; cells[key+1].flags=BROGUE_APPEARANCE_BRIDGE|BROGUE_APPEARANCE_HOLE;
    assert(Shoreline::Resolve(cells,key).water==2 && Shoreline::Resolve(cells,key+1).ground==8);
    cells[key+1].flags=BROGUE_APPEARANCE_HOLE;
    assert(!Shoreline::Resolve(cells,key).water);
    cells[key+1].flags=BROGUE_APPEARANCE_ICE;
    assert(!Shoreline::Resolve(cells,key).water);
    cells[key+1]=water; cells[key+1].liquidKind=BROGUE_LIQUID_DEEP_WATER;
    assert(!Shoreline::Resolve(cells,key).water); // No false bank inside water.
    cells[key+1].liquidKind=BROGUE_LIQUID_LAVA;
    assert(!Shoreline::Resolve(cells,key).water);
    for(int corner:{0,78,2212,2290}) {
        const auto changed=Shoreline::Affected({corner});
        assert(std::count(changed.begin(),changed.end(),true)==4);
    }
    const auto changed=Shoreline::Affected({key});
    assert(std::count(changed.begin(),changed.end(),true)==9);
    assert(changed[key-80] && changed[key+80]);
    std::cout<<"SHORELINE 256 masks, corner distances, privacy, height, deck, recovery dependencies passed\n";
}
