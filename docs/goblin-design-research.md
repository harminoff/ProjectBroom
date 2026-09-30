# Goblin redesign: source, research and art direction

## Authority

Pinned `src/brogue-mapgen/src/brogue/Globals.c:1194` describes a filthy little
primate, pack behavior, and a makeshift stone spear. The catalog's brown glyph
is an identity cue, not a requirement for uniform brown fur. It does not specify
a monkey muzzle, round ears, full fur, green skin, armor or magical eyes.
The [Brogue Wiki](https://brogue.wiki/wiki/Goblin) reproduces the description.
The separate monkey is a mischievous thief; the two should not read as the same
animal with a weapon attached.

## Research and interpretation

- [Smithsonian cranial comparison](https://humanorigins.si.edu/education/how-do-we-know/how-do-we-know-these-are-different-species)
  and [Kabwe skull](https://humanorigins.si.edu/evidence/human-fossils/fossils/kabwe-1)
  demonstrate that primate form includes flatter faces, low foreheads and strong
  brow structures. These are anatomical references, not a claim that goblins
  represent an extinct human species or any living people.
- [British Museum flint spearhead](https://www.britishmuseum.org/collection/object/H_Sturge-504)
  informs the chipped stone material, not a copied mesh or texture.
- [British Museum bound spear](https://www.britishmuseum.org/collection/object/E_Af1846-0731-19)
  documents fibre joining a wooden haft and head. Only the general mechanical
  construction is relevant; the recorded head is iron, unlike Brogue's stone.
  No cultural decoration is copied.

Chosen design: small, wiry, forward-leaning cave humanoid with an angular face,
recessed eyes, swept pointed ears, sparse rough hair and mottled dirty brown
skin. Long fingers, a low brow, and no tail retain primate cues without using
a cartoon monkey face. A narrow irregular haft, leaf-like knapped point and
visible lashings make the existing spear attack legible. Ear shape and hair/skin
distribution and the plain ragged waist wrap are explicitly artistic
interpretation, not additional lore or armor.

## Skills and execution contract

No Blender-specific skill was installed in this session's catalog. Skill
discovery found community guidance, read in full without global installation:

- [Blender modeling](https://github.com/RobLe3/cc-blender-skill/blob/main/plugin/skills/blender-modeling/SKILL.md)
  and its topology reference: custom surface construction, joined organic
  volumes, clean normals and runtime-budgeted geometry.
- [Blender production workflow](https://github.com/RobLe3/cc-blender-skill/blob/main/plugin/skills/blender-pro-workflow/SKILL.md):
  reference first, fixed-view form review before details, and thumbnail critique.

These are community skills, not official Blender guarantees. Current Blender
API documentation was checked through Context7; old example operators are not
copied blindly. Existing project object/bone names take precedence over generic
skill naming suggestions. The established connected-cage and IQM workflow
remains authoritative for assets. That initial pass used no new plugin or
remote asset service. The subsequent
[Higgsfield refinement](goblin-higgsfield-refinement.md) uses Higgsfield's local
background Blender integration with the same procedural master and rig.

Presentation-only contract: X forward / Y lateral / Z up, scale 1, same 19
bones and six clip roles, one 1024px diffuse atlas, closed connected body,
hand-parented spear, no new gameplay. Before backups and views are in
`artifacts/goblin-redesign/before/`. Acceptance requires fixed-view Blender
review, deterministic export, limb/death/UV regressions, packaged Vulkan and
OpenGL captures and the normal seed-27 encounter. Test success is not art approval.
