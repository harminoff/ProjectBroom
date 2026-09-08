/* Shared, synchronous native naming and equipment continuations.
 * Extracted from Items.c (Brian Walker; GNU AGPL v3 or later).
 * Each position executes once; answers resume the retained native frame.
 */
#include "ItemCommandFrame.h"
#include "GlobalsBase.h"
#include "Globals.h"

enum { ITEM_START, ITEM_SELECTED, ITEM_INSCRIPTION_ANSWER, ITEM_INSCRIPTION_TEXT,
       ITEM_KIND_TEXT, ITEM_RELABEL_TEXT, ITEM_RING_REPLACEMENT, ITEM_FINISHED };

static void finishItemFrame(nativeItemCommandFrame *frame) {
    frame->position = ITEM_FINISHED;
    frame->promptKind = NATIVE_ITEM_COMPLETE;
}

static void requestItemText(nativeItemCommandFrame *frame, boolean inscribing) {
    frame->promptKind = NATIVE_ITEM_TEXT;
    frame->escapeMeansNo = false;
    frame->position = inscribing ? ITEM_INSCRIPTION_TEXT : ITEM_KIND_TEXT;
    frame->nativeTextLength = 29;
    if (inscribing) {
        char name[COLS * 3], oldInscription[COLS];
        strcpy(oldInscription, frame->selected->inscription);
        frame->selected->inscription[0] = '\0';
        itemName(frame->selected, name, true, true, NULL);
        strcpy(frame->selected->inscription, oldInscription);
        sprintf(frame->prompt, "inscribe: %s \"", name);
        frame->nativeTextLength = min(29, DCOLS - strLenWithoutEscapes(frame->prompt) - 1);
    } else strcpy(frame->prompt, "call them: \"");
    /* getInputTextString reserves the one-byte closing quote. */
    frame->textLimit = min(frame->nativeTextLength,
                          COLS - mapToWindowX(strLenWithoutEscapes(frame->prompt))) - 1;
}

static void recordItemText(nativeItemCommandFrame *frame, const char *text) {
    frame->recording[frame->recordingCount] = '\0';
    strcat((char *)frame->recording, text);
    recordKeystrokeSequence(frame->recording);
    recordKeystroke(RETURN_KEY, false, false);
}

static void requestKindText(nativeItemCommandFrame *frame) {
    item *selected = frame->selected;
    itemTable *table = tableForItemCategory(selected->category);
    if (table && !table[selected->kind].identified) requestItemText(frame, false);
    else {
        message("you already know what that is.", 0);
        finishItemFrame(frame);
    }
}

static void finishEquipment(nativeItemCommandFrame *frame) {
    item *selected = frame->selected;
    if (selected->flags & ITEM_EQUIPPED) {
        confirmMessages(); message("already equipped.", 0); finishItemFrame(frame); return;
    }
    if (selected->category & (WEAPON|ARMOR))
        frame->replacement = selected->category & WEAPON ? rogue.weapon : rogue.armor;
    if (equipItem(selected, false, frame->replacement)) {
        frame->recording[frame->recordingCount] = 0;
        recordKeystrokeSequence(frame->recording);
        rogue.swappedOut = frame->replacement;
        rogue.swappedIn = rogue.swappedOut ? selected : NULL;
        playerTurnEnded();
    }
    finishItemFrame(frame);
}

static void requestEquipment(nativeItemCommandFrame *frame) {
    item *selected = frame->selected;
    if (!(selected->category & (WEAPON|ARMOR|RING))) {
        confirmMessages(); message("You can't equip that.", 0); finishItemFrame(frame); return;
    }
    if (selected->category & RING) {
        if (selected->flags & ITEM_EQUIPPED) {
            confirmMessages(); message("you are already wearing that ring.", 0); finishItemFrame(frame); return;
        }
        if (rogue.ringLeft && rogue.ringRight) {
            confirmMessages();
            frame->category = RING;
            frame->requiredFlags = ITEM_EQUIPPED;
            frame->forbiddenFlags = 0;
            frame->allowInventoryActions = true;
            frame->position = ITEM_RING_REPLACEMENT;
            frame->promptKind = NATIVE_ITEM_CHOICE;
            strcpy(frame->prompt, "You are already wearing two rings; remove which first?");
            return;
        }
    }
    finishEquipment(frame);
}

