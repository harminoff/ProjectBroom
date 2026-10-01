// Diagnostic route finder: copied snapshots choose intents; Brogue resolves all actions.
// No direct edits to simulation, health, monster placement or RNG.
#include "../../src/brogue-mapgen/src/brogue/BrogueBridge.h"
#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <queue>
#include <vector>
static BrogueBridgeState state;
static BrogueBridgeTurnResult result;
int main(int argc,char **argv) {
    const unsigned seed=argc>1 ? std::atoi(argv[1]) : 1;
    const int kind=argc>2 ? std::atoi(argv[2]) : 6;
    // Optional search limits are diagnostic only; ordinary Brogue actions and
    // the original early-floor route remain unchanged when omitted.
    const int maxSteps=argc>5 ? std::atoi(argv[5]) : 450;
    const int maxDepth=argc>6 ? std::atoi(argv[6]) : 4;
    if(maxSteps<=0 || maxDepth<=0) {
        std::fprintf(stderr,"Search limits must be positive: seed kind waits --visible [maxSteps [maxDepth]]\n");
        return 2;
    }
    brogue_bridge_initialize();brogue_bridge_start_game(seed);
    std::vector<int> actions;unsigned long long observed=0;
    int foundDepth=0;
    int observedCell=-1;
    bool previouslyChasm=false;
    for(int step=0;step<maxSteps;++step) {
        brogue_bridge_get_state(&state);
        if(!state.player.alive)break;
        int goal=-1;const BrogueBridgeCreatureState *target=nullptr;
        for(unsigned i=0;i<state.creatureCount;++i)if(state.creatures[i].kind==kind && state.creatures[i].alive
            && (!observed || state.creatures[i].id==observed)) {
            target=&state.creatures[i];break;
        }
        if(observed && !target) {
            if(kind==7) {
                if(state.depth==foundDepth+1) std::printf("PIT_FALL from=%d to=%d\n",foundDepth,state.depth);
                else {
                    if(observedCell<0 || previouslyChasm || !state.cells[observedCell].isChasm) break;
                    std::printf("PIT_CREATED cell=%d,%d depth=%d\n",observedCell%79,observedCell/79,state.depth);
                }
            }
            // Optional ordinary waits after the pit landing expose nearby goblin
            // presentation for the separate fixed-seed goblin review.
            const int followup=argc>3 ? std::atoi(argv[3]) : 0;
            for(int i=0;i<followup && state.player.alive;++i) {
                brogue_bridge_perform_action((BrogueBridgeAction)8,&result);
                actions.push_back(8);brogue_bridge_get_state(&state);
            }
            unsigned gas=0;for(unsigned i=0;i<state.cellCount;++i)if(state.cells[i].isGas)++gas;
            std::printf("SUCCESS seed=%u depth=%d target=%llu gasCells=%u hash=%llx\n",seed,foundDepth,observed,gas,(unsigned long long)state.stateHash);
            const char* names[]={"N","NE","E","SE","S","SW","W","NW","WAIT"};
            for(int a:actions)std::printf("%s ",names[a]);std::puts("");
            brogue_bridge_shutdown();return 0;
        }
        if(target && target->visibility==BROGUE_VISIBILITY_DIRECT) {
            observed=target->id;foundDepth=state.depth;
            observedCell=target->y*79+target->x;previouslyChasm=state.cells[observedCell].isChasm;
            // Opt-in read-only encounter stop for the next roster model. The
            // original bloat death/fall route is unchanged without this flag.
            if(argc>4 && std::strcmp(argv[4],"--visible")==0
                && std::max(std::abs(state.player.x-target->x),std::abs(state.player.y-target->y))<=3) {
                const int followup=std::atoi(argv[3]);
                for(int i=0;i<followup && state.player.alive;++i) {
                    brogue_bridge_perform_action((BrogueBridgeAction)8,&result);
                    actions.push_back(8);brogue_bridge_get_state(&state);
                }
                if(!state.player.alive)break;
                std::printf("VISIBLE seed=%u depth=%d target=%llu turns=%zu hash=%llx\n",seed,state.depth,observed,actions.size(),(unsigned long long)state.stateHash);
                for(unsigned i=0;i<state.creatureCount;++i) {
                    const auto &c=state.creatures[i];
                    if(c.alive && c.visibility==BROGUE_VISIBILITY_DIRECT)
                        std::printf("CREATURE kind=%d id=%llu xy=%d,%d\n",c.kind,(unsigned long long)c.id,c.x,c.y);
                }
                const char* names[]={"N","NE","E","SE","S","SW","W","NW","WAIT"};
                for(int a:actions)std::printf("%s ",names[a]);std::puts("");
                brogue_bridge_shutdown();return 0;
            }
        }
        const int start=state.player.y*79+state.player.x;
        int prev[2291],first[2291];std::fill(prev,prev+2291,-1);prev[start]=start;
        std::queue<int> queue;queue.push(start);
        const int dx[]={0,1,0,-1},dy[]={-1,0,1,0};
        while(!queue.empty()) {
            int k=queue.front();queue.pop();int x=k%79,y=k/79;
            if(target ? std::max(std::abs(x-target->x),std::abs(y-target->y))<=1
                      : x==state.downStairsX && y==state.downStairsY) {goal=k;break;}
            for(int d=0;d<4;++d) {
                int nx=x+dx[d],ny=y+dy[d],nk=ny*79+nx;
                if(nx<0||nx>=79||ny<0||ny>=29||prev[nk]!=-1)continue;
                const auto &c=state.cells[nk];
                if(c.isSolid||c.isDeepWater||c.isLava||c.isFire||(c.isChasm&&!c.isBridge))continue;
                prev[nk]=k;first[nk]=k==start ? d*2 : first[k];queue.push(nk);
            }
        }
        if(goal<0 || state.depth>maxDepth)break;
        int action=goal==start ? 8 : first[goal];
        auto status=brogue_bridge_perform_action((BrogueBridgeAction)action,&result);
        if(status!=BROGUE_BRIDGE_OK)break;
        actions.push_back(action);
    }
    std::printf("NO_ENCOUNTER seed=%u depth=%d actions=%zu hp=%d\n",seed,state.depth,actions.size(),state.player.hp);
    brogue_bridge_shutdown();return 1;
}
