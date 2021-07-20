import bpy
import os
import xml.etree.ElementTree as ET
import time
from xml.etree.ElementTree import Element
from mathutils import Vector, Quaternion, Matrix
from ..ycdimport import xml_read_value, xml_read_text
from ..ybnimport import read_composite_info_children
from ..tools import xmlhelper
from .shader import ShaderGroup

class Bone:

    def __init__(self):
        self.name = ""
        self.tag = 0
        self.index = 0
        self.parent_index = 0
        self.sibling_index =0 
        self.flags = []
        self.translation = []
        self.rotation = []
        self.scale = []
        self.transform_unk = []

    def read_xml(self, root):

        if root is None:
            return

        flags_item = root.find("Flags")
        translation_item = root.find("Translation")
        rotation_item = root.find("Rotation")
        scale_item = root.find("Scale")

        self.name = root.find("Name").text
        self.tag = xmlhelper.ReadInt(root.find("Tag"))
        self.index = xmlhelper.ReadInt(root.find("Index"))
        self.parent_index = xmlhelper.ReadInt(root.find("ParentIndex"))
        self.sibling_index = xmlhelper.ReadInt(root.find("SiblingIndex"))
        if (flags_item.text != None):
            self.flags = flags_item.text.strip().split(", ")

        self.transform_unk = xmlhelper.ReadQuaternion(root.find("TransformUnk"))

        self.translation = Vector()
        self.translation.x = float(translation_item.attrib["x"])
        self.translation.y = float(translation_item.attrib["y"])
        self.translation.z = float(translation_item.attrib["z"])

        self.rotation = Quaternion()
        self.rotation.w = float(rotation_item.attrib["w"])
        self.rotation.x = float(rotation_item.attrib["x"])
        self.rotation.y = float(rotation_item.attrib["y"])
        self.rotation.z = float(rotation_item.attrib["z"])

        self.scale = Vector()
        self.scale.x = float(scale_item.attrib["x"])
        self.scale.y = float(scale_item.attrib["y"])
        self.scale.z = float(scale_item.attrib["z"])

    @staticmethod
    def from_xml(root):
        bone = Bone()
        bone.read_xml(root)
        return bone

    def create(self, armature):

        if armature is None:
            return None

        # bpy.context.view_layer.objects.active = armature
        edit_bone = armature.data.edit_bones.new(self.name)
        if self.parent_index != -1:
            edit_bone.parent = armature.data.edit_bones[self.parent_index]

        # https://github.com/LendoK/Blender_GTA_V_model_importer/blob/master/importer.py
        mat_rot = self.rotation.to_matrix().to_4x4()
        mat_loc = Matrix.Translation(self.translation)
        mat_sca = Matrix.Scale(1, 4, self.scale)

        edit_bone.head = (0,0,0)
        edit_bone.tail = (0,0.05,0)
        edit_bone.matrix = mat_loc @ mat_rot @ mat_sca
        if edit_bone.parent != None:
            edit_bone.matrix = edit_bone.parent.matrix @ edit_bone.matrix

        return self.name

    def set_properties(self, armature):

        bone = armature.pose.bones[self.name].bone
        bone.bone_properties.tag = self.tag
        # LimitRotation and Unk0 have their special meanings, can be deduced if needed when exporting
        flags_restricted = set(["LimitRotation", "Unk0"])
        for _flag in self.flags:
            if (_flag in flags_restricted):
                continue

            flag = bone.bone_properties.flags.add()
            flag.name = _flag

class Skeleton:

    def __init__(self):
        self.unknown_1c = 0
        self.unknown_50 = 0
        self.unknown_54 = 0
        self.unknown_58 = 0
        self.bones = []

    def read_xml(self, root):
        self.unknown_1c = xmlhelper.ReadInt(root.find("Unknown1C"))
        self.unknown_50 = xmlhelper.ReadInt(root.find("Unknown50"))
        self.unknown_54 = xmlhelper.ReadInt(root.find("Unknown54"))
        self.unknown_58 = xmlhelper.ReadInt(root.find("Unknown58"))

        for node in root.find("Bones"):
            b = Bone().from_xml(node)
            self.bones.append(b)

    @staticmethod
    def from_xml(root):
        skel = Skeleton()
        skel.read_xml(root)
        return skel

