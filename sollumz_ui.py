import bpy
import os 
from .tools import meshgen as MeshGen
from bpy.types import PropertyGroup, Panel, UIList, Operator, AddonPreferences
from bpy.props import CollectionProperty, PointerProperty, StringProperty, IntProperty, BoolProperty, FloatProperty

class SollumzPreferences(AddonPreferences):
    bl_idname = __package__

    shared_textures_path: StringProperty(
        name="Shared textures path",
        subtype='FILE_PATH',
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "shared_textures_path")


class SollumzMainPanel(bpy.types.Panel):
    bl_label = "Sollumz"
    bl_idname = "SOLLUMZ_PT_MAIN_PANEL"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout

        object = context.active_object
                
        if(object == None):
            layout.label(text = "No objects in scene")            
        else:
            
            toolbox = layout.box()
            toolbox.label(text = "Tools") 
            
            actlodbox = toolbox.box()
            actlodbox.label(text = 'Active LOD')
            subrow = actlodbox.row(align=True)
            subrow.prop_tabs_enum(context.scene, "level_of_detail")
            
            toolbox.prop(context.scene, "hide_collision")
            
            selectionbox = layout.box()
            selectionbox.label(text = "Selection Info")
            textbox = selectionbox.box()
            textbox.prop(object, "name", text = "Object Name")

            subbox = selectionbox.box() 
            subbox.props_enum(object, "sollumtype")

            if(object.sollumtype == "Drawable"):
                row = subbox.row()
                subbox.prop(object, "drawble_distance_high")
                subbox.prop(object, "drawble_distance_medium")
                row = subbox.row()
                subbox.prop(object, "drawble_distance_low")
                subbox.prop(object, "drawble_distance_vlow")

            if(object.sollumtype == "Geometry"):
                subbox.prop(object, "level_of_detail")
                subbox.prop(object, "mask")   

            if(object.sollumtype == "Bound Geometry"):
                subbox.prop(object, "bounds_bvh")

            if(object.sollumtype == "Bound Capsule"):
                subbox.prop(object, "bounds_length")
                subbox.prop(object, "bounds_radius")

            if(object.sollumtype == "Bound Cylinder"):
                subbox.prop(object, "bounds_length")
                subbox.prop(object, "bounds_radius")

            if(object.sollumtype == "Bound Disc"):
                subbox.prop(object, "bounds_length")
                subbox.prop(object, "bounds_radius")

            if(object.sollumtype == "Bound Sphere"):
                subbox.prop(object, "bounds_radius")

            if(object.sollumtype == "Clip"):
                for k in ["Hash", "Name", "Type", "Unknown30", "AnimationHash", "StartTime", "EndTime", "Rate"]:
                    subbox.prop(object.clip_properties, k)

            if(object.sollumtype == "Animation"):
                for k in ["Hash", "FrameCount", "SequenceFrameLimit", "Duration", "Unknown10", "Unknown1C"]:
                    subbox.prop(object.anim_properties, k)

def param_name_to_title(pname):
    
    title = ""
    
    a = pname.split("_")
    b = a[0]
    glue = ' '
    c = ''.join(glue + x if x.isupper() else x for x in b).strip(glue).split(glue)
    d = ""
    for word in c:
        d += word
        d += " "
    title = d.title() #+ a[1].upper() dont add back the X, Y, Z, W
    
    return title

def bounds_update(self, context):
    if(self.sollumtype == "Bound Sphere"):
        MeshGen.BoundSphere(mesh=self.data, radius=self.bounds_radius)

    if(self.sollumtype == "Bound Cylinder"):
        MeshGen.BoundCylinder(mesh=self.data, radius=self.bounds_radius, length=self.bounds_length)

    if(self.sollumtype == "Bound Disc"):
        MeshGen.BoundDisc(mesh=self.data, radius=self.bounds_radius, length=self.bounds_length)

    if(self.sollumtype == "Bound Capsule"):
        MeshGen.BoundCapsule(mesh=self.data, radius=self.bounds_radius, length=self.bounds_length)

def scene_lod_update(self, context):
    lod = self.level_of_detail

    for obj in context.scene.objects: 
        if lod == "All":
            obj.hide_viewport = False
        else:
            obj.hide_viewport = obj.level_of_detail != lod

