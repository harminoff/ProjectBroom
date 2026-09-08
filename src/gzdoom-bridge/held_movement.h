#pragma once
#include <cstdint>

// Input pacing only: no direction, map, action result, or gameplay state.
struct HeldMovement
{
    bool held = false;
    bool first = true;
    uint64_t next = 0;

    void press(uint64_t now) {
        if (held) return;
        held = true; first = true; next = now;
    }
    void cancel() { held = false; }
    bool ready(uint64_t now, bool busy) const {
        return held && !busy && now >= next;
    }
    void completed(uint64_t now) {
        // Schedule from completion, not the old deadline. Never catch up.
        const uint64_t delay = first ? 500 : 100;
        first = false;
        next = now + delay;
    }
};
