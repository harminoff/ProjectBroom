// Cosmetic ownership and timelines. Included inside the terrain reconciler.
struct TerrainFragment {
    AActor *actor = nullptr;
    int cell = 0;
    double born = 0, life = 21;
    DVector3 origin, travel;
    bool veil = false;
};
std::vector<TerrainFragment> TerrainFragments;
uint64_t TerrainEventRevision = 0;
int TerrainAnimationTic = -1;

void ClearTerrainAnimations() {
    // Level teardown owns actor destruction; never dereference old-level actors.
    TerrainFragments.clear(); TerrainEventRevision = 0; TerrainAnimationTic = -1;
}
void RemoveTerrainActor(AActor *&actor) {
    if (actor && !(actor->ObjectFlags & OF_EuthanizeMe)) actor->Destroy();
    actor = nullptr;
}
DVector3 TerrainPosition(int key) {
    return DVector3((key%79)*64.0+32,(28-key/79)*64.0+32,TerrainBindings[key].support);
}
void ClearTerrainFragments(int key) {
    for (auto &f : TerrainFragments) if (f.cell == key) RemoveTerrainActor(f.actor);
    TerrainFragments.erase(std::remove_if(TerrainFragments.begin(),TerrainFragments.end(),
        [](const auto &f) { return !f.actor; }),TerrainFragments.end());
}
void SpawnTerrainFragments(int key, const char *type, bool veil = false) {
    if (int(brg_fx_quality) == 0) return;
    const int count = veil ? 1 : int(brg_fx_quality) > 1 ? 12 : 6;
    for (int i = 0; i < count && TerrainFragments.size() < 256; ++i) {
        // Coordinate-based cosmetic layout, with no RNG calls or gameplay data.
        const unsigned n = unsigned(key*37+i*113);
        TerrainFragment f;
        f.cell = key; f.born = primaryLevel->maptime; f.veil = veil;
        f.origin = TerrainPosition(key) + DVector3(veil ? 0 : int(n%49)-24,
            veil ? 0 : int((n/7)%49)-24, veil ? 0 : 4+(i%3)*5);
        f.travel = DVector3(int(n%31)-15,int((n/3)%31)-15,-70-(i%4)*12);
        TerrainActor(f.actor,type,f.origin);
        if (f.actor) {
            if (!strcmp(type,"BrogueTerrainEmber")) { f.life=12; f.actor->Scale=DVector2(.18,.18); }
            f.actor->RenderStyle = STYLE_Translucent;
            f.actor->Angles.Yaw = DAngle::fromDeg(veil ? 0 : n%360);
            TerrainFragments.push_back(f);
        }
    }
}

