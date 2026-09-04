# Project Broom GZDoom integration

This directory contains Project Broom-owned C++ source compiled into the pinned
GZDoom frontend. The small upstream integration seam is recorded in
`patches/gzdoom-project-broom.patch` and applied by `scripts/bootstrap-dev.ps1`.

Do not place Brogue gameplay rules here. This layer translates input to
semantic bridge actions, copies returned state into presentation proxies, and
draws frontend UI. `BrogueBridge.h` remains frontend-neutral and no Brogue
internal pointer crosses this boundary.
