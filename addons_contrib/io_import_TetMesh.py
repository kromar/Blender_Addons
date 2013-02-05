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
- mesh is set to cursor, set it to object center to scene center
- multi file import
- filter filemanager for .tet files
- write barycentric coordinates w.r.t. to a list to export them again

changelog:
    "version": 1.0.0
        - basic import is working
    
    "version": 1.0.1
        - fixed import to cursor problem, will import to scene center now
        
    "version": 1.0.2
        - fixed import orientation
        
    "version": 1.0.3
        - edges append to list; faces only use 3 point of array to prevent nonplanar faces
    
    "version": 1.0.4
        - removed "Tet ending for mesh import
''' 

# ----------------------------------------------------------------------------#        
    
import bpy
import os
from bpy.props import *
#from add_utils import AddObjectHelper, add_object_data # adds helper to filemanager

#addon description
bl_info = {
    "name": "Import: TetMesh",
    "author": "Daniel Grauer (kromar)",
    "version": (1, 0, 4),
    "blender": (2, 6, 0),
    "category": "Import-Export",
    "category": "kromar",
    "location": "File > Import > TetMesh",
    "description": "import TET meshes from TetraMaker (c) AGEIA (.tet)",
    "warning": '', # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": ""
    }

print(" ")
print("*------------------------------------------------------------------------------*")
print("*                          TetMesh import                                      *")
print(" ")
        
def import_tetmesh(self, context, filepath, filename):
    #print("filepath: " + filepath)
    #print("filename: " + filename) 
    
    #split filename to rename the new mesh (add_named doesnt work?)
    objname = filename.split('.')[0] #+ "Tet"
    #print("strip name: " + objname)
        
    verts = []
    edges = []
    faces = []
    renderFaces = []

    '''build the mesh'''
    #open file and write lists 
    file = open(filepath, 'r')
    for line in file:
        if (line.startswith("v")):
            coords = line.split()
            vert = [float(coords[1]), -float(coords[3]), float(coords[2])]
            #print(vert)
            verts.append(vert)
            
        if (line.startswith("t")):
            indices = line.split()

            f1 = [int(indices[1]), int(indices[2]), int(indices[3])]
            f2 = [int(indices[1]), int(indices[2]), int(indices[4])]
            f3 = [int(indices[1]), int(indices[3]), int(indices[4])]
            f4 = [int(indices[2]), int(indices[3]), int(indices[4])]
            
            print('facet: ', f1, f2, f3, f4)
            
            renderFaces.append(f1)
            renderFaces.append(f2)
            renderFaces.append(f3)
            renderFaces.append(f4)
            
            '''
            f1 = [int(indices[1]), int(indices[2]), int(indices[3]), int(indices[4])]
            
            print('facet: ', f1)
            faces.append(f1)
            '''
    
    #create new mesh
    mesh = bpy.data.meshes.new(name=objname)          
    
    # create mesh data, do this in Object mode
    mesh.from_pydata(verts, edges, renderFaces)
    #mesh.from_pydata(verts, edges, faces)
    #mesh.validate(verbose = True)
     
    ob = bpy.data.objects.new(objname, mesh) 
    bpy.context.scene.objects.link(ob)

    
    print(mesh.name + " IMPORTED ")
    #print(renderFaces)
    print("*-------------------------------------------------*")
    print(" ")
# ----------------------------------------------------------------------------#        
    
class TetMeshImporter(bpy.types.Operator): #, AddObjectHelper):
    '''Import TetMesh'''
    bl_idname = "mesh.import_tetmesh"
    bl_label = "Import TetMesh"

    filename = StringProperty(name="File Name", description="filename", default="", maxlen=1024, options={'ANIMATABLE'}, subtype='NONE')
    filepath = StringProperty(name="File Path", description="filepath", default="", maxlen=1024, options={'ANIMATABLE'}, subtype='NONE')
    
    def execute(self, context):
        import_tetmesh(self, context, self.properties.filepath, self.properties.filename)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

# ----------------------------------------------------------------------------#        
    
#dropdown menu
def menu_func(self, context):
    #clear the default name for import
    import_name = "" 
    self.layout.operator(TetMeshImporter.bl_idname, text="TetMesh (.tet)").filename = import_name

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_func)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_func)

if __name__ == "__main__":
    register()
    
print(" ")
print("*                             initialized                                      *")
print("*------------------------------------------------------------------------------*")
print(" ")
