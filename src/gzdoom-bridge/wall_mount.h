// Presentation-only cardinal mount selection. No simulation or engine dependencies.
#pragma once
namespace WallMount {
inline constexpr int DX[4]={-1,1,0,0};
inline constexpr int DY[4]={0,0,-1,1};
inline constexpr double YAW[4]={180,0,90,270};
// Only known exposed faces participate. Prefer the face toward the copied
// player cell; retain an equal-scoring previous face across corner ties.
// Camera panning and an attack target never change the wall mount.
inline int Face(bool visible, bool knownWall, const bool exposed[4], int previous,
                int playerDX, int playerDY) {
    if (!visible || !knownWall) return -1;
    int best = -1, score = -2147483647;
    if (previous >= 0 && previous < 4 && exposed[previous]) {
        best = previous; score = DX[previous]*playerDX + DY[previous]*playerDY;
    }
    for (int i=0;i<4;++i) if (exposed[i]) {
        const int candidate = DX[i]*playerDX + DY[i]*playerDY;
        if (candidate > score) { best=i; score=candidate; }
    }
    return best;
}
}
