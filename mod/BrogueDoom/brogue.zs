// First GZDoom runtime slice for the Brogue map pipeline.
// Map topology is generated before launch; this code validates and consumes
// the UDMF cell metadata and provides hub-safe stair travel.

class BrogueTravelState : Inventory
{
    int LandingKind;

    Default
    {
        Inventory.MaxAmount 1;
        Inventory.Amount 1;
        +INVENTORY.UNDROPPABLE;
        +INVENTORY.UNTOSSABLE;
    }

    States
    {
        Spawn:
            TNT1 A -1;
            Stop;
    }
}

class BrogueStair : Actor
{
    bool Armed;
    bool WasOccupied;
    int ArmDelay;

    override void BeginPlay()
    {
        Super.BeginPlay();
        Disarm();
    }

    void Disarm()
    {
        Armed = false;
        WasOccupied = true;
        ArmDelay = 4;
    }

    Actor OccupyingPlayer()
    {
        for (int playerIndex = 0; playerIndex < MAXPLAYERS; playerIndex++)
        {
            if (!playeringame[playerIndex] || players[playerIndex].mo == null)
                continue;

            Actor pawn = players[playerIndex].mo;
            double dx = pawn.Pos.X - Pos.X;
            double dy = pawn.Pos.Y - Pos.Y;
            if (dx * dx + dy * dy <= 20.0 * 20.0)
                return pawn;
        }
        return null;
    }

    override void Tick()
    {
        Super.Tick();

        // The source-integrated frontend recognizes this native CVar and
        // performs authoritative stair traversal through Brogue CE itself.
        // Keep the ZScript fallback only for the stock GZDoom visual build.
        if (CVar.FindCVar('brg_seed'))
            return;

        if (ArmDelay > 0)
        {
            ArmDelay--;
            return;
        }

        Actor occupant = OccupyingPlayer();
        if (occupant)
        {
            if (Armed && !WasOccupied)
            {
                Armed = false;
                WasOccupied = true;
                Used(occupant);
            }
            else
            {
                WasOccupied = true;
            }
        }
        else
        {
            WasOccupied = false;
            Armed = true;
        }
    }

    virtual int TravelDirection()
    {
        return 0;
    }

    virtual int LandingKind()
    {
        // Descending lands on the destination's upstairs; ascending lands on
        // the destination's downstairs.
        return TravelDirection() > 0 ? 0 : 1;
    }

    override bool Used(Actor user)
    {
        int destinationDepth;
        string destinationMap;
        Inventory oldState;

        if (!user || !user.player)
            return false;

        destinationDepth = Level.levelnum + TravelDirection();
        if (destinationDepth < 1 || destinationDepth > 40)
        {
            Console.Printf("Brogue stairs: no level exists in that direction.");
            return true;
        }

        oldState = user.FindInventory('BrogueTravelState');
        if (oldState)
            user.TakeInventory('BrogueTravelState', 1);
        user.GiveInventory('BrogueTravelState', 1);

        let travelState = BrogueTravelState(user.FindInventory('BrogueTravelState'));
        if (!travelState)
        {
            Console.Printf("Brogue stairs: could not create travel state.");
            return true;
        }
        travelState.LandingKind = LandingKind();

        destinationMap = String.Format("BRG%02d", destinationDepth);
        Level.ChangeLevel(destinationMap, 0, 16 /* CHANGELEVEL_NOINTERMISSION */);
        return true;
    }

    Default
    {
        Radius 20;
        Height 16;
        +SPECIAL;
        +NOGRAVITY;
    }

    States
    {
        Spawn:
            TNT1 A -1;
            Stop;
    }
}

class BrogueUpStair : BrogueStair
{
    override int TravelDirection()
    {
        return -1;
    }
}

class BrogueDownStair : BrogueStair
{
    override int TravelDirection()
    {
        return 1;
    }
}

// Visible projections are separate from the authoritative stair actors. This
// keeps travel and landing coordinates exact while preventing the first-person
// camera from spawning inside the upstairs sprite.
class BrogueStairMarkerBase : Actor
{
    Default
    {
        Radius 1;
        Height 1;
        // MODELDEF assets are authored directly in Doom world units.
        Scale 1.0;
        +NOBLOCKMAP;
        +NOGRAVITY;
        +NOINTERACTION;
    }
}

class BrogueUpStairMarker : BrogueStairMarkerBase
{
    States { Spawn: BRGU A -1; Stop; }
}

class BrogueDownStairMarker : BrogueStairMarkerBase
{
    States { Spawn: BRGN A -1; Stop; }
}

// Spawned only after Brogue reports an authoritative fall transition. The
// model is a presentation-only recess below the destination ceiling; it does
// not alter collision or imply that independently generated floors align.
class BrogueFallShaftMarker : BrogueStairMarkerBase
{
    States { Spawn: BRGF A -1; Stop; }
}

// Closed-door presentation is deliberately separate from map topology. The
// Brogue bridge changes only this non-interactive projection when the
// authoritative DOOR terrain promotes to OPEN_DOOR.
class BrogueDoorMarker : Actor
{
    Default
    {
        Radius 1;
        Height 1;
        Scale 1.0;
        +NOBLOCKMAP;
        +NOGRAVITY;
        +NOINTERACTION;
    }

