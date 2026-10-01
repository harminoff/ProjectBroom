// Only golden irises receive fullbright. No world light or simulation input.
void SetupMaterial(inout Material material)
{
    material.Base = getTexel(vTexCoord.st);
    material.Normal = ApplyNormalMap(vTexCoord.st);
    vec2 uv = vTexCoord.st;
    float eye = step(0.5, uv.x) * (1.0-step(0.75, uv.x))
              * step(0.3330078125, uv.y) * (1.0-step(0.666015625, uv.y));
    material.Bright = vec4(vec3(eye), 0.0);
}
