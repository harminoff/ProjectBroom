// Warden of Yendor: Yendorian light (Brogue's yendorLightColor, a deep violet-magenta).
// Texels inside the painted light key render fullbright with a slow dancing pulse; the key
// matches glow_key() in tools/monster_models/warden_of_yendor_materials.py. All armour keeps
// ordinary lighting. Mesh-local: no world light, visibility rule, simulation input or RNG;
// the pulse uses only renderer time.
void SetupMaterial(inout Material material)
{
    vec4 base = getTexel(vTexCoord.st);
    material.Base = base;
    material.Normal = ApplyNormalMap(vTexCoord.st);
    float key = smoothstep(0.86, 0.92, base.r) * (1.0 - smoothstep(0.42, 0.50, base.g)) * smoothstep(0.58, 0.66, base.b);
    float dance = 0.92 + 0.05*sin(timer*2.1 + pixelpos.z*0.09) + 0.03*sin(timer*5.3 + pixelpos.x*0.07);
    material.Base.rgb *= mix(1.0, dance, key);
    material.Bright = vec4(vec3(key), 0.0);
}