static void finishRemoval(nativeItemCommandFrame *frame) {
    char buf[COLS * 3], name[COLS * 3];
    item *selected = frame->selected;
    if (!(selected->flags & ITEM_EQUIPPED)) {
        itemName(selected, name, false, false, NULL);
        sprintf(buf, "your %s %s not equipped.", name, selected->quantity == 1 ? "was" : "were");
        confirmMessages(); messageWithColor(buf, &itemMessageColor, 0);
    } else if (unequipItem(selected, false)) {
        frame->recording[frame->recordingCount] = 0;
        recordKeystrokeSequence(frame->recording);
        itemName(selected, name, true, true, NULL);
        if (strLenWithoutEscapes(name) > 52) itemName(selected, name, false, true, NULL);
        confirmMessages();
        sprintf(buf, "you are no longer %s %s.", selected->category & WEAPON ? "wielding" : "wearing", name);
        messageWithColor(buf, &itemMessageColor, 0);
        playerTurnEnded();
    }
    finishItemFrame(frame);
}

static boolean canDrop(void) {
    if (cellHasTerrainFlag(player.loc, T_OBSTRUCTS_ITEMS)) return false;
    return true;
}

static void finishDrop(nativeItemCommandFrame *frame) {
    char buf[COLS * 3], name[COLS * 3];
    item *selected = frame->selected;
    if ((selected->flags & ITEM_EQUIPPED) && (selected->flags & ITEM_CURSED)) {
        itemName(selected, name, false, false, NULL);
        sprintf(buf, "you can't; your %s appears to be cursed.", name);
        confirmMessages(); messageWithColor(buf, &itemMessageColor, 0);
    } else if (canDrop()) {
        frame->recording[frame->recordingCount] = 0;
        recordKeystrokeSequence(frame->recording);
        if (selected->flags & ITEM_EQUIPPED) unequipItem(selected, false);
        selected = dropItem(selected);
        selected->flags |= ITEM_PLAYER_AVOIDS;
        itemName(selected, name, true, true, NULL);
        sprintf(buf, "You dropped %s.", name);
        messageWithColor(buf, &itemMessageColor, 0);
        playerTurnEnded();
    } else { confirmMessages(); message("There is already something there.", 0); }
    finishItemFrame(frame);
}

static void advanceSelectedItem(nativeItemCommandFrame *frame) {
    item *selected = frame->selected;
    if (!selected) { finishItemFrame(frame); return; }
    frame->recording[frame->recordingCount++] = selected->inventoryLetter;
    if (frame->command == NATIVE_ITEM_EQUIP) { requestEquipment(frame); return; }
    if (frame->command == NATIVE_ITEM_REMOVE) { finishRemoval(frame); return; }
    if (frame->command == NATIVE_ITEM_DROP) { finishDrop(frame); return; }
    if (frame->command == NATIVE_ITEM_RELABEL) {
        frame->position = ITEM_RELABEL_TEXT;
        frame->promptKind = NATIVE_ITEM_TEXT;
        frame->relabelLetter = true;
        frame->textLimit = frame->nativeTextLength = 1;
        strcpy(frame->prompt, "New letter? (a-z)");
        return;
    }
    confirmMessages();
    if ((selected->flags & ITEM_IDENTIFIED) || selected->category & (WEAPON|ARMOR|CHARM|FOOD|GOLD|AMULET|GEM)) {
        if (selected->category & (WEAPON|ARMOR|CHARM|STAFF|WAND|RING)) requestItemText(frame, true);
        else { message("you already know what that is.", 0); finishItemFrame(frame); }
        return;
    }
    if (selected->category & (WEAPON|ARMOR|STAFF|WAND|RING)) {
        if (tableForItemCategory(selected->category)[selected->kind].identified) requestItemText(frame, true);
        else {
            frame->position = ITEM_INSCRIPTION_ANSWER;
            frame->promptKind = NATIVE_ITEM_CONFIRMATION;
            frame->escapeMeansNo = true;
            strcpy(frame->prompt, "Inscribe this particular item instead of all similar items?");
        }
        return;
    }
    requestKindText(frame);
}

