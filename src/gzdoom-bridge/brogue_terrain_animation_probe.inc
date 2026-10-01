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
void TickTerrainOverlayProbe();
void TickWallFadeProbe();
void TickPotionColorProbe();
void TickFlavorProbe();
void TickTerrainAnimationProbe() {
    TickTerrainOverlayProbe();
    TickWallFadeProbe();
    TickPotionColorProbe();
    TickFlavorProbe();
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

// Explicit renderer-only catalog review. Builds copied presentation state in a
// small gallery; the Brogue session and its terrain are never modified.
CCMD(brg_catalog_tile) {
    if (!Started || !TerrainReady || argv.argc()<3) return;
    const int tile=atoi(argv[1]);
    if (tile<=0 || tile>=int(std::size(TerrainStyles))) return;
    BrogueBridgeTerrainAppearance a{};
    a.knowledge=BROGUE_TERRAIN_VISIBLE; a.structure=TT_FLOOR;
    if (!strcmp(argv[2],"deck")) { a.deck=tile; a.flags=BROGUE_APPEARANCE_BRIDGE; }
    else if (!strcmp(argv[2],"pitdeck")) { a.deck=tile; a.ground=TT_CHASM; a.flags=BROGUE_APPEARANCE_BRIDGE|BROGUE_APPEARANCE_HOLE; }
    else if (!strcmp(argv[2],"wall")) { a.structure=tile; a.flags=BROGUE_APPEARANCE_WALL|BROGUE_APPEARANCE_OPAQUE; }
    else a.ground=tile;
    const int px=State.player.x,py=State.player.y;
    if(px<2 || px>76 || py<4) return;
    static BrogueBridgeState checked;
    Api.getState(&checked); const auto hash=checked.stateHash;
    const auto turn=checked.absoluteTurn;
    for(int dy=-3;dy<=0;++dy) for(int dx=-1;dx<=1;++dx) {
        auto &cell=State.cells[(py+dy)*79+px+dx];
        cell.appearance=TerrainProbeAppearance(-1);
        if(dy==-2) cell.appearance=a;
    }
    ++State.revision;
    ReconcileTerrain(); TickTerrainAnimations(true); SyncPlayer();
    auto camera=players[consoleplayer].mo;
    camera->Angles.Yaw=DAngle::fromDeg(90); camera->PrevAngles.Yaw=camera->Angles.Yaw;
    camera->Angles.Pitch=DAngle::fromDeg(10); camera->PrevAngles.Pitch=camera->Angles.Pitch;
    Api.getState(&checked);
    if(checked.stateHash!=hash || checked.absoluteTurn!=turn) I_Error("Catalog review changed Brogue");
    Printf("CATALOG tile=%d role=%s unchangedHash=true turn=%llu\n",tile,argv[2],(unsigned long long)turn);
}

// Layered material gallery with an independent authoritative hash check.
namespace {
int OverlayProbeStage = -1, OverlayProbeNext = 0;
bool OverlayProbeCapture = false;
bool DebrisProbe = false;
void ApplyOverlayProbe(unsigned tile, unsigned base, unsigned light = 0) {
    const int px=State.player.x, py=State.player.y;
    if (px<2 || px>76 || py<4) I_Error("Overlay gallery needs room around spawn");
    static BrogueBridgeState checked;
    Api.getState(&checked); const auto hash=checked.stateHash, turn=checked.absoluteTurn;
    for (int dy=-3; dy<=0; ++dy) for (int dx=-1; dx<=1; ++dx) {
        auto a=TerrainProbeAppearance(-1);
        a.structure=base; a.layers[0]=base;
        if (base==TT_BRIDGE) { a.deck=base; a.structure=TT_FLOOR; a.flags=BROGUE_APPEARANCE_BRIDGE; }
        if (dy==-2) { a.ground=tile; a.layers[1]=light; a.layers[2]=tile; }
        State.cells[(py+dy)*79+px+dx].appearance=a;
    }
    ++State.revision; ReconcileTerrain(); TickTerrainAnimations(true); SyncPlayer();
    const int key=(py-2)*79+px;
    unsigned expected = base==TT_BRIDGE ? TT_FLOOR : base;
    if (TerrainSubstrate(TerrainState.applied[key])!=expected) I_Error("Overlay replaced substrate");
    if (!tile && !light) for (auto actor:TerrainBindings[key].overlays)
        if (actor) I_Error("Removed coating left a stale actor");
    auto camera=players[consoleplayer].mo;
    camera->Angles.Yaw=DAngle::fromDeg(90); camera->PrevAngles.Yaw=camera->Angles.Yaw;
    camera->Angles.Pitch=DAngle::fromDeg(18); camera->PrevAngles.Pitch=camera->Angles.Pitch;
    Api.getState(&checked);
    if (checked.stateHash!=hash || checked.absoluteTurn!=turn) I_Error("Overlay gallery changed Brogue");
    Printf("OVERLAY tile=%u base=%u light=%u unchangedHash=true\n",tile,base,light);
}
CCMD(brg_overlay_smoke) { OverlayProbeStage=0; OverlayProbeNext=0; OverlayProbeCapture=false; DebrisProbe=false; }
CCMD(brg_debris_smoke) { OverlayProbeStage=0; OverlayProbeNext=0; OverlayProbeCapture=false; DebrisProbe=true; }
void TickTerrainOverlayProbe() {
    if (OverlayProbeStage<0 || !TerrainReady || primaryLevel->maptime<70
        || primaryLevel->maptime<OverlayProbeNext) return;
    static const unsigned cases[][3] = {
        {TT_RED_BLOOD,TT_FLOOR,0}, {TT_SUNLIGHT_POOL,TT_FLOOR,0},
        {TT_RED_BLOOD,TT_MARBLE_FLOOR,0}, {TT_RED_BLOOD,TT_CARPET,0},
        {TT_SACRED_GLYPH,TT_MARBLE_FLOOR,0}, {TT_BONES,TT_CARPET,0},
        {TT_DARKNESS_PATCH,TT_MARBLE_FLOOR,0}, {TT_SPIDERWEB,TT_CARPET,0},
        {TT_EMBERS,TT_FLOOR,0}, {TT_HOLE_EDGE,TT_FLOOR,0},
        {TT_RED_BLOOD,TT_BRIDGE,0}, {TT_RED_BLOOD,TT_MARBLE_FLOOR,TT_SUNLIGHT_POOL},
        {0,TT_MARBLE_FLOOR,0}
    };
    static const unsigned debris[][3] = {
        {TT_TRAMPLED_FOLIAGE,TT_FLOOR,0}, {TT_TRAMPLED_FUNGUS_FOREST,TT_FLOOR,0},
        {TT_GRAY_FUNGUS,TT_FLOOR,0}, {TT_FUNGUS_FOREST,TT_FLOOR,0},
        {TT_ANCIENT_SPIRIT_VINES,TT_FLOOR,0}, {TT_MUD_DOORWAY,TT_FLOOR,0},
        {TT_JUNK,TT_FLOOR,0}, {TT_RUBBLE,TT_FLOOR,0}, {0,TT_FLOOR,0}
    };
    const size_t count=DebrisProbe ? std::size(debris) : std::size(cases);
    if (OverlayProbeStage==int(count)) {
        Printf("OVERLAY passed stages=%zu unchangedHash=true\n",count);
        OverlayProbeStage=-1; AddCommandString("quit"); return;
    }
    if (!OverlayProbeCapture) {
        const auto &c=DebrisProbe ? debris[OverlayProbeStage] : cases[OverlayProbeStage]; ApplyOverlayProbe(c[0],c[1],c[2]);
        OverlayProbeCapture=true; OverlayProbeNext=primaryLevel->maptime+42;
    } else {
        FString command; command.Format("screenshot overlay-%02d.png",OverlayProbeStage);
        AddCommandString(command.GetChars());
        ++OverlayProbeStage; OverlayProbeCapture=false; OverlayProbeNext=primaryLevel->maptime+4;
    }
}
} // namespace

namespace {
int PotionProbe=-1, PotionNext=0;
std::vector<AActor*> PotionProbeActors;
CCMD(brg_potion_color_smoke) { PotionProbe=0; PotionNext=0; }
void TickPotionColorProbe() {
    if (PotionProbe<0 || !TerrainReady || primaryLevel->maptime<70 || primaryLevel->maptime<PotionNext) return;
    if (PotionProbe==6) { Printf("POTION_COLORS passed colors=21 unchangedHash=true\n"); PotionProbe=-1; AddCommandString("quit"); return; }
    if (PotionProbe%2==0) {
        for (auto actor:PotionProbeActors) actor->Destroy();
        PotionProbeActors.clear();
        ApplyOverlayProbe(0,TT_FLOOR);
        auto camera=players[consoleplayer].mo;
        const auto origin=BrogueCellToWorld(State.player.x,State.player.y);
        camera->Angles.Pitch=DAngle::fromDeg(18); camera->PrevAngles.Pitch=camera->Angles.Pitch;
        for(int i=0;i<7;++i) {
            BrogueBridgeItemState item{}; item.category=8; item.kind=-1;
            item.potionColor=1+PotionProbe/2*7+i;
            const auto name=PickupClassName(item);
            item.kindKnown=1; item.kind=7;
            strcpy(item.displayName,"a potion called custom name");
            if (name!=PickupClassName(item)) I_Error("Potion appearance changed on identification/call");
            auto actor=Spawn(primaryLevel,name.GetChars(),origin+DVector3((i-3)*14,64,0),NO_REPLACE);
            if (!actor) I_Error("Missing potion color model");
            PotionProbeActors.push_back(actor);
            Printf("POTION_COLOR index=%u class=%s stable=true\n",item.potionColor,name.GetChars());
        }
    } else {
        FString cmd; cmd.Format("screenshot potion-colors-%d.png",PotionProbe/2); AddCommandString(cmd.GetChars());
    }
    ++PotionProbe; PotionNext=primaryLevel->maptime+24;
}
}

// Explicit copied-state fixture for the runtime upper tier, including a second
#include "flavor_cases.generated.h"
namespace {
int FlavorStage=-1,FlavorNext=0;
std::vector<AActor*> FlavorActors;
CCMD(brg_flavor_smoke) { FlavorStage=0; FlavorNext=0; }
void TickFlavorProbe() {
    if(FlavorStage<0 || !TerrainReady || primaryLevel->maptime<70 || primaryLevel->maptime<FlavorNext) return;
    if(FlavorStage==42) { ClearProjectile(); FlavorStage++; FlavorNext=primaryLevel->maptime+5; return; }
    if(FlavorStage==43) {
        auto iterator=primaryLevel->GetThinkerIterator<AActor>();
        auto ink=PClass::FindActor("BrogueScrollInk");
        while(auto actor=iterator.Next()) if(actor->IsA(ink)) I_Error("Stale scroll lettering after projectile cleanup");
        Printf("FLAVOR_RENDER passed materials=51 scrolls=3 held=2 projectile=1 cleanup=true unchangedHash=true\n"); FlavorStage=-1; AddCommandString("quit"); return;
    }
    if(FlavorStage%2==0) {
        for(auto actor:FlavorActors) actor->Destroy(); FlavorActors.clear();
        ApplyOverlayProbe(0,TT_FLOOR);
        auto origin=BrogueCellToWorld(State.player.x,State.player.y);
        if(FlavorStage<36) for(int i=0;i<3;++i) {
            const auto &c=FlavorCases[FlavorStage/2*3+i];
            BrogueBridgeItemState item{}; item.category=c.category; item.kind=-1;
            strcpy(item.appearance,c.name);
            auto cls=PickupClassName(item);
            item.kindKnown=1; item.kind=0; strcpy(item.displayName,"custom name");
            if(cls!=PickupClassName(item)) I_Error("Flavor changed after identification");
            auto actor=Spawn(primaryLevel,cls.GetChars(),origin+DVector3((i-1)*48,64,0),NO_REPLACE);
            if(!actor) I_Error("Missing flavored model");
            if(item.category==16) AttachScrollTitle(actor,item.appearance);
            FlavorActors.push_back(actor);
            Printf("FLAVOR_RENDER appearance=%s class=%s\n",item.appearance,cls.GetChars());
        }
        else if(FlavorStage<40) {
            auto &item=State.items[State.itemCount++]; item={}; item.id=900000+FlavorStage;
            item.category=FlavorStage==36 ? 32 : 64; item.carried=1;
            strcpy(item.appearance,FlavorStage==36 ? "birch" : "copper");
            VisualDeviceId=item.id; VisualDeviceKind=FlavorStage==36 ? 15 : 16;
            VisualDeviceUntilTic=primaryLevel->maptime+200; SyncWeaponView();
        }
        else {
            VisualDeviceUntilTic=0; SyncWeaponView();
            ThrownItemClass="BrogueFlavorScroll"; ThrownItemCategory=16; ThrownScrollTitle="ABRA KADABRA";
            BrogueBridgeTurnResult result{}; result.eventCount=2;
            for(int i=0;i<2;++i) {
                auto &event=result.events[i]; event.type=BROGUE_EVENT_PROJECTILE_MOVED; event.itemCategory=16;
                event.fromX=State.player.x; event.fromY=State.player.y;
                event.toX=State.player.x; event.toY=State.player.y-1;
            }
            BeginProjectileAnimation(result); Projectile.tics=200;
        }
    } else { FString command; command.Format("screenshot flavors-%02d.png",FlavorStage/2); AddCommandString(command.GetChars()); }
    ++FlavorStage; FlavorNext=primaryLevel->maptime+24;
}
}

// Explicit copied-state fixture for the runtime upper tier, including a second
// snapshot reconciliation. It never descends or edits the Brogue session.
namespace {
int WallFadeStage=-1, WallFadeNext=0;
bool WallFallProbe=false;
CCMD(brg_wall_fade_smoke) { WallFadeStage=0; WallFadeNext=0; }
CCMD(brg_wall_fall_smoke) { WallFadeStage=0; WallFadeNext=0; WallFallProbe=true; }
void TickWallFadeProbe() {
    if (WallFadeStage<0 || !TerrainReady || primaryLevel->maptime<70 || primaryLevel->maptime<WallFadeNext) return;
    static BrogueBridgeState original;
    if (WallFadeStage==0) {
        if (WallFallProbe) {
            AddCommandString("brg_actions N N N N N N N N N W W W W W W N N N N N W N W W N N N N N");
            WallFadeStage=1; WallFadeNext=primaryLevel->maptime+35; return;
        }
        Api.getState(&original);
        State.depth=2; primaryLevel->levelnum=2;
        ClearTerrainBindings();
        ++State.revision; ReconcileTerrain(); SyncPlayer();
        AddCommandString("changesky BRGSKY");
        auto camera=players[consoleplayer].mo;
        camera->Angles.Yaw=DAngle::fromDeg(90); camera->PrevAngles.Yaw=camera->Angles.Yaw;
        camera->Angles.Pitch=DAngle::fromDeg(-40); camera->PrevAngles.Pitch=camera->Angles.Pitch;
    } else if (WallFadeStage==1) {
        if (WallFallProbe) {
            if (State.depth!=2) {
                if (PendingActionIndex>=PendingActions.size()) AddCommandString("brg_confirm yes");
                WallFadeNext=primaryLevel->maptime+10; return;
            }
            auto camera=players[consoleplayer].mo;
            camera->Angles.Yaw=DAngle::fromDeg(180); camera->PrevAngles.Yaw=camera->Angles.Yaw;
            camera->Angles.Pitch=DAngle::fromDeg(-70); camera->PrevAngles.Pitch=camera->Angles.Pitch;
            Api.getState(&original);
        }
        AddCommandString("screenshot wall-fade-initial.png");
    }
    else if (WallFadeStage==2) {
        // Make every appearance dirty without changing topology.
        if (WallFallProbe) PerformAction(BROGUE_ACTION_WAIT,"wall-fade-probe");
        else {
            for (auto &cell:State.cells) cell.appearance.gasRed ^= 1;
            ++State.revision; ReconcileTerrain();
        }
    } else if (WallFadeStage==3) AddCommandString("screenshot wall-fade-reconciled.png");
    else {
        static BrogueBridgeState checked; Api.getState(&checked);
        if (!WallFallProbe && (checked.stateHash!=original.stateHash || checked.absoluteTurn!=original.absoluteTurn)) I_Error("Wall fade fixture changed Brogue");
        Printf("WALL_FADE passed depth=2 authoritativeFall=%d unchangedHash=%s\n", int(WallFallProbe), WallFallProbe ? "not-applicable" : "true");
        WallFadeStage=-1; AddCommandString("quit"); return;
    }
    ++WallFadeStage; WallFadeNext=primaryLevel->maptime+35;
}
}
