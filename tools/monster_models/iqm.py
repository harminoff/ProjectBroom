"""Small deterministic IQM v2 writer for Project Broom's weighted assets.

Original implementation against https://github.com/lsalzman/iqm/blob/master/iqm.h
and the pinned GZDoom reader. File coordinates are X forward, Y lateral, Z up;
unlike OBJ, IQM performs its own Y/Z swap. IQM UV V is top-down in this reader.
"""
import math
import struct


def encode(vertices, normals, uv, triangles, influences, bones, clips, bounds, *,
           mesh_label="Project_Broom_rat", material_path="graphics/BRGRAT.png"):
    """bones: (name,parent,localXYZ); clips: name/fps/loop/frames[bone][TRS10]."""
    text = bytearray(b'\0')
    names = {}
    def name(value):
        if value not in names:
            names[value] = len(text)
            text.extend(value.encode('utf-8') + b'\0')
        return names[value]
    mesh_name, material = name(mesh_label), name(material_path)
    for b in bones: name(b[0])
    for clip in clips: name(clip['name'])
    data = bytearray(124)
    def block(payload):
        while len(data) % 4: data.append(0)
        offset = len(data); data.extend(payload); return offset
    def pack(fmt, rows):
        return b''.join(struct.pack('<'+fmt, *row) for row in rows)
    ot = block(text)
    om = block(struct.pack('<6I',mesh_name,material,0,len(vertices),0,len(triangles)))
    arrays = []
    for typ,fmt,size,code,rows in (
        (0,7,3,'3f',vertices),(1,7,2,'2f',[(u,1-v) for u,v in uv]),
        (2,7,3,'3f',normals),
        (4,1,4,'4B',[[i for i,w in row]+[0]*(4-len(row)) for row in influences]),
        (5,7,4,'4f',[[w for i,w in row]+[0]*(4-len(row)) for row in influences])):
        arrays.append((typ,0,fmt,size,block(pack(code,rows))))
    ova = block(pack('5I',arrays))
    # GZDoom reverses OBJ faces on load, but copies IQM indices directly.
    # IQM therefore needs clockwise file winding for our outward CCW meshes.
    otr = block(pack('3I',[(c,b,a) for a,b,c in triangles]))
    # Explicit boundary adjacency: the pinned loader reads this even if zero.
    oa = block(pack('3I',[(0xffffffff,)*3]*len(triangles)))
    oj = block(pack('Ii10f',[(name(n),p,*loc,0,0,0,1,1,1,1) for n,p,loc in bones]))
    frames = [frame for clip in clips for frame in clip['frames']]
    offsets,scales,masks=[],[],[]
    for b in range(len(bones)):
        low=[min(f[b][c] for f in frames) for c in range(10)]
        high=[max(f[b][c] for f in frames) for c in range(10)]
        step=[(hi-lo)/65535 if hi-lo>1e-10 else 0 for lo,hi in zip(low,high)]
        offsets.append(low); scales.append(step)
        masks.append(sum(1<<c for c,s in enumerate(step) if s))
    op = block(pack('iI20f',[(bones[b][1],masks[b],*offsets[b],*scales[b]) for b in range(len(bones))]))
    animations=[]; first=0
    for clip in clips:
        animations.append((name(clip['name']),first,len(clip['frames']),clip['fps'],int(clip['loop'])))
        first+=len(clip['frames'])
    oan = block(pack('3IfI',animations))
    channels = bytearray()
    for frame in frames:
        for b,row in enumerate(frame):
            for c,scale in enumerate(scales[b]):
                if scale:
                    channels.extend(struct.pack('<H',max(0,min(65535,round((row[c]-offsets[b][c])/scale)))))
    of = block(channels)
    ob = block(pack('8f',bounds))
    header=(2,len(data),0,len(text),ot,1,om,len(arrays),len(vertices),ova,
            len(triangles),otr,oa,len(bones),oj,len(bones),op,len(clips),oan,
            len(frames),sum(m.bit_count() for m in masks),of,ob,0,0,0,0)
    struct.pack_into('<16s27I',data,0,b'INTERQUAKEMODEL\0',*header)
    return bytes(data)


def inspect(data):
    """Independent section parser used by validation; reject malformed files."""
    magic,*h=struct.unpack_from('<16s27I',data)
    assert magic==b'INTERQUAKEMODEL\0' and h[0]==2 and h[1]==len(data)
    def rows(offset,count,fmt):
        size=struct.calcsize('<'+fmt)
        assert 124<=offset<=len(data) and offset+count*size<=len(data)
        return [struct.unpack_from('<'+fmt,data,offset+i*size) for i in range(count)]
    strings=data[h[4]:h[4]+h[3]]
    def name(offset): return strings[offset:].split(b'\0',1)[0].decode()
    arrays={t:(fmt,size,off) for t,flags,fmt,size,off in rows(h[9],h[7],'5I')}
    geometry={t:rows(off,h[8],str(size)+('f' if fmt==7 else 'B')) for t,(fmt,size,off) in arrays.items()}
    joints=rows(h[14],h[13],'Ii10f')
    poses=rows(h[16],h[15],'iI20f')
    anims=[{'name':name(n),'first':f,'count':c,'fps':rate,'loop':bool(loop)} for n,f,c,rate,loop in rows(h[18],h[17],'3IfI')]
    channels=iter(v[0] for v in rows(h[21],h[19]*h[20],'H'))
    frames=[]
    for f in range(h[19]):
        frame=[]
        for p in poses:
            frame.append([p[2+c]+(next(channels)*p[12+c] if p[1]&(1<<c) else 0) for c in range(10)])
        frames.append(frame)
    return {'vertices':geometry[0],'uv':geometry[1],'normals':geometry[2],
            'indices':geometry[4],'weights':geometry[5], 'triangles':rows(h[11],h[10],'3I'),
            'bones':[(name(j[0]),j[1],j[2:]) for j in joints],
            'animations':anims,'frames':frames,'bounds':rows(h[22],h[19],'8f')}
