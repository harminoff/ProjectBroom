#ifndef BROGUE_BRIDGE_INTERNAL_H
#define BROGUE_BRIDGE_INTERNAL_H

#include "Rogue.h"
#include "BrogueBridge.h"
    boolean itemThrowConfirmationPrompt(const item *theItem, char *buffer, size_t size);
    short collectTargetCreatures(const item *theItem, boolean throwing, creature **targets, short capacity, boolean *truncated);
    short previewItemTarget(item *theItem, boolean throwing, pos targetLoc, pos *path, short *maxDistance, BrogueBridgeGuideTermination *reason, int *hazard);
    const char *targetHazardWarning(int hazard);


/* Internal observation hooks. They never resolve gameplay; they only record
 * events while a bridge action is active. Normal Brogue builds link the same
 * adapter and these functions are inert outside a bridge session. */
void brogue_bridge_note_movement(creature *mover, pos from, pos to);
void brogue_bridge_note_player_fall(pos source);
void brogue_bridge_note_terrain_activity(short x, short y, unsigned int activity);
void brogue_bridge_note_attack(creature *attacker, creature *defender, boolean lungeAttack);
void brogue_bridge_note_damage(creature *attacker, creature *defender, short amount, boolean lethal);
void brogue_bridge_note_death(creature *decedent, boolean administrativeDeath);
void brogue_bridge_prepare_thrown_item(item *source, item *projectile, boolean preserveIdentity);
void brogue_bridge_note_projectile_step(item *projectile, pos from, pos to);
void brogue_bridge_note_projectile_impact(item *projectile, pos loc);
void brogue_bridge_note_item_landed(item *projectile, pos loc);

/* Called by Brogue's normal confirm() function. When a bridge command is
 * active, this supplies an already-approved response or captures Brogue's
 * exact prompt and returns a safe negative response so the command can pause. */
boolean brogue_bridge_intercept_confirmation(const char *prompt, boolean *answer);

/* Captures Brogue's own terminal result text after gameOver() has computed it.
 * The adapter copies these values; no Brogue-owned pointer crosses the API. */
void brogue_bridge_note_game_over(const char *cause,
                                  const char *summary,
                                  signed long score,
                                  boolean playerQuit);

#endif
