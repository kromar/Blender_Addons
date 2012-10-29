# ***** BEGIN GPL LICENSE BLOCK *****
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# ***** END GPL LICENCE BLOCK *****

# ----------------------------------------------------------------------------#

'''
todo:
    - add check if nothing is selected 
        - menu entry?
        - warning message when selecting export?
        - class to invoke popups
        
    - select blend folder for export?
    
    - uvmaps asignement messes up, do we need separate uvs for each amterial?
    - geometry export also wipes ghosts? 
    
bugs:
- entered name is written without ending

changelog:
    "version": 1.0.0
        -initial release
        
    "version": 1.0.1
        - adjusted export options
        - release export options from functions
        
    "version": 1.0.2
        - added submenu in export menu
        - added multiple export options
        - added arthros and hystsim export options
    
    "version": 1.0.3
        - hack to remove ghost materials
     
    "version": 1.0.4
        - changed unique names that caused wrong export
        - adjusted export axis for hystsim
        
    "version": 1.0.5
        - cleanup of export options
        - fixed problem in ghost iage check if no image existed
        - objects get reselected after export
        - check for meshes only (no lamps and other stuff should get processed
        
    "version": 1.0.6
        - fixed mesh data
        - 
    "version": 1.0.7
        - reasign textures in uv after export (add ghosts)
         
    "version": 1.0.8
        - new function to remove ghost materials, the function removes all uvimages 
        per face and after exporting the mesh reasigns them so we keep them in multitexture mode
        
'''

# ----------------------------------------------------------------------------#

import bpy
import os
from bpy.props import *

#addon description
bl_info = {
    "name": "Export: ObjBatch",
    "author": "Daniel Grauer",
    "version": (1, 0, 8),
    "blender": (2, 6, 3),
    "category": "Import-Export",
    "category": "kromar",
    "location": "File > Export > ObjBatch > Geometry",
    "description": "export all selected objects to Wavefront (.obj) format",
    "warning": '', # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": ""
    }

print(" ")
print("*------------------------------------------------------------------------------*")
print("*                          BacthObj export                        *")
print(" ")

ArthrosModel = dict(check_existing = True,
         use_selection = True,
         use_animation = False,
         use_apply_modifiers = True,
         use_edges = False,
         use_normals = True,
         use_uvs = True,
         use_materials = True,
         use_triangles = True,
         use_nurbs = False,
         use_vertex_groups = False,
         use_blen_objects = False,
         group_by_object = False,
         group_by_material = True,
         keep_vertex_order = False,
         global_scale = 1,
         axis_forward = 'Y',
         axis_up = 'Z',
         path_mode = 'STRIP',
         filter_glob = "*.obj; *.mtl")

ArthrosGeometry = dict(check_existing = True,
         use_selection = True,
         use_animation = False,
         use_apply_modifiers = True,
         use_edges = False,
         use_normals = True,
         use_uvs = False,
         use_materials = False,
         use_triangles = True,
         use_nurbs = False,
         use_vertex_groups = False,
         use_blen_objects = False,
         group_by_object = False,
         group_by_material = False,
         keep_vertex_order = False,
         global_scale = 1,
         axis_forward = 'Y',
         axis_up = 'Z',
         path_mode = 'STRIP',
         filter_glob = "*.obj; *.mtl")


HystsimModel = dict(check_existing = True,
         use_selection = True,
         use_animation = False,
         use_apply_modifiers = True,
         use_edges = False,
         use_normals = True,
         use_uvs = True,
         use_materials = True,
         use_triangles = True,
         use_nurbs = False,
         use_vertex_groups = False,
         use_blen_objects = False,
         group_by_object = False,
         group_by_material = True,
         keep_vertex_order = False,
         global_scale = 1,
         axis_forward = '-Z',
         axis_up = 'Y',
         path_mode = 'STRIP',
         filter_glob = "*.obj; *.mtl")

HystsimGeometry = dict(check_existing = True,
         use_selection = True,
         use_animation = False,
         use_apply_modifiers = True,
         use_edges = False,
         use_normals = True,
         use_uvs = False,
         use_materials = False,
         use_triangles = True,
         use_nurbs = False,
         use_vertex_groups = False,
         use_blen_objects = False,
         group_by_object = False,
         group_by_material = False,
         keep_vertex_order = False,
         global_scale = 1,
         axis_forward = '-Z',
         axis_up = 'Y',
         path_mode = 'STRIP',
         filter_glob = "*.obj; *.mtl")

# ----------------------------------------------------------------------------#

