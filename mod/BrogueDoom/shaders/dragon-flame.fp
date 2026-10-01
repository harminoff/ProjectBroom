// Dragon: the breath flame pieces and tongues, and the amber eye slits, are painted in atlas cells of BRGDRGN.png
// (upper right). Texels inside those cells render fullbright so dragonfire and the eyes read from far away and in
// dark rooms. Static and mesh-local: no world light, time input or simulation state. Everything else keeps ordinary lighting.
void SetupMaterial(inout Material material)
{
    vec4 base = getTexel(vTexCoord.st);
    material.Base = base;
    material.Normal = ApplyNormalMap(vTexCoord.st);
    float flameU = step(0.875, vTexCoord.s) * (1.0 - step(0.999, vTexCoord.s));
    float flameV = step(0.5, vTexCoord.t) * (1.0 - step(0.75, vTexCoord.t));
    float eyeU = step(0.75, vTexCoord.s) * (1.0 - step(0.875, vTexCoord.s));
    float eyeV = 1.0 - step(0.125, vTexCoord.t);
    material.Bright = vec4(vec3(clamp(flameU * flameV + eyeU * eyeV, 0.0, 1.0)), 0.0);
}
