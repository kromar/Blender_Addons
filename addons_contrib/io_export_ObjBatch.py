# ##### BEGIN GPL LICENSE BLOCK #####
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
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8-80 compliant>


#===============================================================================
# todo:
#===============================================================================
'''
- add check if nothing is selected
    - menu entry?
    - warning message when selecting export?
    - class to invoke popups

- select blend folder for export?

- uvmaps asignement messes up, do we need separate uvs for each amterial?
- geometry export also wipes ghosts?
    
'''


# ----------------------------------------------------------------------------#
import fnmatch
import bpy
import os
from bpy.props import *
from bpy_extras.io_utils import (ExportHelper,
                                path_reference_mode,
                                )

# addon description
bl_info = {
    "name": "Export: ObjBatch",
    "author": "Daniel Grauer (kromar)",
    "version": (1, 0, 9),
    "blender": (2, 6, 8),
    "category": "Import-Export",
    "category": "VirtaMed",
    "location": "File > Export > ObjBatch > Geometry",
    "description": "export all selected objects to Wavefront (.obj) format",
    "warning": '',  # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": ""
    }

print(80 * "-")
print("BatchObj export")


ArthrosModel = dict(
        check_existing=True,
        use_selection=True,
        use_animation=False,
        use_mesh_modifiers=True,
        use_edges=True,
        use_normals=True,
        use_uvs=True,
        use_materials=True,
        use_triangles=True,
        use_nurbs=False,
        use_vertex_groups=False,
        use_smooth_groups=False,
        use_smooth_groups_bitflags=False,
        use_blen_objects=False,
        group_by_object=False,
        group_by_material=True,
        keep_vertex_order=False,
        global_scale=1,
        axis_forward='Y',
        axis_up='Z',
        path_mode='STRIP',
        filter_glob="*.obj; *.mtl")

ArthrosGeometry = dict(
        check_existing=True,
        use_selection=True,
        use_animation=False,
        use_mesh_modifiers=True,
        use_edges=True,
        use_normals=True,
        use_uvs=False,
        use_materials=False,
        use_nurbs=False,
        use_vertex_groups=False,
        use_smooth_groups=False,
        use_smooth_groups_bitflags=False,
        use_blen_objects=False,
        group_by_object=False,
        group_by_material=False,
        keep_vertex_order=False,
        global_scale=1,
        axis_forward='Y',
        axis_up='Z',
        path_mode='STRIP',
        filter_glob="*.obj; *.mtl")


HystsimModel = dict(
        check_existing=True,
        use_selection=True,
        use_animation=False,
        use_mesh_modifiers=True,
        use_edges=True,
        use_normals=True,
        use_uvs=True,
        use_materials=True,
        use_triangles=True,
        use_nurbs=False,
        use_vertex_groups=False,
        use_smooth_groups=False,
        use_smooth_groups_bitflags=False,
        use_blen_objects=False,
        group_by_object=False,
        group_by_material=True,
        keep_vertex_order=False,
        global_scale=1,
        axis_forward='-Z',
        axis_up='Y',
        path_mode='STRIP',
        filter_glob="*.obj; *.mtl")

HystsimGeometry = dict(
        check_existing=True,
        use_selection=True,
        use_animation=False,
        use_mesh_modifiers=True,
        use_edges=True,
        use_normals=True,
        use_uvs=False,
        use_materials=False,
        use_triangles=True,
        use_nurbs=False,
        use_vertex_groups=False,
        use_smooth_groups=False,
        use_smooth_groups_bitflags=False,
        use_blen_objects=False,
        group_by_object=False,
        group_by_material=False,
        keep_vertex_order=False,
        global_scale=1,
        axis_forward='-Z',
        axis_up='Y',
        path_mode='STRIP',
        filter_glob="*.obj; *.mtl")

# ----------------------------------------------------------------------------#
filename_ext = ".obj"

