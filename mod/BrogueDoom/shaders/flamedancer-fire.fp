// Flamedancer: living fire drawn fullbright. Painted value carries the form; a view-angle
// rim reddens silhouettes and a slow shimmer rises up the body. Mesh-local only: no world
// light, visibility rule, simulation input or RNG; the shimmer uses only renderer time.
void SetupMaterial(inout Material material)
{
    vec4 base = getTexel(vTexCoord.st);
    material.Normal = ApplyNormalMap(vTexCoord.st);
    vec3 n = normalize(vWorldNormal.xyz);
    vec3 view = normalize(uCameraPos.xyz - pixelpos.xyz);
    float facing = clamp(abs(dot(n, view)), 0.0, 1.0);
    float rim = pow(1.0 - facing, 2.0);
    float wave = 0.5 + 0.5*sin(pixelpos.z*0.28 - timer*6.0 + pixelpos.x*0.11 + pixelpos.y*0.07);
    vec3 colour = base.rgb*(0.80 + 0.28*facing)*(0.90 + 0.16*wave);
    colour = mix(colour, colour*vec3(1.0, 0.60, 0.38), rim*0.7);
    material.Base = vec4(colour, 1.0);
    material.Bright = vec4(1.0, 1.0, 1.0, 0.0);
}
