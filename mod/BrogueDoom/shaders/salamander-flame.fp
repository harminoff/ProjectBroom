// Opaque scaled body plus atlas-local emission; no world light or gameplay.
void SetupMaterial(inout Material material)
{
    material.Base = getTexel(vTexCoord.st);
    material.Normal = ApplyNormalMap(vTexCoord.st);
    float flame = step(0.79,vTexCoord.s)*(1.0-step(0.83,vTexCoord.s));
    float flicker = 0.94 + 0.04*sin(timer*7.0) + 0.02*sin(timer*13.0);
    material.Base.rgb *= mix(1.0,flicker,flame);
    material.Bright = vec4(vec3(flame),0.0);
}
