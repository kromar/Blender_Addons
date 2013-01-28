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
    - adjust export orientations for each sim
    - 
    
problems:
    - only works on quad meshes
        - way to check first if a mesh contains quads? 
        - might not be needed since its only supposed to export imported tetmeshes
       
    
changelog:
    "version": 1.0.0
        -initial release
        
    "version": 1.0.1
        -added modifier deformation
        -fixed multi object export export
        -fixed rotation
    
    "version": 1.0.2
        - fixed export orientation
        
    "version": 1.0.3
        - cleaned up save and export function
        
    "version": 1.0.4
        - added sim specific exports
        - added check for MESH
        - added check for active
        - added to sim submenus
        - adjsuted export orientation
        - changed face.vertices to face.vertices_raw so it will export triangulated faces with a 0 array entry
        -
        
    "version": 1.1.0
        - updated to bmesh
        - new export method; strip face list into facetes to imitate tetrahedra
''' 

# ----------------------------------------------------------------------------#

import bpy
import bmesh
import os
from bpy.props import *

#addon description
bl_info = {
    "name": "Export: TetMesh",
    "author": "Daniel Grauer",
    "version": (1, 1, 0),
    "blender": (2, 6, 3),
    "category": "Import-Export",
    "location": "File > Export > TetMesh",
    "description": "export meshes to TET file format for TetraMaker (c) AGEIA (.tet)",
    "warning": '', # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": ""
    }

print(" ")
print("*------------------------------------------------------------------------------*")
print("*                          initializing TetMesh export                         *")
print(" ")

debug = True
def logger(msg, *args):
    if debug == True:
        print(str(msg) + str(*args))

    
def save_TetMesh(filepath, amount, sim_type):
    selected = bpy.context.selected_objects
    #process selected objects
    for object in selected:
        if bpy.context.active_object:
            if object.type == 'MESH':
                
                #toggle OBJECT mode
                bpy.ops.object.mode_set(mode = 'OBJECT', toggle = False)
                
                object_name = object.name
                export_name = object.name + ".tet"   #change default name to file name
                
                export_TetMesh(object_name, filepath, sim_type, amount, export_name)
                           
            else:
                print(object.name + "is not a 'MESH' object")
        else:
            print("No active object")         
                    
# ----------------------------------------------------------------------------#

def export_TetMesh(object_name, filepath, sim_type, amount, export_name):
    
    if amount == 1:
        if sim_type == 'Arthros':
            process_mesh(object_name, filepath, sim_type, export_name)
        elif sim_type == 'Hystsim':
            process_mesh(object_name, filepath, sim_type, export_name)
    
    else:
        filepath = filepath + export_name
        if sim_type == 'Arthros':
            process_mesh(object_name, filepath, sim_type, export_name)
        elif sim_type == 'Hystsim':
            process_mesh(object_name, filepath, sim_type, export_name)

# ----------------------------------------------------------------------------#

def process_mesh(object_name, filepath, sim_type, export_name):
    
    object = bpy.data.objects[object_name]    
    
    #create proxy mesh to apply modifiers for export
    mesh = object.to_mesh(bpy.context.scene, True, 'PREVIEW')
    bm = bmesh.new()
    bm.from_mesh(mesh)
        
    vertCount = len(bm.verts[:])
    faceCount = len(bm.faces[:])

    # get the verts and faces and export to file
    file = open(filepath, 'w')
    print("Saving file to:", filepath)
    
    file.write("# Tetrahedral mesh generated using TetraMaker (c) AGEIA" + "\n" + "\n")
    file.write("# " + str(vertCount) + " vertices " + "\n")
    
    #new stuff for local/global coordinates? 
    #bpy.ops.object.add(type='EMPTY', location=bpy.context.object.data.vertices[0].co*bpy.context.object.matrix_world, rotation=(0, 0, 0))
    #vertex.co*object.matrix_world
    #vertex.co*object.matrix_local
        
    #get vertex locations
    for vert in bm.verts:
        vx, vy, vz = vert.co[0], vert.co[1], vert.co[2]
        
        #get origin location
        px, py, pz = object.location[0], object.location[1], object.location[2]
        #new location
        ox, oy, oz = px + vx, py + vy, pz + vz
        #print ("pivotX: ", vx)
        #print (ox, oz, -oy)
        
        if sim_type == 'Arthros':
            file.write("v " + str(ox) + " " + str(oy) + " " + str(oz) + "\n")
        
        elif sim_type == 'Hystsim':
            file.write("v " + str(ox) + " " + str(oz) + " " + str(-oy) + "\n")  

    
   
    realtets = False
    
    for face in bm.faces:  
        if len(face.verts) == 3:
            realtets = True
            break
        else: 
            realtets = False
            break
         
    
    if realtets == True:
        print("*-------------------------------------------------*")  
        print('   3 verts, using facet collection to export')
        
        file.write("\n" + "# " + str(int(faceCount * 0.25)) + " tetrahedra" + "\n")
        print(str(int(faceCount * 0.25)) + " tetrahedra")
        createFacets(file, mesh)
    else:
        print("*-------------------------------------------------*")  
        print('   n verts, using traditional method')
        
        file.write("\n" + "# " + str(int(faceCount)) + " tetrahedra" + "\n")
        print(str(int(faceCount)) + " tetrahedra")
        for face in bm.faces: 
            file.write("t " + str(face.verts[0].index) + " " + str(face.verts[1].index) + " " + str(face.verts[2].index) + " " + str(face.verts[3].index) + "\n")
    
    file.close() 
           
    print(export_name + " EXPORTED ")
    print("Exported type: " + sim_type)
    print("*-------------------------------------------------*")   
 
 
   

# ----------------------------------------------------------------------------#   
#    tetrahedra collection
# ----------------------------------------------------------------------------#

def createFacets(file, mesh):
    
    faces = len(mesh.polygons)
    print('faces:', faces, 'tets:', int(faces*0.25))
    
    tets =[]
    collection =[]
    faceindex = 0
    count = 0
    startcount = 0
    endcount = 4
    
    
    while count < endcount: 
        for poly in mesh.polygons:
            faceindex=poly.index
            
            if faceindex in range(startcount, endcount):
                print('poly index:', faceindex, 'range:', startcount, endcount)  
                
                for vert in poly.vertices:
                    print('vert:', ':', vert)
                    collection.append(vert)
                
                count += 1
             
            if count == endcount:
                print('collection:', collection)
                print('unified:', unifyList(collection))
                
                #print("t " + str(unifyList(collection)[0]) + " " + str(unifyList(collection)[1]) + " " + str(unifyList(collection)[2]) + " " + str(unifyList(collection)[3]))
                file.write("t " + str(unifyList(collection)[0]) + " " + str(unifyList(collection)[1]) + " " + str(unifyList(collection)[2]) + " " + str(unifyList(collection)[3]) + "\n")
               
                #here we need to increase the counters, reset the list and return to the loop
                if endcount < faces:
                    startcount += 4
                    endcount += 4
                    collection =[]
                    
                    print('---------------------next tet -------------------')
                else:
                    print('no faces left')
                    
                 
#lets append all the indices to the facet list
def unifyList(*args):
    facet = []
    for i in args:
        #print('i: ', i)
        for e in i:
            #print('e: ', e)
            if not e in facet:
                facet.append(e)
            else:
                pass
                #print(e, ": already exists, skip")

    return facet


# ----------------------------------------------------------------------------#   
#    export
# ----------------------------------------------------------------------------#

class ArthrosTetMeshExporter(bpy.types.Operator):
    '''Export TetMesh'''
    bl_idname = "mesh.export_tetmesh_arthros"
    bl_label = "Export TetMesh_arthros"

    filepath = StringProperty(name="File Path", description="filepath", default="", maxlen=1024, options={'ANIMATABLE'}, subtype='NONE')
    
    #switch menu entry for single and multiple selections
    def execute(self, context):
        #single selected
        if len(bpy.context.selected_objects) == 1:
            save_TetMesh(self.properties.filepath, 1, 'Arthros')
            return {'FINISHED'}    
        
        #multiple selected
        elif len(bpy.context.selected_objects) > 1:
            save_TetMesh(self.properties.filepath, 2, 'Arthros')
            return {'FINISHED'}
        
    #open the filemanager    
    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

# ----------------------------------------------------------------------------#

class HystsimTetMeshExporter(bpy.types.Operator):
    '''Export TetMesh'''
    bl_idname = "mesh.export_tetmesh_hystsim"
    bl_label = "Export TetMesh_hystsim"

    filepath = StringProperty(name="File Path", description="filepath", default="", maxlen=1024, options={'ANIMATABLE'}, subtype='NONE')
    
    #switch menu entry for single and multiple selections
    def execute(self, context):
        #single selected
        if len(bpy.context.selected_objects) == 1:
            save_TetMesh(self.properties.filepath, 1, 'Hystsim')
            return {'FINISHED'}    
        
        #multiple selected
        elif len(bpy.context.selected_objects) > 1:
            save_TetMesh(self.properties.filepath, 2, 'Hystsim')
            return {'FINISHED'}
        
    #open the filemanager    
    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

# ----------------------------------------------------------------------------#
#    menus
# ----------------------------------------------------------------------------#
'''
def Export_Menu(self, context):
    layout = self.layout
    
    #try to generate menu with our menu class 
    layout.menu(Export_Menu_Arthros.bl_idname, text = "Arthros")
    layout.menu(Export_Menu_HystSim.bl_idname, text = "Hystsim")
      
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
    
#dropdown menu
def arthros_content(self, context):
    layout = self.layout
    
    #single selected
    if len(bpy.context.selected_objects) == 1:
        export_name = bpy.context.active_object.name + ".tet"
        layout.operator(ArthrosTetMeshExporter.bl_idname, text="TetMesh (.tet) - single object").filepath = export_name
    
    #multiple selected
    elif len(bpy.context.selected_objects) > 1:
        export_name = "" 
        layout.operator(ArthrosTetMeshExporter.bl_idname, text="TetMesh (.tet) - multiple objects").filepath = export_name
        
# ----------------------------------------------------------------------------#

def hystsim_content(self, context):
    layout = self.layout
    
    #single selected
    if len(bpy.context.selected_objects) == 1:
        export_name = bpy.context.active_object.name + ".tet"
        layout.operator(HystsimTetMeshExporter.bl_idname, text="TetMesh (.tet) - single object").filepath = export_name
    
    #multiple selected
    elif len(bpy.context.selected_objects) > 1:
        export_name = "" 
        layout.operator(HystsimTetMeshExporter.bl_idname, text="TetMesh (.tet) - multiple objects").filepath = export_name
   

# ----------------------------------------------------------------------------#     
        
def register():
    bpy.utils.register_module(__name__)
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
