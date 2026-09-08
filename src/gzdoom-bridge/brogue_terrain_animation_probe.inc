// Explicit developer-only presentation fixture. Never mutates Brogue's pmap.
namespace {
int TerrainProbeStage = -1, TerrainProbePhase = 0, TerrainProbeNext = 0;
uint64_t TerrainProbeHash = 0;
bool TerrainMeasureFrames = false, TerrainCapture = true, TerrainDense = false;
std::vector<double> TerrainFrameTimes, TerrainUpdateTimes, TerrainDenseTimes;
std::chrono::steady_clock::time_point TerrainPreviousFrame;

void RecordTerrainFrame() {
    if (!TerrainMeasureFrames) return;
    auto now = std::chrono::steady_clock::now();
    if (TerrainPreviousFrame.time_since_epoch().count() && TerrainFrameTimes.size()<20000)
        TerrainFrameTimes.push_back(std::chrono::duration<double,std::milli>(now-TerrainPreviousFrame).count());
    if (TerrainDense && TerrainPreviousFrame.time_since_epoch().count() && TerrainDenseTimes.size()<20000)
        TerrainDenseTimes.push_back(std::chrono::duration<double,std::milli>(now-TerrainPreviousFrame).count());
    TerrainPreviousFrame = now;
}

BrogueBridgeTerrainAppearance TerrainProbeAppearance(int stage) {
    BrogueBridgeTerrainAppearance a{}; a.knowledge = BROGUE_TERRAIN_VISIBLE; a.structure = TT_FLOOR;
    switch(stage) {
    case 0: a.flags = BROGUE_APPEARANCE_WALL | BROGUE_APPEARANCE_OPAQUE; a.structure=TT_WALL; break;
    case 1: case 2: a.mechanism=TT_DOOR; break;
    case 4: case 5:
        a.flags=BROGUE_APPEARANCE_BRIDGE|BROGUE_APPEARANCE_HOLE;
        a.ground=TT_CHASM; a.deck=stage==4?TT_BRIDGE:TT_BRIDGE_FALLING; break;
    case 6: a.flags=BROGUE_APPEARANCE_HOLE; a.ground=TT_CHASM; break;
    case 8: case 9:
        a.flags=BROGUE_APPEARANCE_FLOOD; a.liquid=stage==8?TT_FLOOD_WATER_SHALLOW:TT_FLOOD_WATER_DEEP;
        a.liquidKind=stage==8?BROGUE_LIQUID_SHALLOW_WATER:BROGUE_LIQUID_DEEP_WATER; break;
    case 10: case 11:
        a.flags=BROGUE_APPEARANCE_ICE; a.deck=stage==10?TT_ICE_DEEP:TT_ICE_DEEP_MELT;
        a.bedKind=a.liquidKind=BROGUE_LIQUID_DEEP_WATER; break;
    case 12: a.liquid=TT_DEEP_WATER; a.bedKind=a.liquidKind=BROGUE_LIQUID_DEEP_WATER; break;
    case 13: case 14:
        a.gas=TT_POISON_GAS; a.gasVolume=stage==13?70:12; a.gasRed=80; a.gasGreen=160; a.gasBlue=65;
        if(stage==13) {a.fire=TT_PLAIN_FIRE; a.flags=BROGUE_APPEARANCE_BRIDGE; a.deck=TT_BRIDGE;}
        break;
    case 15: a.mechanism=TT_MACHINE_PRESSURE_PLATE; break;
    case 16: a.mechanism=TT_MACHINE_PRESSURE_PLATE_USED; a.flags=BROGUE_APPEARANCE_DEPRESSED; break;
    case 17: a.mechanism=TT_WALL_LEVER; break;
    case 18: a.mechanism=TT_WALL_LEVER_PULLED; break;
    case 19: a.mechanism=TT_ALTAR_CAGE_CLOSED; break;
    case 20: a.ground=TT_GRASS; break;
    case 21: a.fire=TT_PLAIN_FIRE; break;
    case 22: a.knowledge=BROGUE_TERRAIN_REMEMBERED; break;
    case 23: a.structure=TT_STATUE_INERT; break;
    case 24: a.structure=TT_STATUE_DORMANT; break;
    case 25: a.structure=TT_STATUE_CRACKING; break;
    case 26: a.structure=TT_STATUE_INERT_DOORWAY; break;
    case 27: break; // Returned floor removes every statue component.
    case 28: a.structure=TT_DEMONIC_STATUE; break;
    case 29: case 30: case 31: case 32: case 33: case 34:
        a.flags=BROGUE_APPEARANCE_WALL|BROGUE_APPEARANCE_OPAQUE;
        a.structure=stage==30?TT_HAUNTED_TORCH_DORMANT:stage==31?TT_HAUNTED_TORCH_TRANSITIONING
            :stage==32?TT_HAUNTED_TORCH:TT_TORCH_WALL;
        if(stage==33) a.knowledge=BROGUE_TERRAIN_REMEMBERED;
        if(stage==34) {a.knowledge=BROGUE_TERRAIN_UNKNOWN;a.structure=TT_WALL;}
        break;
    case 35: a.flags=BROGUE_APPEARANCE_WALL|BROGUE_APPEARANCE_OPAQUE; a.structure=TT_WALL; break;
    case 36: break;
    case 37: a.ground=TT_BLOODFLOWER_STALK; break;
    case 38: case 40: case 42: a.ground=TT_BLOODFLOWER_POD; break;
    case 39: case 41: a.gas=TT_HEALING_CLOUD; a.gasVolume=90; a.gasRed=100; a.gasGreen=0; a.gasBlue=0; break;
    case 43: a.knowledge=BROGUE_TERRAIN_REMEMBERED; a.structure=TT_BLOODFLOWER_POD; break;
    case 44: a.knowledge=BROGUE_TERRAIN_UNKNOWN; a.structure=0; break;
    case 45: a.gas=TT_HEALING_CLOUD; a.gasVolume=15; a.gasRed=100; break;
    case 46: a.gas=TT_POISON_GAS; a.gasVolume=70; a.gasRed=80; a.gasGreen=160; a.gasBlue=65; break;
    case 47: break;
    }
    return a;
}

void ApplyTerrainProbe(const BrogueBridgeTerrainAppearance &a) {
    for(int dy=-3;dy<=0;++dy) for(int dx=-1;dx<=1;++dx) {
        const int x=State.player.x+dx,y=State.player.y+dy,key=y*79+x;
        State.cells[key].appearance=a;
        if(TerrainProbeStage>=29 && (dy!=-2 || dx!=0)) State.cells[key].appearance=TerrainProbeAppearance(-1);
        if(dx==0 && dy==0 && ((a.flags&BROGUE_APPEARANCE_WALL)||a.mechanism||IsStatueTile(a.structure)))
            State.cells[key].appearance=TerrainProbeAppearance(-1);
    }
    if(TerrainProbeStage>=37) {
        // Populate the copied renderer fixture, without touching native entities.
        for(unsigned i=0;i<State.itemCount;++i) if(!State.items[i].carried) {
            State.items[i].x=State.player.x-1; State.items[i].y=State.player.y-2;
            State.items[i].visible=true; break;
        }
        if(State.creatureCount) {
            State.creatures[0].x=State.player.x+1; State.creatures[0].y=State.player.y-2;
            State.creatures[0].visibility=BROGUE_VISIBILITY_DIRECT;
        }
    }
    State.revision+=TerrainProbeStage>=37 && TerrainProbeStage!=42 ? 1 : 3; // Deliberately skip revisions and supply no terrain events.
    auto begin=std::chrono::steady_clock::now();
    ReconcileTerrain(); SyncPlayer(); SyncItems(); SyncMonsters();
    if(TerrainProbeStage>=37) {
        unsigned items=0,creatures=0;
        for(const auto &proxy:ItemProxies) if(proxy.actor) {
            if((proxy.actor->Pos()-BrogueCellToWorld(proxy.x,proxy.y)).Length()>.01) I_Error("Bloodwort item placement drift");
            ++items;
        }
        for(const auto &entry:MonsterProxies) if(entry.second.actor && !entry.second.moveTics) {
            const auto &proxy=entry.second;
            if((proxy.actor->Pos()-BrogueCellToWorld(proxy.x,proxy.y)).Length()>.01) I_Error("Bloodwort creature placement drift");
            ++creatures;
        }
        if(!items || !creatures) I_Error("Bloodwort fixture has no entity placement evidence");
        Printf("BLOODWORT_PLACEMENT items=%u creatures=%u immediate=true\n",items,creatures);
    }
    TerrainUpdateTimes.push_back(std::chrono::duration<double,std::milli>(std::chrono::steady_clock::now()-begin).count());
    const auto expected=BrogueCellToWorld(State.player.x,State.player.y);
    if((players[consoleplayer].mo->Pos()-expected).Length()>.01) I_Error("Terrain animation: stale entity support");
}

int TerrainProbeEnd = 23;
void TickTerrainAnimationProbe() {
    if(TerrainProbeStage<0 || !TerrainReady || primaryLevel->maptime<35 || primaryLevel->maptime<TerrainProbeNext) return;
    const int now=primaryLevel->maptime;
    if(!TerrainProbeHash) {
        TerrainProbeHash=State.stateHash;
        TerrainState.Clear(); ApplyTerrainProbe(TerrainProbeAppearance(-1));
        players[consoleplayer].mo->Angles.Yaw=DAngle::fromDeg(90);
        TerrainMeasureFrames=true;
    }
    if(TerrainProbeStage==TerrainProbeEnd) {
        static BrogueBridgeState checked;
        if(Api.getState(&checked)!=BROGUE_BRIDGE_OK || checked.stateHash!=TerrainProbeHash || checked.absoluteTurn!=0)
            I_Error("Terrain animation probe changed Brogue");
        auto report=[](const char *name,std::vector<double> values) {
            if(values.empty()) return;
            std::sort(values.begin(),values.end()); double total=0; for(double v:values) total+=v;
            Printf("TERRAIN_TIMING %s count=%zu mean_ms=%.3f p95_ms=%.3f max_ms=%.3f\n",name,values.size(),total/values.size(),values[values.size()*95/100],values.back());
        };
        report(TerrainCapture?"frame_with_capture_overhead":"frame",TerrainFrameTimes); report("dense_frame",TerrainDenseTimes); report("update",TerrainUpdateTimes);
        Printf("TERRAIN_ANIMATION passed quality=%d stages=%d unchangedHash=%016llx fragments=%zu\n",int(brg_fx_quality),TerrainProbeEnd,(unsigned long long)checked.stateHash,TerrainFragments.size());
        TerrainProbeStage=-1; TerrainMeasureFrames=false; AddCommandString("quit"); return;
    }
    FString capture;
    if(TerrainProbePhase==0) {
        capture.Format("screenshot animation-%02d-before.png",TerrainProbeStage); if(TerrainCapture) AddCommandString(capture.GetChars());
        TerrainProbePhase=1; TerrainProbeNext=now+2;
    } else if(TerrainProbePhase==1) {
        ApplyTerrainProbe(TerrainProbeAppearance(TerrainProbeStage));
        const int key=(State.player.y-(TerrainProbeStage>=29?2:1))*79+State.player.x;
        const double start=TerrainBindings[key].motion.liquidHeight.start;
        ReconcileTerrain();
        if(TerrainBindings[key].motion.liquidHeight.start!=start) I_Error("Duplicate snapshot restarted animation");
        TerrainProbePhase=2; TerrainProbeNext=now+6;
    } else if(TerrainProbePhase==2) {
        capture.Format("screenshot animation-%02d-during.png",TerrainProbeStage); if(TerrainCapture) AddCommandString(capture.GetChars());
        if(TerrainProbeStage==9) {
            const int key=(State.player.y-(TerrainProbeStage>=29?2:1))*79+State.player.x;
            const double pose=TerrainBindings[key].motion.liquidHeight.Value(now);
            ApplyTerrainProbe(TerrainProbeAppearance(8));
            if(int(brg_fx_quality)>0 && std::abs(TerrainBindings[key].motion.liquidHeight.Value(now)-pose)>.001)
                I_Error("Retarget jumped away from current visual pose");
        }
        if(TerrainProbeStage==38) {
            const int key=(State.player.y-2)*79+State.player.x;
            const double pose=TerrainBindings[key].motion.plant.Value(now);
            auto a=TerrainProbeAppearance(38); a.gasRed=17;
            ApplyTerrainProbe(a);
            if(std::abs(TerrainBindings[key].motion.plant.Value(now)-pose)>.001) I_Error("Interrupted bloodwort growth jumped");
            const auto revision=State.revision;
            State.revision-=2; State.cells[key].appearance=TerrainProbeAppearance(37);
            ReconcileTerrain();
            if(BloodwortTile(TerrainState.applied[key])!=TT_BLOODFLOWER_POD) I_Error("Stale bloodwort snapshot restored stalk");
            State.revision=revision; State.cells[key].appearance=a;
        }
        if(TerrainProbeStage==40) ApplyTerrainProbe(TerrainProbeAppearance(43));
        TerrainProbePhase=3; TerrainProbeNext=now+24;
    } else {
        if(!TerrainCapture && (TerrainProbeStage==13 || TerrainProbeStage==39) && TerrainProbePhase==3) {
            TerrainDense=true; TerrainProbePhase=4; TerrainProbeNext=now+210; return;
        }
        TerrainDense=false;
        capture.Format("screenshot animation-%02d-after.png",TerrainProbeStage); if(TerrainCapture) AddCommandString(capture.GetChars());
        const int key=(State.player.y-(TerrainProbeStage>=29?2:1))*79+State.player.x;
        auto &b=TerrainBindings[key];
        if (TerrainProbeStage >= 23 && TerrainProbeStage < 29) {
            const char *expected = TerrainStyleFor(TerrainProbeAppearance(TerrainProbeStage).structure).actor;
            if ((*expected && (!b.mechanism || b.mechanism->GetClass() != PClass::FindActor(expected)))
                || (!*expected && b.mechanism) || b.outgoing) I_Error("Stale or missing statue proxy");
        }
        if(TerrainProbeStage>=29 && TerrainProbeStage<37) {
            const bool lit=TerrainProbeStage<=32;
            const bool physical=TerrainProbeStage<=33;
            if(bool(b.mechanism)!=physical || bool(b.torchFlame)!=lit || b.outgoing)
                I_Error("Stale or missing wall torch component");
            if(b.mechanism && b.mechanism->Sector==b.primary) I_Error("Torch embedded in closed wall");
            if(b.torchFlame && b.torchFlame->GetClass()!=PClass::FindActor(TerrainProbeStage==32
                ?"BrogueTerrainHauntedTorchFlame":"BrogueTerrainTorchFlame")) I_Error("Incorrect torch flame");
            Printf("TORCH_PROBE stage=%d physical=%d flame=%d wallClosed=%d\n",TerrainProbeStage,int(physical),int(lit),int(b.primary->ceilingplane.ZatPoint(0.,0.)==b.primary->floorplane.ZatPoint(0.,0.)));
        }
        if(TerrainProbeStage>=37) {
            const auto a=TerrainProbeAppearance(TerrainProbeStage);
            const unsigned plant=BloodwortTile(a);
            if(bool(b.vegetation)!=bool(plant) || b.mechanism || b.outgoing || b.torchFlame)
                I_Error("Bloodwort owner mismatch");
            if(b.vegetation && b.vegetation->GetClass()!=PClass::FindActor(TerrainStyleFor(plant).actor)) I_Error("Bloodwort identity mismatch");
            if(bool(b.gas)!=bool(a.gasVolume)) I_Error("Bloodwort gas cleanup mismatch");
            Printf("BLOODWORT_PROBE stage=%d plant=%u gas=%u fragments=%zu\n",TerrainProbeStage,plant,a.gas,TerrainFragments.size());
        }
        Printf("TERRAIN_PLANES stage=%d deckTarget=%.2f deckPose=%.2f deckZ=%.2f bedZ=%.2f\n",TerrainProbeStage,b.motion.deckAlpha.target,b.motion.deckAlpha.Value(now),b.deck->ceilingplane.ZatPoint(0.,0.),b.primary->floorplane.ZatPoint(0.,0.));
        for(auto f:b.primary->e->XFloor.ffloors) Printf("TERRAIN_FLOOR role=%s flags=%x alpha=%d top=%.2f bottom=%.2f copied=%d vertex=%d\n",f->model==b.deck?"deck":"liquid",f->flags,f->alpha,f->top.plane->ZatPoint(0.,0.),f->bottom.plane->ZatPoint(0.,0.),int(f->top.copied),f->top.vindex);
        if(std::abs(b.motion.deckAlpha.Value(now)-b.motion.deckAlpha.target)>.001) I_Error("Unsettled terrain timeline");
        if(b.motion.deckAlpha.target==1 && !(TerrainStyleFor(b.motion.deckTile).motion&3) && std::abs(b.deck->ceilingplane.ZatPoint(0.,0.))>.001) I_Error("Terrain plane missed its final render sample");
        if(TerrainFragments.size()) I_Error("Terrain fragments outlived transition");
        ++TerrainProbeStage; TerrainProbePhase=0; TerrainProbeNext=now+3;
    }
}
}
CCMD(brg_terrain_animation_smoke) {
    TerrainProbeEnd=23;
    TerrainCapture=true; TerrainProbeStage=0; TerrainProbePhase=0; TerrainProbeNext=0; TerrainProbeHash=0;
    TerrainFrameTimes.clear(); TerrainUpdateTimes.clear(); TerrainDenseTimes.clear(); TerrainDense=false; TerrainPreviousFrame={};
}

