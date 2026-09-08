// Developer-only renderer foundation. Does not mutate State or call Brogue.
// This intentionally does not claim terrain reconciliation or gameplay parity.
namespace {
int TerrainFixturePhase = -1;
int TerrainFixtureNextTic = 0;
uint64_t TerrainFixtureHash = 0;
bool TerrainFixtureCapture = false;

sector_t *TerrainSector(int base, int key)
{
    auto iterator = primaryLevel->GetSectorTagIterator(base + key);
    const int index = iterator.Next();
    return index < 0 ? nullptr : &primaryLevel->sectors[index];
}

void TerrainPlane(sector_t *sector, int plane, double z, const char *texture)
{
    auto &equation = plane == sector_t::floor ? sector->floorplane : sector->ceilingplane;
    equation.ChangeHeight(z - equation.ZatPoint(0.0, 0.0));
    sector->SetPlaneTexZ(plane, z, true);
    if (texture) sector->SetTexture(plane, TexMan.GetTextureID(texture, ETextureType::Flat));
    P_RecalculateAttached3DFloors(sector);
}

bool TerrainFixtureCell(int key, int mode)
{
    auto sector = TerrainSector(10000, key);
    auto liquid = TerrainSector(30000, key);
    auto deck = TerrainSector(40000, key);
    if (!sector || !liquid || !deck) return false;
    const bool wall = mode == 0;
    const bool flood = mode == 2 || mode == 3;
    const bool ice = mode == 3;
    const bool bridge = mode == 4;
    const bool chasm = mode == 5 || bridge;
    const double bed = chasm ? -128 : 0;
    TerrainPlane(sector, sector_t::floor, bed, chasm ? "BRGVOID" : "BRGEARTH");
    TerrainPlane(sector, sector_t::ceiling, wall ? bed : 224, "BRGCEIL");
    TerrainPlane(liquid, sector_t::floor, flood ? 7 : -520, "BRGWATR");
    TerrainPlane(liquid, sector_t::ceiling, flood ? 8 : -512, "BRGWATR");
    TerrainPlane(deck, sector_t::floor, ice ? 6 : bridge ? -4 : -520, "BRGEARTH");
    TerrainPlane(deck, sector_t::ceiling, ice ? 8.1 : bridge ? 0 : -512, "BRGEARTH");
    TerrainFixtureSupport[key] = ice ? 8.1 : bridge ? 0 : bed;
    for (auto line : sector->Lines) for (auto side : line->sidedef) if (side) {
        side->SetTexture(side_t::top, TexMan.GetTextureID("BRGCAVE", ETextureType::Wall));
        side->SetTexture(side_t::bottom, TexMan.GetTextureID("BRGCLIFF", ETextureType::Wall));
        side->SetTexture(side_t::mid, FTextureID());
    }
    return true;
}

void TickTerrainGeometryFixture()
{
    if (TerrainFixturePhase < 0 || primaryLevel->maptime < TerrainFixtureNextTic) return;
    if (TerrainFixtureCapture) {
        FString capture; capture.Format("screenshot terrain-%02d.png", TerrainFixturePhase - 1);
        AddCommandString(capture.GetChars());
        TerrainFixtureCapture = false;
        TerrainFixtureNextTic = primaryLevel->maptime + 30;
        return;
    }
    if (!TerrainFixtureActive) {
        int bindings = 0;
        for (int key = 0; key < 2291; ++key) {
            auto primary = TerrainSector(10000, key);
            auto liquid = TerrainSector(30000, key);
            auto deck = TerrainSector(40000, key);
            if (!primary || !liquid || !deck) continue;
            if (primaryLevel->PointInSector((key % 79) * 64.0 + 32.0,
                    (28 - key / 79) * 64.0 + 32.0) != primary)
                I_Error("Terrain fixture: primary sector does not contain its cell center");
            if (primary->e->XFloor.ffloors.Size() != 2) continue;
            for (auto floor : primary->e->XFloor.ffloors)
                if (floor->flags & (FF_SOLID | FF_SWIMMABLE)) I_Error("Terrain fixture: gameplay floor flags");
            ++bindings;
            const auto cell = FindStateCell(key % 79, key / 79);
            TerrainFixtureCell(key, !cell || cell->terrainFeature == BROGUE_FEATURE_WALL ? 0 : 1);
        }
        Printf("TERRAIN foundation bindings=%d expected=2291\n", bindings);
        if (bindings != 2291) { TerrainFixturePhase = -1; return; }
        TerrainFixtureHash = State.stateHash;
        TerrainFixtureActive = true;
    }
    // Hold the same view across reversible transitions around the player.
    static const int modes[] = {0,1,0,1,2,3,4,5,1};
    if (TerrainFixturePhase >= int(std::size(modes))) {
        static BrogueBridgeState checked;
        if (Api.getState(&checked) != BROGUE_BRIDGE_OK || checked.stateHash != TerrainFixtureHash
            || checked.absoluteTurn != State.absoluteTurn || checked.revision != State.revision)
            I_Error("Terrain fixture: authoritative state changed");
        Printf("TERRAIN foundation complete unchangedHash=%s turn=%llu revision=%llu\n",
            State.stateHash == TerrainFixtureHash ? "true" : "false",
            (unsigned long long)State.absoluteTurn, (unsigned long long)State.revision);
        TerrainFixturePhase = -1;
        AddCommandString("quit");
        return;
    }
    const int mode = modes[TerrainFixturePhase];
    // Project entities immediately onto the newly settled support plane.
    for (int dy = -2; dy <= 2; ++dy) for (int dx = -2; dx <= 2; ++dx) {
        int x = State.player.x + dx, y = State.player.y + dy;
        if (x < 1 || x >= 78 || y < 1 || y >= 28) continue;
        TerrainFixtureCell(y * 79 + x, dx == 0 && dy == 0 && mode == 0 ? 1 : mode);
    }
    SyncPlayer(); SyncItems(); SyncMonsters();
    if (std::abs(players[consoleplayer].mo->Z() - TerrainFixtureSupport[State.player.y * 79 + State.player.x]) > 0.01)
        I_Error("Terrain fixture: stale player support");
    Printf("TERRAIN phase=%d mode=%d playerZ=%.1f hash=%016llx\n", TerrainFixturePhase, mode,
        BrogueCellToWorld(State.player.x, State.player.y).Z, (unsigned long long)State.stateHash);
    ++TerrainFixturePhase;
    TerrainFixtureCapture = true;
    TerrainFixtureNextTic = primaryLevel->maptime + 5;
}
}