def save_objBatch(filepath, amount, sim_type):

    selected = bpy.context.selected_objects
    
    #process selected objects
    if selected:
        for object in selected:
            if object.type == 'MESH':
                
                #toggle OBJECT mode
                bpy.ops.object.mode_set(mode = 'OBJECT', toggle = False)
                
                export_name = object.name + ".obj"
        
                # deselect all object
                bpy.ops.object.select_all(action = 'DESELECT')
               
                ## select one object to export
                object.select = True
                
                # wipe ghost materials
                mesh = object.data
                #wipe_ghost_materials(mesh)
                export_clean(mesh, filepath, sim_type, amount, export_name)
                
                
                # run the obj export
                #export_objBatch(filepath, sim_type, amount, export_name)
                
                # deselect object once its exported 
                object.select = False
        
            else:
                print(object.name + "is not a 'MESH' object")
    else:
        print("obj export: Nothing selected!")
    #reselect objects
    for objects in selected:
        objects.select = True
        
# ----------------------------------------------------------------------------#

def export_objBatch(filepath, sim_type, amount, export_name):
    
    if amount == 1:
        if sim_type == 'ArthrosModel':
            bpy.ops.export_scene.obj(filepath = filepath, **ArthrosModel)
        elif sim_type == 'ArthrosGeometry':
            bpy.ops.export_scene.obj(filepath = filepath, **ArthrosGeometry)
        elif sim_type == 'HystsimModel':
            bpy.ops.export_scene.obj(filepath = filepath, **HystsimModel)
        elif sim_type == 'HystsimGeometry':
            bpy.ops.export_scene.obj(filepath = filepath, **HystsimGeometry)
        
    else:
        filepath = filepath + export_name
        if sim_type == 'ArthrosModel':
            bpy.ops.export_scene.obj(filepath = filepath, **ArthrosModel)
        elif sim_type == 'ArthrosGeometry':
            bpy.ops.export_scene.obj(filepath = filepath, **ArthrosGeometry)
        elif sim_type == 'HystsimModel':
            bpy.ops.export_scene.obj(filepath = filepath, **HystsimModel)
        elif sim_type == 'HystsimGeometry':
            bpy.ops.export_scene.obj(filepath = filepath, **HystsimGeometry)
        
     
    print("Exported type: " + sim_type)
        
# ----------------------------------------------------------------------------#

def export_clean(mesh, filepath, sim_type, amount, export_name):

    GhostList =[]
    
    for uvmap in mesh.uv_textures:
        #print("UVMap: ", uvmap.name)
        
        for face in uvmap.data:
            image = face.image
            
            if image:
                #remove images from uvfaces
                GhostList.append([face, image])
                
                face.image = None
                #print(image.name , "texture removed from: ", uvmap.name)
            else:
                #print(mesh, ": no image to wipe")
                pass
          
    
    print("uv textures wiped")
    
    export_objBatch(filepath, sim_type, amount, export_name)
    
    
    for i in GhostList:
        #print(i[0], i[1])
        i[0].image =  i[1] 
    print("uv textures reasigned")
# ----------------------------------------------------------------------------#
#    menus
# ----------------------------------------------------------------------------#
'''
#this draws the new menu in FILE>EXPORT
def Export_Menu(self, context):
    layout = self.layout
    
    #try to generate menu with our menu class 
    layout.menu(Export_Menu_Arthros.bl_idname, text = "Arthros")
    layout.menu(Export_Menu_HystSim.bl_idname, text = "Hystsim")
       
# ----------------------------------------------------------------------------#

#draw content in export menus
class Export_Menu_Arthros(bpy.types.Menu):
    bl_label = "arthros export menu"
    bl_idname = "OBJECT_MT_arthros"
    
    def draw(self, context):
        pass

#draw content in export menus
class Export_Menu_HystSim(bpy.types.Menu):
    bl_label = "hystsim export menu"
    bl_idname = "OBJECT_MT_hystsim"
    
    def draw(self, context):
        pass
''' 
# ----------------------------------------------------------------------------#

def arthros_content(self, context):
    
    #single selected
    if len(bpy.context.selected_objects) == 1:
        export_name = bpy.context.active_object.name + ".obj"
        self.layout.operator(ArthrosModelExport.bl_idname, text = "Model (.obj) - single object").filepath = export_name
        self.layout.operator(ArthrosGeometryExport.bl_idname, text = "Geometry (.obj) - single object").filepath = export_name

    #multiple selected
    elif len(bpy.context.selected_objects) > 1:
        export_name = ""
        self.layout.operator(ArthrosModelExport.bl_idname, text = "Model (.obj) - multiple objects").filepath = export_name
        self.layout.operator(ArthrosGeometryExport.bl_idname, text = "Geometry (.obj) - multiple objects").filepath = export_name
    
# ----------------------------------------------------------------------------#

def hystsim_content(self, context):
            
    #single selected
    if len(bpy.context.selected_objects) == 1:
        export_name = bpy.context.active_object.name + ".obj"
        self.layout.operator(HystsimModelExport.bl_idname, text = "Model (.obj) - single object").filepath = export_name
        self.layout.operator(HystsimGeometryExport.bl_idname, text = "Geometry (.obj) - single object").filepath = export_name

    #multiple selected
    elif len(bpy.context.selected_objects) > 1:
        export_name = ""
        self.layout.operator(HystsimModelExport.bl_idname, text = "Model (.obj) - multiple objects").filepath = export_name
        self.layout.operator(HystsimGeometryExport.bl_idname, text = "Geometry (.obj) - multiple objects").filepath = export_name
    
    #layout.operator(OBJECT_MT_popup.bl_idname, text = "test error" )
