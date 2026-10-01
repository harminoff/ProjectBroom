// Black jelly ink: view-dependent rim sheen and a soft ceiling reflection
// added to the lit base colour, so the glossy black mass keeps its outline
// on dark floors. No emission, fullbright, world light, simulation input or RNG.
void SetupMaterial(inout Material material)
{
    vec2 uv = vTexCoord.st;
    material.Base = getTexel(uv);
    material.Normal = ApplyNormalMap(uv);
    material.Specular = texture(speculartexture, uv).rgb;
    material.Glossiness = uSpecularMaterial.x;
    material.SpecularLevel = uSpecularMaterial.y;
    vec3 n = normalize(vWorldNormal.xyz);
    vec3 view = normalize(uCameraPos.xyz - pixelpos.xyz);
    float facing = clamp(abs(dot(n, view)), 0.0, 1.0);
    float gloss = material.Specular.r * material.Specular.r;
    float rim = pow(1.0 - facing, 3.0) * gloss;
    vec3 r = reflect(-view, n);
    float vault = smoothstep(0.25, 0.9, r.y) * gloss;
    material.Base.rgb += rim * vec3(0.24, 0.22, 0.34) + vault * vec3(0.03, 0.03, 0.045);
}
