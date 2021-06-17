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
from .resources.utils import build_bones_dict
from .ybnimport import read_composite_info_children
from .ycdimport import xml_read_value, xml_read_text
from .ydrimport import create_drawable 

class Archetype:
    name = None
    bounds = None

    def __init__(self, xml):
        if xml is None:
            return

        self.name = xml_read_text(xml.find("Name"), "", str)
        self.bounds = read_composite_info_children(xml.find('Bounds'))
    
    def adjust(self, bound_obj, parent):
        bound_obj.location -= parent.location
        bound_obj.rotation_euler.x -= parent.rotation_euler.x
        bound_obj.rotation_euler.y -= parent.rotation_euler.y
        bound_obj.rotation_euler.z -= parent.rotation_euler.z
        bound_obj.scale.x /= parent.scale.x
        bound_obj.scale.y /= parent.scale.y
        bound_obj.scale.z /= parent.scale.z

    def apply(self, cobj=None):

        if cobj is None:
            cobj = bpy.data.objects.new(self.name + "_col", None)

        for bound in self.bounds:
            bpy.context.scene.collection.objects.link(bound)
            bound.parent = cobj

        cobj.sollumtype = "Bound Composite"

        return cobj

    def apply_clean(self):

        for bound in self.bounds:
            bpy.context.scene.collection.objects.link(bound)

        return self.bounds

class Group:
    name = None
    children_part_index = None
    parent_index = None
    children_child_index = None
    children_num = None
    children_groups_num = None
    mass = None

    def __init__(self, xml):

        if xml is None:
            return

        self.name = xml_read_text(xml.find("Name"), "", str)
        self.children_part_index = xml_read_value(xml.find("Index"), 0, int)
        self.parent_index = xml_read_value(xml.find("ParentIndex"), 0, int)
        self.children_child_index = xml_read_value(xml.find("UnkByte4C"), 0, int)
        self.children_num = xml_read_value(xml.find("UnkByte4F"), 0, int)
        self.children_groups_num = xml_read_value(xml.find("UnkByte50"), 0, int)
        self.mass = xml_read_value(xml.find("Mass"), 0, float)

    def set_properties(self, bone=None, child=None):

        if bone is None:
            return

        bone.bone_properties.group.active = True
        bone.bone_properties.group.mass = self.mass
        bone.bone_properties.group.child = child

class Child:
    group_index = None
    tag = None
    drawable = None
    bounds = None

    def __init__(self, xml, filepath, shaders):

        if xml is None:
            return

        self.group_index = xml_read_value(xml.find("GroupIndex"), 0, int)
        self.tag = xml_read_value(xml.find("BoneTag"), 0, int)
        self.drawable = Drawable.from_xml(xml.find('Drawable'), filepath, shaders)

    def apply(self, child=None):

        if child is None:
            child = bpy.data.objects.new("child", None)
            child.sollumtype = "Children"
            bpy.context.scene.collection.objects.link(child)

        if self.drawable is not None:
            drawable = create_drawable(self.drawable)
            drawable.parent = child

        return child

class Fragment:
    name = None
    drawable = None
    archetype = None
    groups = None
    children = None

    def __init__(self, xml, filepath):

        if xml is None:
            return

        self.name = xml_read_text(xml.find("Name"), "Fragment", str)
        drawable_node = xml.find('Drawable')
        physics_node = xml.find('Physics')

        self.drawable = Drawable.from_xml(drawable_node, filepath)
        self.archetype = None
        self.groups = None
        self.children = None

        if physics_node is not None:
            lod1_node = physics_node.find('LOD1')
            self.archetype = Archetype(lod1_node.find('Archetype'))

            self.groups = []
            for group_node in lod1_node.find("Groups"):
                group = Group(group_node)
                self.groups.append(group)

            self.children = []
            shaders = self.drawable.shaders
            for children_node in lod1_node.find("Children"):
                child = Child(children_node, filepath, shaders)
                self.children.append(child)

    def apply(self):

        fragment_node = bpy.data.objects.new(self.name, None)
        fragment_node.sollumtype = "Fragment"
        bpy.context.scene.collection.objects.link(fragment_node)

        drawable_node = create_drawable(self.drawable)
        drawable_node.parent = fragment_node

        bones_dict = build_bones_dict(drawable_node)

        if self.archetype is not None:
            bounds = self.archetype.apply_clean()

        if self.children is not None:
            children_node = bpy.data.objects.new(self.name + "_children", None)
            children_node.parent = fragment_node
            bpy.context.scene.collection.objects.link(children_node)
            children_table = [None] * len(self.groups)

            for i, group in enumerate(self.groups):
                child = bpy.data.objects.new(group.name, None)
                child.sollumtype = "Child"
                bpy.context.scene.collection.objects.link(child)
                children_table[i] = child
                group.set_properties(drawable_node.data.bones[group.name], child)

            for i, child in enumerate(self.children):
                child_node = child.apply(children_table[child.group_index])
                child_node.parent = children_node
                bounds[i].parent = child_node

                children_table[child.group_index].matrix_local = drawable_node.data.bones[bones_dict[child.tag]].matrix_local
                self.archetype.adjust(bounds[i], child_node)

        return fragment_node

def read_yft_xml(self, root):

    # fragment_name = root.find("Name").text
    fragment = Fragment(root, self.filepath)

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

        fragment = read_yft_xml(self, root)
        fragment.apply()

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
