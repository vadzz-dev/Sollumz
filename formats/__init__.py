if "bpy" in locals():
    import importlib
    importlib.reload(ydr)
else:
    from . import ydr

import bpy 