import bpy
import os
import xml.etree.ElementTree as ET
import time
from xml.etree.ElementTree import Element
from mathutils import Vector, Quaternion, Matrix
from ...ycdimport import xml_read_value, xml_read_text
from ...ybnimport import read_composite_info_children
from ...tools import cats as Cats
from .utils import build_bones_dict, get_related_texture, read_shader_info, read_ydr_shaders, create_material, process_uv

class v_vertex:

    def __init__(self, p, tc, tc1, tc2, tc3, tc4, tc5, c, c1, n, t, bw, bi):
        self.Position = p
        self.TexCoord = tc
        self.TexCoord1 = tc1
        self.TexCoord2 = tc2
        self.TexCoord3 = tc3
        self.TexCoord4 = tc4
        self.TexCoord5 = tc5
        self.Color = c
        self.Color1 = c1
        self.Normal = n
        self.Tangent = t
        self.BlendWeights = bw
        self.BlendIndices = bi

def create_model(self, bones, name):
    #create mesh
    mesh = bpy.data.meshes.new("Geometry")
    mesh.from_pydata(self.verts, [], self.index_buffer)
    verts_num = mesh.vertices
    mesh.create_normals_split()
    mesh.validate(clean_customdata=False)
    normals_fixed = []
    for l in mesh.loops:
        normals_fixed.append(self.normals[l.vertex_index])
    
    polygon_count = len(mesh.polygons)
    mesh.polygons.foreach_set("use_smooth", [True] * polygon_count)

    mesh.normals_split_custom_set(normals_fixed)
    mesh.use_auto_smooth = True

    # set uv 
    if(self.texcoords):
        uv0 = mesh.uv_layers.new()
        uv_layer0 = mesh.uv_layers[0]
        for i in range(len(uv_layer0.data)):
            uv = process_uv(self.texcoords[mesh.loops[i].vertex_index])
            uv_layer0.data[i].uv = uv 
    if(self.texcoords1):
        uv1 = mesh.uv_layers.new()
        uv_layer1 = mesh.uv_layers[1]
        for i in range(len(uv_layer1.data)):
            uv = process_uv(self.texcoords1[mesh.loops[i].vertex_index])
            uv_layer1.data[i].uv = uv 
    if(self.texcoords2):
        uv2 = mesh.uv_layers.new()
        uv_layer2 = mesh.uv_layers[2]
        for i in range(len(uv_layer2.data)):
            uv = process_uv(self.texcoords2[mesh.loops[i].vertex_index])
            uv_layer2.data[i].uv = uv 
    if(self.texcoords3):
        uv3 = mesh.uv_layers.new()
        uv_layer3 = mesh.uv_layers[3]
        for i in range(len(uv_layer3.data)):
            uv = process_uv(self.texcoords3[mesh.loops[i].vertex_index])
            uv_layer3.data[i].uv = uv 
    if(self.texcoords4):
        uv4 = mesh.uv_layers.new()
        uv_layer4 = mesh.uv_layers[4]
        for i in range(len(uv_layer4.data)):
            uv = process_uv(self.texcoords4[mesh.loops[i].vertex_index])
            uv_layer4.data[i].uv = uv 
    if(self.texcoords5):
        uv5 = mesh.uv_layers.new()
        uv_layer5 = mesh.uv_layers[5]
        for i in range(len(uv_layer5.data)):
            uv = process_uv(self.texcoords5[mesh.loops[i].vertex_index])
            uv_layer5.data[i].uv = uv 
    
    #set vertex colors 
    if(self.vcolors):
        clr0 = mesh.vertex_colors.new(name = "Vertex Colors") 
        color_layer = mesh.vertex_colors[0]
        for i in range(len(color_layer.data)):
            rgba = self.vcolors[mesh.loops[i].vertex_index]
            color_layer.data[i].color = rgba
    if(self.vcolors1):
        clr1 = mesh.vertex_colors.new(name = "Vertex illumiation") 
        color_layer1 = mesh.vertex_colors[1]
        for i in range(len(color_layer.data)):
            rgba = self.vcolors1[mesh.loops[i].vertex_index]
            color_layer1.data[i].color = rgba
    
    #set tangents - .tangent is read only so can't set them
    #for poly in mesh.polygons:
        #for idx in poly.loop_indicies:
            #mesh.loops[i].tangent = tangents[i]    

    obj = bpy.data.objects.new(name.replace(".#dr", "") + "_mesh", mesh)
    
    #load weights
    # 256 - possibly the maximum of bones?
    if (bones != None and len(bones) > 0 and len(self.blendweights) > 0 and len(verts_num) > 0):
        for i in range(256):
            if (i < len(bones)):
                obj.vertex_groups.new(name=bones[i].name)
            else:
                obj.vertex_groups.new(name="UNKNOWN_BONE." + str(i))

        for vertex_idx in range(len(verts_num)):
            for i in range(0, 4):
                if (self.blendweights[vertex_idx][i] > 0.0):
                    obj.vertex_groups[self.blendindices[vertex_idx][i]].add([vertex_idx], self.blendweights[vertex_idx][i], "ADD")

        Cats.remove_unused_vertex_groups_of_mesh(obj)

    return obj

