// All geometry and proxy ownership for settled, snapshot-driven terrain.
TerrainReconciler TerrainState;
struct TerrainBinding {
    sector_t *primary = nullptr, *liquid = nullptr, *deck = nullptr;
    double support = 0;
    AActor *mechanism = nullptr, *vegetation = nullptr, *fire = nullptr, *gas = nullptr, *lava = nullptr;
    AActor *outgoing = nullptr;
    AActor *torchFlame = nullptr;
    DVector3 torchPosition = {};
    DVector2 torchNormal = {};
    TerrainMotion motion;
    FString shoreWater, shoreGround, shoreDeck;
};
std::array<TerrainBinding, 2291> TerrainBindings;
std::vector<int> TerrainSectorKeys;
FLevelLocals *TerrainLevel = nullptr;
bool TerrainReady = false;
void ClearTerrainAnimations();

const TerrainStyle &TerrainStyleFor(unsigned tile)
{
    return TerrainStyles[tile < std::size(TerrainStyles) ? tile : 0];
}

bool IsBloodwortTile(unsigned tile) { return tile == TT_BLOODFLOWER_STALK || tile == TT_BLOODFLOWER_POD; }
unsigned BloodwortTile(const BrogueBridgeTerrainAppearance &a) {
    if (a.knowledge == BROGUE_TERRAIN_UNKNOWN) return 0;
    return IsBloodwortTile(a.ground) ? a.ground : IsBloodwortTile(a.structure) ? a.structure : 0;
}

bool IsStatueTile(unsigned tile)
{
    return tile == TT_STATUE_INERT || tile == TT_STATUE_DORMANT
        || tile == TT_STATUE_CRACKING || tile == TT_STATUE_INSTACRACK
        || tile == TT_STATUE_INERT_DOORWAY || tile == TT_STATUE_DORMANT_DOORWAY
        || tile == TT_DEMONIC_STATUE;
}

bool IsTorchTile(unsigned tile)
{
    return tile == TT_TORCH_WALL || tile == TT_HAUNTED_TORCH_DORMANT
        || tile == TT_HAUNTED_TORCH_TRANSITIONING || tile == TT_HAUNTED_TORCH;
}

// Use real shared polygons, including cave contours, rather than a cell-edge guess.
bool MountTerrainTorch(int key, bool againstWall = false)
{
    auto &b = TerrainBindings[key];
    double best = 0;
    int bestNeighbor = -1;
    for (auto line : b.primary->Lines) {
        auto other = line->frontsector == b.primary ? line->backsector : line->frontsector;
        if (!other) continue;
        const int index = int(other - &primaryLevel->sectors[0]);
        if (index < 0 || index >= int(TerrainSectorKeys.size())) continue;
        const int neighbor = TerrainSectorKeys[index];
        if (neighbor < 0) continue;
        const auto &a = TerrainState.applied[neighbor];
        if (a.knowledge == BROGUE_TERRAIN_UNKNOWN || bool(a.flags & BROGUE_APPEARANCE_WALL) != againstWall) continue;
        const double dx = line->v2->fX()-line->v1->fX(), dy = line->v2->fY()-line->v1->fY();
        const double length = std::sqrt(dx*dx+dy*dy);
        if (length < 12 || length < best || (length == best && neighbor <= bestNeighbor)) continue;
        const double x = (line->v1->fX()+line->v2->fX())*.5, y = (line->v1->fY()+line->v2->fY())*.5;
        DVector2 normal(-dy/length, dx/length);
        if (normal.X*((neighbor%79)*64+32-x)+normal.Y*((28-neighbor/79)*64+32-y) < 0) normal *= -1;
        if (againstWall) normal *= -1;
        b.torchNormal = normal;
        b.torchPosition = DVector3(x+normal.X, y+normal.Y, againstWall ? b.support : TerrainBindings[neighbor].support);
        best = length; bestNeighbor = neighbor;
    }
    return best > 0;
}

bool IsManacleTile(unsigned tile) { return tile >= TT_MANACLE_TL && tile <= TT_MANACLE_R; }
void TerrainActor(AActor *&actor, const char *className, DVector3 position);

