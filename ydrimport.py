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
from .resources.drawable import Drawable, DrawableDictionary, DrawableModel
from .tools.utils import build_bones_dict
from .tools import cats as Cats
from .sollumz_shaders import create_material

def process_uv(uv):
    u = uv[0]
    v = (uv[1] * -1) + 1.0
    return [u, v]

def create_uv_layer(mesh, num, texcoords):
    mesh.uv_layers.new()
    uv_layer = mesh.uv_layers[num]
    for i in range(len(uv_layer.data)):
        uv = process_uv(texcoords[mesh.loops[i].vertex_index])
        uv_layer.data[i].uv = uv 

def create_vertexcolor_layer(mesh, num, colors):
    mesh.vertex_colors.new(name = "Vertex Colors " + str(num)) 
    color_layer = mesh.vertex_colors[num]
    for i in range(len(color_layer.data)):
        rgba = colors[mesh.loops[i].vertex_index]
        color_layer.data[i].color = rgba

def create_geometry(geometry, bones, name):
    vertices = []
    faces = []
    normals = []
    texcoords0 = []
    texcoords1 = []
    texcoords2 = []
    texcoords3 = []
    texcoords4 = []
    texcoords5 = []
    texcoords6 = []
    texcoords7 = []
    colors0 = []
    colors1 = []
    blendweights = []
    blendindices = []

    vertices_data = geometry.vertex_buffer.vertices
    for v in vertices_data:
        vertices.append(v.position)
        # normals.append(v.normal)

        if(v.texcoord0 != None):
            texcoords0.append(v.texcoord0)
        if(v.texcoord1 != None):
            texcoords1.append(v.texcoord1)
        if(v.texcoord2 != None):
            texcoords2.append(v.texcoord2)
        if(v.texcoord3 != None):
            texcoords3.append(v.texcoord3)
        if(v.texcoord4 != None):
            texcoords4.append(v.texcoord4)
        if(v.texcoord5 != None):
            texcoords5.append(v.texcoord5)
        if(v.texcoord6 != None):
            texcoords6.append(v.texcoord6)
        if(v.texcoord7 != None):
            texcoords7.append(v.texcoord7)

        if(v.colors0 != None):
            colors0.append(v.colors0)
        if(v.colors1 != None):
            colors1.append(v.colors1)

        # if(v.blendweights != None):
        #     blendweights.append(v.blendweights)
        # if(v.blendindices != None):
        #     blendindices.append(v.blendindices)

    # for i in geometry.index_buffer:
    #     faces.append(i)
    faces = geometry.index_buffer.buffer

    mesh = bpy.data.meshes.new("Geometry")
    mesh.from_pydata(vertices, [], faces)
    mesh.create_normals_split()
    mesh.validate(clean_customdata=False)
    polygon_count = len(mesh.polygons)
    mesh.polygons.foreach_set("use_smooth", [True] * polygon_count)
    # maybe normals_split_custom_set_from_vertices(self.normals) is better?
    if vertices_data[0].normal is not None:
        normals_fixed = []
        for l in mesh.loops:
            normals_fixed.append(vertices_data[l.vertex_index].normal)
        
        mesh.normals_split_custom_set(normals_fixed)

    mesh.use_auto_smooth = True

    # set uvs
    uv_layer_count = 0
    if(len(texcoords0) > 0):
        create_uv_layer(mesh, uv_layer_count, texcoords0)
        uv_layer_count += 1
    if(len(texcoords1) > 0):
        create_uv_layer(mesh, uv_layer_count, texcoords1)
        uv_layer_count += 1
    if(len(texcoords2) > 0):
        create_uv_layer(mesh, uv_layer_count, texcoords2)
        uv_layer_count += 1
    if(len(texcoords3) > 0):
        create_uv_layer(mesh, uv_layer_count, texcoords3)
        uv_layer_count += 1
    if(len(texcoords4) > 0):
        create_uv_layer(mesh, uv_layer_count, texcoords4)
        uv_layer_count += 1
    if(len(texcoords5) > 0):
        create_uv_layer(mesh, uv_layer_count, texcoords5)
        uv_layer_count += 1
    if(len(texcoords6) > 0):
        create_uv_layer(mesh, uv_layer_count, texcoords6)
        uv_layer_count += 1
    if(len(texcoords7) > 0):
        create_uv_layer(mesh, uv_layer_count, texcoords7)
        uv_layer_count += 1
    
    #set vertex colors
    if(len(colors0) > 0):
        create_vertexcolor_layer(mesh, 0, colors0)
    if(len(colors1) > 0):
        create_vertexcolor_layer(mesh, 1, colors1)
    
    #set tangents - .tangent is read only so can't set them
    #for poly in mesh.polygons:
        #for idx in poly.loop_indicies:
            #mesh.loops[i].tangent = tangents[i]    

    obj = bpy.data.objects.new(name.replace(".#dr", "") + "_mesh", mesh)
    
    #load weights
    if (bones != None and len(bones) > 0 and vertices_data[0].blendweights is not None and len(vertices_data) > 0):
        num = max(256, len(bones))
        for i in range(num):
            if (i < len(bones)):
                obj.vertex_groups.new(name=bones[i].name)
            else:
                obj.vertex_groups.new(name="UNKNOWN_BONE." + str(i))

        for vertex_idx, vertex in enumerate(vertices_data):
            for i in range(0, 4):
                weight = vertex.blendweights[i] / 255
                index = vertex.blendindices[i]
                if (weight > 0.0):
                    obj.vertex_groups[index].add([vertex_idx], weight, "ADD")

        Cats.remove_unused_vertex_groups_of_mesh(obj)

    return obj

