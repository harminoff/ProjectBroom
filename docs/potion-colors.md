# Potion appearance colors

Potions use all 21 Brogue color names, from crimson through black. The bridge
exports `potionColor`, a one-based index into `itemColorsRef`, by matching the
assigned `potionTable[kind].flavor`. It does not reshuffle colors or parse player
display text. Zero falls back to the generic bottle. ABI v22 occupies two former
padding bytes before actionFlags; existing item offsets and total size remain.

Floor bottles select the color skin even after identification or Call naming.
They all use the generic bottle shape and seal, avoiding hidden-effect ornaments.
The command path retains the selected potion class before an impact consumes the
item, so the thrown proxy can use the same color. No gameplay changes or new RNG.

The original CC-BY-SA-4.0 atlas generator changes only glass pixels; cork, paper
and metal retain their original colors. RGB choices interpret the named colors
artistically; Brogue defines the names rather than a matching 3D RGB palette.

Verification: `tools.test_potion_colors` checks every color, preservation of
non-glass pixels, and bridge exports across five seeds and three naming states.
`python -m tools.capture_terrain_overlays --label potion-colors-vulkan --potions`
captures all 21 colors in a renderer-only gallery and checks identification/Call
class stability. Repeat with `--backend 0` for OpenGL. These gallery items do not
change the Brogue session; they are not interactive throw or save/load evidence.

The broader bridge/resource/map/save tests also run. Local engine, DLL and
launcher are rebuilt together; no online release is changed.
