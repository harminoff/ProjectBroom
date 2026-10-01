// Original Project Broom material. Renderer time only; no simulation inputs.
void SetupMaterial(inout Material material)
{
    material.Base = getTexel(vTexCoord.st);
    material.Normal = ApplyNormalMap(vTexCoord.st);
    // Only the padded sigil tile is emissive. Fur/clothing remain normally lit.
    vec2 uv = vTexCoord.st;
    float sigil = step(0.25, uv.x) * (1.0-step(0.5, uv.x)) * step(0.666015625, uv.y);
    float pulse = 0.72 + 0.28 * sin(timer * 2.4);
    material.Base.rgb *= mix(1.0, pulse, sigil);
    material.Bright = vec4(vec3(sigil), 0.0);
}
