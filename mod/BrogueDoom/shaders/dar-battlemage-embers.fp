// Dar battlemage: source-described ember eyes and heated hands only.
// Texels inside the painted ember key render fullbright; the key matches
// ember_key() in tools/monster_models/dar_battlemage_materials.py.
// Static and mesh-local: no world light, time input or simulation state.
void SetupMaterial(inout Material material)
{
    vec4 base = getTexel(vTexCoord.st);
    material.Base = base;
    material.Normal = ApplyNormalMap(vTexCoord.st);
    float ember = step(0.86, base.r) * step(0.3, base.g) * (1.0 - step(0.86, base.g)) * (1.0 - step(0.34, base.b));
    material.Bright = vec4(vec3(ember), 0.0);
}
