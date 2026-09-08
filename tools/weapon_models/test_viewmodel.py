"""Asset/authority regressions for first-person weapon presentation."""
import hashlib
import json
import math
from pathlib import Path
import struct
import unittest

from tools.weapon_models import viewmodel as vm
from tools.weapon_models.generate import state_lines, WEAPONS

ROOT=Path(__file__).resolve().parents[2]
MODELS=ROOT/'mod/BrogueDoom/models/weapons'


class WeaponViewmodelTests(unittest.TestCase):
    def test_catalog_and_original_source(self):
        registry=json.loads((ROOT/'assets/weapons/brogue_weapon_registry.json').read_text())
        self.assertEqual(registry['weaponCount'],15)
        self.assertEqual(len(registry['weapons']),len(WEAPONS))
        self.assertTrue((ROOT/'assets/weapons/hero-weapons.blend').is_file())
        for item in registry['weapons']:
            self.assertEqual(item['frames'],list(vm.POSE_NAMES))
            self.assertEqual(item['skin'],'graphics/BRGHANDS.png')
            self.assertEqual(item['grip']=='two-handed',item['kind'] in vm.TWO_HANDED)

    def test_all_pose_topologies_and_connected_arm_anchors(self):
        for kind in range(15):
            base=vm.build_parts(kind)
            self.assertLess(sum(len(p.faces) for p in base),14000)
            for frame in range(len(vm.POSE_NAMES)):
                parts=vm.build_parts(kind,frame)
                self.assertEqual([p.name for p in parts],[p.name for p in base])
                for a,b in zip(base,parts):
                    self.assertEqual(a.faces,b.faces)
                    self.assertEqual(a.uv,b.uv)
                    for v in b.vertices: self.assertTrue(all(math.isfinite(x) and abs(x)<512 for x in v))
                    for u,v in b.uv: self.assertTrue(0<u<1 and 0<v<1)
                    for face in b.faces:
                        self.assertEqual(len(face),3)
                        self.assertTrue(all(0<=i<len(b.vertices) for i in face))
                for side in ('R','L'):
                    sleeve=next(p for p in parts if p.name==side+' continuous sleeve')
                    self.assertLess(min(v[2] for v in sleeve.vertices),-48)
                    # Anchor ring never moves during hand/weapon animation.
                    baseline=next(p for p in base if p.name==sleeve.name)
                    self.assertEqual(sleeve.vertices[:17],baseline.vertices[:17])
                    wrist=next(p for p in parts if p.name==side+' wrist')
                    # Ring overlap at the sleeve/wrist transition, not an air gap.
                    self.assertLess(min(math.dist(a,b) for a in sleeve.vertices[-20:] for b in wrist.vertices),3.0)

    def test_hand_revision_preserves_every_arm_and_weapon_pose(self):
        # Hashes captured from the pre-hand-revision generator. Include every
        # non-hand vertex, material, UV and face in all 16 poses, for 15 weapons.
        expected = [
            'c10a8179400f536797330447333fe6fafc2c2c7dc1fc48059a78c450c2cefd4c',
            'a6482e0af7426c342d239cdb7bfc07d25f4c0be759c5c66c9c90920008d4e286',
            '736c7b715b63cf39d2234dd04a8db7ea69aa5b792ae950cb8bd1957b769fd973',
            'b4bf38f6b4962299e8d0da051bc3cf8d862f47ca47bbcf6482a7318e9c581ba5',
            '43e26bbb834ff96db3a9024fdbe1eb41795b78d8ae50626f61d313889ddb7e74',
            'f0d4682673788574b49e9d036b5662dc3a3e15e984321d38bf0640ceff8328b6',
            '2ec4c6953d2ac949c4fd0d72277bb5951ec4ed3cd53c749e99094289842a9f79',
            '4256098549493cff9a76d9732ab7b951d09f2fe309b68083bf7b2e77fd7cae05',
            '620ba47aec45911d1a0c146aec5aa5a7d1ee009e35f4987002817aee5ff71aab',
            '2a14493518ca68c00a96b3664bb14fe8571697a4b47e627116732d0833403a05',
            'b9a62c9537ec9c85211b15962a49e3099d9bae051adba91654351e410838a990',
            '19bdeeef857282665107bc4adf2e1dd015ba2680aa450d195ce84e3a8acdd8bd',
            '51c03871f58ab43eb7c83a713ac07355ca07295f076a94565887409bbe62864e',
            '2e4ef90bee35bb28dda0fa4824adc81a5085e1308cef854188a4a1bd226c9f7d',
            '6add00e7169ff8defde29206cb2633e31451a77f392839043d5b373f828d7ae4',
        ]
        hands={p.name for side in ('R','L') for p in vm.grip_parts(side)}
        for kind, expected_hash in enumerate(expected):
            value=[[(p.name,p.material,p.vertices,p.faces,p.uv)
                    for p in vm.build_parts(kind,f) if p.name not in hands]
                   for f in range(16)]
            actual=hashlib.sha256(json.dumps(value,separators=(',',':')).encode()).hexdigest()
            self.assertEqual(actual,expected_hash,kind)

    def test_hand_winding_mirroring_and_release_surface_integrity(self):
        for pinch in (False,True):
            for opening in (0,.4,.8):
                right=vm.grip_parts('R',pinch,opening)
                left=vm.grip_parts('L',pinch,opening)
                for r,l in zip(right,left):
                    self.assertEqual(l.vertices,[(x,-y,z) for x,y,z in r.vertices])
                    self.assertEqual(l.faces,[(a,c,b) for a,b,c in r.faces])
                    for a,b,c in r.faces:
                        area=vm.cross(vm.sub(r.vertices[b],r.vertices[a]),
                                      vm.sub(r.vertices[c],r.vertices[a]))
                        self.assertGreater(vm.dot(area,area),1e-12,r.name)
                # Extended fingertip travels forward, with its base fixed.
                if opening:
                    closed=vm.grip_parts('R',pinch,0)
                    for r,c in zip(right,closed):
                        if 'articulated finger' in r.name:
                            self.assertGreater(max(v[0] for v in r.vertices),
                                               max(v[0] for v in c.vertices))

    def test_runtime_assets_reproduce_byte_for_byte(self):
        for kind in range(15):
            frames=[vm.build_parts(kind,i) for i in range(len(vm.POSE_NAMES))]
            self.assertEqual((MODELS/f'weapon_{kind:02d}.obj').read_text('ascii'),vm.obj_text(frames[0]))
            self.assertEqual((MODELS/f'weapon_{kind:02d}.md3').read_bytes(),vm.md3_bytes(frames))
        self.assertEqual((ROOT/'mod/BrogueDoom/graphics/BRGHANDS.png').read_bytes(),vm.atlas_bytes())
        from tools.weapon_models.devices import device_parts
        for staff,name in ((True,'staff'),(False,'wand')):
            frames=[device_parts(staff,f) for f in range(9)]
            directory=ROOT/'mod/BrogueDoom/models/devices'
            self.assertEqual((directory/(name+'.obj')).read_text('ascii'),vm.obj_text(frames[0]))
            self.assertEqual((directory/(name+'.md3')).read_bytes(),vm.md3_bytes(frames))


    def test_md3_binary_layout_indices_and_frame_bounds(self):
        for kind in range(15):
            data=(MODELS/f'weapon_{kind:02d}.md3').read_bytes()
            h=struct.unpack_from('<4si64s9i',data)
            self.assertEqual(h[:2],(b'IDP3',15));nf,ns=h[4],h[6]
            self.assertEqual(nf,len(vm.POSE_NAMES));self.assertEqual(h[-1],len(data))
            offset=h[-2]
            for _ in range(ns):
                s=struct.unpack_from('<4s64s10i',data,offset)
                self.assertEqual(s[0],b'IDP3');self.assertEqual(s[3],nf)
                nv,nt=s[5],s[6];ot,os,ou,ov,end=s[7:]
                self.assertEqual(ot,108);self.assertEqual(os,ot+nt*12)
                self.assertEqual(ou,os+68);self.assertEqual(ov,ou+nv*8)
                self.assertEqual(end,ov+nf*nv*8)
                indices=struct.unpack_from('<'+'i'*(nt*3),data,offset+ot)
                self.assertTrue(all(0<=i<nv for i in indices))
                for frame in range(nf):
                    bounds=struct.unpack_from('<10f16s',data,h[-4]+frame*56)
                    for vi in range(nv):
                        vertex=struct.unpack_from('<3hH',data,offset+ov+(frame*nv+vi)*8)
                        for axis in range(3):
                            self.assertGreaterEqual(vertex[axis]/64,bounds[axis]-.016)
                            self.assertLessEqual(vertex[axis]/64,bounds[axis+3]+.016)
                offset+=end
            self.assertEqual(offset,len(data))

    def test_motion_settles_and_does_not_rotate_entire_overlay(self):
        for kind in range(15):
            ready=vm.build_parts(kind,0)
            for end in (8,15):
                self.assertEqual([p.vertices for p in ready],[p.vertices for p in vm.build_parts(kind,end)])
            self.assertNotEqual(ready[0].vertices,vm.build_parts(kind,4)[0].vertices)
        zs=(ROOT/'mod/BrogueDoom/brogue_weapons.zs').read_text()
        for forbidden in ('A_OverlayRotate','A_OverlayOffset','A_Fire','A_Custom','A_Spawn','A_Punch','A_ReFire'):
            self.assertNotIn(forbidden,zs)
        self.assertEqual(zs.count('BridgeAttack:'),15)
        self.assertIn('WRF_NOFIRE | WRF_NOSWITCH',zs)
        for family in vm.FAMILIES: self.assertEqual(len(state_lines('BW00',family)),9)

    def test_every_frame_has_model_and_psprite_binding(self):
        modeldef=(MODELS/'MODELDEF.txt').read_text()
        textures=(ROOT/'mod/BrogueDoom/TEXTURES.txt').read_text()
        for kind in range(15):
            self.assertIn(f'Model 0 "weapon_{kind:02d}.md3"',modeldef)
            for frame in range(len(vm.POSE_NAMES)):
                letter=chr(65+frame)
                self.assertIn(f'FrameIndex BW{kind:02d} {letter} 0 {frame}',modeldef)
                self.assertIn(f'Sprite "BW{kind:02d}{letter}0"',textures)

    def test_throw_model_uses_copied_event_kind_without_gameplay_commands(self):
        native=(ROOT/'src/gzdoom-bridge/brogue_bridge_frontend.cpp').read_text()
        begin=native[native.index('void BeginProjectileAnimation'):native.index('bool TickProjectile')]
        self.assertIn('VisualThrowKind = first->itemKind;',begin)
        self.assertIn('VisualThrowUntilTic = primaryLevel->maptime + 14;',begin)
        self.assertIn('SyncWeaponView();',begin)
        self.assertNotIn('PerformCommand',begin)
        self.assertNotIn('PerformItemCommand',begin)
        events=native[native.index('void ProcessWeaponEvents'):native.index('bool SyncLevelEvent')]
        self.assertIn('BROGUE_EVENT_ATTACK_ATTEMPTED && event.sourceEntityId == 1',events)


if __name__=='__main__': unittest.main()
