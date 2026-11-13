import bpy,numpy as np
for name in ['SB_MainWingPaint_V16','SB_FrontWingPaint_V16']:
 im=bpy.data.images[name];pixels=np.array(im.pixels[:],dtype=np.float32).reshape((-1,4));mask=pixels[:,3]<.5;pixels[mask]=(.016,.043,.095,1.);im.pixels.foreach_set(pixels.ravel());im.save();im.pack()
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
print('PAINT_VISIBLE_IN_TEXTURE_VIEWPORT')