void PrepareTerrainAnimation(int key, const BrogueBridgeTerrainAppearance &old,
    const BrogueBridgeTerrainAppearance &a, bool initial) {
    auto &b = TerrainBindings[key]; auto &m = b.motion;
    m.dirty = true;
    const double now = primaryLevel->maptime;
    const bool visible = a.knowledge == BROGUE_TERRAIN_VISIBLE;
    const bool animate = !initial && visible && old.knowledge == BROGUE_TERRAIN_VISIBLE && int(brg_fx_quality) > 0;
    const bool water = a.liquid && a.liquidKind != BROGUE_LIQUID_NONE;
    const bool deck = a.flags & (BROGUE_APPEARANCE_BRIDGE | BROGUE_APPEARANCE_ICE);
    const double bed = a.flags & BROGUE_APPEARANCE_HOLE ? -128 : a.bedKind == BROGUE_LIQUID_DEEP_WATER ? -24 : a.bedKind == BROGUE_LIQUID_SHALLOW_WATER ? -8 : 0;
    const double surface = a.flags & BROGUE_APPEARANCE_FLOOD ? (a.liquidKind == BROGUE_LIQUID_DEEP_WATER ? 24 : 8) : 0;
    const double density = visible && a.gasVolume ? (std::min)(0.8,0.1+a.gasVolume/120.0) : 0;
    const unsigned oldPlant = BloodwortTile(old), plant = BloodwortTile(a);
    const char *model = IsBloodwortTile(a.structure) ? "" : TerrainStyleFor(a.mechanism ? a.mechanism : a.structure).actor;
    const bool observedPlant = animate && State.revision == TerrainState.revision + 1;
    if (oldPlant != plant || !visible || (old.gas && old.gas != a.gas)) ClearTerrainFragments(key);
    if (observedPlant && plant == TT_BLOODFLOWER_POD && oldPlant != plant) {
        m.plant.Settle(0.05); m.plant.Retarget(1,now,21);
    } else if (!observedPlant || !plant) m.plant.Settle(1);
    if (observedPlant && oldPlant == TT_BLOODFLOWER_POD && !plant && a.gas == TT_HEALING_CLOUD && a.gasVolume && !a.fire)
        SpawnTerrainFragments(key,"BrogueTerrainBloodwortShell");
    auto retarget = [&](TerrainTween &t, double target, int tics) {
        if (animate) t.Retarget(target,now,tics); else t.Settle(target);
    };
    if (!animate) {
        ClearTerrainFragments(key); RemoveTerrainActor(b.outgoing);
        m.activityStart = m.revealStart = -1000;
    }
    // Reuse the same outgoing panel when a rapid subsequent promotion reverses it.
    if (animate && *model && !b.mechanism && b.outgoing && b.outgoing->GetClass() == PClass::FindActor(model)) {
        b.mechanism = b.outgoing; b.outgoing = nullptr;
    }
    if (animate && b.mechanism && b.mechanism->GetClass() != (*model ? PClass::FindActor(model) : nullptr)) {
        RemoveTerrainActor(b.outgoing);
        // Promoted statues become cracks/rubble immediately. Never animate a
        // whole sculpture rising like a retracting door panel.
        if (IsStatueTile(old.structure) || IsTorchTile(old.structure) || IsManacleTile(old.structure) || IsBloodwortTile(old.structure)) RemoveTerrainActor(b.mechanism);
        else { b.outgoing = b.mechanism; b.mechanism = nullptr; }
    }
    retarget(m.mechanism,*model ? 1 : 0,12);
    retarget(m.lever,TerrainStyleFor(a.mechanism).motion&4 ? 28 : 0,12);
    retarget(m.plate,a.flags&BROGUE_APPEARANCE_DEPRESSED ? 2 : 0,12);
    retarget(m.liquidHeight,water ? surface : bed-2,21);
    retarget(m.liquidAlpha,water ? 1 : 0,21);
    retarget(m.deckAlpha,deck ? 1 : 0,21);
    retarget(m.gas,density,12);
    retarget(m.fire,visible && a.fire ? 1 : 0,12);
    retarget(m.gasR,a.gas ? a.gasRed : m.gasR.target,12); retarget(m.gasG,a.gas ? a.gasGreen : m.gasG.target,12); retarget(m.gasB,a.gas ? a.gasBlue : m.gasB.target,12);
    if (water || !animate) m.liquidTile = a.liquid;
    if (deck || !animate) m.deckTile = a.deck;
    if (a.gas || !animate) m.gasTile = a.gas;
    if (!animate) return;
    if (IsStatueTile(old.structure) && strcmp(TerrainStyleFor(old.structure).actor, model)) {
        ClearTerrainFragments(key);
        SpawnTerrainFragments(key,"BrogueTerrainStone");
    }
    if(old.fire && !a.fire) SpawnTerrainFragments(key,"BrogueTerrainEmber");
    if (old.mechanism != a.mechanism || ((old.flags^a.flags)&BROGUE_APPEARANCE_DEPRESSED)) m.activityStart = now;
    const bool wallChange = ((old.flags^a.flags)&BROGUE_APPEARANCE_WALL) != 0;
    const bool groundChange = ((old.flags^a.flags)&BROGUE_APPEARANCE_HOLE) != 0;
    const bool deckChange = old.deck != a.deck;
    if (wallChange || groundChange || deckChange || (old.ground && old.ground != a.ground && !oldPlant && !plant)) {
        ClearTerrainFragments(key);
        if ((old.flags&BROGUE_APPEARANCE_WALL) && a.mechanism) {
            m.revealStart = now; SpawnTerrainFragments(key,"BrogueTerrainVeil",true);
        } else if (wallChange || groundChange) SpawnTerrainFragments(key,"BrogueTerrainStone");
        else if ((old.flags|a.flags)&BROGUE_APPEARANCE_ICE) SpawnTerrainFragments(key,"BrogueTerrainIce");
        else SpawnTerrainFragments(key,"BrogueTerrainWood");
    }
}

