"""Start the user's already-installed Blender MCP add-on. No modeling or installs."""
import bpy
import json
import traceback
from pathlib import Path

report = Path('G:/DEV/mask-project-mayhem/VehicularCombat/Saved/Art/blender-bootstrap.json')
report.parent.mkdir(parents=True, exist_ok=True)
try:
    if 'blender_mcp' not in bpy.context.preferences.addons:
        bpy.ops.preferences.addon_enable(module='blender_mcp')
    bpy.context.scene.blendermcp_port = 9876
    server = getattr(bpy.types, 'blendermcp_server', None)
    if not server or not getattr(server, 'running', False):
        bpy.ops.blendermcp.start_server()
    report.write_text(json.dumps({'status':'started','file':bpy.data.filepath,'version':bpy.app.version_string,'port':9876},indent=2),encoding='utf-8')
except Exception:
    report.write_text(json.dumps({'status':'error','traceback':traceback.format_exc()},indent=2),encoding='utf-8')
    raise
