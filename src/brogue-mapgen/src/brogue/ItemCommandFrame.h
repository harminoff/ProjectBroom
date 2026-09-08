/* Internal Brogue command continuations. Native pointers never cross the ABI. */
#ifndef BROGUE_ITEM_COMMAND_FRAME_H
#define BROGUE_ITEM_COMMAND_FRAME_H

#include "Rogue.h"

typedef enum nativeItemCommandKind {
    NATIVE_ITEM_CALL, NATIVE_ITEM_RELABEL, NATIVE_ITEM_EQUIP, NATIVE_ITEM_REMOVE, NATIVE_ITEM_DROP
} nativeItemCommandKind;
typedef enum nativeItemPromptKind {
    NATIVE_ITEM_COMPLETE, NATIVE_ITEM_CHOICE, NATIVE_ITEM_CONFIRMATION, NATIVE_ITEM_TEXT
} nativeItemPromptKind;
typedef enum nativeItemAnswerKind {
    NATIVE_ITEM_ANSWER_CHOICE, NATIVE_ITEM_ANSWER_YES, NATIVE_ITEM_ANSWER_NO,
    NATIVE_ITEM_ANSWER_TEXT, NATIVE_ITEM_ANSWER_ESCAPE
} nativeItemAnswerKind;

typedef struct nativeItemAnswer {
    nativeItemAnswerKind kind;
    item *selected;
    char text[30];
} nativeItemAnswer;

typedef struct nativeItemCommandFrame {
    nativeItemCommandKind command;
    nativeItemPromptKind promptKind;
    unsigned int position;
    item *selected;
    item *replacement;
    unsigned char recording[100];
    unsigned int recordingCount;
    char prompt[COLS * 3];
    unsigned short category;
    unsigned long requiredFlags, forbiddenFlags;
    short nativeTextLength, textLimit;
    boolean allowInventoryActions, escapeMeansNo, relabelLetter;
} nativeItemCommandFrame;

void beginNativeItemCommand(nativeItemCommandFrame *frame, nativeItemCommandKind command, item *selected);
boolean stepNativeItemCommand(nativeItemCommandFrame *frame, const nativeItemAnswer *answer);
void driveNativeItemCommand(nativeItemCommandFrame *frame);

#endif
