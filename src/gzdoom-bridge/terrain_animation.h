#pragma once
#include <algorithm>
#include <cmath>

// Cosmetic time only. No simulation, event queue, engine types or RNG.
struct TerrainTween {
    double from = 0, target = 0, start = 0, duration = 0;
    double Progress(double now) const {
        return duration <= 0 ? 1 : std::clamp((now-start)/duration, 0.0, 1.0);
    }
    double Value(double now) const {
        const double t = Progress(now), eased = t*t*(3-2*t);
        return from + (target-from)*eased;
    }
    bool Active(double now) const { return Progress(now) < 1; }
    void Settle(double value) { from = target = value; duration = 0; }
    void Retarget(double value, double now, double tics, bool force = false) {
        if (!force && value == target) return;
        from = Value(now); target = value; start = now; duration = tics;
    }
};

struct TerrainMotion {
    bool dirty = false;
    double sampledAt = 0; // Last rendered sample, not necessarily the preceding engine tic.
    TerrainTween liquidHeight, liquidAlpha, deckAlpha, gas, fire, mechanism;
    TerrainTween gasR, gasG, gasB;
    TerrainTween lever, plate, plant;
    double activityStart = -1000, revealStart = -1000;
    unsigned liquidTile = 0, deckTile = 0, gasTile = 0;
    bool Active(double now) const {
        return liquidHeight.Active(now) || liquidAlpha.Active(now) || deckAlpha.Active(now)
            || gas.Active(now) || fire.Active(now) || mechanism.Active(now)
            || gasR.Active(now) || gasG.Active(now) || gasB.Active(now)
            || lever.Active(now) || plate.Active(now) || plant.Active(now)
            || now-activityStart < 12 || now-revealStart < 21;
    }
};
