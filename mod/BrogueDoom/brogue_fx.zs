// Cosmetic effects projected from the authoritative Brogue bridge snapshot.
// These actors never damage, push, block, or otherwise alter gameplay.

class BrogueAmbientFx : Actor
{
	int FxClock;

	int EffectQuality()
	{
		CVar quality = CVar.FindCVar('brg_fx_quality');
		if (quality == null) return 1;
		int value = quality.GetInt();
		if (value < 0) return 0;
		if (value > 2) return 2;
		return value;
	}

	bool NearViewer(double maximumDistance)
	{
		Actor viewer = players[consoleplayer].mo;
		return viewer != null && Distance2D(viewer) <= maximumDistance;
	}

	override void Tick()
	{
		Super.Tick();
		// The reconciler owns lifetime. Basic suppresses emission in subclasses;
		// keeping this inert actor allows quality changes without a new snapshot.
	}

	Default
	{
		Radius 1;
		Height 1;
		+NOBLOCKMAP
		+NOGRAVITY
		+NOCLIP
		+NOTARGET
	}

	States
	{
	Spawn:
		TNT1 A -1;
		Stop;
	}
}

class BrogueLavaFx : BrogueAmbientFx
{
	override void Tick()
	{
		Super.Tick();
		int quality = EffectQuality();
		if (quality == 0 || !NearViewer(1152)) return;
		FxClock++;
		int cadence = quality >= 2 ? 5 : 10;
		if ((FxClock % cadence) != 0) return;
		int count = quality >= 2 ? 2 : 1;
		for (int i = 0; i < count; i++)
		{
			A_SpawnParticle("FF6418", SPF_FULLBRIGHT | SPF_REPLACE,
				frandom[BrogueLavaFx](18, 30), frandom[BrogueLavaFx](2.0, 4.0), 0,
				frandom[BrogueLavaFx](-25, 25), frandom[BrogueLavaFx](-25, 25), frandom[BrogueLavaFx](1, 4),
				frandom[BrogueLavaFx](-0.08, 0.08), frandom[BrogueLavaFx](-0.08, 0.08), frandom[BrogueLavaFx](0.25, 0.65),
				0, 0, -0.012, frandom[BrogueLavaFx](0.55, 0.85), -1, -0.025);
		}
	}
}

class BrogueFireFx : BrogueAmbientFx
{
	override void Tick()
	{
		Super.Tick();
		int quality = EffectQuality();
		if (quality == 0 || !NearViewer(1280)) return;
		FxClock++;
		int cadence = quality >= 2 ? 2 : 4;
		if ((FxClock % cadence) != 0) return;
		int count = quality >= 2 ? 3 : 1;
		for (int i = 0; i < count; i++)
		{
			color ember = random[BrogueFireFx](0, 2) == 0 ? "FFE45A" : "FF4A0A";
			A_SpawnParticle(ember, SPF_FULLBRIGHT | SPF_REPLACE,
				frandom[BrogueFireFx](14, 24), frandom[BrogueFireFx](2.0, 4.5), 0,
				frandom[BrogueFireFx](-20, 20), frandom[BrogueFireFx](-20, 20), frandom[BrogueFireFx](1, 8),
				frandom[BrogueFireFx](-0.12, 0.12), frandom[BrogueFireFx](-0.12, 0.12), frandom[BrogueFireFx](0.55, 1.25),
				0, 0, 0.018, Alpha * frandom[BrogueFireFx](0.70, 1.0), -1, -0.055);
		}
	}
}

class BrogueGasFx : BrogueAmbientFx
{
	override void Tick()
	{
		Super.Tick();
		int quality = EffectQuality();
		if (quality == 0 || !NearViewer(1024)) return;
		FxClock++;
		int cadence = quality >= 2 ? 6 : 12;
		if ((FxClock % cadence) != 0) return;
		int count = quality >= 2 ? 2 : 1;
		for (int i = 0; i < count; i++)
		{
			A_SpawnParticle(FillColor == 0 ? 0x678B58 : FillColor, SPF_REPLACE,
				frandom[BrogueGasFx](30, 55), frandom[BrogueGasFx](4.0, 7.0), 0,
				frandom[BrogueGasFx](-28, 28), frandom[BrogueGasFx](-28, 28), frandom[BrogueGasFx](2, 22),
				frandom[BrogueGasFx](-0.12, 0.12), frandom[BrogueGasFx](-0.12, 0.12), frandom[BrogueGasFx](0.05, 0.20),
				0, 0, 0, Alpha * frandom[BrogueGasFx](0.30, 0.55), -1, frandom[BrogueGasFx](0.015, 0.045));
		}
	}
}