void PositionManacle(int key, unsigned tile, AActor *&actor)
{
    if (!actor || !IsManacleTile(tile)) return;
    auto &b=TerrainBindings[key];
    // Counter OBJ pixel correction so ceiling attachments meet the real plane.
    actor->Scale.Y=primaryLevel->info->pixelstretch;
    if(tile==TT_MANACLE_TL || tile==TT_MANACLE_TR) {
        if(State.depth>1) TerrainActor(actor,"BrogueTerrainManacleCeilingDeep",actor->Pos());
        actor->Scale.Y=primaryLevel->info->pixelstretch;
    } else if(tile>=TT_MANACLE_T) {
        const auto torchPosition=b.torchPosition;
        const auto torchNormal=b.torchNormal;
        if(MountTerrainTorch(key,true)) {
            actor->SetOrigin(b.torchPosition,false);
            actor->Angles.Yaw=DAngle::fromRad(std::atan2(b.torchNormal.Y,b.torchNormal.X));
        } else {
            // An isolated remembered wall manacle has no safe wall to attach to.
            TerrainActor(actor,"BrogueTerrainManacleFloor",actor->Pos());
            actor->Scale.Y=primaryLevel->info->pixelstretch;
        }
        b.torchPosition=torchPosition;
        b.torchNormal=torchNormal;
    }
}

sector_t *FindTerrainSector(int tag)
{
    auto iterator = primaryLevel->GetSectorTagIterator(tag);
    int index = iterator.Next();
    if (index < 0 || iterator.Next() >= 0) return nullptr;
    return &primaryLevel->sectors[index];
}

void ClearTerrainBindings()
{
    TerrainState.Clear(); TerrainReady = false; TerrainLevel = nullptr;
    // Avoid a megabyte-sized aggregate temporary on the Windows game stack.
    for (auto &binding : TerrainBindings) binding = {};
    TerrainSectorKeys.clear();
    ClearTerrainAnimations();
}

void SetTerrainPlane(sector_t *sector, int plane, double z, const char *texture)
{
    auto &equation = plane == sector_t::floor ? sector->floorplane : sector->ceilingplane;
    equation.ChangeHeight(z - equation.ZatPoint(0.0, 0.0));
    sector->SetPlaneTexZ(plane, z, true);
    sector->SetTexture(plane, TexMan.GetTextureID(texture, ETextureType::Flat));
}

double TerrainSupport(int x, int y)
{
    return TerrainBindings[y * 79 + x].support;
}

void TerrainActor(AActor *&actor, const char *className, DVector3 position)
{
    PClassActor *type = *className ? PClass::FindActor(className) : nullptr;
    if (actor && ((actor->ObjectFlags & OF_EuthanizeMe) || actor->GetClass() != type)) {
        if (!(actor->ObjectFlags & OF_EuthanizeMe)) actor->Destroy();
        actor = nullptr;
    }
    if (type && !actor) actor = Spawn(primaryLevel, type, position, NO_REPLACE);
    if (actor) {
        actor->flags &= ~(MF_SOLID | MF_SHOOTABLE | MF_SPECIAL);
        actor->SetOrigin(position, false);
    }
}

void ApplyTerrainCell(int key, const BrogueBridgeTerrainAppearance &a)
{
    auto &binding = TerrainBindings[key];
    bool wall = a.flags & BROGUE_APPEARANCE_WALL;
    bool bridge = a.flags & BROGUE_APPEARANCE_BRIDGE, ice = a.flags & BROGUE_APPEARANCE_ICE;
    bool hole = a.flags & BROGUE_APPEARANCE_HOLE, flood = a.flags & BROGUE_APPEARANCE_FLOOD;
    double bed = hole ? -128 : a.bedKind == BROGUE_LIQUID_DEEP_WATER ? -24
        : a.bedKind == BROGUE_LIQUID_SHALLOW_WATER ? -8 : 0;
    double surface = flood ? (a.liquidKind == BROGUE_LIQUID_DEEP_WATER ? 24 : 8) : 0;
    bool water = a.liquid && a.liquidKind != BROGUE_LIQUID_NONE;
    binding.support = bridge || ice ? 0 : bed;
    const char *floor = hole ? "BRGVOID" : water || ice ? "BRGEARTH"
        : TerrainStyleFor(a.ground ? a.ground : a.structure).floor;
    SetTerrainPlane(binding.primary, sector_t::floor, bed, floor);
    SetTerrainPlane(binding.primary, sector_t::ceiling, wall ? bed : State.depth > 1 ? 352 : 224,
        State.depth > 1 && !wall ? "F_SKY1" : "BRGCEIL");
    SetTerrainPlane(binding.liquid, sector_t::floor, water ? surface - 1 : -520, TerrainStyleFor(a.liquid).floor);
    SetTerrainPlane(binding.liquid, sector_t::ceiling, water ? surface : -512, TerrainStyleFor(a.liquid).floor);
    SetTerrainPlane(binding.deck, sector_t::floor, bridge || ice ? -4 : -520, TerrainStyleFor(a.deck).floor);
    SetTerrainPlane(binding.deck, sector_t::ceiling, bridge || ice ? 0 : -512, TerrainStyleFor(a.deck).floor);
}