CCMD(brg_terrain_geometry_fixture)
{
    TerrainFixturePhase = 0;
    TerrainFixtureNextTic = 0;
    TerrainFixtureCapture = false;
}

namespace {
int TerrainSyncStep = -1, TerrainSyncNext = 0;
bool TerrainInputProbe = false;
void TickTerrainSyncProbe()
{
    if (TerrainSyncStep < 0 || primaryLevel->maptime < 35 || primaryLevel->maptime < TerrainSyncNext) return;
    if (!TerrainReady) I_Error("Terrain sync probe: no settled snapshot before scene");
    if (TerrainSyncStep == 0) AddCommandString("screenshot terrain-initial.png");
    if (TerrainSyncStep == 22) players[consoleplayer].mo->Angles.Yaw = DAngle::fromDeg(270);
    if (TerrainSyncStep == 23) AddCommandString("screenshot terrain-door-before.png");
    if (TerrainSyncStep < 24) {
        PerformAction(TerrainSyncStep < 3 ? BROGUE_ACTION_MOVE_N : TerrainSyncStep < 23
            ? BROGUE_ACTION_MOVE_W : BROGUE_ACTION_MOVE_S, "terrain-sync-probe");
        if (!TerrainReady || TerrainState.revision != State.revision) I_Error("Terrain sync probe: stale snapshot");
        auto pawn = players[consoleplayer].mo;
        auto desired = BrogueCellToWorld(State.player.x, State.player.y);
        if (!pawn || (pawn->Pos() - desired).Length() > 0.01) I_Error("Terrain sync probe: stale player projection");
        ++TerrainSyncStep;
        TerrainSyncNext = primaryLevel->maptime + (TerrainInputProbe && TerrainSyncStep == 24 ? 4 : 12);
    } else if (TerrainSyncStep == 24) {
        auto key = 24*79+18;
        if (State.player.x != 18 || State.player.y != 24 || TerrainBindings[key].mechanism
            || TerrainBindings[key].primary->ceilingplane.ZatPoint(18*64.0+32,4*64.0+32) != 224)
            I_Error("Terrain sync probe: opened door has stale geometry or model");
        if(TerrainInputProbe) {
            const auto &motion=TerrainBindings[key].motion;
            if(int(brg_fx_quality)>0 && (!TerrainBindings[key].outgoing || !motion.mechanism.Active(primaryLevel->maptime)))
                I_Error("Terrain input probe: panel was not animating");
            AddCommandString("screenshot terrain-door-during.png");
            const double pose=motion.mechanism.Value(primaryLevel->maptime);
            const auto turn=State.absoluteTurn;
            PerformAction(BROGUE_ACTION_WAIT,"terrain-animation-input");
            if(State.absoluteTurn!=turn+1 || motion.mechanism.Value(primaryLevel->maptime)!=pose)
                I_Error("Terrain input probe: action delayed or animation restarted");
        } else AddCommandString("screenshot terrain-door-after.png");
        Printf("TERRAIN_SYNC passed session=%llu revision=%llu turn=%llu hash=%016llx openedDoor=18,24 proxies=clean\n",
            (unsigned long long)State.session, (unsigned long long)State.revision,
            (unsigned long long)State.absoluteTurn, (unsigned long long)State.stateHash);
        ++TerrainSyncStep; TerrainSyncNext = primaryLevel->maptime + (TerrainInputProbe ? 21 : 8);
    } else if(TerrainInputProbe && TerrainSyncStep==25) {
        if(TerrainBindings[24*79+18].outgoing) I_Error("Terrain input probe: stale outgoing panel");
        AddCommandString("screenshot terrain-door-after.png");
        Printf("TERRAIN_INPUT passed turn=%llu immediateAction=true retargetContinuous=true\n",(unsigned long long)State.absoluteTurn);
        ++TerrainSyncStep; TerrainSyncNext=primaryLevel->maptime+5;
    } else { TerrainSyncStep = -1; AddCommandString("quit"); }
}
}
CCMD(brg_terrain_sync_smoke) { TerrainSyncStep = 0; TerrainSyncNext = 0; }
CCMD(brg_terrain_animation_input) { TerrainInputProbe=true; TerrainSyncStep=0; TerrainSyncNext=0; }

