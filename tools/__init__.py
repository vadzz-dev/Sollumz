if "bpy" in locals():
    import importlib
    importlib.reload(cats)
    importlib.reload(formatting)
else:
    from . import cats
    from . import formatting