# ----------------------------------------------------------------------------# 

class VIEW3D_MT_Popup(bpy.types.Menu):
    bl_label = "error popup"
    bl_idname = "OBJECT_MT_popup"

    def draw(self, context):
        self.layout.operator_context = 'INVOKE_REGION_WIN'
           
# ----------------------------------------------------------------------------#   
#    export
# ----------------------------------------------------------------------------#

class ArthrosModelExport(bpy.types.Operator):
    '''Export with material and uv'''
    bl_idname = "export.objbatch_model_arthros"
    bl_label = "Export modelObj_arthros"

    filepath = StringProperty(name = "File Path", description = "filepath", default = "", maxlen = 1024, options = {'ANIMATABLE'}, subtype = 'NONE')

    #switch menu entry for single and multiple selections
    def execute(self, context):
        #single selected
        if len(bpy.context.selected_objects) == 1:
            save_objBatch(self.properties.filepath, 1, 'ArthrosModel')
            return {'FINISHED'}

        #multiple selected
        elif len(bpy.context.selected_objects) > 1:
            save_objBatch(self.properties.filepath, 2, 'ArthrosModel')
            return {'FINISHED'}

    #open the filemanager    
    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

# ----------------------------------------------------------------------------#

class ArthrosGeometryExport(bpy.types.Operator):
    '''Export without material or uv'''
    bl_idname = "export.objbatch_geometry_arthros"
    bl_label = "Export geometryObj_arthros"

    filepath = StringProperty(name = "File Path", description = "filepath", default = "", maxlen = 1024, options = {'ANIMATABLE'}, subtype = 'NONE')

    #switch menu entry for single and multiple selections
    def execute(self, context):
        #single selected
        if len(bpy.context.selected_objects) == 1:
            save_objBatch(self.properties.filepath, 1, 'ArthrosGeometry')
            return {'FINISHED'}

        #multiple selected
        elif len(bpy.context.selected_objects) > 1:
            save_objBatch(self.properties.filepath, 2, 'ArthrosGeometry')
            return {'FINISHED'}

    #open the filemanager    
    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

# ----------------------------------------------------------------------------#

class HystsimModelExport(bpy.types.Operator):
    '''Export with material and uv'''
    bl_idname = "export.objbatch_model_hystsim"
    bl_label = "Export modelObj_hystsim"

    filepath = StringProperty(name = "File Path", description = "filepath", default = "", maxlen = 1024, options = {'ANIMATABLE'}, subtype = 'NONE')

    #switch menu entry for single and multiple selections
    def execute(self, context):
        #single selected
        if len(bpy.context.selected_objects) == 1:
            save_objBatch(self.properties.filepath, 1, 'HystsimModel')
            return {'FINISHED'}

        #multiple selected
        elif len(bpy.context.selected_objects) > 1:
            save_objBatch(self.properties.filepath, 2, 'HystsimModel')
            return {'FINISHED'}

    #open the filemanager    
    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

# ----------------------------------------------------------------------------#

class HystsimGeometryExport(bpy.types.Operator):
    '''Export without material or uv'''
    bl_idname = "export.objbatch_geometry_hystsim"
    bl_label = "Export geometryObj_hystsim"

    filepath = StringProperty(name = "File Path", description = "filepath", default = "", maxlen = 1024, options = {'ANIMATABLE'}, subtype = 'NONE')

    #switch menu entry for single and multiple selections
    def execute(self, context):
        #single selected
        if len(bpy.context.selected_objects) == 1:
            save_objBatch(self.properties.filepath, 1, 'HystsimGeometry')
            return {'FINISHED'}

        #multiple selected
        elif len(bpy.context.selected_objects) > 1:
            save_objBatch(self.properties.filepath, 2, 'HystsimGeometry')
            return {'FINISHED'}

    #open the filemanager    
    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}
    

# ----------------------------------------------------------------------------#   
    
def register():
    bpy.utils.register_module(__name__)
    # checking if Export_Menu is in bpy.types would work   
    #bpy.types.INFO_MT_file_export.append(Export_Menu)
    
    bpy.types.OBJECT_MT_arthros.append(arthros_content)
    bpy.types.OBJECT_MT_hystsim.append(hystsim_content)


def unregister():
    bpy.utils.unregister_module(__name__)
    #bpy.types.INFO_MT_file_export.remove(Export_Menu)
    
    bpy.types.OBJECT_MT_arthros.remove(arthros_content)
    bpy.types.OBJECT_MT_hystsim.remove(hystsim_content)

if __name__ == "__main__":
    register()
    

print(" ")
print("*                             initialized                                      *")
print("*------------------------------------------------------------------------------*")
print(" ")
