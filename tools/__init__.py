if "bpy" in locals():
    import importlib
    importlib.reload(cats)
    importlib.reload(meshgen)
    importlib.reload(jenkhash)
    importlib.reload(formatting)
else:
    from . import cats
    from . import meshgen
    from . import cats
    from . import jenkhash
    from . import formatting