CCMD(brg_terrain_animation_benchmark) {
    TerrainProbeEnd=23;
    TerrainCapture=false; TerrainProbeStage=0; TerrainProbePhase=0; TerrainProbeNext=0; TerrainProbeHash=0;
    TerrainFrameTimes.clear(); TerrainUpdateTimes.clear(); TerrainDenseTimes.clear(); TerrainDense=false; TerrainPreviousFrame={};
}

CCMD(brg_statue_smoke) {
    TerrainCapture=true; TerrainProbeStage=23; TerrainProbeEnd=29;
    TerrainProbePhase=0; TerrainProbeNext=0; TerrainProbeHash=0;
    TerrainFrameTimes.clear(); TerrainUpdateTimes.clear(); TerrainDenseTimes.clear();
    TerrainDense=false; TerrainPreviousFrame={};
}

CCMD(brg_torch_smoke) {
    TerrainCapture=true; TerrainProbeStage=29; TerrainProbeEnd=37;
    TerrainProbePhase=0; TerrainProbeNext=0; TerrainProbeHash=0;
    TerrainFrameTimes.clear(); TerrainUpdateTimes.clear(); TerrainDenseTimes.clear();
    TerrainDense=false; TerrainPreviousFrame={};
}

CCMD(brg_bloodwort_smoke) {
    TerrainCapture=true; TerrainProbeStage=37; TerrainProbeEnd=48;
    TerrainProbePhase=0; TerrainProbeNext=0; TerrainProbeHash=0;
    TerrainFrameTimes.clear(); TerrainUpdateTimes.clear(); TerrainDenseTimes.clear();
    TerrainDense=false; TerrainPreviousFrame={};
}

CCMD(brg_bloodwort_benchmark) {
    TerrainCapture=false; TerrainProbeStage=37; TerrainProbeEnd=48;
    TerrainProbePhase=0; TerrainProbeNext=0; TerrainProbeHash=0;
    TerrainFrameTimes.clear(); TerrainUpdateTimes.clear(); TerrainDenseTimes.clear();
    TerrainDense=false; TerrainPreviousFrame={};
}
