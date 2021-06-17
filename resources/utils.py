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

def get_related_texture(texture_dictionary, img_name):

    props = None 
    format = None
    usage = None 
    not_half = False
    hd_split = False
    full = False
    maps_half = False
    
    for t in texture_dictionary:
        tname = t.find("FileName").text 
        if(tname == img_name):
            
            format = t.find("Format").text.split("_")[1] 
            usage = t.find("Usage").text
            uf = t.find("UsageFlags").text
            
            not_half = False
            hd_split = False    
            full = False
            maps_half = False
            x2 = False
            x4 = False
            y4 = False
            x8 = False
            x16 = False 
            x32 = False
            x64 = False
            y64 = False
            x128 = False
            x256 = False
            x512 = False
            y512 = False
            x1024 = False
            y1024 = False
            x2048 = False
            y2048 = False
            embeddedscriptrt = False
            unk19 = False
            unk20 = False
            unk21 = False
            unk24 = False
            
            if("NOT_HALF" in uf):
                not_half = True
            if("HD_SPLIT" in uf):
                hd_split = True
            if("FLAG_FULL" in uf):
                full = True
            if("MAPS_HALF" in uf):
                maps_half = True
            if("X2" in uf):
                x2 = True
            if("X4" in uf):
                x4 = True
            if("Y4" in uf):
                y4 = True
            if("X8" in uf):
                x8 = True
            if("X16" in uf):
                x16 = True
            if("X32" in uf):
                x32 = True
            if("X64" in uf):
                x64 = True
            if("Y64" in uf):
                y64 = True
            if("X128" in uf):
                x128 = True
            if("X256" in uf):
                x256 = True
            if("X512" in uf):
                x512 = True
            if("Y512" in uf):
                y512 = True
            if("X1024" in uf):
                x1024 = True
            if("Y1024" in uf):
                y1024 = True
            if("X2048" in uf):
                x2048 = True
            if("Y2048" in uf):
                y2048 = True
            if("EMBEDDEDSCRIPTRT" in uf):
                embeddedscriptrt = True
            if("UNK19" in uf):
                unk19 = True
            if("UNK20" in uf):
                unk20 = True
            if("UNK21" in uf):
                unk21 = True
            if("UNK24" in uf):
                unk24 = True
            
            
            extra_flags = int(t.find("ExtraFlags").attrib["value"])
            
            props = []
            props.append(format)
            props.append(usage)
            props.append(not_half) 
            props.append(hd_split) 
            props.append(full) 
            props.append(maps_half) 
            props.append(extra_flags)
            props.append(x2)
            props.append(x4)
            props.append(y4)
            props.append(x8)
            props.append(x16)
            props.append(x32)
            props.append(x64)
            props.append(y64)
            props.append(x128)
            props.append(x256)
            props.append(x512)
            props.append(y512)
            props.append(x1024)
            props.append(y1024)
            props.append(x2048)
            props.append(y2048)
            props.append(embeddedscriptrt)
            props.append(unk19)
            props.append(unk20)
            props.append(unk21)
            props.append(unk24)
        
    return props 

def read_shader_info(self, context, filepath, shd_node, td_node):
    
    shaders = []
    
    for shader in shd_node:
        mat = create_material(filepath, td_node, shader)
        shaders.append(mat)
        
    return shaders

def read_ydr_shaders(self, context, filepath, root):
    shd_group = root.find("ShaderGroup")

    if not shd_group:
        return None

    shd_node = shd_group.find("Shaders")
    td_node = shd_group.find("TextureDictionary")  

    shaders = read_shader_info(self, context, filepath, shd_node, td_node)
    return shaders

def create_material(filepath, td_node, shader):
    
    params = shader.find("Parameters")
    
    filename = os.path.basename(filepath)[:-8]
    texture_dir = os.path.dirname(os.path.abspath(filepath)) + "\\" + filename + "\\"
    
    texture_dictionary = None
    if(td_node != None):
        texture_dictionary = []
        for i in td_node:
            texture_dictionary.append(i)
    
    shadern_node = shader.find("FileName")
    if shadern_node is not None and shadern_node.text is not None:
        shadern = shadern_node.text
    else:
        shadern = "default.sps"

    bpy.ops.sollum.createvshader(shadername = shadern)
    mat = bpy.context.scene.last_created_material
    
    nodes = mat.node_tree.nodes 
    for p in params:
        for n in nodes: 
            if(isinstance(n, bpy.types.ShaderNodeTexImage)):
                if(p.attrib["name"] == n.name):
                    texture_pos = p.find("Name")
                    if(hasattr(texture_pos, 'text')):
                        texture_name = texture_pos.text + ".dds" 
                        texture_path = texture_dir + texture_name
                        n.texture_name = texture_name
                        if(os.path.isfile(texture_dir + texture_name)):
                            img = bpy.data.images.load(texture_path, check_existing=True)
                            n.image = img 

                        #deal with special situations
                        if(p.attrib["name"] == "BumpSampler" and hasattr(n.image, 'colorspace_settings')):
                            n.image.colorspace_settings.name = 'Non-Color'

            elif(isinstance(n, bpy.types.ShaderNodeValue)):
                if(p.attrib["name"].lower() == n.name[:-2].lower()): #remove _X
                    value_key = n.name[-1] #X,Y,Z,W
                    if p.attrib["type"] == "Array":
                        value = p.find("Value").attrib[value_key]
                    else:
                        value = p.attrib[value_key]

                    n.outputs[0].default_value = float(value)      
        
    #assign all embedded texture properties
    #### FIND A BETTER WAY TO DO THIS ####
    if(texture_dictionary != None):
        for node in nodes:
            if(isinstance(node, bpy.types.ShaderNodeTexImage)):
                if(node.image != None):
                    texturepath = node.image.filepath
                    texturename = os.path.basename(texturepath)
                    texture_properties = get_related_texture(texture_dictionary, texturename)
                    if(texture_properties != None):
                        node.embedded = True
                        node.format_type = texture_properties[0] 
                        node.usage = texture_properties[1]
                        node.not_half = texture_properties[2] 
                        node.hd_split = texture_properties[3] 
                        node.flag_full = texture_properties[4] 
                        node.maps_half = texture_properties[5]  
                        node.extra_flags = texture_properties[6] 
                        node.x2 = texture_properties[7] 
                        node.x4 = texture_properties[8] 
                        node.y4 = texture_properties[9] 
                        node.x8 = texture_properties[10] 
                        node.x16 = texture_properties[11] 
                        node.x32 = texture_properties[12] 
                        node.x64 = texture_properties[13] 
                        node.y64 = texture_properties[14] 
                        node.x128 = texture_properties[15] 
                        node.x256 = texture_properties[16] 
                        node.x512 = texture_properties[17] 
                        node.y512 = texture_properties[18] 
                        node.x1024 = texture_properties[19] 
                        node.y1024 = texture_properties[20] 
                        node.x2048 = texture_properties[21] 
                        node.y2048 = texture_properties[22] 
                        node.embeddedscriptrt = texture_properties[23] 
                        node.unk19 = texture_properties[24] 
                        node.unk20 = texture_properties[25]
                        node.unk21 = texture_properties[26]
                        node.unk24 = texture_properties[27]
    
    mat.sollumtype = "GTA" 
    
    return mat

def process_uv(uv):
    u = uv[0]
    v = (uv[1] * -1) + 1.0

    return [u, v]