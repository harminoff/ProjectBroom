// Explicit isolated presentation regression; never creates Brogue creatures.
CCMD(brg_monster_visibility_smoke)
{
    if (Started || !primaryLevel || primaryLevel->MapName.CompareNoCase("ART01") != 0 || brg_monster_omniscience)
    {
        Printf("MONSTER_VISIBILITY_SMOKE refused: isolated map and ordinary visibility required\n");
        return;
    }
    int failures = 0;
    for (const char *name : {"BrogueMonsterK01", "BrogueMonsterK23"})
    {
        MonsterProxy probe;
        probe.actor = Spawn(primaryLevel, name, DVector3(0,0,0), NO_REPLACE);
        if (!probe.actor) { ++failures; continue; }
        const AActor *defaults = GetDefaultByType(probe.actor->GetClass());
        // Deliberately disagree with the displayed class: hallucination safety.
        probe.presentationKind = 0;
        for (auto visibility : {BROGUE_VISIBILITY_DIRECT, BROGUE_VISIBILITY_HIDDEN,
                               BROGUE_VISIBILITY_SENSED, BROGUE_VISIBILITY_DIRECT})
        {
            probe.visibility = visibility;
            ApplyMonsterVisibility(probe);
            const bool hidden = visibility == BROGUE_VISIBILITY_HIDDEN;
            const bool sensed = visibility == BROGUE_VISIBILITY_SENSED;
            const double expectedAlpha = hidden ? 0.0 : sensed ? 0.38 : defaults->Alpha;
            const bool correctStyle = hidden || (probe.actor->RenderStyle ==
                (sensed ? LegacyRenderStyles[STYLE_Translucent] : defaults->RenderStyle));
            const bool pass = bool(probe.actor->renderflags & RF_INVISIBLE) == hidden
                && std::abs(probe.actor->Alpha-expectedAlpha) < 0.00001
                && correctStyle && !(probe.actor->flags & MF_SOLID);
            if (!pass) ++failures;
            Printf("MONSTER_VISIBILITY class=%s visibility=%d alpha=%.2f style_ok=%d hidden=%d blocking=%d pass=%d\n",
                name,int(visibility),double(probe.actor->Alpha),int(correctStyle),int(hidden),
                int(bool(probe.actor->flags & MF_SOLID)),int(pass));
        }
        probe.actor->Destroy();
    }
    Printf("MONSTER_VISIBILITY_SMOKE failures=%d Brogue_session=%d\n",failures,int(Started));
}