    States { Spawn: BRGD A -1; Stop; }
}

// A sight-permeable but movement-blocking machine tile. It subclasses the
// normal door marker so the native synchronizer can remove it when Brogue's
// fire simulation promotes the barricade, while retaining distinct artwork.
class BrogueBarricadeMarker : BrogueDoorMarker
{
    States { Spawn: BRGB A -1; Stop; }
}

// Presentation-only projections of Brogue surface-layer terrain. These actors
// never participate in collision, targeting, physics, or gameplay simulation.
class BroguePropBase : Actor
{
    Default
    {
        Radius 1;
        Height 1;
        +NOBLOCKMAP;
        +NOGRAVITY;
        +NOINTERACTION;
    }
}

class BrogueGrassProp : BroguePropBase
{
    Default { Scale 0.65; }
    States { Spawn: BRGG A -1; Stop; }
}

class BrogueFungusProp : BroguePropBase
{
    Default { Scale 0.68; }
    States { Spawn: BGFU A -1; Stop; }
}

class BrogueLuminousFungusProp : BroguePropBase
{
    Default
    {
        Scale 0.72;
        RenderStyle "Add";
        Alpha 0.75;
    }
    States { Spawn: BRGL A -1 Bright; Stop; }
}

class BrogueFoliageProp : BroguePropBase
{
    Default { Scale 0.75; }
    States { Spawn: BRGV A -1; Stop; }
}

class BrogueDeadVegetationProp : BroguePropBase
{
    Default
    {
        Scale 0.58;
        Alpha 0.72;
        RenderStyle "Translucent";
    }
    States { Spawn: BGDV A -1; Stop; }
}

class BrogueWorldHandler : EventHandler
{
    int Width;
    int Height;
    int ExpectedCells;
    int UDMFSector;

    Array<Sector> CellSectors;
    bool MapIsValid;

    void ReportError(string message)
    {
        MapIsValid = false;
        Console.Printf("Brogue map validation failed: %s", message);
        Console.MidPrint(Font.GetFont("BrogueUI"), "\c[White]Brogue map validation failed. See the console for details.");
    }

    bool ValidateMap()
    {
        int index;
        int x;
        int y;

        MapIsValid = true;
        CellSectors.Resize(ExpectedCells);
        for (index = 0; index < ExpectedCells; index++)
            CellSectors[index] = null;

        if (Level.Sectors.Size() <= 0 || Level.Sectors.Size() > ExpectedCells * 3)
        {
            ReportError(String.Format("expected 1-%d traversable sectors, found %d", ExpectedCells, Level.Sectors.Size()));
            return false;
        }

        for (index = 0; index < Level.Sectors.Size(); index++)
        {
            int role = Level.GetUDMFInt(UDMFSector, index, 'user_brogue_role');
            if (role == 1 || role == 2)
                continue; // Reserved liquid/deck controls never bind a Brogue cell.
            if (role != 0)
            {
                ReportError(String.Format("sector %d has invalid terrain role %d", index, role));
                return false;
            }
            x = Level.GetUDMFInt(UDMFSector, index, 'user_brogue_x');
            y = Level.GetUDMFInt(UDMFSector, index, 'user_brogue_y');
            if (x < 0 || x >= Width || y < 0 || y >= Height)
            {
                ReportError(String.Format("sector %d has invalid cell %d,%d", index, x, y));
                return false;
            }
            if (CellSectors[y * Width + x])
            {
                ReportError(String.Format("duplicate cell %d,%d", x, y));
                return false;
            }
            CellSectors[y * Width + x] = Level.Sectors[index];
        }

        return true;
    }

    BrogueStair FindLandingStair(int landingKind)
    {
        ThinkerIterator iterator = ThinkerIterator.Create('BrogueStair');
        Thinker thinker;
        BrogueStair stair;

        while (thinker = iterator.Next())
        {
            stair = BrogueStair(thinker);
            if (stair && ((landingKind == 0 && stair is 'BrogueUpStair')
                       || (landingKind == 1 && stair is 'BrogueDownStair')))
                return stair;
        }
        return null;
    }

    void PlaceTravellingPlayers()
    {
        int playerIndex;
        BrogueTravelState travelState;
        BrogueStair landing;
        PlayerPawn playerPawn;

        for (playerIndex = 0; playerIndex < MAXPLAYERS; playerIndex++)
        {
            if (!playeringame[playerIndex] || players[playerIndex].mo == null)
                continue;
            playerPawn = players[playerIndex].mo;
            travelState = BrogueTravelState(playerPawn.FindInventory('BrogueTravelState'));
            if (!travelState)
                continue;

            landing = FindLandingStair(travelState.LandingKind);
            if (!landing)
            {
                ReportError("travel destination stair is missing");
                continue;
            }
            landing.Disarm();
            playerPawn.SetOrigin(landing.Pos, true);
            playerPawn.TakeInventory('BrogueTravelState', 1);
        }
    }

    override void WorldLoaded(WorldEvent event)
    {
        Width = 79;
        Height = 29;
        ExpectedCells = 79 * 29;
        UDMFSector = 2;
        if (ValidateMap())
            PlaceTravellingPlayers();
    }

    override void PlayerEntered(PlayerEvent event)
    {
        if (MapIsValid)
            PlaceTravellingPlayers();
    }
}