def scene_hide_collision(self, context):
    for obj in context.scene.objects:
        if "Bound" in obj.sollumtype:
            obj.hide_viewport = self.hide_collision 

class SollumzMaterialPanel(bpy.types.Panel):
    bl_label = "Sollumz Material Panel"
    bl_idname = "Sollumz_PT_MAT_PANEL"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"
    
    shadername : bpy.props.StringProperty(default = "default.sps")
    
    def draw(self, context):
        layout = self.layout

        object = context.active_object        
        if(object == None):
            return
        mat = object.active_material  
        
        tbox = layout.box()
        tbox.label(text = "Tools")
        box = tbox.box()
        box.label(text = "Create Shader")
        row = box.row()  
        row.label(text = "Shader Type:")
        row.prop_menu_enum(object, "shadertype", text = object.shadertype)
        box.operator("sollum.createvshader").shadername = object.shadertype
        
        if(mat == None):
            return
        
        #FIX ME ##################################
        #if(mat.sollumtype == "Blender"):
           # box = tbox.box()
            #row = box.row()
           # row.label(text = "Convert To Shader")
            #row.operator("sollum.converttov") 
        
        
        if(mat.sollumtype == "GTA"):
            
            box = layout.box()
            shader_box = box
            box.prop(mat, "name", text = "Shader")
            
            #layout.label(text = "Parameters")
            
            #box = layout.box()
            #box.label(text = "Parameters")
            
            mat_nodes = mat.node_tree.nodes
            
            image_nodes = []
            value_nodes = []
            
            for n in mat_nodes:
                if(isinstance(n, bpy.types.ShaderNodeTexImage)):
                    image_nodes.append(n)
                elif(isinstance(n, bpy.types.ShaderNodeValue)):
                    value_nodes.append(n)
                #else:
            
            for n in image_nodes:
                box = shader_box.box()
                box.label(text = n.name + " Texture")
                
                row = box.row()
                
                row.prop(n, "texture_name")
                
                row.prop(n, "embedded")
                
                if n.embedded:
                    uf_box = box.box()
                    uf_box.label(text = "Texture")
                    if(n.image != None):
                        uf_box.prop(n.image, "filepath", text= "Texture Path:")
                        #n.texture_name = os.path.basename(n.image.filepath)

                    #row.prop(specnode, "type") #gims fault
                    uf_box.prop(n, "format_type")
                    
                    #row = box.row() #gims fault
                    uf_box.prop(n, "usage")
                    uf_box.label(text = "Usage Flags:")
                    uf_row = uf_box.row()
                    uf_row.prop(n, "not_half")
                    uf_row.prop(n, "hd_split")
                    uf_row.prop(n, "flag_full")
                    uf_row.prop(n, "maps_half")
                    uf_row = uf_box.row()
                    uf_row.prop(n, "x2")
                    uf_row.prop(n, "x4")
                    uf_row.prop(n, "y4")
                    uf_row.prop(n, "x8")
                    uf_row = uf_box.row()
                    uf_row.prop(n, "x16")
                    uf_row.prop(n, "x32")
                    uf_row.prop(n, "x64")
                    uf_row.prop(n, "y64")
                    uf_row = uf_box.row()
                    uf_row.prop(n, "x128")
                    uf_row.prop(n, "x256")
                    uf_row.prop(n, "x512")
                    uf_row.prop(n, "y512")
                    uf_row = uf_box.row()
                    uf_row.prop(n, "x1024")
                    uf_row.prop(n, "y1024")
                    uf_row.prop(n, "x2048")
                    uf_row.prop(n, "y2048")
                    uf_row = uf_box.row()
                    uf_row.prop(n, "embeddedscriptrt")
                    uf_row.prop(n, "unk19")
                    uf_row.prop(n, "unk20")
                    uf_row.prop(n, "unk21")
                    uf_row = uf_box.row()
                    uf_row.prop(n, "unk24")
                    
                    uf_box.prop(n, "extra_flags")
                
            prevname = ""
            #value_nodes.insert(1, value_nodes.pop(len(value_nodes) - 1)) #shift last item to second because params are messed up for some reason ? (fixed?)
            for n in value_nodes:
                if(n.name[:-2] not in prevname):
                    #new parameter
                    parambox = shader_box.box()
                    parambox.label(text = param_name_to_title(n.name)) 
                      
                parambox.prop(n.outputs[0], "default_value", text = n.name[-1].upper())
                
                prevname = n.name

