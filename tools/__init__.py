if "bpy" in locals():
    import importlib
    importlib.reload(cats)
    importlib.reload(meshgen)
    importlib.reload(jenkhash)
    importlib.reload(xmlhelper)
    importlib.reload(utils)
else:
    from . import cats
    from . import meshgen
    from . import jenkhash
    from . import xmlhelper
    from . import utils
