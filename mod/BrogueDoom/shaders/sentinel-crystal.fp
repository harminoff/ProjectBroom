// Sentinel warding crystal: only the crystal atlas region (u >= 0.75, v < 0.25,
// matching GLOW_REGION in tools/monster_models/sentinel_animation.py) renders
// fullbright with a slow shimmer. Stone stays lit by existing lights.
// Mesh-local presentation only: no dynamic light, simulation input or RNG.
void SetupMaterial(inout Material material)
{
    vec2 uv = vTexCoord.st;
    vec4 base = getTexel(uv);
    material.Normal = ApplyNormalMap(uv);
    float crystal = step(0.75, uv.x) * (1.0 - step(0.25, uv.y));
    float shimmer = 0.9 + 0.1*sin(timer*2.3 + uv.y*40.0);
    material.Base = vec4(mix(base.rgb, base.rgb*shimmer*1.15, crystal), base.a);
    material.Bright = vec4(vec3(crystal), 0.0);
}