def read_model(self, index_buffer, vertices):

    self.verts = []
    faces = index_buffer
    self.normals = []
    self.texcoords = []
    self.texcoords1 = []
    self.texcoords2 = []
    self.texcoords3 = []
    self.texcoords4 = []
    self.texcoords5 = []
    self.tangents = []
    self.vcolors = [] 
    self.vcolors1 = [] 
    self.blendweights = [] 
    self.blendindices = [] 

    for v in vertices:
        if(v.Position != None):
            self.verts.append(Vector((v.Position[0], v.Position[1], v.Position[2])))
        else:
            return None #SHOULD NEVER HAPPEN
        if(v.Normal != None):
            self.normals.append(v.Normal)
        if(v.TexCoord != None):
            self.texcoords.append(v.TexCoord)
        if(v.TexCoord1 != None):
            self.texcoords1.append(v.TexCoord1)
        if(v.TexCoord2 != None):
            self.texcoords2.append(v.TexCoord2)
        if(v.TexCoord3 != None):
            self.texcoords3.append(v.TexCoord3)
        if(v.TexCoord4 != None):
            self.texcoords4.append(v.TexCoord4)
        if(v.TexCoord5 != None):
            self.texcoords5.append(v.TexCoord5)
        if(v.Tangent != None):
            self.tangents.append(Vector((v.Tangent[0], v.Tangent[1], v.Tangent[2])))
        if(v.Color != None):
            self.vcolors.append(v.Color)
        if(v.Color1 != None):
            self.vcolors1.append(v.Color1)
        if(v.BlendWeights != None):
            self.blendweights.append(v.BlendWeights)
        if(v.BlendIndices != None):
            self.blendindices.append(v.BlendIndices)

