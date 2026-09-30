// Spectral sword: fullbright additive projected image. Painted value is opacity, so
// the pink-white edges and point read strongest; glancing surfaces gain a crimson
// rim and a slow projection flicker rolls through the image. Mesh-local only: no world light,
// visibility rule, simulation input or RNG; the sheen uses only renderer time.
void SetupMaterial(inout Material material)
{
    vec4 base = getTexel(vTexCoord.st);
    material.Normal = ApplyNormalMap(vTexCoord.st);
    vec3 n = normalize(vWorldNormal.xyz);
    vec3 view = normalize(uCameraPos.xyz - pixelpos.xyz);
    float facing = clamp(abs(dot(n, view)), 0.0, 1.0);
    float rim = pow(1.0 - facing, 2.0);
    float glow = max(base.r, max(base.g, base.b));
    float sheen = 0.9 + 0.1*sin(timer*3.4 + pixelpos.y*0.35);
    vec3 colour = base.rgb*(0.95 + 0.7*rim)*sheen + rim*glow*vec3(0.85, 0.18, 0.30);
    material.Base = vec4(colour, base.a);
    material.Bright = vec4(1.0, 1.0, 1.0, 0.0);
}
