// Flame turret: opaque mechanism plus atlas-local emission; no world light or gameplay.
// Only the rightmost atlas column (u >= 0.875) holds the pilot flame, ember eyes and
// attack blast tongue; everything else keeps ordinary lighting.
void SetupMaterial(inout Material material)
{
    material.Base = getTexel(vTexCoord.st);
    material.Normal = ApplyNormalMap(vTexCoord.st);
    float fire = step(0.875, vTexCoord.s);
    float flicker = 0.93 + 0.05*sin(timer*8.0) + 0.02*sin(timer*17.0);
    material.Base.rgb *= mix(1.0, flicker, fire);
    material.Bright = vec4(vec3(fire), 0.0);
}
