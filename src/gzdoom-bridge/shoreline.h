#pragma once
#include "../brogue-mapgen/src/brogue/BrogueBridge.h"
#include <array>
#include <vector>

// Copied appearance only: no pmap, gameplay depth/physics, events or RNG.
namespace Shoreline {
constexpr int DX[] = {0,1,0,-1,1,1,-1,-1};
constexpr int DY[] = {-1,0,1,0,-1,1,1,-1};
inline unsigned Normalize(unsigned mask) {
    // Cardinal half-planes already cover the adjacent corner quadrants.
    for (int i=0;i<4;++i) if (mask & ((1u<<i)|(1u<<((i+1)%4)))) mask &= ~(16u<<i);
    return mask;
}
inline bool Known(const BrogueBridgeTerrainAppearance &a) { return a.knowledge != BROGUE_TERRAIN_UNKNOWN; }
inline bool Water(const BrogueBridgeTerrainAppearance &a) {
    return Known(a) && a.liquid && (a.liquidKind==BROGUE_LIQUID_SHALLOW_WATER || a.liquidKind==BROGUE_LIQUID_DEEP_WATER);
}
inline bool Deck(const BrogueBridgeTerrainAppearance &a) { return a.flags & (BROGUE_APPEARANCE_BRIDGE|BROGUE_APPEARANCE_ICE); }
inline int WaterHeight(const BrogueBridgeTerrainAppearance &a) {
    return a.flags&BROGUE_APPEARANCE_FLOOD ? (a.liquidKind==BROGUE_LIQUID_DEEP_WATER ? 24 : 8) : 0;
}
inline bool Bank(const BrogueBridgeTerrainAppearance &a, int surface) {
    if (!Known(a)) return false;
    if (a.flags&BROGUE_APPEARANCE_WALL) return true;
    if (a.flags&BROGUE_APPEARANCE_ICE) return false;
    if (a.flags&BROGUE_APPEARANCE_BRIDGE) return surface==0;
    return !a.liquid && !(a.flags&BROGUE_APPEARANCE_HOLE) && surface==0;
}
struct Masks { unsigned water=0, ground=0; };
inline Masks Resolve(const std::array<BrogueBridgeTerrainAppearance, BROGUE_BRIDGE_MAX_CELLS> &cells, int key) {
    Masks out;
    const auto &a=cells[key];
    if (!Known(a)) return out;
    for(int i=0;i<8;++i) {
        const int x=key%79+DX[i], y=key/79+DY[i];
        if(x<0 || x>=79 || y<0 || y>=29) continue;
        const auto &b=cells[y*79+x];
        if(Water(a) && !Deck(a) && Bank(b,WaterHeight(a))) out.water|=1u<<i;
        if(!(a.flags&BROGUE_APPEARANCE_WALL) && Bank(a,0) && Water(b) && !Deck(b) && WaterHeight(b)==0) out.ground|=1u<<i;
    }
    out.water=Normalize(out.water); out.ground=Normalize(out.ground);
    return out;
}
// Includes corner dependencies, without broadening the geometry reconciler.
inline std::array<bool,BROGUE_BRIDGE_MAX_CELLS> Affected(const std::vector<int> &changed) {
    std::array<bool,BROGUE_BRIDGE_MAX_CELLS> result{};
    for(int key:changed) for(int dy=-1;dy<=1;++dy) for(int dx=-1;dx<=1;++dx) {
        const int x=key%79+dx,y=key/79+dy;
        if(x>=0 && x<79 && y>=0 && y<29) result[y*79+x]=true;
    }
    return result;
}
}
