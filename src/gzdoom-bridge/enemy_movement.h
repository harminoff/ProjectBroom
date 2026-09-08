#pragma once
#include <algorithm>
#include <cmath>

namespace EnemyMovement {
// Presentation frustum only. Brogue visibility and movement remain authoritative.
inline bool InView(double forward, double right, double up, double horizontal,
                   double vertical, double radius = 24)
{
    return forward + radius > 0 && std::abs(right) <= forward * horizontal + radius
        && std::abs(up) <= forward * vertical + radius;
}
inline int Duration(bool observed, double distance, int tileTics)
{
    if (!observed || distance <= 0 || distance > 64 * std::sqrt(2.0) + .01) return 0;
    return int(std::ceil(std::clamp(tileTics, 5, 70) * distance / 64));
}
inline double Remaining(int movement, int total, int pulse, int death)
{
    return std::max({total > 0 ? double(movement) / total : 0.0, pulse / 5.0, death / 7.0});
}
}
