"""Load baked, connected skin topology; accessories retain their own bones.

Blender is an authoring dependency only. Rebuild with blender_skin.py after
changing the blockout or weights. Ordinary builds verify the fingerprint and
consume the committed bake, without launching Blender or changing topology.
"""
import gzip
import hashlib
import json
import sys
from .rat import ROOT, Part


def selected(enemy, name):
    # New creatures declare CONNECTED_SKIN(name) -> bool in their own
    # <enemy>_animation module instead of editing this shared selector.
    hook=getattr(sys.modules.get(f'tools.monster_models.{enemy}_animation'),'CONNECTED_SKIN',None)
    if hook is not None:return bool(hook(name))
    if enemy in ('naga','salamander'):return name.startswith('skin_')
    if enemy == 'pixie':return name.startswith('skin_')
    if enemy == 'zombie':return name == 'pelvis' or name.startswith(('torso','head_','shoulder_','arm_','leg_','hand_','foot_'))
    if enemy == 'wraith':return name == 'pelvis' or name.startswith(('torso','head_','shoulder_','arm_','leg_','hand_','foot_'))
    if enemy == 'dar_blademaster':return name in ('pelvis','torso') or name.startswith(('head_','shoulder_','arm_','leg_','hand_','foot_'))
    if enemy == 'troll':return name == 'pelvis' or name.startswith(('torso','head_','shoulder_','arm_','leg_','hand_','foot_'))
    if enemy in ('ogre','ogre_shaman'):return name in ('pelvis','torso') or name.startswith(('head_','shoulder_','arm_','leg_','hand_','foot_'))
    if enemy == 'centaur':
        return (name in ('horse_body','tail_dock') or name.startswith(('torso','head_','shoulder_','arm_','hand_'))
                or (name.startswith(('fore_','hind_'))))
    if enemy == 'bog_monster':return name == 'mantle' or name.startswith('tentacle_')
    if enemy == 'vampire_bat':
        return not name.startswith(('eye','ear_inner','nostril','mouth','fang','claw'))
    if enemy == 'toad':
        return (name in ('body','belly','head','throat')
                or name.startswith(('head_brow','head_lid','gland','fore_','hind_','foot_','toe_')))
    if enemy in ('goblin', 'goblin_conjurer', 'goblin_mystic'):
        return (name in ('pelvis','torso','neck','head_cranium','head_face','head_muzzle','head_nose')
                or name.startswith(('arm_','leg_','shoulder_','hand_','foot_','coat_','head_cheek','head_brow'))
                or name.startswith('head_ear_') and 'inner' not in name)
    if enemy == 'monkey':
        return name in ('pelvis','torso','neck','head_skull','head_face','head_muzzle','tail') or name.startswith(('shoulder_','arm_','leg_','hand_','foot_'))
    if enemy == 'kobold':
        return (name in ('pelvis','torso','neck','head_cranium','head_muzzle','tail')
                or name.startswith(('arm_','leg_','shoulder_','hand_'))
                or (name.startswith('foot_') and 'claw' not in name))
    if enemy == 'jackal':
        return (name in ('coat','neck','head_skull','head_cheek','head_muzzle','tail')
                or name.startswith(('fore_','hind_'))
                or (name.startswith('paw_') and 'claw' not in name))
    return (name in ('Rat_continuous_coat','Tail_tapered_rings')
            or (name.startswith(('Fore_','Hind_')) and 'claw' not in name))


def fingerprint(enemy, parts, weights):
    def stable(value):
        if isinstance(value,float):return round(value,8)
        if isinstance(value,(list,tuple)):return [stable(v) for v in value]
        return value
    data=[(p.name,p.vertices,p.uv,list(p.triangles()),
           [weights(p,v,u) for v,u in zip(p.vertices,p.uv)])
          for p in parts if selected(enemy,p.name)]
    return hashlib.sha256(json.dumps(stable(data),separators=(',',':')).encode()).hexdigest()


def path(enemy): return ROOT/f'assets/monsters/{enemy}/connected-skin.json.gz'


def attach(enemy, parts, weights):
    data=json.loads(gzip.decompress(path(enemy).read_bytes()))
    if data['sourceHash'] != fingerprint(enemy,parts,weights):
        raise ValueError(f'{enemy} skin bake is stale: run background Blender blender_skin.py -- {enemy}')
    part=Part('Connected_skin',data['vertices'],data['uv'],data['faces'])
    part.skin_weights=data['weights']
    part.skin_topology=data['topology']
    return [part]+[p for p in parts if not selected(enemy,p.name)]
