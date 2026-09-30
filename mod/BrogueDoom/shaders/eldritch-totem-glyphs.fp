// Eldritch totem: fullbright red ichor core and spectral-blue blades (atlas
// column u >= 0.75, see relic_kit.GLOW_U) plus the painted glyph channels,
// keyed by their exact colour in eldritch_totem_materials.GLYPH.
// Static and mesh-local: no world light, time input, simulation state or RNG.
void SetupMaterial(inout Material material)
{
    vec2 uv = vTexCoord.st;
    vec4 base = getTexel(uv);
    material.Base = base;
    material.Normal = ApplyNormalMap(uv);
    float column = step(0.75, uv.x);
    float glyph = step(0.9, base.r) * (1.0 - step(0.3, base.g)) * (1.0 - step(0.3, base.b));
    material.Bright = vec4(vec3(max(column, glyph)), 0.0);
}
