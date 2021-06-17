if "bpy" in locals():
    import importlib
    importlib.reload(drawable)
    importlib.reload(utils)
else:
    from . import drawable
    from . import utils
    
import bpy 