def save_objBatch(filepath, amount, sim_type):
    selected = bpy.context.selected_objects
   
    # process selected objects
    if selected:
        for ob in selected:
            # only poly and nurbs curves supported
            if ob.type == 'MESH':                  
                # make sure we are in object mode
                if bpy.ops.object.mode_set.poll():
                    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                    
                export_name = ob.name + filename_ext
                bpy.ops.object.select_all(action='DESELECT')
                ob.select = True
                # wipe ghost materials
                wipeGhostMaterials(ob, filepath, sim_type, amount, export_name)
                # export_objBatch(filepath, sim_type, amount, export_name)
                ob.select = False
                
            elif ob.type == 'POLY' \
                or ob.type == 'CURVE':
                # make sure we are in object mode
                if bpy.ops.object.mode_set.poll():
                    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                    
                export_name = ob.name + filename_ext
                bpy.ops.object.select_all(action='DESELECT')
                ob.select = True
                # wipe ghost materials
                mesh = ob.data
                # wipeGhostMaterials(mesh, filepath, sim_type, amount, export_name)
                export_objBatch(filepath, sim_type, amount, export_name)
                ob.select = False
                
                
            else:
                print(ob.name + "is not a 'MESH' object")
    else:
        print("obj export: Nothing selected!")
    # reselect objects
    for ob in selected:
        ob.select = True
# ----------------------------------------------------------------------------#

def wipeGhostMaterials(ob, filepath, sim_type, amount, export_name):
    GhostList = []
    if ob.type == 'MESH':
        mesh = ob.data
        for uvmap in mesh.uv_textures:
            # print("UVMap: ", uvmap.name)
            for face in uvmap.data:
                image = face.image
                if image:
                    # remove images from uvfaces
                    GhostList.append([face, image])
                    face.image = None
                    # print(image.name , "texture removed from: ", uvmap.name)
                else:
                    # print(mesh, ": no image to wipe")
                    pass
                
        print("uv textures wiped")
        export_objBatch(filepath, sim_type, amount, export_name)
        for i in GhostList:
            # print(i[0], i[1])
            i[0].image = i[1]
        print("uv textures reasigned")
    else:
        export_objBatch(filepath, sim_type, amount, export_name)

# ----------------------------------------------------------------------------#

def isAddonEnabled(self,context):
    mod = None
    if not addon_name:
        addon_name = "io_export_VertexGroups"
    else:
        addon_name = addon_name
        
    '''
    for mod in addon_utils.modules():
        print(mod)
    #'''    
        
    #'''
    if addon_name not in addon_utils.addons_fake_modules:
        print("%s: Addon not isntalled." % addon_name)
        
    else:
        default, state = addon_utils.check(addon_name)
        if not state:
            try:
                mod = addon_utils.enable(addon_name, default_set = False, persistent = False)
            except:
                print("%s: Could not enable Addon on the fly." % addon_name)
        else: 
            print("%s: enabled and running." % addon_name)
        
    #'''  
# ----------------------------------------------------------------------------#
 
def export_objBatch(filepath, sim_type, amount, export_name):
    if amount == 1:
        if sim_type == 'ArthrosModel':
            bpy.ops.export_scene.obj(filepath=filepath, **ArthrosModel)
        elif sim_type == 'ArthrosGeometry':
            bpy.ops.export_scene.obj(filepath=filepath, **ArthrosGeometry)
        elif sim_type == 'HystsimModel':
            bpy.ops.export_scene.obj(filepath=filepath, **HystsimModel)
        elif sim_type == 'HystsimGeometry':
            bpy.ops.export_scene.obj(filepath=filepath, **HystsimGeometry)
    else:
        filepath = filepath + export_name 
        if sim_type == 'ArthrosModel':
            bpy.ops.export_scene.obj(filepath=filepath, **ArthrosModel)
        elif sim_type == 'ArthrosGeometry':
            bpy.ops.export_scene.obj(filepath=filepath, **ArthrosGeometry)
        elif sim_type == 'HystsimModel':
            bpy.ops.export_scene.obj(filepath=filepath, **HystsimModel)
        elif sim_type == 'HystsimGeometry':
            bpy.ops.export_scene.obj(filepath=filepath, **HystsimGeometry)
    print("Exported type: " + sim_type)


    
