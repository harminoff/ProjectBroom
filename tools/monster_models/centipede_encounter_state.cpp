// Read-only copied-state diagnostic for the natural centipede route.
#include "../../src/brogue-mapgen/src/brogue/BrogueBridge.h"
#include <fstream>
#include <sstream>
#include <string>
#include <cstdio>
static BrogueBridgeState state;
static BrogueBridgeTurnResult result;
int main(int argc,char**argv) {
    if(argc<2)return 2;
    std::ifstream input(argv[1]);std::string line,route;
    while(std::getline(input,line))if(!line.empty())route=line;
    for(int i=2;i<argc;++i)route+=" "+std::string(argv[i]);
    brogue_bridge_initialize();brogue_bridge_start_game(1525);
    std::istringstream words(route);std::string word;unsigned count=0;
    const char* names[]={"N","NE","E","SE","S","SW","W","NW","WAIT"};
    while(words>>word) {
        int action=0;while(action<9 && word!=names[action])++action;
        if(action==9)return 3;
        if(brogue_bridge_perform_action((BrogueBridgeAction)action,&result)!=BROGUE_BRIDGE_OK)return 4;
        ++count;
    }
    brogue_bridge_get_state(&state);
    std::printf("seed=1525 depth=%d actions=%u player=%d,%d hp=%d hash=%016llx\n",state.depth,count,state.player.x,state.player.y,state.player.hp,(unsigned long long)state.stateHash);
    for(unsigned i=0;i<state.creatureCount;++i) {
        const auto& c=state.creatures[i];
        if(c.kind==17)std::printf("CENTIPEDE id=%llu xy=%d,%d direct=%d alive=%d isAlly=%d isCaptive=%d bookkeeping=%llx hp=%d\n",
            (unsigned long long)c.id,c.x,c.y,c.visibility==BROGUE_VISIBILITY_DIRECT,c.alive,c.isAlly,
            (c.bookkeepingFlags & (1ULL<<8))!=0,(unsigned long long)c.bookkeepingFlags,c.hp);
    }
    for(int y=21;y<29;++y) {
        std::printf("map y=%d ",y);
        for(int x=25;x<36;++x)std::putchar(x==state.player.x&&y==state.player.y?'@':state.cells[y*79+x].isSolid?'#':'.');
        std::puts("");
    }
    brogue_bridge_shutdown();return 0;
}