#include "brogue_shoreline_frontend.inc"
#include "brogue_terrain_animation.inc"

void SyncTerrainOwnedActors()
{
    for (int key = 0; key < 2291; ++key) {
        auto &binding = TerrainBindings[key];
        const auto &a = TerrainState.applied[key];
        DVector3 position((key % 79) * 64.0 + 32, (28 - key/79) * 64.0 + 32, binding.support);
        const bool visible = a.knowledge == BROGUE_TERRAIN_VISIBLE;
        const bool known = a.knowledge != BROGUE_TERRAIN_UNKNOWN;
        const unsigned mechanical = a.mechanism ? a.mechanism : a.structure;
        const bool torch = IsTorchTile(mechanical);
        const bool mounted = torch && known && MountTerrainTorch(key);
        TerrainActor(binding.mechanism, known && !IsBloodwortTile(mechanical) && (!torch || mounted) ? TerrainStyleFor(mechanical).actor : "", mounted ? binding.torchPosition : position);
        if (binding.mechanism && torch) {
            binding.mechanism->Angles.Yaw = DAngle::fromRad(std::atan2(binding.torchNormal.Y,binding.torchNormal.X));
        } else if (binding.mechanism) {
            const int x = key % 79, y = key / 79;
            auto open = [&](int dx, int dy) {
                const int nx = x + dx, ny = y + dy;
                return nx >= 0 && nx < 79 && ny >= 0 && ny < 29
                    && !(TerrainState.applied[ny * 79 + nx].flags & BROGUE_APPEARANCE_WALL);
            };
            binding.mechanism->Angles.Yaw = DAngle::fromDeg(IsStatueTile(mechanical)
                ? (open(0, 1) ? 270 : open(1, 0) ? 0 : open(0, -1) ? 90 : 180)
                : (open(1, 0) || open(-1, 0) ? 0 : 90));
        }
        TerrainActor(binding.vegetation, known ? TerrainStyleFor(BloodwortTile(a) ? BloodwortTile(a) : a.ground).actor : "", position);
        PositionManacle(key,a.ground,binding.vegetation);
        PositionManacle(key,mechanical,binding.mechanism);
        if (binding.mechanism && (a.flags & BROGUE_APPEARANCE_DEPRESSED)) binding.mechanism->SetOrigin(position + DVector3(0,0,-2), false);
        // These independent owners allow gas, flames and liquids to coexist.
        TerrainActor(binding.fire, visible && a.fire ? "BrogueTerrainFire" : "", position);
        TerrainActor(binding.gas, visible && (a.gasVolume || binding.motion.gas.Value(primaryLevel->maptime) > 0) ? (binding.motion.gasTile == TT_HEALING_CLOUD ? "BrogueTerrainBloodwortSpores" : "BrogueTerrainGas") : "", position);
        TerrainActor(binding.lava, visible && a.liquidKind == BROGUE_LIQUID_LAVA ? "BrogueLavaFx" : "", position);
        TerrainActor(binding.torchFlame, visible && mounted ? (mechanical == TT_HAUNTED_TORCH
            ? "BrogueTerrainHauntedTorchFlame" : "BrogueTerrainTorchFlame") : "",
            // OBJ rendering compensates for the map's pixel stretch; actor origins do not.
            binding.torchPosition+DVector3(binding.torchNormal.X*8,binding.torchNormal.Y*8,68/primaryLevel->info->pixelstretch));
        if (binding.gas) {
            binding.gas->Alpha = (std::min)(0.8, 0.1 + a.gasVolume / 120.0);
            binding.gas->fillcolor = PalEntry(a.gasRed, a.gasGreen, a.gasBlue);
        }
    }
}

