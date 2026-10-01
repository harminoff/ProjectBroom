// Phoenix: the flame plumes, wing-tip tongues, crest, embers and glowing eyes
// (atlas column u >= 0.75, see relic_kit.GLOW_U) render fullbright, echoing
// Brogue's PHOENIX_LIGHT. Body plumage, horn, talons and ash stay lit
// normally. Static and mesh-local: no world light, time input, simulation
// state or RNG.
void SetupMaterial(inout Material material)
{
    vec2 uv = vTexCoord.st;
    material.Base = getTexel(uv);
    material.Normal = ApplyNormalMap(uv);
    float glow = step(0.75, uv.x);
    material.Bright = vec4(vec3(glow), 0.0);
}
