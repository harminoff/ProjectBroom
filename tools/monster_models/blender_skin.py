"""Fuse a closed blockout, retopologize, and transfer UVs/normalized skin weights.

Run in isolated Blender 5.2 background: --python blender_skin.py -- kobold.
No downloaded geometry. Canonical topology ordering; cold bakes are checked for determinism.
"""
import gzip, importlib, json, sys, hashlib
from pathlib import Path
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import barycentric_transform

ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from tools.monster_models.connected_skin import selected, fingerprint, path


def canonicalize(obj):
    """Remove allocator/voxel traversal order from the retopology input."""
    old=obj.data
    coordinates=[tuple(round(c,5) for c in v.co) for v in old.vertices]
    vertices=sorted(set(coordinates));lookup={v:i for i,v in enumerate(vertices)}
    faces=[]
    for polygon in old.polygons:
        face=tuple(lookup[coordinates[i]] for i in polygon.vertices)
        if len(set(face))!=len(face):continue
        start=face.index(min(face));faces.append(face[start:]+face[:start])
    mesh=bpy.data.meshes.new('Canonical cage');mesh.from_pydata(vertices,[],sorted(faces));mesh.update()
    obj.data=mesh;bpy.data.meshes.remove(old)
    print('CAGE_HASH',hashlib.sha256(json.dumps([vertices,sorted(faces)]).encode()).hexdigest(),flush=True)


