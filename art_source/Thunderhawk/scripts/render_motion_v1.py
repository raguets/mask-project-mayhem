import bpy,os
s=bpy.context.scene; root=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
s.render.engine='BLENDER_WORKBENCH'; s.display.shading.light='STUDIO'; s.display.shading.color_type='MATERIAL'; s.display.shading.show_shadows=True
s.render.resolution_x=720; s.render.resolution_y=504; s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG'; s.render.filepath=os.path.join(root,'renders','v1','sequence','frame_'); s.frame_start=1; s.frame_end=193; s.frame_step=2
bpy.ops.render.render(animation=True)