def create_drawable_model(drawable_model, materials, bones, name, key):
    
    objs = []
    for mesh in drawable_model.geometries:
        obj = create_geometry(mesh, bones, name)
        obj.sollumtype = "Geometry"
        obj.level_of_detail = key
        obj.mask = drawable_model.render_mask
        if materials is not None:
            obj.data.materials.append(materials[mesh.shader_index])
            
        bpy.context.scene.collection.objects.link(obj)
        objs.append(obj)

    return objs

def create_bone(bone, armature):

    if armature is None:
        return None

    # bpy.context.view_layer.objects.active = armature
    edit_bone = armature.data.edit_bones.new(bone.name)
    if bone.parent_index != -1:
        edit_bone.parent = armature.data.edit_bones[bone.parent_index]

    # https://github.com/LendoK/Blender_GTA_V_model_importer/blob/master/importer.py
    mat_rot = bone.rotation.to_matrix().to_4x4()
    mat_loc = Matrix.Translation(bone.translation)
    mat_sca = Matrix.Scale(1, 4, bone.scale)

    edit_bone.head = (0,0,0)
    edit_bone.tail = (0,0.05,0)
    edit_bone.matrix = mat_loc @ mat_rot @ mat_sca
    if edit_bone.parent != None:
        edit_bone.matrix = edit_bone.parent.matrix @ edit_bone.matrix

    return bone.name

def set_bone_properties(bone, armature):

    bl_bone = armature.pose.bones[bone.name].bone
    bl_bone.bone_properties.tag = bone.tag
    # LimitRotation and Unk0 have their special meanings, can be deduced if needed when exporting
    flags_restricted = set(["LimitRotation", "Unk0"])
    for _flag in bone.flags:
        if (_flag in flags_restricted):
            continue

        flag = bl_bone.bone_properties.flags.add()
        flag.name = _flag

def create_skeleton(skeleton, armature):
    
    if skeleton is None:
        return None

    bpy.context.view_layer.objects.active = armature
    bones = skeleton.bones
    bpy.ops.object.mode_set(mode='EDIT')

    for bone in bones:
        create_bone(bone, armature)

    bpy.ops.object.mode_set(mode='OBJECT')

    for bone in bones:
        set_bone_properties(bone, armature)

    return armature

