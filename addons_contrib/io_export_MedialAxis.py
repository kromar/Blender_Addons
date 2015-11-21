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

'''
todo:
    - separate export orientations for each sim
    - include in new expor menu structure
'''

# ----------------------------------------------------------------------------#

import bpy
import os
from bpy.props import *
from xml.dom.minidom import Document

# addon description
bl_info = {
    "name": "Export: MedialAxis",
    "author": "Daniel Grauer (kromar)",
    "version": (1, 0, 4),
    "blender": (2, 6, 0),
    "category": "Import-Export",
    "category": "VirtaMed",
    "location": "File > Export > MedialAxis",
    "description": "export medial axis (.xml)",
    "warning": '',    # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": ""
    }

print(80 * "-")
print("initializing MedialAxis export")

def save_MedialAxis(filepath, amount, sim_type):
    selected_objects = bpy.context.selected_objects
    for object in selected_objects:
        if bpy.context.active_object:
            if object.type == 'MESH':

                # toggle OBJECT mode
                if bpy.ops.object.mode_set.poll():
                    bpy.ops.object.mode_set(mode = 'OBJECT', toggle = False)

                object_name = object.name
                export_name = object.name + ".xml"    # change default name to file name

                export_MedialAxis(object_name, filepath, sim_type, amount, export_name)

            else:
                print(object.name + "is not a 'MESH' object")
        else:
            print("No active object")

# ----------------------------------------------------------------------------#

def export_MedialAxis(object_name, filepath, sim_type, amount, export_name):
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
    # create document structure
    doc = Document()

    rootElement = doc.createElement("virtamed")
    doc.appendChild(rootElement)

    PathElem = doc.createElement("MedialAxis")
    rootElement.appendChild(PathElem)

    VertList = doc.createElement("Vertices")
    PathElem.appendChild(VertList)

    EdgeList = doc.createElement("Edges")
    PathElem.appendChild(EdgeList)

    object = bpy.data.objects[object_name]

    # create proxy mesh to apply modifiers for export
    mesh = object.to_mesh(bpy.context.scene,
                          apply_modifiers = True,
                          settings = 'RENDER',
                          calc_tessface = True,
                          calc_undeformed = False)


    # get vertex coordinates
    for vert in mesh.vertices:
        VertListElem = doc.createElement("Vertex")
        VertList.appendChild(VertListElem)
        vx, vy, vz = vert.co[0], vert.co[1], vert.co[2]
        VertListElem.setAttribute("index", repr(vert.index))

        # get originvector
        px, py, pz = object.location[0], object.location[1], object.location[2]
        ox, oy, oz = vx + px, vy + py, vz + pz

        # create xml output
        if sim_type == 'Arthros':
            VertListElem.setAttribute("x", repr(ox))
            VertListElem.setAttribute("y", repr(oy))
            VertListElem.setAttribute("z", repr(oz))

        elif sim_type == 'Hystsim':
            VertListElem.setAttribute("x", repr(ox))
            VertListElem.setAttribute("y", repr(oz))
            VertListElem.setAttribute("z", repr(-oy))

    VertList.appendChild(VertListElem)

    # write the edge key list

    for edge in mesh.edges:
        # create a new entry for every edge index
        EdgeListElem = doc.createElement("Edge")
        EdgeList.appendChild(EdgeListElem)
        EdgeListElem.setAttribute("index", repr(edge.index))

        # seperate keys
        k1, k2 = edge.key[0], edge.key[1]
        EdgeListElem.setAttribute("k1", repr(k1))
        EdgeListElem.setAttribute("k2", repr(k2))

    EdgeList.appendChild(EdgeListElem)


    # write vertex groups
    for Vgroup in object.vertex_groups:
        print("LabelName: ", Vgroup.name, Vgroup.index)

        vertGroup = doc.createElement(Vgroup.name)
        vertGroup.setAttribute("index", repr(Vgroup.index))
        PathElem.appendChild(vertGroup)

    print(doc.toprettyxml(indent = "   "))

    f = open(filepath, 'w')
    print("Saving file to:", filepath)
    f.write(doc.toprettyxml(indent = "   "))
    f.close()

    print(export_name + " EXPORTED ")
    print("*-------------------------------------------------*")
    print(" ")

# ----------------------------------------------------------------------------#
# export
# ----------------------------------------------------------------------------#

