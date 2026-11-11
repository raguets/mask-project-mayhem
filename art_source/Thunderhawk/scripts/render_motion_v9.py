"""Render editable Blender animation and wrap JPEG frames in a standard MJPEG AVI.
No external video encoder is required; source JPEG frames are retained.
"""
import bpy, math, struct, json
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[1]; out=root/'renders'/'v9'
s=bpy.context.scene; cam=s.camera
s.render.engine='BLENDER_WORKBENCH'
s.display.shading.light='STUDIO'; s.display.shading.color_type='MATERIAL'
s.display.shading.show_shadows=True; s.display.shading.show_cavity=True
s.view_settings.view_transform='Standard'; s.view_settings.exposure=0.0
s.render.resolution_x=800; s.render.resolution_y=560; s.render.resolution_percentage=100
s.render.image_settings.file_format='JPEG'; s.render.image_settings.quality=88
cam.data.type='PERSP'; cam.data.lens=48
def aim(target): cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
def chunk(tag,data): return tag+struct.pack('<I',len(data))+data+(b'\0' if len(data)%2 else b'')
def avi(path,paths,fps):
    frames=[p.read_bytes() for p in paths]; n=len(frames); width,height=800,560; largest=max(map(len,frames))
    header=struct.pack('<14I',round(1e6/fps),largest*fps,0,0x10,n,0,1,largest,width,height,0,0,0,0)
    stream=struct.pack('<4s4sIHH8I4h',b'vids',b'MJPG',0,0,0,0,1,fps,0,n,largest,0xffffffff,0,0,0,width,height)
    bitmap=struct.pack('<IiiHHIIiiII',40,width,height,1,24,int.from_bytes(b'MJPG','little'),width*height*3,0,0,0,0)
    hdrl=chunk(b'LIST',b'hdrl'+chunk(b'avih',header)+chunk(b'LIST',b'strl'+chunk(b'strh',stream)+chunk(b'strf',bitmap)))
    idx=[]; chunks=[]; offset=4
    for frame in frames:
        c=chunk(b'00dc',frame); chunks.append(c)
        idx.append(struct.pack('<4sIII',b'00dc',0x10,offset,len(frame))); offset+=len(c)
    data=b'AVI '+hdrl+chunk(b'LIST',b'movi'+b''.join(chunks))+chunk(b'idx1',b''.join(idx))
    path.write_bytes(b'RIFF'+struct.pack('<I',len(data))+data)
    # Verify actual frame chunks against the AVI index, plus RIFF length.
    assert path.stat().st_size==len(data)+8
    assert all(frame.startswith(b'\xff\xd8') and frame.endswith(b'\xff\xd9') for frame in frames)
    return {'path':str(path.relative_to(root)),'frames':n,'fps':fps,'size_bytes':path.stat().st_size,'codec':'MJPG','media_player_playback':'NOT_RUN'}
reports=[]
for mode in ('transformation','turntable'):
    folder=out/(mode+'_frames'); folder.mkdir(parents=True,exist_ok=True); paths=[]
    indices=list(range(1,194,2)) if mode=='transformation' else list(range(72))
    for i,fr in enumerate(indices):
        if mode=='transformation':
            s.frame_set(fr); cam.location=(5.5,-6.3,3.0); aim((0,0,.9))
        else:
            s.frame_set(1); angle=2*math.pi*i/len(indices)
            cam.location=(7*math.cos(angle),7*math.sin(angle),3.0); aim((0,0,.65))
        path=folder/('%04d.jpg'%(fr if mode=='transformation' else i))
        s.render.filepath=str(path); bpy.ops.render.render(write_still=True); paths.append(path)
    reports.append(avi(out/(mode+'.avi'),paths,12))
(root/'video_v9.json').write_text(json.dumps(reports,indent=2),encoding='utf-8')
print('V9_VIDEOS',reports)


