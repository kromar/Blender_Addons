# ##### BEGIN GPL LICENSE BLOCK #####
#
#This program is free software; you can redistribute it and/or
#modify it under the terms of the GNU General Public License
#as published by the Free Software Foundation; either version 2
#of the License, or (at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software Foundation,
#Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

#<pep8-80 compliant>


#======================================================================#
#     todo
#======================================================================#

'''
- mesh is set to cursor, set it to object center to scene center
- multi file import
- write barycentric coordinates w.r.t. to a list to export them again

'''


# ----------------------------------------------------------------------------#

import bpy
import os
from bpy.props import *
from bpy_extras.io_utils import (ImportHelper, axis_conversion)

filename_ext = ".tet"

#addon description
bl_info = {
    "name": "Import: TetMesh",
    "author": "Daniel Grauer (kromar)",
    "version": (1, 2, 0),
    "blender": (2, 7, 4),
    "category": "Import-Export",
    "category": "VirtaMed",
    "location": "File > Import > TetMesh",
    "description": "import TET meshes from TetraMaker (c) AGEIA (.tet)",
    "warning": '',    #used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": ""
    }

print(80 * "-")
print("TetMesh import")


def import_tetmesh(self, context, filepath, filename, global_matrix):
    #print("filepath: " + filepath)
    #print("filename: " + filename)
    print(global_matrix)

    #split filename to rename the new mesh (add_named doesnt work?)
    objname = filename.split('.')[0]    #+ "Tet"
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
            vert = [float(coords[1]), float(coords[2]), float(coords[3])]
            #print(vert)
            verts.append(vert)

        if (line.startswith("t")):
            indices = line.split()

            f1 = [int(indices[1]), int(indices[2]), int(indices[3])]
            f2 = [int(indices[1]), int(indices[2]), int(indices[4])]
            f3 = [int(indices[1]), int(indices[3]), int(indices[4])]
            f4 = [int(indices[2]), int(indices[3]), int(indices[4])]

            #print('facet: ', f1, f2, f3, f4)

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
    mesh = bpy.data.meshes.new(name = objname)

    #create mesh data, do this in Object mode
    mesh.from_pydata(verts, edges, renderFaces)
    #mesh.from_pydata(verts, edges, faces)
    #mesh.validate(verbose = True)

    ob = bpy.data.objects.new(objname, mesh)
    bpy.context.scene.objects.link(ob)
    
    # apply rotation matrix to object
    ob.matrix_world = global_matrix
    #apply rotation


    print(mesh.name + " IMPORTED ")
    #print(renderFaces)
    print("*-------------------------------------------------*")
    print(" ")
# ----------------------------------------------------------------------------#

class TetMeshImporter(bpy.types.Operator, ImportHelper):    #, AddObjectHelper):
    '''Import TetMesh'''
    bl_idname = "mesh.import_tetmesh"
    bl_label = "Import TetMesh"
    bl_options =  {'PRESET'}
    
    filename_ext = filename_ext
    filter_glob = StringProperty(default = "*.tet",
                                options = {'HIDDEN'},
                                )
                                    
    filename = StringProperty(name = "File Name",
                                description = "filename",
                                default = "",
                                maxlen = 1024,
                                options = {'ANIMATABLE'},
                                subtype = 'NONE')
    
    filepath = StringProperty(name = "File Path",
                                description = "filepath",
                                default = "",
                                maxlen = 1024,
                                options = {'ANIMATABLE'},
                                subtype = 'NONE')
                                
    axis_forward = EnumProperty( name="Forward",
                                items=(('X', "X Forward", ""),
                                       ('Y', "Y Forward", ""),
                                       ('Z', "Z Forward", ""),
                                       ('-X', "-X Forward", ""),
                                       ('-Y', "-Y Forward", ""),
                                       ('-Z', "-Z Forward", ""),
                                       ),
                                default='Y')
    
    axis_up = EnumProperty(name="Up",
                            items=(('X', "X Up", ""),
                                   ('Y', "Y Up", ""),
                                   ('Z', "Z Up", ""),
                                   ('-X', "-X Up", ""),
                                   ('-Y', "-Y Up", ""),
                                   ('-Z', "-Z Up", ""),
                                   ),
                            default='Z')
                            
    def execute(self, context):         
        global_matrix = axis_conversion(from_forward=self.axis_forward,
                                        from_up=self.axis_up).to_4x4()   
        print(global_matrix)                                
        import_tetmesh(self, context, self.properties.filepath, self.properties.filename, global_matrix)
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
    self.layout.operator(TetMeshImporter.bl_idname, text = "TetMesh (.tet)").filename = import_name

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_func)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_func)

if __name__ == "__main__":
    register()


print("initialized")
print(80 * "-")
