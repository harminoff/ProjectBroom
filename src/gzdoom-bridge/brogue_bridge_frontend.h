#pragma once

struct event_t;
struct usercmd_t;

bool BrogueBridge_HandleInput(const event_t *event);
bool BrogueBridge_WantsSearchEscape(void);
void BrogueBridge_CancelSearchForUi(void);
bool BrogueBridge_OwnsPlayerPosition(void);
void BrogueBridge_PrepareTiccmd(usercmd_t *cmd);
void BrogueBridge_DrawHud(void);
void BrogueBridge_PrepareScene(void);
void BrogueBridge_Shutdown(void);

bool BrogueBridge_SaveOnClose();
void BrogueBridge_TickPersistence();
const char *BrogueBridge_MapOverride(const char *name);
void BrogueBridge_DrawPersistence();
bool BrogueBridge_ConfirmNewGame();
bool BrogueBridge_UsesNativeSaves();
