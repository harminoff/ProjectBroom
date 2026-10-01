#pragma once

#include <cmath>

namespace HudProjection {

struct ViewCoordinates {
    double forward;
    double right;
    double up;
};

// UZDoom yaw zero faces +X and increasing yaw turns toward +Y. Screen-right
// is the clockwise perpendicular (sin(yaw), -cos(yaw)).
inline ViewCoordinates ToView(double dx, double dy, double dz, double yaw, double pitch)
{
    const double flat = dx * std::cos(yaw) + dy * std::sin(yaw);
    return {
        flat * std::cos(pitch) - dz * std::sin(pitch),
        dx * std::sin(yaw) - dy * std::cos(yaw),
        flat * std::sin(pitch) + dz * std::cos(pitch),
    };
}

inline bool Inside(double forward, double x, double y,
                   double left, double top, double right, double bottom,
                   double projectedRadius = 0)
{
    return forward > 1
        && x >= left - projectedRadius && x <= right + projectedRadius
        && y >= top - projectedRadius && y <= bottom + projectedRadius;
}

} // namespace HudProjection
