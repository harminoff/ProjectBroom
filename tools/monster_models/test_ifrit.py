"""Ifrit: anatomy, vortex tail, baked skin light, chain skinning, clearance, key poses, floor death, ember key and bytes."""
import collections
import math
import unittest
from . import ifrit_animation as g, ifrit_materials as m, iqm
from .skeletal_registry import find


def closed(part):
    edges=collections.Counter();keys=[tuple(round(c,5) for c in v) for v in part.vertices]
    for a,b,c in part.triangles():
        for i,j in ((a,b),(b,c),(c,a)):edges[tuple(sorted((keys[i],keys[j])))]+=1
    return set(edges.values())=={2}


RINGS=('belt','sash_wrap','collar','earring','ring')


class IfritTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parts,cls.v,cls.n,cls.uv,cls.t,cls.w=g.geometry()
        cls.clips,cls.bounds=g.animation_data(cls.v,cls.w)
        cls.named={c['name']:c for c in cls.clips}
        cls.owner=[p.name for p in cls.parts for _ in p.vertices]
        cls.first={};k=0
        for p in cls.parts:
            cls.first[p.name]=(k,k+len(p.vertices));k+=len(p.vertices)

    def deformed(self,clip,fraction):
        frames=self.named[clip]['frames'];return g.deform(self.v,self.w,frames[min(len(frames)-1,int(len(frames)*fraction))])

    def points(self,frame_points,prefix):
        return [frame_points[i] for name,(a,b) in self.first.items() if name.startswith(prefix) for i in range(a,b)]

    def test_anatomy_is_sculpted_and_legless(self):
        names={p.name for p in self.parts}
        for want in ('Connected_skin','head','jaw','brow_ridge','cheek_1','mouth','tooth_up_3','fang_up_1','fang_low_-1',
                     'horn_1','horn_-1','moustache_1_0','goatee','beard_tuft','collar','belt','scimitar_L','scimitar_R',
                     'edge_strip_L','edge_strip_R','vortex_core','smoke_sheet_0','smoke_wisp_5'):
            self.assertIn(want,names)
        for p in self.parts:
            if not p.name.startswith(RINGS):self.assertTrue(closed(p),p.name)
        self.assertEqual(self.clips[0]['name'],'idle')
        self.assertFalse([n for n in names if 'dust_band' in n or n.startswith('ring_')])      # the coiled-spring rings are gone
        low=[p.name for p in self.parts if max(v[2] for v in p.vertices)<g.K*26]
        self.assertTrue(all(n.startswith(('smoke_','vortex')) for n in low),low)             # nothing but smoke below the belt
        torso=[p for p in self.parts if p.name=='Connected_skin'][0];head=[p for p in self.parts if p.name=='head'][0]
        span=lambda p:max(v[1] for v in p.vertices)-min(v[1] for v in p.vertices)
        self.assertGreater(span(torso),2.4*span(head))

    def test_torso_neck_shoulders_and_arms_are_one_connected_skin(self):
        skin=[p for p in self.parts if p.name=='Connected_skin'];self.assertEqual(len(skin),1);skin=skin[0]
        self.assertFalse([p.name for p in self.parts if p.name.startswith('skin_')])         # no separate muscle balloons remain
        self.assertEqual(len(skin.skin_topology),len(skin.vertices))
        # One closed, connected surface: every cage edge shared by two faces, a single component.
        ids=skin.skin_topology;edges=collections.Counter();graph=collections.defaultdict(set)
        for a,b,c in skin.triangles():
            for x,y in ((ids[a],ids[b]),(ids[b],ids[c]),(ids[c],ids[a])):
                edges[tuple(sorted((x,y)))]+=1;graph[x].add(y);graph[y].add(x)
        self.assertEqual(set(edges.values()),{2})
        seen={ids[0]};todo=[ids[0]]
        while todo:
            for n in graph[todo.pop()]:
                if n not in seen:seen.add(n);todo.append(n)
        self.assertEqual(len(seen),len(graph))
        # It spans torso, neck, both shoulders, elbows and wrists, with blended (not rigid) joint weights.
        first=0
        used=set();blended=0
        for row in self.w[:len(skin.vertices)]:
            for b,_ in row:used.add(g.BONES[b][0])
            blended+=len(row)>1
        for bone in ('spine','chest','neck','sh_L','sh_R','el_L','el_R','wr_L','wr_R'):self.assertIn(bone,used)
        self.assertGreater(blended,.3*len(skin.vertices))
        # Coincident vertices share one weight set (no cracks at UV splits).
        by={}
        for i,v in enumerate(skin.vertices):
            self.assertEqual(by.setdefault(tuple(v),self.w[i]),self.w[i])
        # Jewellery, head, blades and the vortex stay rigid attachments with a single bone each.
        for name in ('collar','belt','head','scimitar_L','smoke_sheet_0','bracer_L'):
            a,b=self.first[name];self.assertTrue(all(len(self.w[i])<=4 for i in range(a,b)))
        a,b=self.first['scimitar_R'];self.assertEqual({bn for i in range(a,b) for bn,_ in self.w[i]},{g.IDS['wr_R']})

    def test_vortex_is_layered_ragged_and_narrows_to_a_point(self):
        sheets=[p for p in self.parts if p.name.startswith('smoke_sheet')]
        self.assertGreaterEqual(len(sheets),9)
        radius=lambda pts,z0,z1:max((math.hypot(v[0],v[1]) for v in pts if z0<=v[2]<=z1),default=0)
        allv=[v for p in self.parts if p.name.startswith(('smoke_','vortex')) for v in p.vertices]
        top=radius(allv,g.K*22,g.K*28);mid=radius(allv,g.K*10,g.K*16);bottom=radius(allv,0,g.K*4)
        self.assertGreater(top,g.K*10);self.assertLess(bottom,.35*top)
        self.assertGreater(min(v[2] for v in allv),-.01);self.assertLess(min(v[2] for v in allv),g.K*1.5)   # ends near the floor
        for p in sheets:                                                                    # ragged: widths vary along the sheet
            widths=[math.dist(p.vertices[i*9],p.vertices[i*9+4]) for i in range(1,len(p.vertices)//9-1)]
            self.assertGreater(max(widths)/min(widths),1.4,p.name)

    def test_skin_light_is_baked_from_geometry(self):
        skin=[p for p in self.parts if p.role=='skin']
        shades=[b for p in skin for b in p.pv];glows=[a for p in skin for a in p.pa]
        self.assertLess(min(shades),.12)                                                   # near-black crevices
        self.assertGreater(max(shades),.55);self.assertLess(max(shades),.98)                # highlights never blow out
        self.assertGreater(max(glows),.4)                                                  # ember under-glow on undersides
        for p in skin:
            for a,b in zip(p.pa,p.pv):self.assertTrue(0<=a<=1 and 0<=b<=1)
        body=[p for p in skin if p.name=='Connected_skin'][0]
        self.assertGreater(len(set(body.pv)),20)                                            # continuous shading over the fused skin
        # Coincident (UV-split) vertices of the fused skin carry identical baked shading: no seam patches.
        seen={}
        for v,a,b in zip(body.vertices,body.pa,body.pv):
            self.assertEqual(seen.setdefault(tuple(round(c,5) for c in v),(a,b)),(a,b))
        # skin paint stays desaturated: no texel of the ramp is a saturated purple.
        for b in range(0,65):
            r,gg,bb=m.pigment('skin',0,b/64,10,10);self.assertLess(max(r,gg,bb)-min(r,gg,bb),110)
        self.assertLess(m.pigment('skin',0,1.0,10,10)[0],200)

    def test_face_is_large_fanged_and_faces_plus_x(self):
        head=[p for p in self.parts if p.name=='head'][0];jaw=[p for p in self.parts if p.name=='jaw'][0]
        span=lambda p,a:max(v[a] for v in p.vertices)-min(v[a] for v in p.vertices)
        self.assertGreater(span(head,1),g.K*5.0*2*1.2)                                     # enlarged skull
        teeth=[p for p in self.parts if p.name.startswith(('tooth','fang'))];self.assertGreaterEqual(len(teeth),14)
        eyes=[v for p in self.parts if p.name.startswith('eye_') for v in p.vertices]
        centre_x=sum(v[0] for v in head.vertices)/len(head.vertices)
        self.assertGreater(sum(v[0] for v in eyes)/len(eyes),centre_x+g.K*3)
        self.assertTrue(all(m.ember_key(m.pigment('fire',a,b,40,40))>.95 for a in (.2,.5,.8) for b in (.1,.5,.9)))

    def test_blades_curve_and_have_dark_spines(self):
        for n,s in (('L',-1),('R',1)):
            path=g.blade_path(s);chord=math.dist(path[0],path[-1])
            length=math.fsum(math.dist(a,b) for a,b in zip(path,path[1:]))
            self.assertGreater(length/chord,1.02)
            tip_forward=path[-1][0]-path[0][0]
            self.assertGreater(tip_forward,12)                                             # sabre sweep toward +X
        edge=m.pigment('steel',.02,.5,50,50);spine=m.pigment('steel',.5,.5,50,50)
        self.assertGreater(sum(edge),2.2*sum(spine))
        for a in (0,.3,.5,.8):self.assertLess(m.ember_key(m.pigment('steel',a,.7,50,50)),.05)   # steel itself is never fullbright

    def test_weights(self):
        for weights in self.w:
            self.assertTrue(1<=len(weights)<=4)
            self.assertAlmostEqual(math.fsum(a for _,a in weights),1,places=9)
            self.assertTrue(all(0<=a<=1 for _,a in weights))
        used={g.BONES[b][0] for row in self.w for b,_ in row}
        self.assertEqual(used,{n for n,_,_ in g.BONES}-{'root'})
        for frame in (f for c in self.clips for f in c['frames']):
            self.assertTrue(all(tuple(b[7:])==(1,1,1) for b in frame))

    def test_rest_pose_is_the_authored_shape_and_loops(self):
        rest=g.deform(self.v,self.w,[(*l,0,0,0,1,1,1,1) for _,_,l in g.BONES])
        self.assertLess(max(math.dist(a,b) for a,b in zip(rest,self.v)),1e-6)
        for name in ('idle','fly'):
            a=g.deform(self.v,self.w,g.pose(name,0));b=g.deform(self.v,self.w,g.pose(name,1))
            self.assertLess(max(math.dist(x,y) for x,y in zip(a,b)),1e-6,name)

    def test_centered_clearance_every_frame(self):
        for i,b in enumerate(self.bounds):
            self.assertGreater(b[0],-32,i);self.assertGreater(b[1],-32,i)
            self.assertLess(b[3],32,i);self.assertLess(b[4],32,i);self.assertGreater(b[2],-.001,i)

    def test_key_poses_on_middle_frame(self):
        idle=self.deformed('idle',0)
        for clip in ('slash','discord','recoil'):
            mid=self.deformed(clip,.5);first=self.deformed(clip,0)
            self.assertGreater(max(math.dist(a,b) for a,b in zip(idle,mid)),10,clip)
            self.assertGreater(max(math.dist(a,b) for a,b in zip(first,mid)),10,clip)
        blades=[i for i,o in enumerate(self.owner) if o.startswith('scimitar')]
        idle_top=max(idle[i][2] for i in blades);slash=self.deformed('slash',.5)
        self.assertLess(max(slash[i][2] for i in blades),.5*idle_top)
        self.assertGreater(max(abs(slash[i][1]) for i in blades),24)

    def test_discord_rears_back_flings_the_blades_wide_and_bursts_embers(self):
        idle=self.deformed('idle',0);discord=self.deformed('discord',.5)
        head=lambda pts:self.points(pts,'brow_ridge')
        idle_head=head(idle);cast_head=head(discord)
        self.assertLess(sum(p[0] for p in cast_head)/len(cast_head),sum(p[0] for p in idle_head)/len(idle_head)-2)   # torso rears back
        self.assertLess(sum(p[2] for p in cast_head)/len(cast_head),sum(p[2] for p in idle_head)/len(idle_head))     # and the head drops
        blades=self.points(discord,'scimitar')
        self.assertLess(max(p[2] for p in blades),.9*max(p[2] for p in self.points(idle,'scimitar')))              # blades no longer stand tall
        flecks=self.points(discord,'fleck')
        self.assertGreater(max(abs(p[1]) for p in flecks),18)                                # swirl reaches far out to the sides
        self.assertGreater(max(p[2] for p in flecks)-min(p[2] for p in flecks),20)           # rising column of embers
        for pts in (idle,self.deformed('slash',.5),self.deformed('recoil',.5)):
            flecks=self.points(pts,'fleck');torso=self.points(pts,'torso')
            self.assertLess(max(math.hypot(p[0]-3,p[1]) for p in flecks),16)                 # hidden inside the chest otherwise

    def test_collapse_ends_flat_on_the_floor_with_embers_out(self):
        last=self.deformed('collapse',1.0)
        self.assertLess(max(p[2] for p in last),32)
        frame=self.named['collapse']['frames'][-1];rest=[l for _,_,l in g.BONES];ids=g.IDS
        for eye in ('eye_L','eye_R'):
            self.assertAlmostEqual(frame[ids[eye]][0]-rest[ids[eye]][0],-3.4*g.K,places=4)
        self.assertAlmostEqual(frame[ids['crown']][2]-rest[ids['crown']][2],-10.5*g.K,places=4)
        for n in ('L','R'):                                                                  # edge strips sink into the blades
            self.assertAlmostEqual(frame[ids['edge_'+n]][0]-rest[ids['edge_'+n]][0],3.4*g.K,places=4)
        early=self.named['collapse']['frames'][len(self.named['collapse']['frames'])//4]
        self.assertGreater(early[ids['crown']][2]-rest[ids['crown']][2],-1.0)

    def test_ember_key_marks_only_fire(self):
        for role in ('skin','horn','hair','cloth','gold','ivory','steel'):
            worst=max(m.ember_key(m.pigment(role,a/10,b/10,17*a,23*b)) for a in range(11) for b in range(11))
            self.assertLess(worst,.05,role)
        self.assertGreater(max(m.ember_key(m.pigment('smoke',.25,.5,x,y)) for x in range(0,200,3) for y in range(0,200,3)),.9)  # ember sparks exist
        self.assertGreater(max(m.ember_key(m.pigment('core',.5,.5,x,y)) for x in range(0,200,3) for y in range(0,200,3)),.9)

    def test_profile_durations_and_report(self):
        row=find('MK_IFRIT')
        self.assertEqual(row['clips'],[c['name'] for c in self.clips])
        for role,count,fps in ((2,26,35),(3,28,35),(4,14,35),(5,40,35)):
            self.assertGreaterEqual(row['durations'][role],math.ceil(count*35/fps))
        for bad in ('visualScale','emissive','additiveFlame'):self.assertNotIn(bad,row)
        self.assertEqual(row['report'],'docs/ifrit-animation.md');self.assertTrue(row['traits'])

    def test_exact_runtime_texture_shader_and_inert_proxy(self):
        data=iqm.encode(self.v,self.n,self.uv,self.t,self.w,g.BONES,self.clips,self.bounds,
                        mesh_label='Project_Broom_ifrit',material_path=g.SKIN)
        self.assertEqual(data,(g.ROOT/g.MODEL).read_bytes())
        self.assertEqual(g.texture_bytes(),(g.ROOT/'mod/BrogueDoom'/g.SKIN).read_bytes())
        shader=(g.ROOT/g.SHADER).read_text()
        self.assertIn('material.Bright',shader);self.assertIn('smoothstep(0.80, 0.90, base.r)',shader)
        pending=g.ROOT/'assets/monsters/skeletal_pending/MK_IFRIT.gldefs'
        gldefs=pending.read_text() if pending.is_file() else (g.ROOT/'mod/BrogueDoom/GLDEFS').read_text()
        self.assertIn('shaders/ifrit-embers.fp',gldefs)
        self.assertNotIn('specular',gldefs.split('BRGIFRIT')[1].split('}')[0])              # no glossy plastic highlight
        text=(g.ROOT/'mod/BrogueDoom/brogue_monsters.zs').read_text()
        proxy=text.split('class BrogueMonsterK64 :')[1].split('class ')[0]
        self.assertIn('BrogueMonsterProxyBase',proxy)
        for forbidden in ('A_Explode','A_CustomMissile','A_Chase','A_Damage','+SOLID','Random'):
            self.assertNotIn(forbidden,proxy)


if __name__=='__main__':unittest.main()