class Joint:
    type = None
    tag = None
    min = None
    max = None

    def __init__(self, xml, type):

        self.type = type
        self.tag = xml_read_value(xml.find("BoneId"), 0, int)

        min_item = xml.find("Min")
        self.min = Vector()
        self.min.x = float(min_item.attrib["x"])
        self.min.y = float(min_item.attrib["y"])
        self.min.z = float(min_item.attrib["z"])

        max_item = xml.find("Max")
        self.max = Vector()
        self.max.x = float(max_item.attrib["x"])
        self.max.y = float(max_item.attrib["y"])
        self.max.z = float(max_item.attrib["z"])

    def apply(self, bone):

        if bone is None:
            return None

        constraint = bone.constraints.new('LIMIT_ROTATION')
        constraint.owner_space = 'LOCAL'
        constraint.use_limit_x = True
        constraint.use_limit_y = True
        constraint.use_limit_z = True
        constraint.max_x = float(self.max.x)
        constraint.max_y = float(self.max.y)
        constraint.max_z = float(self.max.z)
        constraint.min_x = float(self.min.x)
        constraint.min_y = float(self.min.y)
        constraint.min_z = float(self.min.z)

        return bone.name

    def write(self, bone):
        if bone is None:
            return None
        
        nodes = []
        for con in bone.constraints:
            if con.type == 'LIMIT_ROTATION':
                self.type = "RotationLimits"
                self.tag = bone.bone.bone_properties.tag
                self.min = Vector(con.min_x, con.min_y, con.min_z)
                self.max = Vector(con.max_x, con.max_y, con.max_z)
                con_node = Element(self.type)

                tag_node = Element("BoneId")
                tag_node.set("value", str(self.tag))

                unka_node = Element("UnknownA")
                unka_node.set("value", "0")

                min_node = Element("Min")
                min_node.set("x", con.min_x)
                min_node.set("y", con.min_y)
                min_node.set("z", con.min_z)

                max_node = Element("Max")
                max_node.set("x", con.max_x)
                max_node.set("y", con.max_y)
                max_node.set("z", con.max_z)

                con_node.append(tag_node)
                con_node.append(unka_node)
                con_node.append(min_node)
                con_node.append(max_node)
                nodes.append(con_node)

        return nodes

class Vertex:

    def __init__(self):
        self.position = None
        self.blendweights = None
        self.blendindices = None
        self.colors0 = None
        self.colors1 = None
        self.texcoord0 = None
        self.texcoord1 = None
        self.texcoord2 = None
        self.texcoord3 = None
        self.texcoord4 = None
        self.texcoord5 = None
        self.texcoord6 = None
        self.texcoord7 = None
        self.tangent = None
        self.normal = None

    @staticmethod    
    def from_xml(layout, data):
        
        result = Vertex()

        for i in range(len(layout)):
            current_data = data[i].split()
            current_layout_key = layout[i]
            if(current_layout_key == "Position"):
                result.position = xmlhelper.StringListToFloatList(current_data)
            elif(current_layout_key == "BlendWeights"):
                result.blendweights = xmlhelper.StringListToIntList(current_data)
            elif(current_layout_key == "BlendIndices"):
                result.blendindices = xmlhelper.StringListToIntList(current_data)
            elif(current_layout_key == "Colour0"):
                result.colors0 = xmlhelper.StringListToFloatList(current_data)
            elif(current_layout_key == "Colour1"):
                result.colors1 = xmlhelper.StringListToFloatList(current_data)
            elif(current_layout_key == "TexCoord0"):
                result.texcoord0 = xmlhelper.StringListToFloatList(current_data)
            elif(current_layout_key == "TexCoord1"):
                result.texcoord1 = xmlhelper.StringListToFloatList(current_data)
            elif(current_layout_key == "TexCoord2"):
                result.texcoord2 = xmlhelper.StringListToFloatList(current_data)
            elif(current_layout_key == "TexCoord3"):
                result.texcoord3 = xmlhelper.StringListToFloatList(current_data)
            elif(current_layout_key == "TexCoord4"):
                result.texcoord4 = xmlhelper.StringListToFloatList(current_data)
            elif(current_layout_key == "TexCoord5"):
                result.texcoord5 = xmlhelper.StringListToFloatList(current_data)
            elif(current_layout_key == "TexCoord6"):
                result.texcoord6 = xmlhelper.StringListToFloatList(current_data)
            elif(current_layout_key == "TexCoord7"):
                result.texcoord7 = xmlhelper.StringListToFloatList(current_data)
            elif(current_layout_key == "Tangent"):
                result.tangent = xmlhelper.StringListToFloatList(current_data)
            elif(current_layout_key == "Normal"):
                result.normal = xmlhelper.StringListToFloatList(current_data)

        return result

