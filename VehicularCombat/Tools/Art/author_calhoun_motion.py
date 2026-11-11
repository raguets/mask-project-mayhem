"""Live MCP: apply the tested on-foot gait workflow to Calhoun's own exported rig."""
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');T=P/'VehicularCombat/Tools/Art'
code=(T/'author_onfoot_motion.py').read_text(encoding='utf-8-sig')
a=code.index('CONTRACT=json.loads');b=code.index('\nSTATE=',a)
code=code[:a]+"CONTRACT=[{'name':'Calhoun','file':'Raven_GameReady.blend','rig':'Calhoun_GameRig','meshes':['CalhounBody','CalhounHair','CalhounMask']}]"+code[b:]
code=code.replace("ROOT/'SourceArt/MASK/Editable'/data['file']", "ROOT.parent/'art_source/GameReady/Raven'/data['file']")
code=code.replace("bpy.ops.wm.open_mainfile(filepath=str(OUT/'Matt/Matt_Locomotion.blend'));return None", "bpy.ops.wm.open_mainfile(filepath=str(ROOT.parent/'art_source/Raven/Raven_V16_Assembly.blend'));bpy.app.driver_namespace.pop('_mask_asset_review_active',None);return None")
code=code.replace("def init_actor(index):", "def init_actor(index):")
exec(compile(code,'<calhoun-locomotion>','exec'))
