if "bpy" in locals():
    import importlib
    importlib.reload(xml)
    importlib.reload(cats)
    importlib.reload(meshgen)
    importlib.reload(jenkhash)
    importlib.reload(xmlhelper)
    importlib.reload(utils)
else:
    from . import xml
    from . import cats
    from . import meshgen
    from . import jenkhash
    from . import xmlhelper
    from . import utils

import bpy
