// Only the native copied-state projection creates these non-interacting meshes.
class BrogueSearchPlate : Actor
{
    Default
    {
        Radius 1;
        Height 1;
        +NOBLOCKMAP;
        +NOGRAVITY;
        +NOINTERACTION;
        RenderStyle "Translucent";
    }
    States { Spawn: BRGD A -1; Stop; }
}

class BrogueSearchFire : BrogueSearchPlate {}
class BrogueSearchFlood : BrogueSearchPlate {}
class BrogueSearchNet : BrogueSearchPlate {}
class BrogueSearchAlarm : BrogueSearchPlate {}
class BrogueSearchVent : BrogueSearchPlate {}
class BrogueSearchLever : BrogueSearchPlate {}
class BrogueSearchRim : BrogueSearchPlate {}
class BrogueSearchCover : BrogueSearchPlate {}