void ObserveTerrainAnimationEvents(const BrogueBridgeTurnResult &result) {
    if (!TerrainReady || result.revision <= TerrainEventRevision || int(brg_fx_quality) == 0) return;
    TerrainEventRevision = result.revision;
    for (unsigned i=0; i<result.eventCount; ++i) {
        const auto &event = result.events[i];
        if (event.type != BROGUE_EVENT_TERRAIN_ACTIVATED || event.x < 0 || event.x >= 79 || event.y < 0 || event.y >= 29) continue;
        const int key = event.y*79+event.x;
        if (State.cells[key].appearance.knowledge == BROGUE_TERRAIN_VISIBLE)
            TerrainBindings[key].motion.activityStart = primaryLevel->maptime;
    }
}

void TerrainAnimatedPlane(TerrainBinding &b, sector_t *control, double z, double alpha, const char *texture, double thickness) {
    const double top = alpha > 0.001 ? z : -512;
    SetTerrainPlane(control,sector_t::floor,top-thickness,texture);
    SetTerrainPlane(control,sector_t::ceiling,top,texture);
    for (auto floor : b.primary->e->XFloor.ffloors) if (floor->model == control) {
        // A persistent alpha mask must keep the bed in the translucent floor
        // clipping path even when the cosmetic appearance tween has settled.
        const int maximum = control==b.liquid && b.shoreWater.IsNotEmpty() ? 254 : 255;
        floor->alpha = int(std::clamp(alpha,0.0,1.0)*maximum);
        if (floor->alpha < 255) floor->flags |= FF_TRANSLUCENT;
        else floor->flags &= ~FF_TRANSLUCENT;
    }
    // Alpha participates in clipping; update originals before rebuilding copies.
    P_RecalculateAttached3DFloors(control);
}