CCMD(brg_terrain_cell)
{
    if (argv.argc() != 3 || !TerrainReady) { Printf("Usage: brg_terrain_cell x y (settled scene required)\n"); return; }
    const int x = atoi(argv[1]), y = atoi(argv[2]);
    if (x < 0 || x >= 79 || y < 0 || y >= 29) return;
    const int cellKey = y * 79 + x;
    const auto &desired = State.cells[cellKey].appearance, &applied = TerrainState.applied[cellKey];
    const auto &b = TerrainBindings[cellKey];
    int blockers = 0;
    for (auto line : b.primary->Lines) if (line->backsector && (line->flags & (ML_BLOCKING | ML_BLOCK_PLAYERS))) ++blockers;
    Printf("TERRAIN cell=%d,%d session=%llu depth=%d desiredRevision=%llu appliedRevision=%llu equal=%d knowledge=%u/%u flags=%u/%u\n",
        x,y,(unsigned long long)State.session,State.depth,(unsigned long long)State.revision,
        (unsigned long long)TerrainState.revision,int(!memcmp(&desired,&applied,sizeof(applied))),
        desired.knowledge,applied.knowledge,desired.flags,applied.flags);
    Printf("TERRAIN layers structure=%u ground=%u liquid=%u deck=%u mechanism=%u fire=%u gas=%u volume=%u\n",
        applied.structure,applied.ground,applied.liquid,applied.deck,applied.mechanism,applied.fire,applied.gas,applied.gasVolume);
    Printf("TERRAIN planes bed=%.1f ceiling=%.1f liquid=%.1f deck=%.1f support=%.1f blockers=%d owners=%d,%d,%d,%d,%d material=%s\n",
        b.primary->floorplane.ZatPoint(0.0,0.0),b.primary->ceilingplane.ZatPoint(0.0,0.0),
        b.liquid->ceilingplane.ZatPoint(0.0,0.0),b.deck->ceilingplane.ZatPoint(0.0,0.0),b.support,blockers,
        int(b.mechanism!=nullptr),int(b.vegetation!=nullptr),int(b.fire!=nullptr),int(b.gas!=nullptr),int(b.lava!=nullptr),
        TerrainStyleFor(applied.ground ? applied.ground : applied.structure).floor);
}