void beginNativeItemCommand(nativeItemCommandFrame *frame, nativeItemCommandKind command, item *selected) {
    memset(frame, 0, sizeof(*frame));
    frame->command = command;
    frame->selected = selected;
    static const unsigned char keys[] = {CALL_KEY, RELABEL_KEY, EQUIP_KEY, UNEQUIP_KEY, DROP_KEY};
    frame->recording[frame->recordingCount++] = keys[command];
    if (command == NATIVE_ITEM_RELABEL && !KEYBOARD_LABELS && !rogue.playbackMode) {
        finishItemFrame(frame);
        return;
    }
    if (!selected) {
        if (command == NATIVE_ITEM_CALL) {
            /* Preserve the native selection flags and their restoration point. */
            for (item *it = packItems->nextItem; it; it = it->nextItem) {
                if ((it->category & (POTION|SCROLL)) && tableForItemCategory(it->category)[it->kind].identified)
                    it->flags &= ~ITEM_CAN_BE_IDENTIFIED;
                else it->flags |= ITEM_CAN_BE_IDENTIFIED;
            }
            frame->category = WEAPON|ARMOR|SCROLL|RING|POTION|STAFF|WAND|CHARM;
            frame->requiredFlags = ITEM_CAN_BE_IDENTIFIED;
            strcpy(frame->prompt, KEYBOARD_LABELS ? "Call what? (a-z, shift for more info; or <esc> to cancel)" : "Call what?");
        } else if (command == NATIVE_ITEM_EQUIP) {
            frame->category = WEAPON|ARMOR|RING;
            frame->forbiddenFlags = ITEM_EQUIPPED;
            strcpy(frame->prompt, KEYBOARD_LABELS ? "Equip what? (a-z, shift for more info; or <esc> to cancel)" : "Equip what?");
        } else if (command == NATIVE_ITEM_REMOVE) {
            frame->category = ALL_ITEMS;
            frame->requiredFlags = ITEM_EQUIPPED;
            strcpy(frame->prompt, KEYBOARD_LABELS ? "Remove (unequip) what? (a-z or <esc> to cancel)" : "Remove (unequip) what?");
        } else if (command == NATIVE_ITEM_DROP) {
            frame->category = ALL_ITEMS;
            strcpy(frame->prompt, KEYBOARD_LABELS ? "Drop what? (a-z, shift for more info; or <esc> to cancel)" : "Drop what?");
        } else {
            frame->category = ALL_ITEMS;
            strcpy(frame->prompt, KEYBOARD_LABELS ? "Relabel what? (a-z, shift for more info; or <esc> to cancel)" : "Relabel what?");
        }
        frame->allowInventoryActions = true;
        frame->promptKind = NATIVE_ITEM_CHOICE;
        frame->position = ITEM_SELECTED;
    } else advanceSelectedItem(frame);
}

