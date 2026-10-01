// Lich: the source's green lich light on the phylactery gem and eye pinpoints.
// Texels inside the painted glow key render fullbright; the key matches
// glow_key() in tools/monster_models/lich_materials.py.
// Static and mesh-local: no world light, time input or simulation state.
void SetupMaterial(inout Material material)
{
    vec4 base = getTexel(vTexCoord.st);
    material.Base = base;
    material.Normal = ApplyNormalMap(vTexCoord.st);
    float glow = (1.0 - step(0.6, base.r)) * step(0.86, base.g) * step(0.35, base.b) * (1.0 - step(0.85, base.b));
    material.Bright = vec4(vec3(glow), 0.0);
}
