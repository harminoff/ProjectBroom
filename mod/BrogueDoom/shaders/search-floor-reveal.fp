// Original Project Broom surface-local reveal. No time/noise or gameplay RNG.
float revealNoise(vec2 p)
{
    vec2 i = floor(p), f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    vec4 n = fract(sin(vec4(dot(i, vec2(127.1,311.7)),
        dot(i+vec2(1,0), vec2(127.1,311.7)),
        dot(i+vec2(0,1), vec2(127.1,311.7)),
        dot(i+vec2(1,1), vec2(127.1,311.7)))) * 43758.5453);
    return mix(mix(n.x,n.y,f.x), mix(n.z,n.w,f.x), f.y);
}
vec4 ProcessTexel()
{
    vec2 uv = vec2(pixelpos.x, -pixelpos.z) / 128.0;
    vec4 texel = getTexel(uv);
    float progress = clamp(vColor.a, 0.0, 1.0);
    if (progress < 0.999) {
        float n = revealNoise(uv * 12.0);
        texel.a *= smoothstep(n - 0.18, n + 0.18, progress * 1.36 - 0.18);
    }
    return texel;
}
