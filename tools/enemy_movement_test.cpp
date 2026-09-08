#include "../src/gzdoom-bridge/enemy_movement.h"
#include <cassert>
int main() {
 using namespace EnemyMovement;
 assert(Duration(false,64,28)==0);
 assert(Duration(true,64,28)==28);
 assert(Duration(true,64*std::sqrt(2.),28)==40);
 assert(Duration(true,128,28)==0);
 assert(Duration(true,0,28)==0);
 assert(Duration(true,64,1)==5 && Duration(true,64,100)==70);
 assert(InView(64,0,0,1,.75));
 assert(!InView(-64,0,0,1,.75));
 assert(!InView(64,100,0,1,.75));
 assert(!InView(64,0,100,1,.75));
 assert(InView(64,80,0,1,.75)); // Partial body at the edge.
 assert(Remaining(28,28,0,0)==1);
 assert(Remaining(14,28,0,0)==.5);
 assert(Remaining(0,28,0,0)==0);
 assert(Remaining(0,0,5,7)==1);
}
