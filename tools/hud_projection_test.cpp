#include "../src/gzdoom-bridge/hud_projection.h"

#include <cassert>
#include <cmath>

int main()
{
    using HudProjection::Inside;
    using HudProjection::ToView;
    constexpr double halfPi = 1.5707963267948966;

    // Yaw zero faces east: map north is screen-left and south is screen-right.
    auto east = ToView(64, 0, 0, 0, 0);
    auto north = ToView(0, 64, 0, 0, 0);
    auto south = ToView(0, -64, 0, 0, 0);
    assert(east.forward > 0 && std::abs(east.right) < 0.001);
    assert(north.right < 0);
    assert(south.right > 0);

    // Facing north: east is screen-right and west is screen-left.
    auto northFacingEast = ToView(64, 0, 0, halfPi, 0);
    auto northFacingWest = ToView(-64, 0, 0, halfPi, 0);
    assert(northFacingEast.right > 0);
    assert(northFacingWest.right < 0);

    assert(Inside(64, 500, 300, 200, 30, 900, 650));
    assert(!Inside(64, 150, 300, 200, 30, 900, 650));
    assert(Inside(64, 185, 300, 200, 30, 900, 650, 24));
    assert(!Inside(-1, 500, 300, 200, 30, 900, 650, 24));
}
