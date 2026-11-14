import bpy
import blender_mcp
def start():
    if not hasattr(bpy.types, 'blender_mcp_server'):
        bpy.types.blender_mcp_server = blender_mcp.BlenderMCPServer(port=9876)
    bpy.types.blender_mcp_server.start()
    return None
bpy.app.timers.register(start, first_interval=2)
