// Guardian spirit: fullbright additive crimson light (Brogue's spectral image colour,
// the same as the spectral sword) that is strongest at the rim, so the allied spectral
// knight reads as one bright outline around a dim core. Faces turned away from the
// camera add nothing (no stacked back plates), and light near the floor dims, so the
// collapsed armour of the fade is left only dimly glowing. Painted black stays empty.
// Mesh-local presentation only: no dynamic light, visibility rule, simulation input or
// RNG; the shimmer uses renderer time.
void SetupMaterial(inout Material material)
{
    vec4 base = getTexel(vTexCoord.st);
    material.Normal = ApplyNormalMap(vTexCoord.st);
    vec3 n = normalize(vWorldNormal.xyz);
    vec3 view = normalize(uCameraPos.xyz - pixelpos.xyz);
    float side = dot(n, view);
    float front = smoothstep(-0.02, 0.12, side);
    float facing = clamp(abs(side), 0.0, 1.0);
    float rim = pow(1.0 - facing, 1.6);
    float glow = max(base.r, max(base.g, base.b));
    float shimmer = 0.9 + 0.1*sin(timer*3.4 + pixelpos.z*0.11);
    float dim = mix(0.4, 1.0, smoothstep(3.0, 14.0, pixelpos.z));
    vec3 colour = base.rgb*(0.25 + 1.6*rim)*shimmer + rim*glow*vec3(0.85, 0.18, 0.30);
    material.Base = vec4(colour*front*dim, base.a);
    material.Bright = vec4(1.0, 1.0, 1.0, 0.0);
}
