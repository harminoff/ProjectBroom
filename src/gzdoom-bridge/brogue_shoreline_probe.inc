// Explicit developer fixture: modifies copied presentation only, never Brogue.
namespace {
int ShoreProbeStage=-1, ShoreProbeNext=0;
bool ShoreProbeCapture=false, ShoreProbeBenchmark=false;
uint64_t ShoreProbeHash=0, ShoreProbeTurn=0;
std::chrono::steady_clock::time_point ShoreProbePrevious;
std::vector<double> ShoreProbeFrames;
void RecordShorelineFrame() {
    if(!ShoreProbeBenchmark || ShoreProbeStage<0 || !ShoreProbeCapture) return;
    const auto now=std::chrono::steady_clock::now();
    if(ShoreProbePrevious.time_since_epoch().count()) ShoreProbeFrames.push_back(std::chrono::duration<double,std::milli>(now-ShoreProbePrevious).count());
    ShoreProbePrevious=now;
}
void ShoreProbeScene(int stage) {
    const int px=State.player.x,py=State.player.y;
    std::vector<int> dirt;
    for(int dy=-7;dy<=1;++dy) for(int dx=-5;dx<=5;++dx) {
        const int x=px+dx,y=py+dy;
        if(x<0||x>=79||y<0||y>=29) continue;
        auto &a=State.cells[y*79+x].appearance;
        a={}; a.structure=TT_FLOOR; a.knowledge=BROGUE_TERRAIN_VISIBLE;
        const bool wall=dy==-7||abs(dx)==5;
        const bool island=(dy==-3&&(dx==0||dx==1)) || (dy==-4&&dx==1);
        const bool pool=dy<=-1 && !wall;
        if(wall) {a.structure=TT_WALL; a.flags=BROGUE_APPEARANCE_WALL|BROGUE_APPEARANCE_OPAQUE;}
        else if(pool && (!island || stage==5)) {
            a.liquid=dx<0 ? TT_SHALLOW_WATER : TT_DEEP_WATER;
            a.bedKind=a.liquidKind=dx<0 ? BROGUE_LIQUID_SHALLOW_WATER : BROGUE_LIQUID_DEEP_WATER;
            if(stage==5 && island) {a.deck=TT_BRIDGE; a.flags=BROGUE_APPEARANCE_BRIDGE;}
            if(stage==6) {a.liquid=0;a.deck=TT_ICE_DEEP;a.flags=BROGUE_APPEARANCE_ICE;}
            if(stage==8) a.flags=BROGUE_APPEARANCE_FLOOD;
            if(stage==9 && dx>=0) a.knowledge=BROGUE_TERRAIN_UNKNOWN;
            if(stage==10) a.knowledge=BROGUE_TERRAIN_REMEMBERED;
        } else {
            if(stage==3) a.ground=TT_GRASS;
            dirt.push_back(y*79+x);
        }
    }
    for(unsigned i=0;i<State.itemCount;++i) if(!State.items[i].carried) State.items[i].visible=false;
    for(unsigned i=0;i<State.creatureCount;++i) State.creatures[i].visibility=BROGUE_VISIBILITY_HIDDEN;
    State.revision+=3; // Missing event/revision recovery, like restored snapshots.
    brg_shorelines=stage!=0;
    ReconcileTerrain();
    // Material-only comparison for flagstone, whose ordinary catalog aliases
    // still map to earth. No catalog change is made to manufacture this scene.
    for(int key:dirt) {
        auto &b=TerrainBindings[key];
        const char *base=stage==4 ? "BRGFLAG" : stage==3 ? "BRGMOSS" : "BRGEARTH";
        b.shoreGround=ShorelineMaterial(base,brg_shorelines ? Shoreline::Resolve(TerrainState.applied,key).ground : 0);
        b.primary->SetTexture(sector_t::floor,TexMan.GetTextureID(b.shoreGround.IsNotEmpty()?b.shoreGround.GetChars():base,ETextureType::Flat));
    }
    players[consoleplayer].mo->Angles.Yaw=DAngle::fromDeg(90);
    players[consoleplayer].mo->Angles.Pitch=DAngle::fromDeg(stage==2?8:26);
    SyncPlayer(); SyncItems(); SyncMonsters(); TickTerrainAnimations(true);
}
void TickShorelineProbe() {
    if(ShoreProbeStage<0 || !TerrainReady || primaryLevel->maptime<35 || primaryLevel->maptime<ShoreProbeNext) return;
    if(!ShoreProbeHash) {ShoreProbeHash=State.stateHash;ShoreProbeTurn=State.absoluteTurn;}
    if(ShoreProbeStage==(ShoreProbeBenchmark?2:11)) {
        static BrogueBridgeState checked;
        if(Api.getState(&checked)!=BROGUE_BRIDGE_OK || checked.stateHash!=ShoreProbeHash || checked.absoluteTurn!=ShoreProbeTurn) I_Error("Shoreline probe changed Brogue");
        Printf("SHORELINE passed stages=%d unchangedHash=%016llx turn=%llu\n",ShoreProbeStage,(unsigned long long)checked.stateHash,(unsigned long long)checked.absoluteTurn);
        ShoreProbeStage=-1; AddCommandString("quit"); return;
    }
    if(!ShoreProbeCapture) {
        ShoreProbeScene(ShoreProbeStage);
        ShoreProbeFrames.clear(); ShoreProbePrevious={};
        ShoreProbeCapture=true; ShoreProbeNext=primaryLevel->maptime+(ShoreProbeBenchmark?245:40); return;
    }
    int water=0,wet=0;
    for(auto &b:TerrainBindings) if(b.primary) {
        water+=b.shoreWater.IsNotEmpty(); wet+=b.shoreGround.IsNotEmpty()||b.shoreDeck.IsNotEmpty();
        for(auto f:b.primary->e->XFloor.ffloors) {
            if(f->flags&(FF_SOLID|FF_SWIMMABLE)) I_Error("Shoreline acquired gameplay flags");
            if(f->model==b.liquid && b.shoreWater.IsNotEmpty() && (!(f->flags&FF_TRANSLUCENT)||f->alpha>=255)) I_Error("Shoreline bed clipping is opaque");
        }
    }
    Printf("SHORELINE stage=%d water=%d wet=%d quality=%d\n",ShoreProbeStage,water,wet,int(brg_fx_quality));
    if(ShoreProbeStage==0 && (water||wet)) I_Error("Shoreline baseline was not restored");
    if(ShoreProbeStage==1 && (!water||!wet)) I_Error("Shoreline owners absent");
    if(ShoreProbeBenchmark) {
        if(ShoreProbeFrames.size()>30) {
            // Exclude initialization/warmup; capture no images in this interval.
            ShoreProbeFrames.erase(ShoreProbeFrames.begin(),ShoreProbeFrames.begin()+30);
            std::sort(ShoreProbeFrames.begin(),ShoreProbeFrames.end());
            double total=0;for(double x:ShoreProbeFrames) total+=x;
            Printf("SHORELINE_TIMING enabled=%d frames=%zu mean_ms=%.3f p95_ms=%.3f\n",ShoreProbeStage,ShoreProbeFrames.size(),total/ShoreProbeFrames.size(),ShoreProbeFrames[ShoreProbeFrames.size()*95/100]);
        }
    } else {
        FString command;command.Format("screenshot shore-%02d.png",ShoreProbeStage);AddCommandString(command.GetChars());
    }
    ++ShoreProbeStage; ShoreProbeCapture=false; ShoreProbeNext=primaryLevel->maptime+4;
}
}
CCMD(brg_shoreline_smoke) {ShoreProbeStage=0;ShoreProbeNext=0;ShoreProbeCapture=false;ShoreProbeHash=0;ShoreProbeBenchmark=false;}
CCMD(brg_shoreline_benchmark) {ShoreProbeStage=0;ShoreProbeNext=0;ShoreProbeCapture=false;ShoreProbeHash=0;ShoreProbeBenchmark=true;}
