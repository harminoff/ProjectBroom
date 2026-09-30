// Phylactery: only the lich-green soul gem (atlas column u >= 0.75, see
// relic_kit.GLOW_U) renders fullbright, matching Brogue's LICH_LIGHT colour.
// Static and mesh-local: no world light, time input, simulation state or RNG.
void SetupMaterial(inout Material material)
{
    vec2 uv = vTexCoord.st;
    material.Base = getTexel(uv);
    material.Normal = ApplyNormalMap(uv);
    float gem = step(0.75, uv.x);
    material.Bright = vec4(vec3(gem), 0.0);
}