class SOLLUMZ_UL_BoneFlags(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index): 
        custom_icon = 'FILE'

        if self.layout_type in {'DEFAULT', 'COMPACT'}: 
            layout.prop(item, 'name', text='', icon = custom_icon, emboss=False, translate=False)
        elif self.layout_type in {'GRID'}: 
            layout.alignment = 'CENTER' 
            layout.prop(item, 'name', text='', icon = custom_icon, emboss=False, translate=False)

class SOLLUMZ_OT_BoneFlags_NewItem(Operator): 
    bl_idname = "sollumz_flags.new_item" 
    bl_label = "Add a new item"
    def execute(self, context): 
        bone = context.active_pose_bone.bone
        bone.bone_properties.flags.add() 
        return {'FINISHED'}

class SOLLUMZ_OT_BoneFlags_DeleteItem(Operator): 
    bl_idname = "sollumz_flags.delete_item" 
    bl_label = "Deletes an item" 
    @classmethod 
    def poll(cls, context): 
        return context.active_pose_bone.bone.bone_properties.flags

    def execute(self, context): 
        bone = context.active_pose_bone.bone

        list = bone.bone_properties.flags
        index = bone.bone_properties.ul_flags_index
        list.remove(index) 
        bone.bone_properties.ul_flags_index = min(max(0, index - 1), len(list) - 1) 
        return {'FINISHED'}

class SollumzBonePanel(Panel):
    bl_label = "Sollumz Bone Panel"
    bl_idname = "SOLLUMZ_PT_BONE_PANEL"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "bone"

    def draw(self, context):
        layout = self.layout

        if (context.active_pose_bone == None):
            return

        bone = context.active_pose_bone.bone

        layout.prop(bone, "name", text = "Bone Name")
        layout.prop(bone.bone_properties, "tag", text = "BoneTag")

        layout.label(text="Flags")
        layout.template_list("SOLLUMZ_UL_BoneFlags", "Flags", bone.bone_properties, "flags", bone.bone_properties, "ul_flags_index")
        row = layout.row() 
        row.operator('sollumz_flags.new_item', text='New')
        row.operator('sollumz_flags.delete_item', text='Delete')

class SollumzGroupPanel(Panel):
    bl_parent_id = "SOLLUMZ_PT_BONE_PANEL"
    bl_label = "Group Properties"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "bone"
    
    def draw(self, context):
        layout = self.layout

        if (context.active_pose_bone == None):
            return
            
        bone = context.active_pose_bone.bone

        group = bone.bone_properties.group

        layout.label(text="Do not touch these unless you know what you are doing!", icon="ERROR")
        layout.prop(group, "active", text = "Active")

        if(group.active == False):
            return

        layout.prop(group, "mass", text = "Mass")
        layout.prop(group, "child", text = "Child")

class SollumzAnimPanel(bpy.types.Panel):
    bl_label = "Sollumz Animation"
    bl_idname = "SOLLUMZ_PT_ANIM_PANEL"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout

        active_object = context.active_object

        if active_object is None:
            layout.label(text = "No objects selected")
            return

        if active_object.animation_data is None:
            layout.label(text = "Selected object has no animation assigned")
            return
        
        action = active_object.animation_data.action

        if action is None:
            layout.label(text = "No animations selected")
            return

        layout.prop(action, "Hash", text = "Hash")
        layout.prop(action, "ParentAnimHash", text = "Parent Animation Hash")
        layout.prop(action, "FrameCount", text = "Frame Count")
        layout.prop(action, "SequenceFrameLimit", text = "Sequence Frame Limit")
        layout.prop(action, "Duration", text = "Duration (sec)")
        layout.prop(action, "Unknown10", text = "Unknown10")
        layout.prop(action, "Unknown1C", text = "Unknown1C")        

classes = (
    SollumzMaterialPanel,
    SollumzMainPanel,
    SollumzBonePanel,
    SollumzGroupPanel,
    SollumzAnimPanel,
    SollumzPreferences,
    SOLLUMZ_UL_BoneFlags,
    SOLLUMZ_OT_BoneFlags_NewItem,
    SOLLUMZ_OT_BoneFlags_DeleteItem,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
