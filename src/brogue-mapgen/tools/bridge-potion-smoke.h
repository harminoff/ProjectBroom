/* Harness-only appearance cases; normal snapshot export and rejected actions. */
static int runPotionSmoke(BrogueBridgeState *state) {
    item *potion=addItemToPack(generateItem(POTION, POTION_LIFE));
    BrogueBridgeTurnResult result;
    int color, mode, found;
    pmap[player.loc.x][player.loc.y-1].layers[DUNGEON]=WALL;
    for (color=0;color<NUMBER_ITEM_COLORS;++color) {
        strcpy(potionTable[POTION_LIFE].flavor,itemColorsRef[color]);
        for (mode=0;mode<3;++mode) {
            potionTable[POTION_LIFE].identified=mode==2;
            potionTable[POTION_LIFE].called=mode==1;
            potion->flags &= ~ITEM_IDENTIFIED;
            strcpy(potionTable[POTION_LIFE].callTitle,"custom label");
            if (brogue_bridge_perform_action(BROGUE_ACTION_MOVE_N,&result)!=BROGUE_BRIDGE_OK || result.consumedTurn) return 1;
            if (brogue_bridge_get_state(state)!=BROGUE_BRIDGE_OK) return 1;
            found=0;
            for (uint32_t i=0;i<state->itemCount;++i) {
                BrogueBridgeItemState *copy=&state->items[i];
                if (!copy->carried || copy->category!=POTION || copy->kind!=POTION_LIFE) continue;
                if (copy->potionColor!=color+1) return 1;
                if (mode==0 && !strstr(copy->displayName,itemColorsRef[color])) return 1;
                found=1;
            }
            if (!found) return 1;
        }
    }
    printf("POTION_COLORS colors=21 namingModes=3 passed=true\n");
    return 0;
}