# ----------------------------------------------------------------------------#
# menus
# ----------------------------------------------------------------------------#
def arthros_content(self, context):
    # single selected
    if len(bpy.context.selected_objects) == 1:
        export_name = bpy.context.active_object.name
        self.layout.operator(ArthrosModelExport.bl_idname,
                             text="Model (.obj) - single object").filepath = export_name
        self.layout.operator(ArthrosGeometryExport.bl_idname,
                             text="Geometry (.obj) - single object").filepath = export_name
    # multiple selected
    elif len(bpy.context.selected_objects) > 1:
        export_name = ""
        self.layout.operator(ArthrosModelExport.bl_idname,
                             text="Model (.obj) - multiple objects").filepath = export_name
        self.layout.operator(ArthrosGeometryExport.bl_idname,
                             text="Geometry (.obj) - multiple objects").filepath = export_name

# ----------------------------------------------------------------------------#

def hystsim_content(self, context):
    # single selected
    if len(bpy.context.selected_objects) == 1:
        export_name = bpy.context.active_object.name
        self.layout.operator(HystsimModelExport.bl_idname,
                             text="Model (.obj) - single object").filepath = export_name
        self.layout.operator(HystsimGeometryExport.bl_idname,
                             text="Geometry (.obj) - single object").filepath = export_name
    # multiple selected
    elif len(bpy.context.selected_objects) > 1:
        export_name = ""
        self.layout.operator(HystsimModelExport.bl_idname,
                             text="Model (.obj) - multiple objects").filepath = export_name
        self.layout.operator(HystsimGeometryExport.bl_idname,
                             text="Geometry (.obj) - multiple objects").filepath = export_name
    # layout.operator(OBJECT_MT_popup.bl_idname, text = "test error" )
# ----------------------------------------------------------------------------#

class VIEW3D_MT_Popup(bpy.types.Menu):
    bl_label = "error popup"
    bl_idname = "OBJECT_MT_popup"
    
    def draw(self, context):
        self.layout.operator_context = 'INVOKE_REGION_WIN'


# ----------------------------------------------------------------------------#
# export
# ----------------------------------------------------------------------------#
default_path = 'STRIP'

class ArthrosModelExport(bpy.types.Operator, ExportHelper):
    '''Export with material and uv'''
    bl_idname = "export.objbatch_model_arthros"
    bl_label = "Export modelObj_arthros"
    bl_options = {'PRESET'}
    
    filename_ext = filename_ext    
    filter_glob = StringProperty(
                                default="*.obj;*.mtl",
                                options={'HIDDEN'},
                                )
    
    path_reference_mode[1]['default'] = default_path
    path_mode = path_reference_mode
    check_extension = True
    
    filepath = StringProperty(
                              name="File Path",
                              description="filepath",
                              default="", maxlen=1024,
                              options={'ANIMATABLE'},
                              subtype='NONE'
                              )
    
    # switch menu entry for single and multiple selections
    def execute(self, context):
        keywords = self.as_keywords()
        ArthrosModel['path_mode'] = keywords['path_mode']
        
        # single selected
        if len(bpy.context.selected_objects) == 1:
            file = self.properties.filepath
            save_objBatch(file, 1, 'ArthrosModel')              
            return {'FINISHED'}
        
        # multiple selected
        elif len(bpy.context.selected_objects) > 1: 
            # we might have a problem here when exporting multiple objects with the new filepath?             
            file = self.properties.filepath
            print(file)        
            save_objBatch(self.properties.filepath, 2, 'ArthrosModel')
            return {'FINISHED'}
    
    # open the filemanager
    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self) 
        return {'RUNNING_MODAL'}
    
    
# ----------------------------------------------------------------------------#

class ArthrosGeometryExport(bpy.types.Operator, ExportHelper):
    '''Export without material or uv'''
    bl_idname = "export.objbatch_geometry_arthros"
    bl_label = "Export geometryObj_arthros"
    bl_options = {'PRESET'}
    
    filename_ext = filename_ext  
    filter_glob = StringProperty(
                                default="*.obj;*.mtl",
                                options={'HIDDEN'},
                                )
    
    path_reference_mode[1]['default'] = default_path
    path_mode = path_reference_mode
    check_extension = True
    
    filepath = StringProperty(
                              name="File Path",
                              description="filepath",
                              default="",
                              maxlen=1024,
                              options={'ANIMATABLE'},
                              subtype='NONE'
                              )

    # switch menu entry for single and multiple selections
    def execute(self, context):
        keywords = self.as_keywords()
        ArthrosGeometry['path_mode'] = keywords['path_mode']
        
        # single selected
        if len(bpy.context.selected_objects) == 1:
            file = self.properties.filepath
            save_objBatch(file, 1, 'ArthrosGeometry')       
            return {'FINISHED'}
        
        # multiple selected
        elif len(bpy.context.selected_objects) > 1:
            save_objBatch(self.properties.filepath, 2, 'ArthrosGeometry')
            return {'FINISHED'}

    # open the filemanager
    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

