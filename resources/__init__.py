if "bpy" in locals():
    import importlib
    importlib.reload(drawable)
    importlib.reload(fragment)
    importlib.reload(shader)
else:
    from . import drawable
    from . import fragment
    from . import shader
    
import bpy 