void TickTerrainAnimations(bool force = false) {
    if (!TerrainReady || TerrainFixtureActive || !primaryLevel) return;
    if(ShorelineEnabled!=bool(brg_shorelines) || ShorelineQuality!=int(brg_fx_quality)) UpdateShorelines({},true);
    const int now = primaryLevel->maptime;
    if (!force && TerrainAnimationTic == now) return;
    TerrainAnimationTic = now;
    const bool basic = int(brg_fx_quality) == 0;
    for (int key=0; key<2291; ++key) {
        auto &b = TerrainBindings[key]; auto &m = b.motion;
        const auto &a = TerrainState.applied[key];
        const bool visible = a.knowledge == BROGUE_TERRAIN_VISIBLE;
        if (basic && m.Active(now)) {
            m.dirty = true;
            for (auto t : {&m.liquidHeight,&m.liquidAlpha,&m.deckAlpha,&m.gas,&m.fire,&m.mechanism,&m.gasR,&m.gasG,&m.gasB,&m.lever,&m.plate,&m.plant}) t->Settle(t->target);
            m.activityStart = m.revealStart = -1000;
        }
        // Commit endpoints even when a slow frame skips several engine tics.
        const bool unstable = visible && !basic && (TerrainStyleFor(a.deck).motion & 3);
        const bool moving = m.Active(now) || m.Active(m.sampledAt) || unstable || (visible && !basic && (b.fire || b.gas));
        if (!m.dirty && !moving && !b.outgoing) continue;
        const bool planes = m.dirty || m.liquidHeight.Active(m.sampledAt) || m.liquidAlpha.Active(m.sampledAt) || m.deckAlpha.Active(m.sampledAt) || unstable;
        m.dirty = false; m.sampledAt = now;
        if(planes) {
        TerrainAnimatedPlane(b,b.liquid,m.liquidHeight.Value(now),m.liquidAlpha.Value(now),b.shoreWater.IsNotEmpty() ? b.shoreWater.GetChars() : TerrainStyleFor(m.liquidTile).floor,1);
        const double deckZ = -8*(1-m.deckAlpha.Value(now)) + (unstable ? std::sin(now*.6+key)*.35 : 0);
        TerrainAnimatedPlane(b,b.deck,deckZ,m.deckAlpha.Value(now),b.shoreDeck.IsNotEmpty() ? b.shoreDeck.GetChars() : TerrainStyleFor(m.deckTile).floor,4);
        }
        const auto position = TerrainPosition(key);
        const double mechanism = m.mechanism.Value(now);
        const double pulse = visible && !basic && now-m.activityStart < 12 ? std::sin((now-m.activityStart)*3.141592653589793/12) : 0;
        if (b.mechanism) {
            b.mechanism->RenderStyle = STYLE_Translucent;
            const double reveal = std::clamp((now-m.revealStart)/21.0,0.0,1.0);
            b.mechanism->Alpha = reveal;
            const bool panel = b.mechanism->IsA(PClass::FindActor("BrogueDoorMarker"))
                || b.mechanism->IsA(PClass::FindActor("BrogueTerrainGate")) || b.mechanism->IsA(PClass::FindActor("BrogueTerrainCage"));
            b.mechanism->SetOrigin(IsManacleTile(a.structure) ? b.mechanism->Pos() : IsTorchTile(a.structure) ? b.torchPosition
                : position + DVector3(0,0,panel ? (1-mechanism)*80 : -2*pulse-m.plate.Value(now)),false);
            if (b.mechanism->IsA(PClass::FindActor("BrogueSearchLever")))
                b.mechanism->Angles.Pitch = DAngle::fromDeg(-m.lever.Value(now)-pulse*12);
        }
        if (b.outgoing) {
            b.outgoing->RenderStyle = STYLE_Translucent;
            b.outgoing->Alpha = mechanism;
            b.outgoing->SetOrigin(position+DVector3(0,0,(1-mechanism)*80),false);
            if (!visible || basic || !m.mechanism.Active(now)) RemoveTerrainActor(b.outgoing);
        }
        if (b.vegetation && BloodwortTile(a)) {
            const double growth = m.plant.Value(now);
            b.vegetation->Scale = DVector2(growth,growth);
            b.vegetation->SetOrigin(position,false);
        }
        if (b.gas) {
            b.gas->Scale = DVector2(1+(basic?0:.035*std::sin(now*.07+key)),1);
            // Bounded analytical drift; never accumulates velocity or calls RNG.
            b.gas->SetOrigin(position+DVector3(basic?0:2*std::sin(now*.09+key),
                basic?0:2*std::cos(now*.07+key),basic?0:2*std::sin(now*.06+key)),false);
            b.gas->Angles.Yaw=DAngle::fromDeg((key*137)%360+(basic?0:6*std::sin(now*.025+key)));
            b.gas->Alpha = m.gas.Value(now);
            b.gas->fillcolor = PalEntry(int(m.gasR.Value(now)),int(m.gasG.Value(now)),int(m.gasB.Value(now)));
            if (!visible || (!a.gasVolume && !m.gas.Active(now))) RemoveTerrainActor(b.gas);
        }
        if (b.fire) {
            b.fire->Scale = DVector2(1,basic ? 1 : 1+.12*std::sin(now*.8+key));
            b.fire->Alpha = m.fire.Value(now);
            if (!visible || (!a.fire && !m.fire.Active(now))) RemoveTerrainActor(b.fire);
        }
    }
    for (auto &f : TerrainFragments) {
        if (basic || TerrainState.applied[f.cell].knowledge != BROGUE_TERRAIN_VISIBLE || now-f.born >= f.life) {
            RemoveTerrainActor(f.actor); continue;
        }
        const double t = std::clamp((now-f.born)/f.life,0.0,1.0);
        f.actor->Alpha = 1-t*t;
        if (!f.veil) {
            f.actor->SetOrigin(f.origin+DVector3(f.travel.X*t,f.travel.Y*t,18*std::sin(t*3.141592653589793)+f.travel.Z*t*t),false);
            f.actor->Angles.Pitch = DAngle::fromDeg(t*145);
            f.actor->Angles.Roll = DAngle::fromDeg(t*90);
        }
    }
    TerrainFragments.erase(std::remove_if(TerrainFragments.begin(),TerrainFragments.end(),[](auto &f){return !f.actor;}),TerrainFragments.end());
}