class VertexBuffer:

    def __init__(self):
        self.flags = 0
        self.layout = []
        self.data = ""
        self.vertices = []

    def read_xml(self, root):
        self.flags = xmlhelper.ReadInt(root.find("Flags"))

        layout = root.find("Layout")
        for node in layout:
            self.layout.append(node.tag)

        data_node = root[2]
        if data_node is None:
            return
            
        self.data = data_node.text.strip()

        lines = self.data.split("\n")
        for line in lines:
            v = Vertex.from_xml(self.layout, line.strip().split(" " * 3))
            self.vertices.append(v)

class Geometry:

    def __init__(self):
        self.shader_index = 0
        self.bounding_box_min = []
        self.bounding_box_max = []
        self.vertex_buffer = "" 
        self.index_buffer = []

    def read_xml(self, root):
        self.shader_index = xmlhelper.ReadInt(root.find("ShaderIndex"))
        self.bounding_box_min = xmlhelper.ReadVector(root.find("BoundingBoxMin"))
        self.bounding_box_max = xmlhelper.ReadVector(root.find("BoundingBoxMax"))

        vb = VertexBuffer()
        vb.read_xml(root.find("VertexBuffer"))
        self.vertex_buffer = vb
        if not len(self.vertex_buffer.vertices) > 0:
            return

        index_buffer = root.find("IndexBuffer")[0].text.strip().replace("\n", "").split()
        
        i_buf = []
        for num in index_buffer:
            i_buf.append(int(num))

        self.index_buffer = [i_buf[i * 3:(i + 1) * 3] for i in range((len(i_buf) + 3 - 1) // 3 )] #split index buffer into 3s for each triangle

    @staticmethod
    def from_xml(root):
        geo = Geometry()
        geo.read_xml(root)
        return geo

    @staticmethod
    def set_parent(obj, armature):
        obj.parent = armature
        mod = obj.modifiers.new("Armature", 'ARMATURE')
        mod.object = armature

class DrawableModel:

    def __init__(self):
        self.render_mask = 0
        self.flags = 0
        self.has_skin = False
        self.bone_index = 0
        self.unknown_1 = 0
        self.geometries = []

    def read_xml(self, root):
        if root is None:
            return

        self.render_mask = int(root.find("RenderMask").attrib["value"])

        for model in root.find('Geometries'):
            d_obj = Geometry.from_xml(model)
            self.geometries.append(d_obj)

    @staticmethod
    def from_xml(root):
        model = DrawableModel()
        model.read_xml(root)
        return model

    @staticmethod
    def set_parent(objs, armature):
        if objs is not None:
            for obj in objs:
                Geometry.set_parent(obj, armature)

class Drawable:

    def __init__(self):

        self.name = "Drawable"
        self.bounding_sphere_center = [0, 0, 0]
        self.bounding_sphere_radius = 0
        self.bounding_box_min = [0, 0, 0]
        self.bounding_box_max = [0, 0, 0]
        self.lod_dist_high = 0 #9998?
        self.lod_dist_med= 0 #9998?
        self.lod_dist_low = 0 #9998?
        self.lod_dist_vlow = 0 #9998?
        self.flags_high = 0 
        self.flags_med = 0 
        self.flags_low = 0  
        self.flags_vlow = 0
        self.unknown_9A = 0

        self.shader_group = None
        self.skeleton = None
        self.bounds = []
        self.joints = []
        self.drawable_models_high = []
        self.drawable_models_med = []
        self.drawable_models_low = []
        self.drawable_models_vlow = []

    def read_xml(self, root, shaders=None):

        if root is None:
            return

        self.name = xml_read_text(root.find("Name"), "Drawable", str)

        if (root.find("DrawableModelsHigh") == None and root.find("DrawableModelsMedium") == None and root.find("DrawableModelsLow") == None):
            return

        self.lod_dist_high = float(root.find("LodDistHigh").attrib["value"])
        self.lod_dist_med = float(root.find("LodDistMed").attrib["value"])
        self.lod_dist_low = float(root.find("LodDistLow").attrib["value"])
        self.lod_dist_vlow = float(root.find("LodDistVlow").attrib["value"])

        sg = root.find("ShaderGroup")
        if(sg != None):
            shader_group = ShaderGroup()
            shader_group.read_xml(root.find("ShaderGroup"))
            self.shader_group = shader_group

        skeleton_node = root.find("Skeleton")
        if skeleton_node is not None:
            self.skeleton = Skeleton.from_xml(skeleton_node)

        joints_node = root.find("Joints")
        if joints_node is not None:
            self.joints = []
            if joints_node.find("RotationLimits") is not None:
                for item in joints_node.find("RotationLimits"):
                    joint = Joint(item, "RotationLimits")
                    self.joints.append(joint)

        dmh = root.find("DrawableModelsHigh")
        if(dmh != None):
            for node in dmh:
                dm = DrawableModel()
                dm.read_xml(node)
                self.drawable_models_high.append(dm)

        dmm = root.find("DrawableModelsMed")
        if(dmm != None):
            for node in dmm:
                dm = DrawableModel()
                dm.read_xml(node)
                self.drawable_models_med.append(dm)

        dml = root.find("DrawableModelsLow")
        if(dml != None):
            for node in dml:
                dm = DrawableModel()
                dm.read_xml(node)
                self.drawable_models_low.append(dm)

        dmvl = root.find("DrawableModelsVlow")
        if(dmvl != None):
            for node in dmvl:
                dm = DrawableModel()
                dm.read_xml(node)
                self.drawable_models_vlow.append(dm)

        bounds_node = root.find("Bounds")
        if bounds_node is not None:
            self.bounds = read_composite_info_children(bounds_node)

    @staticmethod
    def from_xml(root, shaders=None):
        drawable = Drawable()
        drawable.read_xml(root, shaders)
        return drawable

    def get_bones(self):
        if self.skeleton is None:
            return None

        return self.skeleton.bones

    def is_empty(self):
        if len(self.drawable_models_high) > 0:
            return False

        if len(self.drawable_models_med) > 0:
            return False

        if len(self.drawable_models_low) > 0:
            return False

        if len(self.drawable_models_vlow) > 0:
            return False

        return True

class DrawableDictionary:

    def __init__(self):

        self.drawables = []

    def read_xml(self, root):

        if root is None:
            return

        for item in root:
            if item is None:
                continue

            drawable = Drawable.from_xml(item)
            self.drawables.append(drawable)

    @staticmethod
    def from_xml(root):
        drawable_dict = DrawableDictionary()
        drawable_dict.read_xml(root)
        return drawable_dict