class ArthrosMedialAxisExporter(bpy.types.Operator):
    '''Export MedialAxis'''
    bl_idname = "mesh.export_medialaxis_arthros"
    bl_label = "Export MedialAxis_arthros"

    filepath = StringProperty(name = "File Path", description = "filepath", default = "", maxlen = 1024, options = {'ANIMATABLE'}, subtype = 'NONE')

    # switch menu entry for single and multiple selections
    def execute(self, context):
        # single selected
        if len(bpy.context.selected_objects) == 1:
            save_MedialAxis(self.properties.filepath, 1, 'Arthros')
            return {'FINISHED'}

        # multiple selected
        elif len(bpy.context.selected_objects) > 1:
            save_MedialAxis(self.properties.filepath, 2, 'Arthros')
            return {'FINISHED'}

    # open the filemanager
    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

# ----------------------------------------------------------------------------#

class HystsimMedialAxisExporter(bpy.types.Operator):
    '''Export MedialAxis'''
    bl_idname = "mesh.export_medialaxis_hystsim"
    bl_label = "Export MedialAxis_hystsim"

    filepath = StringProperty(name = "File Path", description = "filepath", default = "", maxlen = 1024, options = {'ANIMATABLE'}, subtype = 'NONE')

    # switch menu entry for single and multiple selections
    def execute(self, context):
        # single selected
        if len(bpy.context.selected_objects) == 1:
            save_MedialAxis(self.properties.filepath, 1, 'Hystsim')
            return {'FINISHED'}

        # multiple selected
        elif len(bpy.context.selected_objects) > 1:
            save_MedialAxis(self.properties.filepath, 2, 'Hystsim')
            return {'FINISHED'}

    # open the filemanager
    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

# ----------------------------------------------------------------------------#
# menus
# ----------------------------------------------------------------------------#

# this draws the new menu in FILE>EXPORT

def Export_Menu(self, context):
    bl_label = "export menu"
    bl_idname = "OBJECT_MT_menu"

    # create new content
    self.layout.menu(Export_Menu_Arthros.bl_idname, text = "Arthros")
    self.layout.menu(Export_Menu_HystSim.bl_idname, text = "Hystsim")

# draw content in export menus
class Export_Menu_Arthros(bpy.types.Menu):
    bl_label = "Arthros"
    bl_idname = "OBJECT_MT_arthros"

    def draw(self, context):
        pass

# draw content in export menus
class Export_Menu_HystSim(bpy.types.Menu):
    bl_label = "Hystsim"
    bl_idname = "OBJECT_MT_hystsim"

    def draw(self, context):
        pass

# ----------------------------------------------------------------------------#

# dropdown menu
def arthros_content(self, context):

    # single selected
    if len(bpy.context.selected_objects) == 1:
        export_name = bpy.context.active_object.name + ".xml"
        self.layout.operator(ArthrosMedialAxisExporter.bl_idname, text = "MedialAxis (.xml) - single object").filepath = export_name

    # multiple selected
    elif len(bpy.context.selected_objects) > 1:
        export_name = ""
        self.layout.operator(ArthrosMedialAxisExporter.bl_idname, text = "MedialAxis (.xml) - multiple objects").filepath = export_name

# ----------------------------------------------------------------------------#

def hystsim_content(self, context):

    # single selected
    if len(bpy.context.selected_objects) == 1:
        export_name = bpy.context.active_object.name + ".xml"
        self.layout.operator(HystsimMedialAxisExporter.bl_idname, text = "MedialAxis (.xml) - single object").filepath = export_name

    # multiple selected
    elif len(bpy.context.selected_objects) > 1:
        export_name = ""
        self.layout.operator(HystsimMedialAxisExporter.bl_idname, text = "MedialAxis (.xml) - multiple objects").filepath = export_name

# ----------------------------------------------------------------------------#

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_export.append(Export_Menu)
    bpy.types.OBJECT_MT_arthros.append(arthros_content)
    bpy.types.OBJECT_MT_hystsim.append(hystsim_content)

def unregister():
    bpy.utils.unregister_module(__name__)
    # bpy.types.INFO_MT_file_export.remove(Export_Menu)
    bpy.types.OBJECT_MT_arthros.remove(arthros_content)
    bpy.types.OBJECT_MT_hystsim.remove(hystsim_content)

if __name__ == "__main__":
    register()


print("initialized")
print(80 * "-")
