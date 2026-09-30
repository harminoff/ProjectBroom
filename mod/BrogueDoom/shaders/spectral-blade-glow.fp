// Spectral blade: fullbright additive conjured light. Painted value is opacity, so
// the white-hot edge and point read strongest; glancing surfaces gain a violet-blue
// rim and a slow sheen travels up the blade. Mesh-local only: no world light,
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
    float sheen = 0.88 + 0.12*sin(timer*2.6 - pixelpos.y*0.21);
    vec3 colour = base.rgb*(0.95 + 0.7*rim)*sheen + rim*glow*vec3(0.22, 0.30, 0.85);
    material.Base = vec4(colour, base.a);
    material.Bright = vec4(1.0, 1.0, 1.0, 0.0);
}
