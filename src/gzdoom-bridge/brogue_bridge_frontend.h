#pragma once

struct event_t;
struct ticcmd_t;

bool BrogueBridge_HandleInput(const event_t *event);
void BrogueBridge_PrepareTiccmd(ticcmd_t *cmd);
void BrogueBridge_DrawHud(void);
void BrogueBridge_Shutdown(void);