def read_model_info(self, xml):
    self.vertex_buffer = []
    i_buffer = []

    self.shader_index = xml_read_value(xml.find("ShaderIndex"), 0, int)
    vb = xml.find("VertexBuffer")
    self.vertex_buffer = map(lambda line : line.strip(), vb[2].text.strip().split("\n"))

    ib = xml.find("IndexBuffer")
    i_buffer = ib[0].text.strip().replace("\n", "").split()
    self.vertices = self.get_vertices_from_data(vb.find("Layout"), self.vertex_buffer)

    i_buf = []
    for num in i_buffer:
        i_buf.append(int(num))

    self.index_buffer = [i_buf[i * 3:(i + 1) * 3] for i in range((len(i_buf) + 3 - 1) // 3 )] #split index buffer into 3s for each triangle

    # this is for the rare cases that model with no bone but have weights
    bone_ids = xml.find("BoneIDs")
    if (bone_ids is not None and bone_ids.text is not None):
        self.bone_ids = bone_ids.text.split(", ")
    
class Bone:
    name = None
    tag = None
    index = None
    parent_index = None
    sibling_index = None
    flags = None
    translation = None
    rotation = None
    scale = None

    def __init__(self, xml):

        if xml is None:
            return

        self.name = xml_read_text(xml.find("Name"), "Drawable", str)
        self.tag = xml_read_value(xml.find("Tag"), 0, int)
        self.index = xml_read_value(xml.find("Index"), 0, int)
        self.parent_index = xml_read_value(xml.find("ParentIndex"), 0, int)
        self.sibling_index = xml_read_value(xml.find("SiblingIndex"), 0, int)

        flags_item = xml.find("Flags")
        translation_item = xml.find("Translation")
        rotation_item = xml.find("Rotation")
        scale_item = xml.find("Scale")

        if (flags_item.text != None):
            self.flags = flags_item.text.strip().split(", ")

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

class Mesh:
    shader_index = None
    bone_ids = None

    verts = None
    normals = None
    texcoords = None
    texcoords1 = None
    texcoords2 = None
    texcoords3 = None
    texcoords4 = None
    texcoords5 = None
    tangents = None
    vcolors = None
    vcolors1 = None
    blendweights = None
    blendindices = None

    vertex_buffer = None
    index_buffer = None

    def __init__(self, xml):
        if xml is None:
            return

        read_model_info(self, xml)
        read_model(self, self.index_buffer, self.vertices) #supply shaderindex into texturepaths because the shaders are always in order

    def apply(self, shaders, bones, name):
        obj = create_model(self, bones, name)
        obj.data.materials.append(shaders[self.shader_index])

        return obj

    @staticmethod
    def get_vertices_from_data(layout, v_buffer):
        #find the position of the variable in the vertex layout
        layers = []
        for idx in range(len(layout)):
            layers.append(layout[idx].tag)
            
        # print(layers)
        vertices = []
        for v in v_buffer:
            position = None
            texcoords = None
            texcoords1 = None
            texcoords2 = None
            texcoords3 = None
            texcoords4 = None
            texcoords5 = None
            color = None
            color1 = None
            normal = None
            tangents = None
            blendw = None
            blendi = None

            tokens = v.split(" " * 3) #each vert value is split by 3 spaces

            if len(tokens) != len(layers):
                print("Incorrect layout data!")

            for i in range(len(tokens)):
                layer = layers[i]
                token = tokens[i]

                if layer == "Position":
                    position = list(map(lambda x: float(x), token.split()))
                elif layer == "Normal":
                    normal = list(map(lambda x: float(x), token.split()))
                elif layer == "Colour0":
                    color = list(map(lambda x: float(x) / 255, token.split()))
                elif layer == "Colour1":
                    color1 = list(map(lambda x: float(x) / 255, token.split()))
                elif layer == "TexCoord0":
                    texcoords = list(map(lambda x: float(x), token.split()))
                elif layer == "TexCoord1":
                    texcoords1 = list(map(lambda x: float(x), token.split()))
                elif layer == "TexCoord2":
                    texcoords2 = list(map(lambda x: float(x), token.split()))
                elif layer == "TexCoord3":
                    texcoords3 = list(map(lambda x: float(x), token.split()))
                elif layer == "TexCoord4":
                    texcoords4 = list(map(lambda x: float(x), token.split()))
                elif layer == "TexCoord5":
                    texcoords5 = list(map(lambda x: float(x), token.split()))
                elif layer == "Tangent":
                    tangents = list(map(lambda x: float(x), token.split()))
                elif layer == "BlendWeights":
                    blendw = list(map(lambda x: float(x) / 255, token.split()))
                elif layer == "BlendIndices":
                    blendi = list(map(lambda x: int(x), token.split()))

            vertices.append(v_vertex(position, texcoords, texcoords1, texcoords2, texcoords3, texcoords4, texcoords5, color, color1, normal, tangents, blendw, blendi))

        return vertices

    @staticmethod
    def set_parent(obj, armature):
        obj.parent = armature
        mod = obj.modifiers.new("Armature", 'ARMATURE')
        mod.object = armature

class DrawableModel:
    key = None
    render_mask = None
    meshes = None

    def __init__(self, xml, key):
        if xml is None:
            return

        self.render_mask = int(xml.find("RenderMask").attrib["value"])
        self.key = key

        self.meshes = []
        for model in xml.find('Geometries'):
            d_obj = Mesh(model)
            self.meshes.append(d_obj)

    def apply(self, shaders, bones, name):
        
        if self.meshes is not None:
            objs = []
            for mesh in self.meshes:
                obj = mesh.apply(shaders, bones, name)
                obj.sollumtype = "Geometry"
                obj.level_of_detail = self.key
                obj.mask = self.render_mask
                bpy.context.scene.collection.objects.link(obj)
                objs.append(obj)

        return objs

    @staticmethod
    def set_parent(objs, armature):
        if objs is not None:
            for obj in objs:
                Mesh.set_parent(obj, armature)

class Drawable:
    name = None
    lods = None
    shaders = None
    bones = None
    joints = None
    drawable_models = None
    bounds = None

    def __init__(self, xml, filepath, shaders=None):

        if xml is None:
            return

        self.name = xml_read_text(xml.find("Name"), "Drawable", str)

        if (xml.find("DrawableModelsHigh") == None and xml.find("DrawableModelsMedium") == None and xml.find("DrawableModelsLow") == None):
            return

        dd_high = float(xml.find("LodDistHigh").attrib["value"])
        dd_med = float(xml.find("LodDistMed").attrib["value"])
        dd_low = float(xml.find("LodDistLow").attrib["value"])
        dd_vlow = float(xml.find("LodDistVlow").attrib["value"])
        self.lods = [dd_high, dd_med, dd_low, dd_vlow]

        if shaders is None:
            self.shaders = read_ydr_shaders(self, bpy.context, filepath, xml)
        else:
            self.shaders = shaders

        skeleton_node = xml.find("Skeleton")
        if skeleton_node is not None:
            bones_node = skeleton_node.find("Bones")
            self.bones = []
            for item in bones_node:
                bone = Bone(item)
                self.bones.append(bone)

        joints_node = xml.find("Joints")
        if joints_node is not None:
            self.joints = []
            if joints_node.find("RotationLimits") is not None:
                for item in joints_node.find("RotationLimits"):
                    joint = Joint(item, "RotationLimits")
                    self.joints.append(joint)

        self.drawable_models = []
        keys = ["High", "Medium", "Low"]
        for key in keys:
            if(xml.find("DrawableModels" + key) != None):
                dm_node = xml.find("DrawableModels" + key)
                for dm in dm_node:
                    objects = DrawableModel(dm, key)

                self.drawable_models.append(objects)

        bound_node = xml.find("Bounds")
        if bound_node is not None:
            self.bounds = read_composite_info_children(bound_node)

    def apply(self, armature=None, bones_override=None):

        if armature is None:
            skel = bpy.data.armatures.new(self.name + ".skel")
            armature = bpy.data.objects.new(self.name, skel)
            armature.sollumtype = "Drawable"
            bpy.context.scene.collection.objects.link(armature)

            if self.lods is not None:
                armature.drawble_distance_high = self.lods[0]
                armature.drawble_distance_medium = self.lods[1]
                armature.drawble_distance_low = self.lods[2]
                armature.drawble_distance_vlow = self.lods[3]

        bpy.context.view_layer.objects.active = armature

        if self.bones is not None:
            bpy.ops.object.mode_set(mode='EDIT')

            for bone in self.bones:
                _bone = bone.create(armature)

            bpy.ops.object.mode_set(mode='OBJECT')

            for bone in self.bones:
                bone.set_properties(armature)

        if self.joints is not None:
            bones_dict = build_bones_dict(armature)
            if bones_dict is not None:
                for joint in self.joints:
                    bone = armature.pose.bones.get(bones_dict[joint.tag])
                    joint.apply(bone)

        bones = self.bones
        if bones_override is not None:
            bones = bones_override

        if self.drawable_models is not None:
            for model in self.drawable_models:
                drawable_model = model.apply(self.shaders, bones, self.name)
                DrawableModel.set_parent(drawable_model, armature)

        if self.bounds is not None:
            cobj = bpy.data.objects.new(self.name + "_col", None)
            
            if(cobj == None):
                return #log error 
            
            for child in self.bounds:
                bpy.context.scene.collection.objects.link(child)
                child.parent = cobj 
                
            cobj.sollumtype = "Bound Composite"
            cobj.parent = armature
            bpy.context.scene.collection.objects.link(cobj)

        return armature

class DrawableDictionary:
    bones_override = None
    drawables = None
    drawable_with_bones_name = None

    def __init__(self, xml, filepath):

        if xml is None:
            return

        self.drawables = []
        # we need to get the name of that particular drawable and its bones before loading other data
        for item in xml:
            if item.find("Skeleton") is not None:
                self.drawable_with_bones_name = item.find("Name").text
                bones_node = item.find("Skeleton").find("Bones")
                self.bones_override = []
                for i in bones_node:
                    bone = Bone(i)
                    self.bones_override.append(bone)

                break

        for item in xml:
            if item is None:
                continue

            drawable = Drawable(item, filepath, None)
            self.drawables.append(drawable)

    def apply(self, filepath):

        name = os.path.basename(filepath)[:-8]
        vmodels = []
        # bones are shared in single ydd however they still have to be placed under a paticular drawable
        # temp armature, to be merged
        armature_temp = bpy.data.armatures.new("ARMATURE_TEMP")
        armature_temp_obj = bpy.data.objects.new("ARMATURE_TEMP", armature_temp)
        bpy.context.scene.collection.objects.link(armature_temp_obj)
        bpy.context.view_layer.objects.active = armature_temp_obj

        armature_with_bones_obj = None

        mod_objs = []

        for drawable in self.drawables:
            vmodel_obj = drawable.apply(None, self.bones_override)
            if (armature_with_bones_obj == None and self.drawable_with_bones_name != None and drawable.name == self.drawable_with_bones_name):
                armature_with_bones_obj = vmodel_obj

            vmodels.append(vmodel_obj)
        
        vmodel_dict_obj = bpy.data.objects.new(name, None)
        vmodel_dict_obj.sollumtype = "Drawable Dictionary"

        for vmodel in vmodels:
            vmodel.parent = vmodel_dict_obj
        
        bpy.context.scene.collection.objects.link(vmodel_dict_obj)

        if (armature_with_bones_obj == None):
            armature_with_bones_obj = vmodels[0]

        for obj in mod_objs:
            mod = obj.modifiers.new("Armature", 'ARMATURE')
            mod.object = armature_with_bones_obj

        bpy.ops.object.select_all(action='DESELECT')
        armature_temp_obj.select_set(True)
        armature_with_bones_obj.select_set(True)
        bpy.context.view_layer.objects.active = armature_with_bones_obj
        bpy.ops.object.join()