bool ReconcileTerrain()
{
    if (!Started || !primaryLevel || State.depth != primaryLevel->levelnum || TerrainFixtureActive) return false;
    // Brogue owns revisits. Never serialize a second, stale copy of its world in a Doom hub.
    primaryLevel->flags2 |= LEVEL2_FORGETSTATE;
    if (TerrainLevel != primaryLevel) {
        ClearTerrainBindings();
        // Legacy generated maps remain supported until regenerated by the compiler.
        if (!FindTerrainSector(30000)) return false;
        TerrainSectorKeys.assign(primaryLevel->sectors.Size(), -1);
        for (int key = 0; key < 2291; ++key) {
            auto &binding = TerrainBindings[key];
            binding.primary = FindTerrainSector(10000 + key);
            binding.liquid = FindTerrainSector(30000 + key);
            binding.deck = FindTerrainSector(40000 + key);
            if (!binding.primary || !binding.liquid || !binding.deck
                || primaryLevel->PointInSector((key%79)*64.0+32, (28-key/79)*64.0+32) != binding.primary)
                I_Error("Brogue terrain: incomplete coordinate bindings at %d", key);
            TerrainSectorKeys[binding.primary - &primaryLevel->sectors[0]] = key;
        }
        TerrainLevel = primaryLevel;
        // Replace map-load model placement with snapshot-owned components.
        auto iterator = primaryLevel->GetThinkerIterator<AActor>();
        auto prop = PClass::FindActor("BroguePropBase"), door = PClass::FindActor("BrogueDoorMarker");
        while (auto actor = iterator.Next()) if ((prop && actor->IsA(prop)) || (door && actor->IsA(door))) actor->Destroy();
    }
    TerrainReconciler::Batch batch;
    auto result = TerrainState.Prepare(State, primaryLevel->levelnum, batch);
    if (result == TerrainReconciler::Rejected) return TerrainReady;
    if (result == TerrainReconciler::Ready) {
        for (int key : batch.changed) {
            PrepareTerrainAnimation(key, TerrainState.applied[key], State.cells[key].appearance, batch.initial);
            ApplyTerrainCell(key, State.cells[key].appearance);
        }
        // Commit the complete geometry first, then recompute shared surfaces.
        for (int key : batch.boundaries) for (auto line : TerrainBindings[key].primary->Lines) {
            if (line->backsector) line->flags &= ~(ML_BLOCKING | ML_BLOCK_PLAYERS);
            for (int index = 0; index < 2; ++index) if (auto side = line->sidedef[index]) {
                auto opposite = index == 0 ? line->backsector : line->frontsector;
                int otherKey = opposite ? TerrainSectorKeys[opposite - &primaryLevel->sectors[0]] : key;
                const auto &own = State.cells[key].appearance;
                const auto &other = State.cells[otherKey >= 0 ? otherKey : key].appearance;
                const auto &wall = other.flags & BROGUE_APPEARANCE_WALL ? other : own;
                const char *edge = (own.flags | other.flags) & BROGUE_APPEARANCE_HOLE ? "BRGCLIFF"
                    : own.liquid || other.liquid ? "BRGEARTH" : TerrainStyleFor(wall.structure).wall;
                side->SetTexture(side_t::top, TexMan.GetTextureID(TerrainStyleFor(wall.structure).wall, ETextureType::Wall));
                side->SetTexture(side_t::bottom, TexMan.GetTextureID(edge, ETextureType::Wall));
                if (line->backsector) side->SetTexture(side_t::mid, FTextureID());
            }
        }
        for (int key : batch.changed) {
            P_RecalculateAttached3DFloors(TerrainBindings[key].liquid);
            P_RecalculateAttached3DFloors(TerrainBindings[key].deck);
            P_Recalculate3DFloors(TerrainBindings[key].primary);
        }
        TerrainState.Commit(State); TerrainReady = true;
        UpdateShorelines(batch.changed, batch.initial);
        if (brg_debug) Printf("TERRAIN commit session=%llu depth=%d revision=%llu cells=%zu boundaries=%zu initial=%d\n",
            (unsigned long long)State.session, State.depth, (unsigned long long)State.revision,
            batch.changed.size(), batch.boundaries.size(), int(batch.initial));
    }
    if (result == TerrainReconciler::Ready) SyncTerrainOwnedActors();
    if (result == TerrainReconciler::Ready) TickTerrainAnimations(true);
    return TerrainReady;
}