def build(enemy):
    if not bpy.app.background: raise RuntimeError('Use isolated background Blender')
    bpy.ops.wm.read_factory_settings(use_empty=True)
    rig=importlib.import_module('tools.monster_models.'+enemy+'_animation')
    parts=rig.build_parts(); vertices=[]; faces=[]; uv=[]; weights=[];owners=[]
    for p in parts:
        if not selected(enemy,p.name): continue
        base=len(vertices);vertices.extend(p.vertices);uv.extend(p.uv)
        weights.extend(rig.weights(p,v,u) for v,u in zip(p.vertices,p.uv))
        for a,b,c in p.triangles():
            if (Vector(p.vertices[b])-Vector(p.vertices[a])).cross(Vector(p.vertices[c])-Vector(p.vertices[a])).length_squared>1e-10:
                faces.append((base+a,base+b,base+c));owners.append(p.name)
    tree=BVHTree.FromPolygons(vertices,faces,all_triangles=True)
    source_faces={name:[t for t,owner in zip(faces,owners) if owner==name] for name in sorted(set(owners))}
    source_trees={name:BVHTree.FromPolygons(vertices,triangles,all_triangles=True) for name,triangles in source_faces.items()}
    mesh=bpy.data.meshes.new('Closed blockout');mesh.from_pydata(vertices,[],faces);mesh.update()
    obj=bpy.data.objects.new('Connected skin',mesh);bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active=obj;obj.select_set(True)
    # Weld UV duplicates and remove degenerate pole triangles before volume fusion.
    bm=bmesh.new();bm.from_mesh(mesh)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
    canonicalize(obj)
    modifier=obj.modifiers.new('Fuse overlapping anatomical volumes','REMESH')
    modifier.mode='VOXEL';modifier.voxel_size=.14 if enemy=='rat' else .24
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    canonicalize(obj)
    modifier=obj.modifiers.new('Relax blockout junctions','SMOOTH');modifier.factor=1;modifier.iterations=4
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    canonicalize(obj)
    # Collapse the canonicalized fused surface to a bounded animation cage.
    # QuadriFlow was evaluated here but its floating solver did not reproduce
    # byte-identical cold bakes. This deterministic reduction keeps the closed
    # surface; skin continuity and the actual clip poses are verified separately.
    modifier=obj.modifiers.new('Bounded connected animation cage','DECIMATE')
    modifier.decimate_type='COLLAPSE'
    modifier.ratio=min(1,5600/sum(len(f.vertices)-2 for f in obj.data.polygons))
    modifier.use_collapse_triangulate=True
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    canonicalize(obj)
    mesh=obj.data;mesh.update()
    # Reduction can leave a tiny cap hole where an axis-aligned primitive pole
    # meets the voxel grid. Close only small boundary loops, then verify them.
    bm=bmesh.new();bm.from_mesh(mesh)
    boundary=[e for e in bm.edges if e.is_boundary]
    if boundary:
        if any(e.calc_length()>.6 for e in boundary):raise RuntimeError('Large open boundary in fused skin')
        bmesh.ops.holes_fill(bm,edges=boundary,sides=8)
        if any(e.is_boundary for e in bm.edges):raise RuntimeError('Unclosed skin boundary')
        bmesh.ops.triangulate(bm,faces=[f for f in bm.faces if len(f.verts)>3])
        bm.to_mesh(mesh);mesh.update()
    bm.free()
    points=[tuple(v.co) for v in mesh.vertices];polygons=[tuple(f.vertices) for f in mesh.polygons]
    neighbors=[set() for _ in points]
    for e in mesh.edges:
        a,b=e.vertices;neighbors[a].add(b);neighbors[b].add(a)
    visited=set();components=[]
    for i in range(len(points)):
        if i in visited:continue
        todo=[i];group=[];visited.add(i)
        while todo:
            n=todo.pop();group.append(n)
            for v in sorted(neighbors[n]):
                if v not in visited:visited.add(v);todo.append(v)
        components.append(group)
    if len(components)!=1:
        components.sort(key=len,reverse=True)
        crumbs=components[1:]
        if any(len(c)>4 or max(max(points[i][a] for i in c)-min(points[i][a] for i in c) for a in range(3))>.5 for c in crumbs):
            raise RuntimeError(f'{enemy}: disconnected body components {[len(c) for c in components]}')
        # Sub-voxel slivers at pointed toe ends are not anatomical components.
        keep=sorted(components[0]);remap={old:new for new,old in enumerate(keep)}
        polygons=[tuple(remap[i] for i in f) for f in polygons if all(i in remap for i in f)]
        neighbors=[{remap[j] for j in neighbors[i]} for i in keep]
        points=[points[i] for i in keep];components=[list(range(len(points)))]
    transferred=[]
    for point in points:
        co,normal,index,distance=tree.find_nearest(Vector(point));ids=faces[index]
        factors=barycentric_transform(co,*(Vector(vertices[i]) for i in ids),Vector((1,0,0)),Vector((0,1,0)),Vector((0,0,1)))
        blend={}
        for i,factor in zip(ids,factors):
            for bone,w in weights[i]:blend[bone]=blend.get(bone,0)+max(0,factor)*w
        transferred.append(blend)
    # Shared vertices receive one weight set, including across material seams.
    # Local relaxation creates a parent/limb transition instead of a rigid cut.
    for _ in range(5):
        relaxed=[]
        for i,blend in enumerate(transferred):
            out={b:w*.5 for b,w in blend.items()}
            for n in sorted(neighbors[i]):
                for b,w in transferred[n].items():out[b]=out.get(b,0)+w*.5/len(neighbors[i])
            relaxed.append(out)
        transferred=relaxed
    normalized=[]
    for blend in transferred:
        keep=sorted(blend.items(),key=lambda x:(-x[1],x[0]))[:4];total=sum(w for b,w in keep)
        normalized.append([(b,w/total) for b,w in keep])
    # Project each polygon to one source part: no interpolation across atlas
    # regions. UV seams split export vertices but retain identical position/weights.
    outv=[];outu=[];outw=[];outf=[];topology=[];lookup={}
    uv_bounds={p.name:[(min(u[a] for u in p.uv),max(u[a] for u in p.uv)) for a in range(2)] for p in parts}
    for face in polygons:
        center=sum((Vector(points[i]) for i in face),Vector())/len(face)
        _,_,index,_=tree.find_nearest(center);owner=owners[index];new=[];mapped_face=[]
        for i in face:
            closest,_,index,_=source_trees[owner].find_nearest(Vector(points[i]));ids=source_faces[owner][index]
            factors=barycentric_transform(closest,*(Vector(vertices[j]) for j in ids),Vector((1,0,0)),Vector((0,1,0)),Vector((0,0,1)))
            f=[max(0,min(1,a)) for a in factors];total=sum(f)
            if total<1e-12:
                nearest=min(range(3),key=lambda j:(Vector(points[i])-Vector(vertices[ids[j]])).length_squared)
                f=[float(j==nearest) for j in range(3)];total=1
            mapped_face.append([round(sum(uv[j][axis]*a/total for j,a in zip(ids,f)),7) for axis in range(2)])
        # A polygon crossing a cylindrical UV wrap must stay at the tile edge,
        # not sample through the belly/other side of the atlas. The UV copies
        # still share geometry and bone weights on both sides of this seam.
        for axis,(low,high) in enumerate(uv_bounds[owner]):
            values=[u[axis] for u in mapped_face];mid=(low+high)/2
            if max(values)-min(values)>.6*(high-low):
                upper=sum(v>mid for v in values)>len(values)/2
                for u in mapped_face:
                    if upper and u[axis]<mid:u[axis]=round(high,7)
                    if not upper and u[axis]>mid:u[axis]=round(low,7)
        for i,mapped in zip(face,map(tuple,mapped_face)):
            key=(i,mapped)
            if key not in lookup:
                lookup[key]=len(outv);outv.append(points[i]);outu.append(mapped);outw.append(normalized[i]);topology.append(i)
            new.append(lookup[key])
        outf.append(new)
    data={'version':1,'blender':bpy.app.version_string,'sourceHash':fingerprint(enemy,parts,rig.weights),
          'vertices':outv,'uv':outu,'faces':outf,'weights':outw,'topology':topology,
          'cageVertices':len(points),'cageFaces':len(polygons),'components':len(components)}
    target=path(enemy);target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes(gzip.compress(json.dumps(data,separators=(',',':')).encode(),mtime=0))
    print('CONNECTED_SKIN_OK',enemy,len(points),len(polygons),len(outv),flush=True)


if __name__=='__main__':build(sys.argv[sys.argv.index('--')+1])
