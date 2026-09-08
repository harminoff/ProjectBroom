/* All artificial terrain, health and creature setup stays in this harness. */
static int runBloodwortSmoke(BrogueBridgeState *state) {
    const uint64_t seed=state->gameSeed;
    BrogueBridgeTurnResult result;
#define BW_CHECK(c) do { if (!(c)) { fprintf(stderr,"BLOODWORT failed line=%d: %s\n",__LINE__,#c); return 1; } } while(0)
    for (int scenario=0; scenario<7; ++scenario) {
        uint64_t hashes[300]={0}, messages[300]={0};
        short continuations[300]={0};
        const int steps=scenario==3?300:scenario==1?2:1;
        for (int route=0; route<2; ++route) {
            brogue_bridge_shutdown();
            BW_CHECK(brogue_bridge_start_game(seed)==BROGUE_BRIDGE_OK);
            creatureIterator it=iterateCreatures(monsters);
            while(hasNextCreature(it)) killCreature(nextCreature(&it),true);
            pmap[player.loc.x][player.loc.y].flags &= ~HAS_PLAYER;
            player.loc=(pos){40,14};
            for(int x=36;x<=44;++x) for(int y=9;y<=17;++y) {
                memset(&pmap[x][y],0,sizeof(pcell));
                pmap[x][y].layers[DUNGEON]=(x==36||x==44||y==9||y==17)?WALL:FLOOR;
                pmap[x][y].flags=DISCOVERED;
            }
            pmap[40][14].flags|=HAS_PLAYER;
            pmap[40][15].layers[DUNGEON]=WALL; // Inert observer refresh direction.
            player.info.maxHP=player.currentHP=5000;
            player.status[STATUS_NUTRITION]=30000;
            pmap[40][13].layers[SURFACE]=scenario==0?BLOODFLOWER_STALK:BLOODFLOWER_POD;
            if(scenario==3) for(int sx=37;sx<=43;sx+=2) for(int sy=10;sy<=12;sy+=2) pmap[sx][sy].layers[SURFACE]=BLOODFLOWER_STALK;
            updateVision(true);
            if(scenario==2) {
                BW_CHECK(exposeTileToFire(40,13,true));
                BW_CHECK(pmap[40][13].layers[SURFACE]!=BLOODFLOWER_POD);
                BW_CHECK(pmap[40][13].layers[GAS]==HEALING_CLOUD && pmap[40][13].volume>0);
            }
            if(scenario>=4) {
                player.info.maxHP=30; player.currentHP=10;
                player.turnsUntilRegen=30000; player.regenPerTurn=0;
                pmap[40][14].layers[GAS]=HEALING_CLOUD; pmap[40][14].volume=1000;
                if(scenario==5) player.info.flags|=MONST_INANIMATE;
                if(scenario==6) player.bookkeepingFlags|=MB_SUBMERGED;
            }
            int regrown=0, spread=0;
            for(int step=0;step<steps;++step) {
                const boolean wait=scenario>=2 && !(scenario==3 && step%30==0);
                if(scenario==3 && step%30==0) {
                    // Controlled repeated interaction; ordinary native stalk
                    // promotions run independently throughout the lifecycle.
                    pmap[40][13].layers[SURFACE]=BLOODFLOWER_POD;
                }
                const unsigned long before=rogue.absoluteTurnNumber;
                if(route) {
                    BW_CHECK(brogue_bridge_perform_action(wait?BROGUE_ACTION_WAIT:BROGUE_ACTION_MOVE_N,&result)==BROGUE_BRIDGE_OK);
                    BW_CHECK(result.actionAccepted==(scenario!=0));
                    BW_CHECK(result.consumedTurn==(scenario!=0));
                } else executeKeystroke(wait?REST_KEY:UP_KEY,false,false);
                BW_CHECK(rogue.absoluteTurnNumber==before+(scenario!=0));
                if(scenario==4) BW_CHECK(player.currentHP>10);
                if(scenario==5 || scenario==6) BW_CHECK(player.currentHP==10);
                if(scenario==3) {
                    for(int x=37;x<44;++x) for(int y=10;y<17;++y) {
                        if((x!=40 || y!=13) && pmap[x][y].layers[SURFACE]==BLOODFLOWER_POD) ++regrown;
                        if((x!=40 || y!=13) && pmap[x][y].layers[GAS]==HEALING_CLOUD) ++spread;
                    }
                }
                if(scenario==1) {
                    BW_CHECK(player.loc.x==40 && player.loc.y==(step?13:14));
                    BW_CHECK(pmap[40][13].layers[SURFACE]!=BLOODFLOWER_POD);
                }
                if(scenario==0) BW_CHECK(player.loc.x==40 && player.loc.y==14);
                /* Copy through the public observer, using rejected movement;
                 * settle STABLE_MEMORY identically on both execution routes. */
                const int py=player.loc.y;
                enum tileType prior=pmap[40][py+1].layers[DUNGEON];
                pmap[40][py+1].layers[DUNGEON]=WALL;
                for(int read=0;read<2;++read) {
                    BW_CHECK(brogue_bridge_perform_action(BROGUE_ACTION_MOVE_S,&result)==BROGUE_BRIDGE_OK);
                    BW_CHECK(!result.consumedTurn);
                }
                BW_CHECK(brogue_bridge_get_state(state)==BROGUE_BRIDGE_OK);
                pmap[40][py+1].layers[DUNGEON]=prior;
                uint64_t messageHash=1469598103934665603ULL;
                for(size_t byte=0;byte<sizeof(state->messages);++byte) {
                    messageHash^=((const unsigned char *)state->messages)[byte]; messageHash*=1099511628211ULL;
                }
                if(!route) messages[step]=messageHash;
                else BW_CHECK(messages[step]==messageHash);
                rogue.RNG=RNG_SUBSTANTIVE;
                short continuation=rand_range(0,30000);
                if(!route) {hashes[step]=state->stateHash; continuations[step]=continuation;}
                else {
                    if(hashes[step]!=state->stateHash) fprintf(stderr,"BLOODWORT mismatch scenario=%d step=%d native=%016llx bridge=%016llx\n",scenario,step,(unsigned long long)hashes[step],(unsigned long long)state->stateHash);
                    BW_CHECK(hashes[step]==state->stateHash && continuations[step]==continuation);
                }
                BW_CHECK(!rogue.gameHasEnded);
            }
            if(scenario==2) {
                int remaining=1,ticks=0;
                while(remaining && ticks<200) {
                    updateEnvironment(); ++ticks; remaining=0;
                    for(int x=37;x<44;++x) for(int y=10;y<17;++y)
                        if(pmap[x][y].layers[GAS]==HEALING_CLOUD && pmap[x][y].volume) ++remaining;
                }
                BW_CHECK(!remaining);
                printf("BLOODWORT native-dissipation ticks=%d remaining=0\n",ticks);
            }
            if(scenario==3) { printf("BLOODWORT lifecycle regrown=%d spread=%d\n",regrown,spread); BW_CHECK(regrown>0 && spread>0); }
        }
        printf("BLOODWORT scenario=%d steps=%d hash=%016llx rng=%d native=executeKeystroke\n",scenario,steps,(unsigned long long)hashes[steps-1],continuations[steps-1]);
    }
#undef BW_CHECK
    return 0;
}

