import bpy
import os
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element
from mathutils import Vector, Quaternion, Matrix
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator
import time
import random 
from .ybnimport import read_composite_info_children 
from .ycdimport import xml_read_value, xml_read_text
from .formats.ydr.drawable import Drawable, DrawableDictionary
from .formats.ydr.utils import read_ydr_shaders

def read_ydr_xml(self, context, filepath, root):

    fname = os.path.basename(filepath)
    name = fname[:-8] #removes file extension

    model_name = root.find("Name").text

    if model_name == None:
        model_name = name

    shaders = read_ydr_shaders(self, context, filepath, root)
    drawable = Drawable(root, filepath, shaders)

    return drawable

def read_ydd_xml(self, context, filepath, root):

    drawable_dict = DrawableDictionary(root, filepath)

    return drawable_dict

class ImportYDR(Operator, ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "importxml.ydr"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Import Ydr"

    # ImportHelper mixin class uses this
    filename_ext = ".ydr.xml"

    filter_glob: StringProperty(
        default="*.ydr.xml",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        start = time.time()
        
        tree = ET.parse(self.filepath)
        root = tree.getroot()

        drawable = read_ydr_xml(self, context, self.filepath, root)
        vmodel_obj = drawable.apply()

        finished = time.time()
        
        difference = finished - start
        
        print("start time: " + str(start))
        print("end time: " + str(finished))
        print("difference in seconds: " + str(difference))
        print("difference in milliseconds: " + str(difference * 1000))
                
        return {'FINISHED'}

class ImportYDD(Operator, ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "importxml.ydd"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Import Ydd"

    # ImportHelper mixin class uses this
    filename_ext = ".ydd.xml"

    filter_glob: StringProperty(
        default="*.ydd.xml",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        start = time.time()

        tree = ET.parse(self.filepath)
        root = tree.getroot()

        name = os.path.basename(self.filepath)[:-8]
        drawable_dict = read_ydd_xml(self, context, self.filepath, root)
        drawable_dict.apply(self.filepath)

        finished = time.time()
        
        difference = finished - start
        
        print("start time: " + str(start))
        print("end time: " + str(finished))
        print("difference in seconds: " + str(difference))
        print("difference in milliseconds: " + str(difference * 1000))

        return {'FINISHED'}


# Only needed if you want to add into a dynamic menu
def menu_func_import_ydr(self, context):
    self.layout.operator(ImportYDR.bl_idname, text="Ydr (.ydr.xml)")
# Only needed if you want to add into a dynamic menu
def menu_func_import_ydd(self, context):
    self.layout.operator(ImportYDD.bl_idname, text="Ydd (.ydd.xml)")

def register():
    bpy.utils.register_class(ImportYDR)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import_ydr)
    bpy.utils.register_class(ImportYDD)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import_ydd)

def unregister():
    bpy.utils.unregister_class(ImportYDR)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import_ydr)
    bpy.utils.unregister_class(ImportYDD)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import_ydd)
