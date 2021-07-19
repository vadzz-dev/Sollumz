if "bpy" in locals():
    import importlib
    importlib.reload(drawable)
    importlib.reload(shader)
    importlib.reload(utils)
else:
    from . import drawable
    from . import shader
    from . import utils
    
import bpy 