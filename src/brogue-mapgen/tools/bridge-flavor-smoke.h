/* Harness-only naming permutations exercise the normal copied-state exporter. */
static int runFlavorSmoke(BrogueBridgeState *state) {
    const unsigned categories[]={STAFF,WAND,RING,SCROLL};
    const int counts[]={NUMBER_ITEM_WOODS,NUMBER_ITEM_METALS,NUMBER_ITEM_GEMS,3};
    const char (*names[])[30]={itemWoodsRef,itemMetalsRef,itemGemsRef,NULL};
    const char *titles[]={"ABRA KADABRA","ZELGO MER","READ ME"};
    BrogueBridgeTurnResult result;
    pmap[player.loc.x][player.loc.y-1].layers[DUNGEON]=WALL;
    for(int c=0;c<4;++c) {
        item *it=addItemToPack(generateItem(categories[c],0));
        itemTable *table=tableForItemCategory(categories[c]);
        for(int n=0;n<counts[c];++n) {
            const char *appearance=c==3 ? titles[n] : names[c][n];
            strcpy(table[0].flavor,appearance);
            for(int mode=0;mode<3;++mode) {
                table[0].identified=mode==2; table[0].called=mode==1;
                strcpy(table[0].callTitle,"custom title"); it->flags &= ~ITEM_IDENTIFIED;
                if(brogue_bridge_perform_action(BROGUE_ACTION_MOVE_N,&result)!=BROGUE_BRIDGE_OK || result.consumedTurn) return 1;
                if(brogue_bridge_get_state(state)!=BROGUE_BRIDGE_OK) return 1;
                int found=0;
                for(uint32_t i=0;i<state->itemCount;++i) {
                    BrogueBridgeItemState *copy=&state->items[i];
                    if(copy->category!=categories[c] || copy->kind!=0 || !copy->carried) continue;
                    if(strcmp(copy->appearance,appearance)) return 1;
                    found=1;
                }
                if(!found) return 1;
            }
        }
    }
    printf("FLAVORS materials=51 titles=3 namingModes=3 passed=true\n"); return 0;
}