def create_drawable(drawable, filepath=None, armature=None, bones_override=None, clean=False):

    if clean is True:
        if drawable.is_empty() is True:
            return None

    if armature is None:
        skel = bpy.data.armatures.new(drawable.name + ".skel")
        armature = bpy.data.objects.new(drawable.name, skel)
        armature.sollumtype = "Drawable"
        bpy.context.scene.collection.objects.link(armature)

        armature.drawble_distance_high = drawable.lod_dist_high
        armature.drawble_distance_medium = drawable.lod_dist_med
        armature.drawble_distance_low = drawable.lod_dist_low
        armature.drawble_distance_vlow = drawable.lod_dist_vlow

    bpy.context.view_layer.objects.active = armature
    create_skeleton(drawable.skeleton, armature)

    if len(drawable.joints) > 0:
        bones_dict = build_bones_dict(armature)
        if bones_dict is not None:
            for joint in drawable.joints:
                bone = armature.pose.bones.get(bones_dict[joint.tag])
                joint.apply(bone)

    bones = drawable.get_bones()
    if bones_override is not None:
        bones = bones_override

    materials = None
    if (drawable.shader_group is not None):
        shaders = drawable.shader_group.shaders
        texture_dictionary = drawable.shader_group.texture_dictionary
        materials = []
        for shader in shaders:
            materials.append(create_material(shader, texture_dictionary, filepath))

    for dm in drawable.drawable_models_high:
        model = create_drawable_model(dm, materials, bones, drawable.name, "High")
        DrawableModel.set_parent(model, armature)

    for dm in drawable.drawable_models_med:
        model = create_drawable_model(dm, materials, bones, drawable.name, "Medium")
        DrawableModel.set_parent(model, armature)

    for dm in drawable.drawable_models_low:
        model = create_drawable_model(dm, materials, bones, drawable.name, "Low")
        DrawableModel.set_parent(model, armature)

    for dm in drawable.drawable_models_vlow:
        model = create_drawable_model(dm, materials, bones, drawable.name, "Very Low")
        DrawableModel.set_parent(model, armature)

    if len(drawable.bounds) > 0:
        cobj = bpy.data.objects.new(drawable.name + "_col", None)
        
        if(cobj == None):
            return #log error 
        
        for child in drawable.bounds:
            bpy.context.scene.collection.objects.link(child)
            child.parent = cobj 
            
        cobj.sollumtype = "Bound Composite"
        cobj.parent = armature
        bpy.context.scene.collection.objects.link(cobj)

    return armature

def create_drawable_dict(drawable_dict, filepath):

    name = os.path.basename(filepath)[:-8]
    vmodels = []
    # bones are shared in single ydd however they still have to be placed under a paticular drawable

    armature_with_bones_obj = None
    mod_objs = []
    drawable_with_bones = None
    for drawable in drawable_dict.drawables:
        if drawable.get_bones() is not None:
            drawable_with_bones = drawable
            break

    for drawable in drawable_dict.drawables:
        vmodel_obj = create_drawable(drawable, filepath, armature=None, bones_override=drawable_with_bones.get_bones())
        if (armature_with_bones_obj == None and drawable_with_bones is not None and drawable.skeleton is not None):
            armature_with_bones_obj = vmodel_obj

        for obj in vmodel_obj.children:
            mod_objs.append(obj)
            
        vmodels.append(vmodel_obj)
    
    vmodel_dict_obj = bpy.data.objects.new(name, None)
    vmodel_dict_obj.sollumtype = "Drawable Dictionary"

    for vmodel in vmodels:
        vmodel.parent = vmodel_dict_obj
    
    bpy.context.scene.collection.objects.link(vmodel_dict_obj)

    if (armature_with_bones_obj is not None):
        for obj in mod_objs:
            mod = obj.modifiers.get("Armature")
            if mod is None:
                continue

            mod.object = armature_with_bones_obj

    return vmodel_dict_obj

def read_ydr_xml(root):

    drawable = Drawable.from_xml(root)

    return drawable

def read_ydd_xml(root):

    drawable_dict = DrawableDictionary.from_xml(root)

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

        drawable = read_ydr_xml(root)
        vmodel_obj = create_drawable(drawable)

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
        drawable_dict = read_ydd_xml(root)
        create_drawable_dict(drawable_dict, self.filepath)

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
