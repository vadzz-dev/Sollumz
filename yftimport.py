import bpy
import os
import xml.etree.ElementTree as ET
from mathutils import Vector, Quaternion
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator
import time
import random 
from .tools import cats as Cats
from .resources.drawable import Drawable
from .resources.fragment import Fragment
from .tools.utils import build_bones_dict
from .ydrimport import create_drawable 

def adjust_archetype(bound_obj, parent):
    bound_obj.location -= parent.location
    bound_obj.rotation_euler.x -= parent.rotation_euler.x
    bound_obj.rotation_euler.y -= parent.rotation_euler.y
    bound_obj.rotation_euler.z -= parent.rotation_euler.z
    bound_obj.scale.x /= parent.scale.x
    bound_obj.scale.y /= parent.scale.y
    bound_obj.scale.z /= parent.scale.z

def create_archetype(archetype, cobj=None):

    if cobj is None:
        cobj = bpy.data.objects.new(archetype.name + "_col", None)

    for bound in archetype.bounds:
        bpy.context.scene.collection.objects.link(bound)
        bound.parent = cobj

    cobj.sollumtype = "Bound Composite"

    return cobj

def create_archetype_clean(archetype):

    for bound in archetype.bounds:
        bpy.context.scene.collection.objects.link(bound)

    return archetype.bounds

def create_group(group, bone=None, child=None):

    if bone is None:
        return

    bone.bone_properties.group.active = True
    bone.bone_properties.group.mass = group.mass
    bone.bone_properties.group.child = child

def create_child(child, filepath, child_obj=None):

    if child_obj is None:
        child_obj = bpy.data.objects.new("Child", None)
        child_obj.sollumtype = "Child"
        bpy.context.scene.collection.objects.link(child_obj)

    if child.drawable is not None:
        drawable = create_drawable(child.drawable, filepath, clean=True)
        if drawable is not None:
            drawable.parent = child_obj

    return child_obj

def create_fragment(fragment, filepath):

    fragment_node = bpy.data.objects.new(fragment.name, None)
    fragment_node.sollumtype = "Fragment"
    bpy.context.scene.collection.objects.link(fragment_node)

    drawable_node = create_drawable(fragment.drawable, filepath)
    drawable_node.parent = fragment_node

    bones_dict = build_bones_dict(drawable_node)

    if fragment.archetype is not None:
        bounds = create_archetype_clean(fragment.archetype)

    if len(fragment.children):
        children_node = bpy.data.objects.new(fragment.name + "_children", None)
        children_node.parent = fragment_node
        bpy.context.scene.collection.objects.link(children_node)
        children_table = [None] * len(fragment.groups)

        for i, group in enumerate(fragment.groups):
            child = bpy.data.objects.new(group.name, None)
            child.sollumtype = "Child"
            bpy.context.scene.collection.objects.link(child)
            children_table[i] = child
            create_group(group, drawable_node.data.bones[group.name], child)

        for i, child in enumerate(fragment.children):
            child_node = create_child(child, filepath, children_table[child.group_index])
            child_node.parent = children_node
            bounds[i].parent = child_node

            children_table[child.group_index].matrix_local = drawable_node.data.bones[bones_dict[child.tag]].matrix_local
            adjust_archetype(bounds[i], child_node)

    return fragment_node

def read_yft_xml(root):

    # fragment_name = root.find("Name").text
    fragment = Fragment()
    fragment.read_xml(root)

    return fragment

class ImportYFT(Operator, ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "importxml.yft"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Import Yft"

    # ImportHelper mixin class uses this
    filename_ext = ".yft.xml"

    filter_glob: StringProperty(
        default="*.yft.xml",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        start = time.time()

        tree = ET.parse(self.filepath)
        root = tree.getroot()

        fragment = read_yft_xml(root)
        create_fragment(fragment, self.filepath)

        finished = time.time()
        
        difference = finished - start
        
        print("start time: " + str(start))
        print("end time: " + str(finished))
        print("difference in seconds: " + str(difference))
        print("difference in milliseconds: " + str(difference * 1000))
                
        return {'FINISHED'}

# Only needed if you want to add into a dynamic menu
def menu_func_import_yft(self, context):
    self.layout.operator(ImportYFT.bl_idname, text="Yft (.yft.xml)")

def register():
    bpy.utils.register_class(ImportYFT)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import_yft)

def unregister():
    bpy.utils.unregister_class(ImportYFT)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import_yft)
