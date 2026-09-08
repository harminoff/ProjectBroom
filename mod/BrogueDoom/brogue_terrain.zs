// Native animation owns these models and their lifetimes. No physics or actions.
// Do not name this file TERRAIN: that basename is an engine definition lump.
class BrogueTerrainStone : Actor
{
    Default
    {
        Radius 1; Height 1;
        +NOINTERACTION; +NOBLOCKMAP; +NOGRAVITY;
        RenderStyle "Translucent";
    }
    States { Spawn: BRGD A -1; Stop; }
}
class BrogueTerrainWood : BrogueTerrainStone {}
class BrogueTerrainIce : BrogueTerrainStone {}
class BrogueTerrainVeil : BrogueTerrainStone {}
class BrogueTerrainCage : BrogueTerrainStone {}
class BrogueTerrainGate : BrogueTerrainStone {}
class BrogueTerrainStatueMarble : BrogueTerrainStone {}
class BrogueTerrainStatueCracked : BrogueTerrainStone {}
class BrogueTerrainStatueBroken : BrogueTerrainStone {}
class BrogueTerrainStatueDemon : BrogueTerrainStone {}
class BrogueTerrainTorch : BrogueTerrainStone {}
class BrogueTerrainManacleFloor : BrogueTerrainStone {}
class BrogueTerrainManacleCeiling : BrogueTerrainStone {}
class BrogueTerrainManacleCeilingDeep : BrogueTerrainStone {}
class BrogueTerrainManacleWall : BrogueTerrainStone {}
class BrogueTerrainTorchFlame : BrogueTerrainStone
{
    override void Tick()
    {
        Super.Tick();
        let quality = CVar.FindCVar('brg_fx_quality');
        double wave = quality && quality.GetInt() > 0 ? sin(Level.Time * 41 + Pos.X) : 0;
        Scale = (1 + wave * 0.04, 1 + wave * 0.09);
    }
    Default { RenderStyle "Add"; }
    States { Spawn: BRGD A -1 Bright; Stop; }
}
class BrogueTerrainHauntedTorchFlame : BrogueTerrainTorchFlame {}
// Settled physical hazard volumes remain visible at Basic quality.
class BrogueTerrainFire : BrogueTerrainStone
{
    Default { +NOINTERACTION; RenderStyle "Translucent"; }
    States { Spawn: BRGD A -1 Bright; Stop; }
}
class BrogueTerrainGas : BrogueTerrainStone
{
    // ZScript's Stencil property maps to STYLE_TranslucentStencil internally.
    Default { +NOINTERACTION; RenderStyle "Stencil"; }
    States { Spawn: BRGD A -1; Stop; }
}
class BrogueTerrainEmber : BrogueTerrainStone
{
    States { Spawn: BRGD A -1 Bright; Stop; }
}

class BrogueTerrainBloodwortStalk : BrogueTerrainStone {}
class BrogueTerrainBloodwortPod : BrogueTerrainStone {}
class BrogueTerrainBloodwortShell : BrogueTerrainStone {}
class BrogueTerrainBloodwortSpores : BrogueTerrainGas {}
