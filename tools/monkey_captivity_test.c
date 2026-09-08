/* Public bridge regression: natural seed-2 captive, no simulation mutation. */
#define NOMINMAX
#include <windows.h>
#include <assert.h>
#include <stdio.h>
#include "../src/brogue-mapgen/src/brogue/BrogueBridge.h"
#include "../src/brogue-mapgen/src/brogue/Rogue.h"
#undef assert
#define assert(condition) do { if (!(condition)) { fprintf(stderr, "Failed line %d: %s\n", __LINE__, #condition); return 90; } } while (0)
static BrogueBridgeState state;
static BrogueBridgeTurnResult result;
int main(int argc,char **argv) {
 assert(argc==2); HMODULE dll=LoadLibraryA(argv[1]); assert(dll);
 BrogueBridgeResult (*start)(uint64_t)=(void*)GetProcAddress(dll,"brogue_bridge_start_game");
 BrogueBridgeResult (*get)(BrogueBridgeState*)=(void*)GetProcAddress(dll,"brogue_bridge_get_state");
 BrogueBridgeResult (*action)(BrogueBridgeAction,BrogueBridgeTurnResult*)=(void*)GetProcAddress(dll,"brogue_bridge_perform_action");
 BrogueBridgeResult (*command)(const BrogueBridgeCommand*,BrogueBridgeTurnResult*)=(void*)GetProcAddress(dll,"brogue_bridge_perform_command");
 assert(start&&get&&action&&command);assert(start(2)==BROGUE_BRIDGE_OK);
 int path[]={6,6,7,7,7,7,0,0,0,0,0,0,0,0,0,6};
 for(int i=0;i<16;i++)assert(action(path[i],&result)==BROGUE_BRIDGE_OK);
 assert(get(&state)==BROGUE_BRIDGE_OK);uint64_t revision=state.revision,hash=state.stateHash,turn=state.turn;
 assert(turn==16);assert(hash==0x9d3e5201b678eaddULL);
 int manacleKeys[8],manacleTiles[8],manacleCount=0;
 for(unsigned i=0;i<state.creatureCount;i++)if(state.creatures[i].id==12) {
  assert(state.creatures[i].bookkeepingFlags & MB_CAPTIVE);
  for(int dy=-1;dy<=1;dy++)for(int dx=-1;dx<=1;dx++) {
   int key=(state.creatures[i].y+dy)*79+state.creatures[i].x+dx;
   int tile=state.cells[key].layers[SURFACE];
   if(tile>=MANACLE_TL && tile<=MANACLE_R) {
    assert(state.cells[key].appearance.knowledge==BROGUE_TERRAIN_VISIBLE);
    assert(state.cells[key].appearance.ground==tile);
    manacleKeys[manacleCount]=key;manacleTiles[manacleCount++]=tile;
   }
  }
 }
 assert(manacleCount>0);
 for(int retry=0;retry<2;retry++) {
  assert(action(BROGUE_ACTION_MOVE_W,&result)==BROGUE_BRIDGE_CONFIRMATION_REQUIRED);
  assert(get(&state)==BROGUE_BRIDGE_OK);assert(state.revision==revision&&state.stateHash==hash&&state.turn==turn);
 }
 BrogueBridgeCommand c={0};c.apiVersion=BROGUE_BRIDGE_API_VERSION;c.type=BROGUE_COMMAND_ACTION;c.action=BROGUE_ACTION_MOVE_W;c.expectedRevision=revision-1;c.confirmed=1;
 assert(command(&c,&result)==BROGUE_BRIDGE_STALE_REVISION);
 assert(get(&state)==BROGUE_BRIDGE_OK);assert(state.stateHash==hash&&state.revision==revision);
 c.expectedRevision=revision;assert(command(&c,&result)==BROGUE_BRIDGE_OK);
 assert(get(&state)==BROGUE_BRIDGE_OK);assert(state.turn==17&&state.stateHash==0x891359fb198ed00fULL);
 int freed=0;for(unsigned i=0;i<state.creatureCount;i++)if(state.creatures[i].id==12)freed=state.creatures[i].isAlly&&!(state.creatures[i].bookkeepingFlags&256);
 assert(freed);hash=state.stateHash;revision=state.revision;
 for(int i=0;i<manacleCount;i++)assert(state.cells[manacleKeys[i]].layers[SURFACE]==manacleTiles[i]);
 printf("MANACLES_OK copied=%d retained_after_release=1\n",manacleCount);
 assert(command(&c,&result)==BROGUE_BRIDGE_STALE_REVISION);
 assert(get(&state)==BROGUE_BRIDGE_OK);assert(state.stateHash==hash&&state.revision==revision);
 for(int i=0;i<8;i++){int status=action(BROGUE_ACTION_WAIT,&result);get(&state);if(status!=BROGUE_BRIDGE_OK){printf("CONTINUATION_END status=%d hp=%d\n",status,state.player.hp);break;}printf("CONTINUATION %llu %016llx\n",(unsigned long long)state.turn,(unsigned long long)state.stateHash);}
 puts("CAPTIVITY_OK prompt=unchanged decline=unchanged stale=unchanged duplicate=unchanged freed=ally");
 return 0;
}
