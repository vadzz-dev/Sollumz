import os
import xml.etree.ElementTree as ET
import time
from xml.etree.ElementTree import Element
from mathutils import Vector, Quaternion, Matrix
from .drawable import Drawable
from ..ycdimport import xml_read_text, xml_read_value
from ..ybnimport import read_composite_info_children
from ..tools import xmlhelper

class Archetype:

    def __init__(self):

        self.name = ""
        self.bounds = []
    
    def read_xml(self, root):

        if root is None:
            return

        self.name = xml_read_text(root.find("Name"), "", str)
        self.bounds = read_composite_info_children(root.find('Bounds'))

class Group:

    # both group and child can be the children of a group, similar but somehow different to how bones are structured
    # Index - index of the first child of the group's children
    # ParentIndex - index of parent group
    # UnkByte4C - index of first group of the group's children
    # UnkByte4F - the number of children
    # UnkByte50 - the number of groups
    # the rest of unk stuffs are to be researched, usually identical in general cases

    def __init__(self):

        self.name = ""
        self.child_children_index = 0
        self.group_parent_index = 0
        self.group_children_index = 0
        self.child_children_num = 0
        self.group_children_num = 0
        self.mass = 0

    def read_xml(self, root):

        if root is None:
            return

        self.name = xml_read_text(root.find("Name"), "", str)
        self.child_children_index = xml_read_value(root.find("Index"), 0, int)
        self.group_parent_index = xml_read_value(root.find("ParentIndex"), 0, int)
        self.group_children_index = xml_read_value(root.find("UnkByte4C"), 0, int)
        self.child_children_num = xml_read_value(root.find("UnkByte4F"), 0, int)
        self.group_children_num = xml_read_value(root.find("UnkByte50"), 0, int)
        self.mass = xml_read_value(root.find("Mass"), 0, float)

class Child:

    # bounds can be linked to a child, as we got the same number of children and bounds in one fragment 

    def __init__(self):

        self.group_index = 0
        self.tag = 0
        self.drawable = None
        self.bounds = []

    def read_xml(self, root):

        if root is None:
            return

        self.group_index = xml_read_value(root.find("GroupIndex"), 0, int)
        self.tag = xml_read_value(root.find("BoneTag"), 0, int)
        self.drawable = Drawable.from_xml(root.find('Drawable'))

class Fragment:

    def __init__(self):

        self.name = "Fragment"
        self.drawable = None
        self.archetype = None
        self.groups = []
        self.children = []
        
    def read_xml(self, root):

        if root is None:
            return

        drawable_node = root.find('Drawable')
        physics_node = root.find('Physics')

        self.name = xml_read_text(root.find("Name"), "Fragment", str)
        self.drawable = Drawable.from_xml(drawable_node)

        if physics_node is not None:
            lod1_node = physics_node.find('LOD1')
            self.archetype = Archetype()
            self.archetype.read_xml(lod1_node.find('Archetype'))

            for group_node in lod1_node.find("Groups"):
                group = Group()
                group.read_xml(group_node)
                self.groups.append(group)

            for children_node in lod1_node.find("Children"):
                child = Child()
                child.read_xml(children_node)
                self.children.append(child)