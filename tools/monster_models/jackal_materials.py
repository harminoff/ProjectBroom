"""Original brown canine skin: deterministic diffuse fur, no simulation RNG."""
import math,struct,zlib
from .rat import TILES
SKIN='graphics/BRGJACK.png'

def texture_bytes(palette=None,back_shading=True):
 size=1024;pixels=bytearray((25,20,16))*size*size
 palette=palette or {'fur':(145,98,57),'ear':(92,53,35),'tail':(120,77,43),'paw':(182,144,94),'eye':(12,9,6),'claw':(205,189,153),'whisker':(213,152,45)}
 for tile,(x0,y0,x1,y1) in TILES.items():
  for y in range(max(0,y0-6),min(size,y1+7)):
   for x in range(max(0,x0-6),min(size,x1+7)):
    u=(x-x0)/(x1-x0);v=(y-y0)/(y1-y0);base=palette[tile]
    noise=(((x*1619+y*31337)^(x*y*6971))&255)/255-.5
    detail=noise*7
    if tile in ('fur','tail'):
     row=math.floor(v*190);col=math.floor(u*95)
     seed=(((col*1619+row*31337)^(col*row*6971))&255)/255
     along=u*95%1;across=v*190%1
     center=.3+seed*.35+along*.12
     stroke=max(0,1-abs(across-center)*8)*math.sin(math.pi*along)
     detail+=(seed-.48)*31*stroke+5*math.sin(u*41)*math.sin(v*37)
     if tile=='fur' and back_shading:
      saddle=max(0,1-abs(v-.25)*4)*43
      belly=max(0,1-abs(v-.75)*5)*17
      detail+=belly-saddle
    elif tile=='ear':detail+=7*math.sin(u*23)+3*math.sin(v*110)
    elif tile=='paw':detail+=5*math.sin(u*170+v*17)
    elif tile=='eye':detail=noise*2
    index=(y*size+x)*3;pixels[index:index+3]=bytes(max(0,min(255,round(c+detail))) for c in base)
 def chunk(k,d):return struct.pack('>I',len(d))+k+d+struct.pack('>I',zlib.crc32(k+d)&0xffffffff)
 raw=b''.join(b'\0'+pixels[y*size*3:(y+1)*size*3] for y in range(size))
 return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',size,size,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(raw,9))+chunk(b'IEND',b'')
