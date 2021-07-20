if "bpy" in locals():
    import importlib
    importlib.reload(drawable)
    importlib.reload(shader)
else:
    from . import drawable
    from . import shader
    
import bpy 