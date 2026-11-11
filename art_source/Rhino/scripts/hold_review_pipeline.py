"""Pause this project's queued controller, allowing an active image batch to finish."""
import bpy,gc,types
stopped=[]
for fn in gc.get_objects():
 if isinstance(fn,types.FunctionType) and fn.__name__=='advance':
  namespace=fn.__globals__;steps=namespace.get('steps')
  if steps and steps[0][0].startswith('audit') and bpy.app.timers.is_registered(fn):
   bpy.app.timers.unregister(fn);stopped.append(str(namespace.get('A')))
print('RHINO_QUEUED_CONTROLLER_HELD_ACTIVE_RENDER_CONTINUES',stopped)
