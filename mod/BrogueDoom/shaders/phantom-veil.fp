// Phantom veil: fullbright additive ectoplasm whose glancing edges glow, so the
// apparition reads as a luminous outline around a dim interior. Painted black
// sockets and mouth stay empty. Mesh-local only: no world light, visibility
// rule, simulation input or RNG; the slow shimmer uses only renderer time.
void SetupMaterial(inout Material material)
{
    vec4 base = getTexel(vTexCoord.st);
    material.Normal = ApplyNormalMap(vTexCoord.st);
    vec3 n = normalize(vWorldNormal.xyz);
    vec3 view = normalize(uCameraPos.xyz - pixelpos.xyz);
    float facing = clamp(abs(dot(n, view)), 0.0, 1.0);
    float rim = pow(1.0 - facing, 2.0);
    float glow = max(base.r, max(base.g, base.b));
    float shimmer = 0.92 + 0.08*sin(timer*1.7 + pixelpos.y*0.09);
    vec3 colour = base.rgb*(0.5 + 1.35*rim)*shimmer + rim*glow*vec3(0.30, 0.22, 0.42);
    material.Base = vec4(colour, base.a);
    material.Bright = vec4(1.0, 1.0, 1.0, 0.0);
}