boolean stepNativeItemCommand(nativeItemCommandFrame *frame, const nativeItemAnswer *answer) {
    char buf[COLS * 3], name[COLS * 3];
    item *selected = frame->selected;
    if (!answer || frame->position == ITEM_FINISHED) return false;
    switch (frame->position) {
        case ITEM_RING_REPLACEMENT:
            if (answer->kind != NATIVE_ITEM_ANSWER_CHOICE && answer->kind != NATIVE_ITEM_ANSWER_ESCAPE) return false;
            frame->replacement = answer->kind == NATIVE_ITEM_ANSWER_ESCAPE ? NULL : answer->selected;
            if (!frame->replacement || frame->replacement->category != RING || !(frame->replacement->flags & ITEM_EQUIPPED)) {
                if (frame->replacement) message("Invalid entry.", 0);
                finishItemFrame(frame);
            } else {
                frame->recording[frame->recordingCount++] = frame->replacement->inventoryLetter;
                finishEquipment(frame);
            }
            return true;
        case ITEM_SELECTED:
            if (answer->kind != NATIVE_ITEM_ANSWER_CHOICE && answer->kind != NATIVE_ITEM_ANSWER_ESCAPE) return false;
            if (frame->command == NATIVE_ITEM_CALL) updateIdentifiableItems();
            frame->selected = answer->kind == NATIVE_ITEM_ANSWER_ESCAPE ? NULL : answer->selected;
            advanceSelectedItem(frame);
            return true;
        case ITEM_INSCRIPTION_ANSWER:
            if (answer->kind == NATIVE_ITEM_ANSWER_YES) {
                frame->recording[frame->recordingCount++] = 'y';
                requestItemText(frame, true);
            } else if (answer->kind == NATIVE_ITEM_ANSWER_NO || answer->kind == NATIVE_ITEM_ANSWER_ESCAPE) {
                frame->recording[frame->recordingCount++] = 'n';
                requestKindText(frame);
            } else return false;
            return true;
        case ITEM_INSCRIPTION_TEXT:
        case ITEM_KIND_TEXT:
            if (answer->kind == NATIVE_ITEM_ANSWER_ESCAPE) {
                if (frame->position == ITEM_INSCRIPTION_TEXT) confirmMessages();
                finishItemFrame(frame);
                return true;
            }
            if (answer->kind != NATIVE_ITEM_ANSWER_TEXT) return false;
            if (!memchr(answer->text, 0, sizeof(answer->text)) || strlen(answer->text) > (size_t)frame->textLimit) return false;
            for (const unsigned char *p = (const unsigned char *)answer->text; *p; ++p)
                if (*p < ' ' || *p > '~') return false;
            if (frame->position == ITEM_INSCRIPTION_TEXT) {
                strcpy(selected->inscription, answer->text);
                confirmMessages();
                itemName(selected, name, true, true, NULL);
                sprintf(buf, "%s %s.", selected->quantity > 1 ? "they're" : "it's", name);
                messageWithColor(buf, &itemMessageColor, 0);
                recordItemText(frame, selected->inscription);
            } else {
                recordItemText(frame, answer->text);
                itemTable *table = tableForItemCategory(selected->category);
                strcpy(table[selected->kind].callTitle, answer->text);
                table[selected->kind].called = answer->text[0] != '\0';
                confirmMessages();
                itemName(selected, buf, false, true, NULL);
                messageWithColor(buf, &itemMessageColor, 0);
            }
            finishItemFrame(frame);
            return true;
        case ITEM_RELABEL_TEXT: {
            if (answer->kind == NATIVE_ITEM_ANSWER_ESCAPE) { finishItemFrame(frame); return true; }
            if (answer->kind != NATIVE_ITEM_ANSWER_TEXT || !answer->text[0] || answer->text[1]) return false;
            char label = answer->text[0];
            if (label >= 'A' && label <= 'Z') label += 'a' - 'A';
            if (label >= 'a' && label <= 'z') {
                if (label != selected->inventoryLetter) {
                    frame->recording[frame->recordingCount++] = label;
                    frame->recording[frame->recordingCount] = '\0';
                    recordKeystrokeSequence(frame->recording);
                    item *oldItem = itemOfPackLetter(label);
                    if (oldItem) {
                        oldItem->inventoryLetter = selected->inventoryLetter;
                        itemName(oldItem, name, true, true, NULL);
                        sprintf(buf, "Relabeled %s as (%c);", name, oldItem->inventoryLetter);
                        messageWithColor(buf, &itemMessageColor, 0);
                    }
                    selected->inventoryLetter = label;
                    itemName(selected, name, true, true, NULL);
                    sprintf(buf, "%selabeled %s as (%c).", oldItem ? " r" : "R", name, label);
                    messageWithColor(buf, &itemMessageColor, 0);
                } else {
                    itemName(selected, name, true, true, NULL);
                    sprintf(buf, "%s %s already labeled (%c).", name, selected->quantity == 1 ? "is" : "are", label);
                    messageWithColor(buf, &itemMessageColor, 0);
                }
            }
            finishItemFrame(frame);
            return true;
        }
        default: return false;
    }
}

void driveNativeItemCommand(nativeItemCommandFrame *frame) {
    while (frame->promptKind != NATIVE_ITEM_COMPLETE) {
        nativeItemAnswer answer = {0};
        if (frame->promptKind == NATIVE_ITEM_CHOICE) {
            answer.kind = NATIVE_ITEM_ANSWER_CHOICE;
            answer.selected = promptForItemOfType(frame->category, frame->requiredFlags, frame->forbiddenFlags,
                                                  frame->prompt, frame->allowInventoryActions);
        } else if (frame->promptKind == NATIVE_ITEM_CONFIRMATION) {
            answer.kind = confirm(frame->prompt, true) ? NATIVE_ITEM_ANSWER_YES : NATIVE_ITEM_ANSWER_NO;
        } else if (frame->relabelLetter) {
            temporaryMessage(frame->prompt, 0);
            do { answer.text[0] = nextKeyPress(true); } while (!answer.text[0]);
            answer.kind = NATIVE_ITEM_ANSWER_TEXT;
        } else {
            answer.kind = getInputTextString(answer.text, frame->prompt, frame->nativeTextLength, "", "\"", TEXT_INPUT_NORMAL, false)
                ? NATIVE_ITEM_ANSWER_TEXT : NATIVE_ITEM_ANSWER_ESCAPE;
        }
        if (!stepNativeItemCommand(frame, &answer)) {
            brogueAssert(false);
            return;
        }
    }
}
