// Mesh-local blue flame emission, no world light, damage, RNG or game input.
void SetupMaterial(inout Material material)
{
    material.Base = getTexel(vTexCoord.st);
    material.Normal = ApplyNormalMap(vTexCoord.st);
    float flicker = 0.91 + 0.06*sin(timer*7.0) + 0.03*sin(timer*13.0);
    material.Base.rgb *= flicker;
    material.Base.a *= 0.55;
    material.Bright = vec4(1.0, 1.0, 1.0, 0.0);
}
