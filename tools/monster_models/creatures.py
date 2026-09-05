"""Original source-directed static creature models. No gameplay dependencies.

Shared anatomical primitives, individually specified recipes; +X forward, Z up.
The existing rat is preserved byte for byte. All output is deterministic.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
import zlib

from . import rat
from .bestiary import ROOT, INDEX, profiles, source_records, write_index

TAU = math.tau
TILE = dict(body='fur', accent='ear', wood='tail', cloth='paw', dark='eye', bone='claw', glow='whisker')


class Sculpt:
    def __init__(self):
        self.parts = []

    def oval(self, name, c, r, mat='body', seg=20, rings=12):
        p = rat.ellipsoid(name, c, r, TILE[mat], seg, rings)
        self.parts.append(p)
        return p

    def strand(self, name, points, mat='body', sides=10, samples=3, ribbed=False):
        p = rat.tube(name, points, TILE[mat], sides, samples, ribbed)
        self.parts.append(p)
        return p

    def box(self,name,c,r,mat='cloth'):
        p=rat.Part(name)
        for i,(x,y,z) in enumerate(((-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1))):
            p.vertex((c[0]+x*r[0],c[1]+y*r[1],c[2]+z*r[2]),TILE[mat],.15+.7*(i%2),.15+.7*(i//4))
        p.faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
        self.parts.append(p)
        return p

    def plate(self, name, outline, thickness=.5, mat='cloth'):
        """Closed thin solid, with a Y-normal face; outward triangulated winding."""
        p = rat.Part(name)
        for side in (-1, 1):
            for i,(x,y,z) in enumerate(outline):
                p.vertex((x,y+side*thickness/2,z), TILE[mat], .1+.8*i/max(1,len(outline)-1), .2 if side<0 else .8)
        n = len(outline)
        # Input outlines need not be planar, but must be simple/convex.
        normal = rat.cross(rat.sub(outline[1],outline[0]),rat.sub(outline[2],outline[0]))
        front = tuple(range(n))
        if normal[1] > 0:
            front = tuple(reversed(front))
        p.faces.extend((front,tuple(i+n for i in reversed(front))))
        for i,a in enumerate(front):
            b = front[(i+1)%n]
            p.faces.append((a,a+n,b+n,b))
        self.parts.append(p)
        return p

    def eyes(self, x, y, z, size=1, mat='dark'):
        for side in (-1,1):
            self.oval(f'Eye_{side}',(x,side*y,z),(size*.5,size*.8,size),mat,12,8)
            self.oval(f'Eye_glint_{side}',(x+size*.42,side*y,z+size*.25),(.12*size,.20*size,.20*size),'glow',8,6)

    def teeth(self, x, width, z, count=6, size=1):
        for i in range(count):
            y = width*(i/(count-1)-.5)
            self.strand(f'Tooth_{i}',[(x,y,z,size*.3),(x+.3,y,z-size,size*.04)],'bone',6,1)

    def hand(self, c, side, claws=False, mat='body'):
        x,y,z = c
        self.oval(f'Palm_{side}',c,(1.4,1.4,2.1),mat)
        for finger in range(4):
            yy = y+(finger-1.5)*.65
            self.strand(f'Finger_{side}_{finger}',[(x+.3,yy,z+.4,.40),(x+1,yy,z-1.6,.32),(x+.3,yy,z-2.3,.18)],mat,8,2)
            if claws:
                self.strand(f'Nail_{side}_{finger}',[(x+.3,yy,z-2.1,.22),(x+1.2,yy,z-3.2,.02)],'bone',6,2)
        self.strand(f'Thumb_{side}',[(x,y+side,z+.7,.55),(x+1.5,y+side*1.2,z,.4),(x+1.7,y,z-.5,.2)],mat,8,2)

    def weapon(self, name, c, weapon='sword', mat='wood'):
        x,y,z = c
        self.strand(name+'_grip',[(x,y,z-3,.65),(x,y,z+5,.65)],mat,10,1)
        if weapon in ('club','staff','spear','axe'):
            self.strand(name+'_shaft',[(x,y,z-10,.75),(x,y,z+23,.65)],mat,12,2)
        if weapon=='club':
            self.strand(name+'_knotted_head',[(x,y,z+7,1.1),(x+1,y,z+18,3.0),(x,y,z+23,2.2)],'wood',14,3)
            for n in range(4):
                self.oval(name+f'_knot_{n}',(x+1.8,y+(-1)**n,z+11+n*2),(1.1,.7,1),'wood',10,7)
        elif weapon=='staff':
            self.strand(name+'_crook',[(x,y,z+20,1),(x+3,y,z+24,1),(x+5,y,z+21,.7)],'wood',10,3)
            self.oval(name+'_relic',(x+4,y,z+19),(1.5,1.5,2),'glow',8,5)
        elif weapon=='spear':
            self.plate(name+'_stone_spearhead',[(x-2,y,z+22),(x,y,z+30),(x+2,y,z+22),(x,y,z+20)],1,'bone')
        elif weapon=='axe':
            self.plate(name+'_axehead',[(x,y,z+19),(x+5,y,z+23),(x+9,y,z+20),(x+9,y,z+12),(x+5,y,z+14),(x,y,z+14)],1.2,'bone')
        else:
            self.strand(name+'_guard',[(x-3,y,z+4,.45),(x+3,y,z+4,.45)],'bone',8,1)
            if weapon=='scimitar':
                self.plate(name+'_curved_blade',[(x-1,y,z+5),(x-.8,y,z+15),(x+1,y,z+23),(x+5,y,z+28),(x+3,y,z+19),(x+2,y,z+6)],.5,'bone')
            else:
                self.plate(name+'_blade',[(x-1.2,y,z+5),(x-1,y,z+24),(x,y,z+29),(x+1,y,z+24),(x+1.2,y,z+5)],.5,'bone')


def humanoid(s, traits, zbase=0):
    t = set(traits)
    stone = bool(t & {'stone','spectral','warden'})
    gaunt = bool(t & {'gaunt','undead'})
    brute = 'brute' in t
    body = 'body'
    width = 8 if brute else 4.8 if gaunt else 6
    # Organic limbs overlap at every joint. Rooted feet are not separate blocks.
    for side in (-1,1):
        s.strand(f'Leg_{side}',[(-1,side*3,27,3 if brute else 2.4),(1,side*3.7,16,2.1),(-.5,side*4,4,1.5)],body,14,4)
        s.oval(f'Foot_{side}',(2,side*4,2),(4,2.1,2),body)
    s.oval('Pelvis',(0,0,27),(4.5,width,5),body)
    s.strand('Continuous_torso',[(0,0,28,width*.8),(-1,0,34,width*.75),(-2 if 'hunched' in t else 0,0,42,width*1.1),(1,0,46,width*.8)],body,24,4)
    s.strand('Neck',[(1,0,44,2.7),(2 if not 'hunched' in t else 5,0,50,2.5)],body,16,3)
    head_x = 5 if 'hunched' in t else 2
    s.oval('Cranium',(head_x,0,53),(3.5,4,4.8),body,24,16)
    s.oval('Jaw',(head_x+1,0,50),(3.2,3.1,2),body)
    for side in (-1,1):
        s.oval(f'Shoulder_{side}',(0,side*(width+1),43),(3,3,3),body)
        hand = (4,side*(width+5),28)
        if 'raised_crystal' in t:
            hand=(2,side*(width+3),58)
        s.strand(f'Arm_{side}',[(0,side*(width+1),43,2.8),(1,side*(width+5),35 if hand[2]<40 else 48,2),(hand[0],hand[1],hand[2],1.4)],body,14,4)
        s.hand(hand,side,bool(t & {'blood_nails','claws','demon'}),body)
        if 'lizard' in t or 'elf' in t or 'primate' in t or 'demon' in t:
            if 'primate' in t:
                s.oval(f'Rounded_ear_{side}',(head_x,side*4,53),(1,1.5,1.7),'accent')
            else:
                s.strand(f'Pointed_ear_{side}',[(head_x,side*3,53,1.1),(head_x-1,side*6,56,.05)],'body',10,2)
    if 'faceless' not in t:
        if 'lizard' in t:
            s.oval('Long_reptile_muzzle',(head_x+3,0,51),(4,2.5,1.5),'body')
        elif 'primate' in t:
            s.oval('Primate_muzzle',(head_x+3,0,51),(2,2.7,1.6),'accent')
            s.oval('Brow',(head_x+3,0,54.2),(1.2,3.4,1),'body')
        else:
            s.oval('Nose',(head_x+3.5,0,52),(1.3,1,1.7),'body')
        s.eyes(head_x+3,2.2,54,1,'glow' if t & {'golden_eyes','ember_eyes','undead'} else 'dark')
        if t & {'fangs','lizard','demon'}:
            s.teeth(head_x+4.2,4,50.8,6,1)
    if 'tail' in t or 'lizard' in t:
        s.strand('Curled_tail',[(-3,0,26,1.8),(-12,0,20,1.1),(-17,2,24,.7),(-14,4,32,.15)],body,12,6)
    for name in ('club','staff','spear','sword','axe'):
        if name in t:
            s.weapon(name,(4,-(width+5),28),name,'body' if stone else 'wood')
    if 'twin_scimitars' in t:
        for side in (-1,1):
            s.weapon(f'Scimitar_{side}',(4,side*(width+5),28),'scimitar')
    if 'robe' in t or 'cloak' in t or 'hunched' in t:
        for n in range(12):
            a=TAU*n/12
            s.strand(f'Drapery_fold_{n}',[(-1+4*math.cos(a),width*.8*math.sin(a),39,1.6),(-1+5*math.cos(a),width*math.sin(a),25,1.7),(-2+6*math.cos(a),width*1.2*math.sin(a),5+(n%3),1.1)],'cloth',10,5)
    if 'cloak' in t:
        for side in (-1,1):
            s.plate(f'High_collar_{side}',[(-1,side*4,45),(-4,side*7,57),(2,side*5,48)],1,'cloth')
    if t & {'armor','knight','plates','warden'}:
        s.oval('Breastplate',(3,0,39),(3,width+1,7),'cloth',12,8)
        for side in (-1,1):
            s.oval(f'Pauldron_{side}',(0,side*(width+1),44),(3.7,4,3),'cloth',12,8)
            s.oval(f'Greave_{side}',(1.7,side*4,12),(1.5,2.6,7),'cloth',12,8)
        s.oval('Helmet',(head_x-.2,0,54),(3.8,4.3,4.5),'cloth',12,9)
        s.strand('Visor_slit',[(head_x+3.5,-2.6,54,.22),(head_x+3.6,2.6,54,.22)],'dark',6,1)
    if t & {'ribs','gaunt'}:
        for n in range(6):
            for side in (-1,1):
                s.strand(f'Exposed_rib_{side}_{n}',[(4,0,43-n*1.5,.4),(3.8,side*3,42-n*1.5,.45),(1,side*width,42-n*1.5,.25)],'bone',8,3)
    if 'torn_flesh' in t:
        for n in range(9):
            s.strand(f'Flesh_strip_{n}',[(4,-4+n,40,.45),(4.5,-4+n,32-n%4,.16)],'accent',6,3)
    if t & {'warts','misshapen'}:
        for n in range(26):
            a=n*2.4
            s.oval(f'Wart_{n}',(4*math.cos(a),width*math.sin(a),31+n%17),(.6,.65,.6),'accent',8,5)
    if t & {'relics','phylactery','crest'}:
        s.strand('Necklace',[(2,-4,47,.25),(5,0,40,.25),(2,4,47,.25)],'bone',6,4)
        for n in range(5):
            s.oval(f'Relic_{n}',(5,-3+n*1.5,39+abs(2-n)),(.6,.6,1.4),'glow' if 'phylactery' in t else 'bone',8,6)
    if 'crest' in t or 'demon' in t:
        for side in (-1,1):
            s.strand(f'Crest_horn_{side}',[(head_x-1,side*2.5,56,.9),(head_x-3,side*4,61,.65),(head_x+1,side*4,63,.04)],'bone',10,4)
    if 'sigils' in t:
        for n in range(5):
            z=34+n*2
            s.strand(f'Chest_sigil_{n}',[(4,-2,z,.25),(4.6,0,z+1,.25),(4,2,z,.25)],'glow',6,1)
    if 'hot_hands' in t:
        for side in (-1,1):
            for n in range(3):
                s.strand(f'Hand_ember_{side}_{n}',[(4,side*(width+5)+n,29,.4),(5,side*(width+5)+n,33,.01)],'glow',6,3)
    if 'raised_crystal' in t:
        s.oval('Aloft_crystal',(2,0,63),(3,3,6),'glow',6,4)
        s.strand('Crystal_cradle',[(2,-(width+3),58,.9),(2,0,59,.9),(2,width+3,58,.9)],'body',10,3)
    if 'wings' in t:
        wings(s, feather=True, z=40, span=24)
    if 'storm' in t:
        for n in range(4):
            controls=[]
            for j in range(22):
                a=j*.34+n*1.5
                controls.append((-2+7*math.cos(a),7*math.sin(a),4+j*1.3,.6))
            s.strand(f'Storm_coil_{n}',controls,'accent',8,2)
    if zbase:
        for p in s.parts:
            p.vertices=[(x,y,z+zbase) for x,y,z in p.vertices]


def wings(s, feather=False, z=20, span=24):
    for side in (-1,1):
        root=(-2,side*3,z)
        elbow=(1,side*span*.53,z+7)
        tip=(-3,side*span,z+8)
        s.strand(f'Wing_arm_{side}',[(*root,1.3),(*elbow,.85),(*tip,.25)],'body',12,4)
        for n in range(6):
            end=(-12+n*1.5,side*(span-n*2.5),z-5+n*.7)
            if feather:
                s.strand(f'Flight_feather_{side}_{n}',[(*elbow,.9),(*end,.65),(end[0]-6,end[1],end[2]-2,.025)],'accent' if n%2 else 'body',8,4)
                for barb in range(3):
                    s.strand(f'Feather_barb_{side}_{n}_{barb}',[(end[0]+barb,end[1],end[2],.2),(end[0]-2+barb,end[1]+side*1.3,end[2]-.4,.015)],'glow',6,1)
            else:
                s.strand(f'Wing_finger_{side}_{n}',[(*elbow,.45),(*end,.13)],'body',8,2)
                prev = tip if n==0 else (-12+(n-1)*1.5,side*(span-(n-1)*2.5),z-5+(n-1)*.7)
                s.plate(f'Wing_membrane_{side}_{n}',[elbow,prev,end,root],.15,'accent')


def quadruped(s,t,horse=False):
    s.parts.append(rat.loft('Continuous_animal_trunk',[(-14,17,1,2),(-11,18,5,6),(-4,18,6,6),(4,19,5,7),(10,21,4,6),(13,24,3,4)],28,4))
    for x in (-10,9):
        for side in (-1,1):
            y=side*4
            s.strand(f'Jointed_leg_{x}_{side}',[(x,y,19,2.2),(x+(-2 if x<0 else 1),y,11,1.3),(x-1,y,3,.9)],'body',12,4)
            s.oval(f'Hoof_paw_{x}_{side}',(x,y,1.5),(2,1.4,1.5),'dark' if horse else 'body')
            if not horse:
                for toe in range(3):
                    s.oval(f'Toe_{x}_{side}_{toe}',(x+1.3,y+(toe-1)*.8,.9),(1,.5,.6),'accent',10,7)
    s.strand('Neck',[(10,0,20,4),(13,0,30 if horse else 26,3),(15,0,35 if horse else 27,2.8)],'body',20,4)
    hz=35 if horse else 27
    s.oval('Head',(16,0,hz),(4,3,4),'body',24,14)
    s.oval('Long_muzzle',(20,0,hz-2),(4,2,2),'body')
    s.oval('Nose',(23,0,hz-2),(1,2,1.3),'dark')
    s.eyes(18,2.4,hz+1,.8)
    for side in (-1,1):
        s.strand(f'Ear_{side}',[(15,side*2,hz+3,1.2),(14,side*3,hz+8,.04)],'body',12,3)
    s.strand('Tail',[(-13,0,19,1.5),(-20,1,15,1.2),(-22,3,8,.35)],'body',14,5)
    if horse:
        for n in range(12):
            s.strand(f'Mane_strand_{n}',[(10+n*.4,0,24+n*.8,.45),(8+n*.3,2,22+n*.8,.3),(7+n*.3,3,20+n*.8,.02)],'glow' if 'rainbow' in t else 'wood',8,3)
    else:
        s.teeth(20,3.5,hz-3,6,.8)
        for n in range(12):
            s.strand(f'Ruff_{n}',[(10,-3+n*.5,24,.55),(8,-3+n*.5,27,.02)],'body',6,2)
    if 'horn' in t:
        s.strand('Spiral_horn',[(17,0,hz+3,1.1),(20,0,hz+14,.025)],'glow',12,8,True)


def serpent(s,t):
    eel='eel' in t
    controls=[(-23,8,3,.08),(-17,10,3,1.2),(-10,4,4,2),(-6,-6,4,3),(2,-9,5,3.2),(8,-2,6,3.6),(11,3,8 if eel else 18,3.8)]
    s.strand('Continuous_serpentine_body',controls,'body',24,6,False)
    if eel:
        s.oval('Eel_head',(13,4,8),(5,3,2.5),'body')
        s.eyes(16,2,9,.65)
        s.teeth(17,4,7,8,.7)
        for n in range(12):
            x=-17+n*2
            s.plate(f'Dorsal_fin_{n}',[(x,3,5),(x+1,3,9),(x+3,3,6)],.2,'accent')
    else:
        s.strand('Upright_serpent_neck',[(11,3,16,4),(8,1,29,3.8),(10,0,37,3)],'body',24,5)
        s.oval('Reptile_skull',(12,0,39),(4,4,4),'body')
        s.oval('Reptile_muzzle',(16,0,38),(4,3,2),'body')
        s.eyes(15,3.2,41,.9)
        s.teeth(19,5,37,8,1)
        for side in (-1,1):
            s.strand(f'Serpent_arm_{side}',[(8,side*3,29,1.8),(12,side*8,23,1.2),(17,side*8,25,.8)],'body',12,4)
            s.hand((17,side*8,25),side,True)
        if 'lash' in t:
            s.strand('Burning_lash',[(17,-8,25,.6),(24,-9,19,.5),(29,-6,6,.4),(24,5,4,.2),(17,9,12,.02)],'glow',10,6)
        for n in range(16):
            s.oval(f'Ventral_scale_{n}',(12+n*.15,0,16+n*1.3),(1.8,3.2,.45),'accent',12,6)


def arthropod(s,centipede=False):
    count=12 if centipede else 2
    for n in range(count):
        x=(-18+n*3.2) if centipede else (-5 if n==0 else 7)
        s.oval(f'Carapace_{n}',(x,0,7),(3,4,3) if centipede else ((10,8,7) if n==0 else (5,5,4)),'body',20,12)
    nlegs=12 if centipede else 4
    for side in (-1,1):
        for n in range(nlegs):
            x=-18+n*3.2 if centipede else 3+n*2
            reach=8 if centipede else 18
            endx=x-2 if centipede else x+(n-1.5)*5
            s.strand(f'Leg_{side}_{n}',[(x,side*3,7,.8),(x-1,side*reach*.7,11, .65),(endx,side*reach,1,.15)],'body',10,4)
    hx=21 if centipede else 12
    s.oval('Head',(hx,0,7),(3,4,3),'body')
    for side in (-1,1):
        s.strand(f'Venom_incisor_{side}',[(hx+1,side*2,7,1),(hx+5,side*3,5,.65),(hx+5,side*.5,3,.02)],'bone',12,4)
        if centipede:
            s.strand(f'Antenna_{side}',[(hx+1,side*2,9,.35),(hx+4,side*4,12,.20),(hx+7,side*6,11,.03)],'accent',8,5)
    for n in range(4 if not centipede else 1):
        s.eyes(hx+2,1+n*.7,8+n*.6,.45,'glow')


def slime(s,t):
    s.oval('Low_spreading_mass',(0,0,5),(14,13,5),'body',32,16)
    s.oval('Raised_asymmetric_lobe',(-3,1,10),(10,9,8),'body',28,16)
    for n in range(16):
        a=n*TAU/16
        s.oval(f'Pseudopod_{n}',(12*math.cos(a),11*math.sin(a),2.3),(3.5,3,2.3),'body',16,10)
    for n in range(18):
        a=n*2.4
        s.oval(f'Surface_bubble_{n}',(7*math.cos(a),7*math.sin(a),12+n%5),(1.1,1.1,1.0),'accent',12,8)


def tentacles(s,t):
    tower='tower' in t
    h=35 if tower else 20 if 'mantle' in t else 9
    s.oval('Mantle_core',(-2,0,h),(9,10,h),'body',28,18)
    for n in range(10 if tower else 8):
        a=n*TAU/(10 if tower else 8)
        c,ss=math.cos(a),math.sin(a)
        z=12+n*2.5 if tower else 6
        controls=[(3*c,3*ss,z,3.5),(12*c,12*ss,z*.6,2.5),(20*c,20*ss,3+(n%3)*6,1.5),(23*math.cos(a+.35),23*math.sin(a+.35),8+(n%3)*9,.7),(18*math.cos(a+.65),18*math.sin(a+.65),12+(n%3)*8,.035)]
        s.strand(f'Tentacle_{n:02d}',controls,'accent' if 'pale' in t else 'body',14,7)
        if 'suckers' in t:
            for j in range(7):
                r=7+j*1.6
                s.oval(f'Sucker_{n}_{j}',(r*c,r*ss,z*(1-(r-3)/25)+.6),(.65,.65,.3),'accent',10,7)
    if not tower:
        s.eyes(7,6,h+3,1.6)
    else:
        for n in range(5):
            s.strand(f'High_whip_{n}',[(0,0,30,2),(-5+n*2,4,47,1.1),(n*3-6,7,60,.05)],'body',12,6)


def bloat(s,t):
    s.oval('Gas_bladder',(0,0,16),(11,10,15),'body',36,24)
    for n in range(14):
        a=n*TAU/14
        controls=[]
        for j in range(13):
            p=-1.35+j*2.7/12
            angle=a+.08*math.sin(j*1.8)
            controls.append((11.05*math.cos(p)*math.cos(angle),10.05*math.cos(p)*math.sin(angle),16+15.05*math.sin(p),.11))
        s.strand(f'Membrane_vein_{n}',controls,'accent',6,2)
    s.strand('Trailing_membrane_seam',[(0,0,2,1.2),(1,1,-2,.5),(-1,1,-4,.025)],'accent',10,4)


def toad(s):
    s.oval('Broad_warty_body',(-2,0,9),(11,10,8),'body',28,18)
    s.oval('Wide_head',(7,0,9),(7,9,5),'body',28,16)
    s.oval('Throat_sac',(9,0,5),(5,7,3),'accent')
    for side in (-1,1):
        s.oval(f'Powerful_haunch_{side}',(-7,side*9,6),(7,5,5),'body')
        s.strand(f'Hind_leg_{side}',[(-9,side*10,7,2),(-2,side*13,2,1.1),(-9,side*15,1,.5)],'body',12,4)
        s.strand(f'Foreleg_{side}',[(6,side*7,9,1.8),(10,side*11,4,1),(14,side*11,1,.5)],'body',12,4)
        for j in range(4):
            s.strand(f'Toe_{side}_{j}',[(14,side*11,1,.4),(17,side*(9+j),.3,.07)],'accent',8,3)
        s.oval(f'Eye_tower_{side}',(8,side*6,13),(3,3,3),'body')
    s.eyes(10,6,14,1.4)
    s.strand('Wide_mouth',[(12,-7,7,.18),(14,0,7,.18),(12,7,7,.18)],'dark',8,3)
    for n in range(44):
        a=n*2.4; r=math.sqrt(n/44)
        x=-3+8*r*math.cos(a); y=8*r*math.sin(a)
        z=9+8*math.sqrt(max(.01,1-r*r*.9))
        s.oval(f'Wart_{n}',(x,y,z),(.7,.7,.6),'accent',8,6)


def turret(s,t):
    # A wall-like backing is visual only. Existing actors stay nonblocking.
    s.box('Stone_wall_mount',(-5,0,18),(4,13,17),'cloth')
    s.oval('Iron_housing',(0,0,18),(6,9,9),'dark',12,8)
    s.strand('Barrel',[(0,0,18,3.3),(14,0,18,3.3)],'wood',16,1)
    s.oval('Dark_muzzle',(14.2,0,18),(.1,2.5,2.5),'dark',16,10)
    for side in (-1,1):
        for z in (7,29):
            s.oval(f'Mount_bolt_{side}_{z}',(-.8,side*9,z),(1,.9,.9),'bone',8,6)
    if 'crossbow' in t or 'darts' in t:
        s.strand('Spring_loaded_bow',[(7,-13,16,1.1),(4,-7,19,1.2),(3,0,20,1.2),(4,7,19,1.2),(7,13,16,1.1)],'wood',10,4)
        s.strand('Bowstring',[(7,-13,16,.15),(10,0,17,.15),(7,13,16,.15)],'bone',6,1)
        for n in range(3 if 'darts' in t else 1):
            s.strand(f'Loaded_projectile_{n}',[(0,n-1,20,.25),(16,n-1,20,.25),(18,n-1,20,.02)],'bone',8,1)
        for n in range(10):
            a=n*TAU/10
            s.oval(f'Gear_tooth_{n}',(0,7+3*math.cos(a),12+3*math.sin(a)),(1,.6,.6),'bone',8,6)
    if 'crystals' in t:
        for n in range(5):
            s.oval(f'Charged_crystal_{n}',(0,(n-2)*3,29),(1.5,1.5,5),'glow',6,4)
    if 'nozzle' in t:
        s.oval('Copper_pressure_vessel',(-1,0,29),(5,7,6),'accent',16,10)
        for side in (-1,1):
            s.strand(f'Fuel_line_{side}',[(0,side*5,29,.7),(7,side*6,23,.7),(9,side*3,18,.7)],'wood',10,4)
    for n in range(5):
        s.strand(f'Engraved_mark_{n}',[(-.8,-7+n*3.5,6,.15),(-.7,-6+n*3.5,10,.15)],'glow' if 'sigils' in t else 'accent',6,1)


def totem(s,t,prism=False):
    if prism:
        # Six-sided mirrored pillar; diffuse facets, not a fake real reflection.
        s.strand('Shoulder_high_prism',[(0,0,1,8),(0,0,40,8)],'bone',6,1)
        for n in range(6):
            a=n*TAU/6
            s.strand(f'Mirror_edge_{n}',[(8*math.cos(a),8*math.sin(a),1,.22),(8*math.cos(a),8*math.sin(a),40,.22)],'glow',6,1)
        return
    mat='wood' if 'wood' in t else 'body'
    s.strand('Carved_column',[(0,0,1,9),(0,0,6,9),(0,0,8,6),(0,0,37,5),(0,0,42,8)],mat,12,3)
    for n in range(4):
        z=12+n*7
        s.oval(f'Carved_mask_{n}',(4,0,z),(3,5,3),'bone' if 'bone' in t else 'accent',12,8)
        s.eyes(6.6,2,z+1,.6,'glow')
    for side in (-1,1):
        s.strand(f'Crosspiece_{side}',[(0,side*2,33,1.5),(0,side*12,33,1.2)],mat,10,2)
        for n in range(3):
            s.strand(f'Charm_cord_{side}_{n}',[(0,side*(7+n*2),33,.15),(0,side*(7+n*2),27-n,.15)],'cloth',6,1)
            s.oval(f'Charm_{side}_{n}',(0,side*(7+n*2),25-n),(1,1,2),'bone',10,7)
    s.oval('Power_stone',(0,0,45),(3,3,4),'glow',8,6)


def winged(s,t):
    bird='bird' in t
    fairy='fairy' in t
    s.oval('Breast',(0,0,18),(5,4,8),'body',24,16)
    s.oval('Head',(3,0,27),(3,3,3.7),'body',24,14)
    s.eyes(5.5,2,28,.7)
    if bird:
        s.strand('Hooked_beak',[(5,0,27,1.6),(9,0,26,.7),(8.5,0,24,.04)],'bone',12,4)
        for n in range(7):
            s.strand(f'Tail_plume_{n}',[(-3,(n-3)*.5,14,.8),(-11,(n-3),5,.65),(-22,(n-3)*1.5,2+n%2,.03)],'accent' if n%2 else 'glow',10,6)
    elif not fairy:
        for side in (-1,1):
            s.strand(f'Ear_{side}',[(2,side*2,28,1.1),(1,side*4,34,.04)],'body',10,3)
        s.teeth(6,3,25,4,.9)
    for side in (-1,1):
        s.strand(f'Leg_{side}',[(0,side*2,12,1),(2,side*3,8,.7),(3,side*3,5,.3)],'body',10,4)
        for j in range(3):
            s.strand(f'Talon_{side}_{j}',[(3,side*3,5,.3),(5,side*3+(j-1),4,.02)],'bone',6,3)
        if fairy:
            s.strand(f'Fairy_arm_{side}',[(0,side*3,22,1),(3,side*6,17,.4)],'body',10,3)
            s.hand((3,side*6,17),side)
    wings(s,feather=bird,z=21,span=25 if not fairy else 18)
    if 'demon' in t:
        # Fury is a winged demon, not a large copy of the vampire bat.
        for side in (-1,1):
            s.strand(f'Fury_reaching_arm_{side}',[(0,side*3,22,1.4),(6,side*8,17,1),(10,side*8,20,.6)],'body',12,4)
            s.hand((10,side*8,20),side,True)
            s.strand(f'Fury_crown_horn_{side}',[(1,side*2,29,1),(0,side*4,35,.5),(3,side*4,36,.03)],'bone',10,4)


def flame(s,t):
    humanoid_flame='humanoid' in t
    if humanoid_flame:
        humanoid(s, ['gaunt'])
    else:
        s.oval('Luminous_core',(0,0,10),(5,5,8),'glow',24,16)
    for n in range(14):
        a=n*2.4
        x,y=5*math.cos(a),5*math.sin(a)
        z=8+n%6*7 if humanoid_flame else 6
        s.strand(f'Flame_tongue_{n}',[(x,y,z,2),(x+2,y,z+7,1.4),(x-1,y+1,z+14,.4),(x+2,y,z+19,.015)],'glow' if n%3==0 else 'body',12,5)


def specter(s,t):
    s.oval('Hood',(0,0,44),(6,6,9),'body',24,16)
    s.oval('Hollow_face',(5,0,44),(1,4,5),'dark',20,12)
    s.eyes(6,2,46,.6,'glow')
    for n in range(16):
        a=n*TAU/16
        s.strand(f'Ragged_shroud_{n}',[(3*math.cos(a),4*math.sin(a),46,2),(6*math.cos(a),7*math.sin(a),31,2),(8*math.cos(a),10*math.sin(a),10,1.4),(10*math.cos(a),12*math.sin(a),n%4*2,.02)],'body',12,6)
    for side in (-1,1):
        s.strand(f'Reaching_arm_{side}',[(0,side*5,38,2),(3,side*10,30,1),(9,side*10,28,.6)],'body',12,5)
        s.hand((9,side*10,28),side,True)


def worm(s,t):
    controls=[]
    for j in range(32):
        a=j*TAU/18
        r=14-j*.2
        controls.append((r*math.cos(a),r*math.sin(a),6+j*1.2,4.2))
    controls.extend([(7,0,47,4.5),(11,0,51,5)])
    s.strand('Massive_coiled_trunk',controls,'body',24,3,True)
    for n in range(24):
        a=TAU*n/24
        s.strand(f'Radial_maw_tooth_{n}',[(15,4*math.cos(a),51+4*math.sin(a),.55),(16,2*math.cos(a),51+2*math.sin(a),.04)],'bone',8,2)
    s.oval('Maw_darkness',(15.3,0,51),(.2,3.4,3.4),'dark',24,12)


def dragon(s,t):
    # Grounded serpent, deliberately no invented flight wings.
    trunk=[(-20,8,3,.05),(-17,12,5,2),(-10,8,10,4),(-8,-3,14,6),(0,-5,20,7),(5,0,30,6),(7,0,42,4.5),(13,0,46,4)]
    s.strand('Great_serpent_trunk',trunk,'body',32,7)
    s.oval('Dragon_skull',(16,0,47),(6,4.5,3.6),'body',28,18)
    s.oval('Powerful_jaws',(21,0,45),(6,4,2.5),'body',24,14)
    s.eyes(19,4,49,1.1,'glow')
    s.teeth(25,6,44,10,1.5)
    for side in (-1,1):
        s.strand(f'Crown_horn_{side}',[(12,side*3,50,1.6),(8,side*5,57,.9),(12,side*6,60,.03)],'bone',12,5)
        for z,x in ((12,-6),(27,5)):
            s.strand(f'Clawed_limb_{side}_{z}',[(x,side*4,z,2.5),(x+3,side*10,z-4,1.8),(x+7,side*10,3,1)],'body',16,5)
            for j in range(3):
                s.strand(f'Claw_{side}_{z}_{j}',[(x+7,side*10+j-1,3,.55),(x+10,side*10+j-1,1,.02)],'bone',8,3)
    # Attach ridges to the actual sampled trunk, never an unrelated coordinate
    # formula (which can leave decorative scales floating beside a bent neck).
    for n,(x,y,z,r) in enumerate(rat.spline(trunk,4)[5:-3]):
        s.strand(f'Dorsal_spine_{n}',[(x-r*.8,y,z,1),(x-r-3,y,z+2,.035)],'accent',8,3)
    for side in (-1,1):
        s.strand(f'Heavy_dragon_brow_{side}',[(17,side*3.8,50,1),(20,side*3.6,50,.7)],'accent',12,3)
        s.oval(f'Nostril_{side}',(25,side*2,46),(.25,.5,.5),'dark',10,8)


def dryad(s):
    s.strand('Gnarled_trunk',[(0,0,3,6),(-2,1,18,5),(1,-1,35,5),(0,0,46,3)],'wood',22,6,True)
    s.oval('Wooden_face',(3,0,42),(3,4,5),'wood')
    s.eyes(5.6,2,43,.65,'glow')
    for n in range(9):
        a=n*TAU/9
        s.strand(f'Prop_root_{n}',[(0,0,12,2.2),(9*math.cos(a),9*math.sin(a),4,1.3),(14*math.cos(a+.2),14*math.sin(a+.2),.3,.15)],'wood',12,5)
    for side in (-1,1):
        s.strand(f'Branch_arm_{side}',[(0,side*3,35,2.5),(2,side*11,30,1.7),(8,side*14,37,.8)],'wood',12,5)
        for n in range(5):
            s.strand(f'Twig_finger_{side}_{n}',[(8,side*14,37,.55),(10+n,side*(14+n*.5),43-n,.3),(12+n,side*(15+n),42-n,.02)],'wood',8,4)
    for n in range(12):
        a=n*2.4
        s.strand(f'Crown_branch_{n}',[(0,0,44,1.4),(7*math.cos(a),7*math.sin(a),51, .8),(11*math.cos(a+.3),11*math.sin(a+.3),57+n%3,.04)],'wood',10,5)
        s.oval(f'Leaf_cluster_{n}',(9*math.cos(a),9*math.sin(a),54),(2,1.2,.6),'body',10,6)


def build_parts(record):
    p=profiles()[record['symbol']]
    recipe,t=p['recipe'],p['traits']
    s=Sculpt()
    if recipe=='humanoid': humanoid(s,t)
    elif recipe=='quadruped': quadruped(s,t,'horse' in t)
    elif recipe=='serpent': serpent(s,t)
    elif recipe=='bloat': bloat(s,t)
    elif recipe=='toad': toad(s)
    elif recipe=='slime': slime(s,t)
    elif recipe in ('spider','centipede'): arthropod(s,recipe=='centipede')
    elif recipe=='tentacles': tentacles(s,t)
    elif recipe=='winged': winged(s,t)
    elif recipe=='turret': turret(s,t)
    elif recipe in ('totem','prism'): totem(s,t,recipe=='prism')
    elif recipe=='flame': flame(s,t)
    elif recipe=='specter': specter(s,t)
    elif recipe=='worm': worm(s,t)
    elif recipe=='dragon': dragon(s,t)
    elif recipe=='dryad': dryad(s)
    elif recipe=='blade':
        s.weapon('Spectral_sword',(0,0,12),'sword','body')
        s.oval('Spectral_pommel',(0,0,8),(1.2,1.1,1.3),'glow',12,8)
        s.oval('Guard_gem',(0,-.65,16),(.6,.25,.7),'glow',10,7)
        for side in (-1,1):
            s.strand(f'Spectral_edge_{side}',[(side,0,18,.09),(side*.7,0,35,.09),(0,0,40,.025)],'glow',6,3)
        for n in range(6):
            a=n*TAU/6
            s.strand(f'Hilt_inlay_{n}',[(.65*math.cos(a),.65*math.sin(a),9,.09),(.65*math.cos(a),.65*math.sin(a),15,.09)],'bone',6,1)
    elif recipe=='gem':
        s.oval('Soul_gem',(0,0,9),(5,5,8),'glow',8,5)
        for side in (-1,1):
            s.strand(f'Gem_setting_{side}',[(0,side*4,15,.5),(0,side*6,5,.6),(0,0,1,.6)],'bone',8,3)
    elif recipe=='egg':
        s.oval('Translucent_membrane_interpretation',(0,0,10),(7,7,10),'accent',28,20)
        s.oval('Bright_yolk_window',(5,0,10),(2.5,4,5),'glow',24,16)
        for n in range(24):
            a=n*TAU/24
            s.oval(f'Ash_nest_{n}',(8*math.cos(a),8*math.sin(a),1),(2,1.5,1),'dark',10,6)
    elif recipe=='centaur':
        quadruped(s,['horse'],True)
        # Remove equine neck/head, not its four-legged body.
        s.parts=[part for part in s.parts if not any(part.name.startswith(n) for n in ('Neck','Head','Long_muzzle','Nose','Eye','Ear','Mane'))]
        torso=Sculpt(); humanoid(torso,['bow'])
        torso.parts=[part for part in torso.parts if not part.name.startswith(('Leg','Foot','Pelvis'))]
        for part in torso.parts:
            part.vertices=[(x+8,y,z-4) for x,y,z in part.vertices]
        s.parts.extend(torso.parts)
        s.strand('Great_bow',[(14,-12,15,.7),(18,-12,28,.9),(14,-12,44,.7)],'wood',12,6)
        s.strand('Bowstring',[(14,-12,15,.12),(14,-12,44,.12)],'bone',6,1)
        s.strand('Nocked_arrow',[(5,-12,29,.2),(26,-12,29,.2),(28,-12,29,.025)],'bone',8,1)
        s.strand('Quiver',[(-1,5,31,2),(-3,5,44,2)],'cloth',12,1)
        for n in range(5): s.strand(f'Quiver_arrow_{n}',[(-3,4+n*.4,40,.17),(-4,4+n*.4,50,.17)],'wood',6,1)
    else: raise ValueError(recipe)
    vertices=[v for part in s.parts for v in part.vertices]
    low=[min(v[i] for v in vertices) for i in range(3)]
    high=[max(v[i] for v in vertices) for i in range(3)]
    clearance=16 if 'MONST_FLIES' in record['catalogTokens'] else 0
    scale=[p['dimensions'][i]/(high[i]-low[i]) for i in range(3)]
    for part in s.parts:
        part.vertices=[((x-(low[0]+high[0])/2)*scale[0],(y-(low[1]+high[1])/2)*scale[1],(z-low[2])*scale[2]+clearance) for x,y,z in part.vertices]
    return s.parts


def texture_bytes(record):
    """Original diffuse texture: seven padded anatomical/material UV regions."""
    traits=set(profiles()[record['symbol']]['traits'])
    color=record['color']
    rgb=tuple(max(25,min(225,round(color[c]*2.1))) for c in ('red','green','blue'))
    if 'black' in traits: rgb=(22,25,31)
    if 'pale' in traits: rgb=(182,174,153)
    if 'stone' in traits: rgb=(126,130,134)
    if 'horse' in traits and 'rainbow' in traits: rgb=(202,200,185)
    if 'white_hot' in traits: rgb=(240,214,155)
    if 'blue' in traits: rgb=(45,105,216)
    if 'primate' in traits or 'lizard' in traits: rgb=(115,91,61)
    if 'elf' in traits: rgb=(108,101,123)
    if 'undead' in traits: rgb=(146,144,112)
    if 'pale' in traits and record['symbol']=='MK_BOG_MONSTER': rgb=(161,150,124)
    palette={'fur':rgb,'ear':tuple(min(240,int(c*.75+37)) for c in rgb),
             'tail':(97,67,39),'paw':tuple(max(25,int(color[c]*1.3)) for c in ('red','green','blue')),
             'eye':(15,17,21),'claw':(194,180,140),'whisker':(233,181,74)}
    if 'golden_eyes' in traits: palette['whisker']=(250,192,45)
    if 'sigils' in traits: palette['whisker']=tuple(max(75,min(250,round(color[c]*2.5))) for c in ('red','green','blue'))
    if 'blue' in traits: palette['whisker']=(145,206,255)
    if 'red_eyes' in traits or 'ember_eyes' in traits: palette['whisker']=(248,51,22)
    if 'spectral' in traits or 'ectoplasm' in traits: palette['claw']=rgb; palette['whisker']=(145,231,220)
    if 'stone' in traits: palette['tail']=(87,88,82); palette['claw']=(162,168,168); palette['paw']=(94,102,111)
    size=1024
    pixels=bytearray((28,30,33))*size*size
    for tile,(x0,y0,x1,y1) in rat.TILES.items():
        base=palette[tile]
        for y in range(max(0,y0-6),min(size,y1+7)):
            for x in range(max(0,x0-6),min(size,x1+7)):
                u=(x-x0)/max(1,x1-x0); v=(y-y0)/max(1,y1-y0)
                noise=((x*13+y*29+(x*y)%73+record['kind']*7)%23-11)*.45
                detail=noise+4*math.sin(u*35+v*19)
                if tile=='fur':
                    if traits & {'scales','chitin','segments'}:
                        scale_v=(v*34)%1; scale_u=(u*48+int(v*34)*.5)%1
                        detail+=-17 if scale_v<.10 or scale_u<.08 else 5*math.sin(scale_v*math.pi)
                    elif 'fur' in traits:
                        detail+=9*math.sin(v*560+u*35)*math.sin(u*28)
                    elif 'membrane' in traits:
                        detail+=9*math.sin(u*7)*math.sin(v*12)
                    elif traits & {'stone','cracks'}:
                        detail+=-24 if abs(math.sin(u*47+math.sin(v*35)))<.05 else 0
                    elif 'goo' in traits:
                        detail+=15*math.sin(u*17+v*12)*math.sin(v*18)
                    else: detail+=5*math.sin(u*81)*math.sin(v*93)
                elif tile=='tail': detail+=12*math.sin(v*180+math.sin(u*19)*3)
                elif tile=='paw': detail+=3*((x+y)%4)+5*math.sin(u*78)
                elif tile=='claw': detail+=8*math.sin(u*9)+v*12
                elif tile=='whisker' and 'rainbow' in traits:
                    base=tuple(140+85*math.sin(u*TAU+i*TAU/3) for i in range(3))
                index=(y*size+x)*3
                pixels[index:index+3]=bytes(max(0,min(255,round(c+detail))) for c in base)
    raw=b''.join(b'\0'+pixels[y*size*3:(y+1)*size*3] for y in range(size))
    def chunk(kind,data): return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',size,size,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(raw,9))+chunk(b'IEND',b'')


def obj_bytes(parts, symbol):
    return rat.obj_bytes(parts).replace(b'original detailed rat',('original creature '+symbol).encode('ascii'),1)


def build(kinds=None):
    records=source_records()
    metrics={}
    if INDEX.exists():
        for e in json.loads(INDEX.read_text())['creatures']:
            metrics[e['symbol']]={key:e['art'][key] for key in ('triangles','parts','bounds','objSha256','skinSha256') if key in e['art']}
    for record in records:
        k=record['kind']
        if k<2 or (kinds is not None and k not in kinds): continue
        symbol=record['symbol']; slug=symbol.removeprefix('MK_').lower()
        parts=build_parts(record)
        model=obj_bytes(parts,symbol); skin=texture_bytes(record)
        (ROOT/f'mod/BrogueDoom/models/monsters/{k:02d}_{slug}.obj').write_bytes(model)
        (ROOT/f'mod/BrogueDoom/graphics/BRGM{k:02d}.png').write_bytes(skin)
        vertices=[v for p in parts for v in p.vertices]
        metrics[symbol]={'triangles':sum(sum(1 for _ in p.triangles()) for p in parts),'parts':len(parts),
                         'bounds':[[round(min(v[i] for v in vertices),5) for i in range(3)], [round(max(v[i] for v in vertices),5) for i in range(3)]],
                         'objSha256':hashlib.sha256(model).hexdigest(),'skinSha256':hashlib.sha256(skin).hexdigest()}
        print(f"BRG-M{k:02d} {symbol}: {len(parts)} parts, {metrics[symbol]['triangles']} triangles",flush=True)
    write_index(metrics)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kind',type=int,action='append',help='Stable Brogue kind to rebuild (repeatable; 2–67)')
    args=parser.parse_args()
    if args.kind and any(k<2 or k>67 for k in args.kind): parser.error('Only non-rat kinds 2–67 are generated here')
    build(args.kind)
