// Mirrored totem: the opaque silver-mirror glass (atlas column
// 0.5 <= u < 0.75) keeps its painted reflected banding and gains a small
// view-dependent term (a fake vault/horizon/floor environment), so the
// gleam shifts as the viewer moves without any see-through read. Mirror
// texels are partly fullbright so the prism gleams in the darkness; the
// flash crystal (u >= 0.75, see relic_kit.GLOW_U) is fully fullbright.
// Mesh-local only: camera position is the sole input; no world light, time,
// simulation state or RNG.
vec3 MirrorEnvironment(vec3 r)
{
    float h = r.y;
    vec3 vault = mix(vec3(0.62, 0.66, 0.76), vec3(0.20, 0.22, 0.30), smoothstep(0.05, 0.8, h));
    vec3 floorColour = mix(vec3(0.30, 0.27, 0.25), vec3(0.08, 0.07, 0.07), smoothstep(0.1, 0.7, -h));
    vec3 c = h > -0.05 ? vault : floorColour;
    c += vec3(0.45, 0.48, 0.55) * exp(-pow((h + 0.04) / 0.07, 2.0));
    float azimuth = atan(r.x, r.z);
    c *= 0.82 + 0.18 * sin(azimuth * 7.0);
    return c;
}

void SetupMaterial(inout Material material)
{
    vec2 uv = vTexCoord.st;
    vec4 base = getTexel(uv);
    material.Normal = ApplyNormalMap(uv);
    float mirror = step(0.5, uv.x) * (1.0 - step(0.75, uv.x));
    float flash = step(0.75, uv.x);
    vec3 n = normalize(vWorldNormal.xyz);
    vec3 view = normalize(uCameraPos.xyz - pixelpos.xyz);
    vec3 env = MirrorEnvironment(reflect(-view, n));
    float e = dot(env, vec3(0.333));
    vec3 reflected = base.rgb * (0.8 + 0.5 * (e - 0.35)) + 0.05 * env;
    material.Base = vec4(mix(base.rgb, reflected, mirror), base.a);
    material.Bright = vec4(vec3(max(mirror * 0.3, flash)), 0.0);
}