# ----------------------------------------------------------------------------#

class HystsimModelExport(bpy.types.Operator, ExportHelper):
    '''Export with material and uv'''
    bl_idname = "export.objbatch_model_hystsim"
    bl_label = "Export modelObj_hystsim"
    bl_options = {'PRESET'}
    
    filename_ext = filename_ext  
    filter_glob = StringProperty(
                                default="*.obj;*.mtl",
                                options={'HIDDEN'},
                                )
    
    path_reference_mode[1]['default'] = default_path
    path_mode = path_reference_mode
    check_extension = True
    
    filepath = StringProperty(
                              name="File Path", 
                              description="filepath", 
                              default="", 
                              maxlen=1024, 
                              options={'ANIMATABLE'}, 
                              subtype='NONE')

    # switch menu entry for single and multiple selections
    def execute(self, context):
        keywords = self.as_keywords()
        HystsimModel['path_mode'] = keywords['path_mode']
        
        # single selected
        if len(bpy.context.selected_objects) == 1:
            file = self.properties.filepath
            save_objBatch(file, 1, 'HystsimModel')      
            return {'FINISHED'}
        
        # multiple selected
        elif len(bpy.context.selected_objects) > 1:
            save_objBatch(self.properties.filepath, 2, 'HystsimModel')
            return {'FINISHED'}
        

    # open the filemanager
    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        # self.path_reference_mode[mode] = 'COPY'
        return {'RUNNING_MODAL'}

    

# ----------------------------------------------------------------------------#

class HystsimGeometryExport(bpy.types.Operator, ExportHelper):
    '''Export without material or uv'''
    bl_idname = "export.objbatch_geometry_hystsim"
    bl_label = "Export geometryObj_hystsim"
    bl_options = {'PRESET'}
    
    filename_ext = filename_ext  
    filter_glob = StringProperty(
                                default="*.obj;*.mtl",
                                options={'HIDDEN'},
                                )
    
    path_reference_mode[1]['default'] = default_path
    path_mode = path_reference_mode
    check_extension = True
    
    filepath = StringProperty(
                              name="File Path", 
                              description="filepath", 
                              default="", 
                              maxlen=1024, 
                              options={'ANIMATABLE'}, 
                              subtype='NONE')
    
    # switch menu entry for single and multiple selections
    def execute(self, context):
        keywords = self.as_keywords()
        HystsimGeometry['path_mode'] = keywords['path_mode']
        
        # single selected
        if len(bpy.context.selected_objects) == 1:
            file = self.properties.filepath     
            save_objBatch(file, 1, 'HystsimGeometry')
            return {'FINISHED'}
        
        # multiple selected
        elif len(bpy.context.selected_objects) > 1:
            save_objBatch(self.properties.filepath, 2, 'HystsimGeometry')
            return {'FINISHED'}

    # open the filemanager
    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}


# ----------------------------------------------------------------------------#


    
def register():
    bpy.utils.register_module(__name__)
    # checking if Export_Menu is in bpy.types would work
    # bpy.types.INFO_MT_file_export.append(Export_Menu)
    bpy.types.OBJECT_MT_arthros.append(arthros_content)
    bpy.types.OBJECT_MT_hystsim.append(hystsim_content)

def unregister():
    bpy.utils.unregister_module(__name__)
    # bpy.types.INFO_MT_file_export.remove(Export_Menu)
    bpy.types.OBJECT_MT_arthros.remove(arthros_content)
    bpy.types.OBJECT_MT_hystsim.remove(hystsim_content)

if __name__ == "__main__":
    register()

print(80 * "-")
