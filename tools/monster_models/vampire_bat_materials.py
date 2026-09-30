"""Original charcoal fur and warm leathery bat atlas; no emission."""
import math
from .toad_materials import png, noise, SIZE
from .rat import TILES
SKIN='graphics/BRGBAT.png'
ROLES=('fur','membrane','ear','bone','dark','nose')
RECTS={n:(i%3*340+10,i//3*512+10,i%3*340+330,i//3*512+502) for i,n in enumerate(ROLES)}
def role(n):
 if n.startswith(('digit','arm','thumb')):return 'fur'
 if n.startswith(('fang','claw')):return 'bone'
 if n.startswith(('eye','mouth','nostril')):return 'dark'
 if n.startswith(('wing','digit','thumb','leg','toe','tail')):return 'membrane'
 if n.startswith('ear_inner'):return 'ear'
 if n.startswith(('nose','muzzle')):return 'nose'
 return 'fur'
def repack(parts):
 for p in parts:
  x0,y0,x1,y1=RECTS[role(p.name)];mapped=[]
  for u,v in p.uv:
   x,y=u*SIZE,(1-v)*SIZE
   old=next(r for r in TILES.values() if r[0]-.01<=x<=r[2]+.01 and r[1]-.01<=y<=r[3]+.01)
   a,b=(x-old[0])/(old[2]-old[0]),(y-old[1])/(old[3]-old[1])
   mapped.append(((x0+a*(x1-x0))/SIZE,1-(y0+b*(y1-y0))/SIZE))
  p.uv=mapped
 return parts
def texture_bytes():
 pixels=bytearray(SIZE*SIZE*3)
 for name,(x0,y0,x1,y1) in RECTS.items():
  base=dict(fur=(83,77,73),membrane=(117,86,78),ear=(139,99,91),bone=(204,194,164),dark=(17,12,11),nose=(101,77,73))[name]
  for y in range(y0-10,y1+10):
   for x in range(x0-10,x1+10):
    u=max(0,min(1,(x-x0)/(x1-x0)));v=max(0,min(1,(y-y0)/(y1-y0)))
    grain=noise(x,y)*9;cloud=math.sin(u*18+math.sin(v*24))*math.sin(v*22)*7
    d=grain+cloud
    if name=='fur':d+=3*math.sin(u*300+math.sin(v*21)*4)*noise(int(u*450),int(v*60))
    if name=='membrane':d+=2*math.sin(v*130+math.sin(u*37)*2)*noise(int(u*80),int(v*40))
    if name=='bone':d=grain*0.3+v*15
    if name=='dark':d=grain*.2
    pixels[(y*SIZE+x)*3:(y*SIZE+x)*3+3]=bytes(max(0,min(255,round(c+d))) for c in base)
 return png(pixels)
