if "bpy" in locals():
    import importlib
    importlib.reload(cats)
    importlib.reload(meshgen)
    importlib.reload(jenkhash)
    importlib.reload(xmlhelper)
else:
    from . import cats
    from . import meshgen
    from . import jenkhash
    from . import xmlhelper
