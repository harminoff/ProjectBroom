// Original Project Broom shoreline treatment, CC0-1.0.
// Neighbor data is selected from copied, knowledge-safe terrain snapshots.
float shoreNoise(vec2 p) {
    // Continuous, stationary spatial variation: corners never restart a wave.
    return sin(p.x*.39+sin(p.y*.27))*sin(p.y*.31+p.x*.13);
}
float shoreDistance(vec2 p) {
    vec2 cell = fract(p/64.0)*64.0;
    float d=128.0;
    if(texelFetch(shoreMask,ivec2(0,0),0).r>.5) d=min(d,cell.y);
    if(texelFetch(shoreMask,ivec2(1,0),0).r>.5) d=min(d,64.0-cell.x);
    if(texelFetch(shoreMask,ivec2(2,0),0).r>.5) d=min(d,64.0-cell.y);
    if(texelFetch(shoreMask,ivec2(3,0),0).r>.5) d=min(d,cell.x);
    if(texelFetch(shoreMask,ivec2(4,0),0).r>.5) d=min(d,length(vec2(64.0-cell.x,cell.y)));
    if(texelFetch(shoreMask,ivec2(5,0),0).r>.5) d=min(d,length(vec2(64.0)-cell));
    if(texelFetch(shoreMask,ivec2(6,0),0).r>.5) d=min(d,length(vec2(cell.x,64.0-cell.y)));
    if(texelFetch(shoreMask,ivec2(7,0),0).r>.5) d=min(d,length(cell));
    return max(0.0,d + shoreNoise(p)*1.6);
}
vec4 ProcessTexel() {
    // Renderer coordinates: horizontal map Y is pixelpos.z. Negation makes
    // increasing shader Y point south, matching Brogue's row-major masks.
    vec2 p=vec2(pixelpos.x,-pixelpos.z);
    float d=shoreDistance(p);
    float edge=1.0-smoothstep(0.0,SHORE_WIDTH,d);
    vec2 uv=p/128.0;
#if SHORE_WATER > 0
    // Preserve the legacy wave scale/speed in this material's own sampling.
    float phase=timer*.225;
    vec2 warp=sin(6.2831853*(uv.yx+vec2(phase)))*.1;
    vec4 color=getTexel(uv+warp);
    color.rgb*=mix(.88,.52,edge);
    float ripple=pow(max(0.0,sin(d*1.9-timer*2.1+shoreNoise(p))),10.0);
    ripple*=edge*(1.0-edge)*(.5+.5*shoreNoise(p*.6));
    color.rgb+=vec3(.035,.05,.052)*ripple;
    float core=SHORE_WATER==2 ? .97 : .85;
    color.a*=mix(.18,core,1.0-edge);
    return color;
#else
    vec4 color=getTexel(uv);
    color.rgb*=mix(vec3(1.0),vec3(.69,.75,.74),edge);
    // Land stays opaque; one distance field covers all corner joins.
    return color;
#endif
}
