// Included after settled plane helpers and before terrain animation.
#include "shoreline.h"
bool ShorelineEnabled = true;
int ShorelineQuality = -1;

FString ShorelineMaterial(const char *base, unsigned mask, int water=0, bool still=false) {
    char family=0;
    if(water) family=water==BROGUE_LIQUID_DEEP_WATER ? (still?'T':'D') : (still?'S':'W');
    else if(mask) {
        if(!strcmp(base,"BRGEARTH") || !strcmp(base,"BRGSLDG")) family='E';
        else if(!strcmp(base,"BRGMOSS")) family='M';
        else if(!strcmp(base,"BRGFLAG")) family='F';
        else if(!strcmp(base,"BRGBRID")) family='B';
    }
    FString name;
    if(family) name.Format("BS%c%02X",family,mask);
    return name;
}

void UpdateShorelines(const std::vector<int> &changed, bool force=false) {
    force=force || ShorelineEnabled!=bool(brg_shorelines) || ShorelineQuality!=int(brg_fx_quality);
    ShorelineEnabled=bool(brg_shorelines); ShorelineQuality=int(brg_fx_quality);
    auto affected=Shoreline::Affected(changed);
    for(int key=0;key<2291;++key) if(force || affected[key]) {
        auto &b=TerrainBindings[key];
        const auto &a=TerrainState.applied[key];
        const auto masks=ShorelineEnabled ? Shoreline::Resolve(TerrainState.applied,key) : Shoreline::Masks{};
        const char *ground=a.flags&BROGUE_APPEARANCE_HOLE ? "BRGVOID" : a.liquid || (a.flags&BROGUE_APPEARANCE_ICE) ? "BRGEARTH"
            : TerrainStyleFor(a.ground ? a.ground : a.structure).floor;
        b.shoreGround=ShorelineMaterial(ground,masks.ground);
        b.shoreDeck=ShorelineMaterial(TerrainStyleFor(a.deck).floor,masks.ground);
        b.shoreWater=ShorelineEnabled && Shoreline::Water(a) && !Shoreline::Deck(a)
            ? ShorelineMaterial("BRGWATR",masks.water,a.liquidKind,a.knowledge!=BROGUE_TERRAIN_VISIBLE || ShorelineQuality==0) : FString();
        b.primary->SetTexture(sector_t::floor,TexMan.GetTextureID(b.shoreGround.IsNotEmpty() ? b.shoreGround.GetChars() : ground,ETextureType::Flat));
        b.motion.dirty=true;
    }
}
