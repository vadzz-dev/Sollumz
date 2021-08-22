import bpy
import os
import xml.etree.ElementTree as ET
import time
from xml.etree.ElementTree import Element
from mathutils import Vector, Quaternion, Matrix

def build_bones_dict(obj):
    if (obj == None):
        return None

    if (obj.pose == None):
        return None

    bones_dict = {}
    for pose_bone in obj.pose.bones:
        bones_dict[pose_bone.bone.bone_properties.tag] = pose_bone.name

    return bones_dict
    
def format_float(num):
    return str(round(num, 7)).rstrip('.0')