// Ifrit: eyes, ember-forged blade edges, crown flame and storm embers only. Texels inside the
// painted ember key render fullbright; the key matches ember_key() in
// tools/monster_models/ifrit_materials.py. Everything else keeps ordinary lighting.
// Mesh-local: no world light, visibility rule, simulation input or RNG; the flicker uses only
// renderer time.
void SetupMaterial(inout Material material)
{
    vec4 base = getTexel(vTexCoord.st);
    material.Base = base;
    material.Normal = ApplyNormalMap(vTexCoord.st);
    float ember = smoothstep(0.80, 0.90, base.r) * smoothstep(0.22, 0.30, base.g)
                * (1.0 - smoothstep(0.80, 0.90, base.g)) * (1.0 - smoothstep(0.30, 0.40, base.b));
    float flicker = 0.93 + 0.05*sin(timer*8.0 + pixelpos.z*0.2) + 0.02*sin(timer*17.0);
    material.Base.rgb *= mix(1.0, flicker, ember);
    material.Bright = vec4(vec3(ember), 0.0);
}