class BrogueBurstFx : Actor
{
	int EffectQuality()
	{
		CVar quality = CVar.FindCVar('brg_fx_quality');
		return quality == null ? 1 : quality.GetInt();
	}

	Default
	{
		Radius 1;
		Height 1;
		+NOBLOCKMAP
		+NOGRAVITY
		+NOCLIP
		+NOTARGET
	}

	States
	{
	Spawn:
		TNT1 A 4;
		Stop;
	}
}

class BrogueWaterSplashFx : BrogueBurstFx
{
	override void PostBeginPlay()
	{
		Super.PostBeginPlay();
		int count = EffectQuality() >= 2 ? 12 : 6;
		for (int i = 0; i < count; i++)
		{
			double angle = frandom[BrogueSplashFx](0, 360);
			double speed = frandom[BrogueSplashFx](0.45, 1.25);
			A_SpawnParticle("4AA9D8", SPF_REPLACE, frandom[BrogueSplashFx](16, 28),
				frandom[BrogueSplashFx](1.8, 3.4), 0, 0, 0, frandom[BrogueSplashFx](0, 3),
				cos(angle) * speed, sin(angle) * speed, frandom[BrogueSplashFx](0.8, 1.8),
				0, 0, -0.10, frandom[BrogueSplashFx](0.55, 0.85), -1, -0.045);
		}
	}
}

class BrogueImpactFx : BrogueBurstFx
{
	override void PostBeginPlay()
	{
		Super.PostBeginPlay();
		int count = EffectQuality() >= 2 ? 12 : 6;
		for (int i = 0; i < count; i++)
		{
			double angle = frandom[BrogueImpactFx](0, 360);
			double speed = frandom[BrogueImpactFx](0.8, 2.0);
			A_SpawnParticle("FFD36A", SPF_FULLBRIGHT | SPF_REPLACE,
				frandom[BrogueImpactFx](8, 16), frandom[BrogueImpactFx](1.2, 2.4), 0,
				0, 0, 0, cos(angle) * speed, sin(angle) * speed, frandom[BrogueImpactFx](-0.4, 1.0),
				0, 0, -0.04, 0.9, -1, -0.065);
		}
	}
}

class BrogueDamageFx : BrogueBurstFx
{
	override void PostBeginPlay()
	{
		Super.PostBeginPlay();
		int count = EffectQuality() >= 2 ? 10 : 5;
		for (int i = 0; i < count; i++)
		{
			double angle = frandom[BrogueDamageFx](0, 360);
			double speed = frandom[BrogueDamageFx](0.35, 1.15);
			A_SpawnParticle("9E2028", SPF_REPLACE, frandom[BrogueDamageFx](14, 24),
				frandom[BrogueDamageFx](2.0, 3.8), 0, 0, 0, 0,
				cos(angle) * speed, sin(angle) * speed, frandom[BrogueDamageFx](0.1, 0.8),
				0, 0, -0.05, 0.75, -1, -0.045);
		}
	}
}

class BrogueDeathFx : BrogueBurstFx
{
	override void PostBeginPlay()
	{
		Super.PostBeginPlay();
		int count = EffectQuality() >= 2 ? 18 : 9;
		for (int i = 0; i < count; i++)
		{
			double angle = frandom[BrogueDeathFx](0, 360);
			double speed = frandom[BrogueDeathFx](0.25, 1.25);
			color mote = random[BrogueDeathFx](0, 2) == 0 ? "5C171D" : "47413E";
			A_SpawnParticle(mote, SPF_REPLACE, frandom[BrogueDeathFx](22, 40),
				frandom[BrogueDeathFx](2.5, 5.0), 0, 0, 0, frandom[BrogueDeathFx](-4, 8),
				cos(angle) * speed, sin(angle) * speed, frandom[BrogueDeathFx](0.15, 0.9),
				0, 0, -0.025, 0.65, -1, -0.035);
		}
	}
}
