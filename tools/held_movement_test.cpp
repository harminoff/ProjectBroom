#include "../src/gzdoom-bridge/held_movement.h"
#include <cassert>

int main() {
    HeldMovement hold;
    assert(!hold.ready(1000, false));
    hold.press(1000);
    assert(hold.ready(1000, false));
    hold.completed(1020); // bridge call took 20ms
    hold.press(1100); // duplicate down must not reset repeat delay
    assert(!hold.ready(1519, false));
    assert(hold.ready(1520, false));
    assert(!hold.ready(2000, true)); // visible animation or queued input
    hold.completed(2000);
    assert(!hold.ready(2099, false));
    assert(hold.ready(2100, false));
    hold.completed(9000); // stalled render: one step, never a catch-up burst
    assert(!hold.ready(9000, false));
    hold.cancel();
    assert(!hold.ready(10000, false));
    hold.press(10000);
    assert(!hold.ready(10000, true));
    hold.cancel(); // release while animation blocks the first step
    assert(!hold.ready(11000, false));
    hold.press(12000);
    hold.completed(12000);
    assert(!hold.ready(12100, false)); // a fresh hold gets the initial delay
    assert(hold.ready(12500, false));
}
