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
    - add submenu in export list for type exports

bugs:
    - 

changelog:

    
"version": 1.1    
    fixed:         filepath
    added:         folder selection for multiple objects
    changed:     the way that single and multiple objects get handled
    
"version": (1,1,2),
    fixed operator and registration
    changed version #
    
"version": (1,2,0),
    exclude weights that are 0.0
    added vert count to VertexLabel
    
"version": (1,2,1),
    changed bl_info category to "Import-Export"
    
"version": (1,2,2),
    changed bl_info category
    
"version": (1,2,3),
    - fixed multiple export
'''

# ----------------------------------------------------------------------------#

import bpy
from os.path import *
from bpy.props import *
from xml.dom.minidom import Document

#addon description
bl_info = {
    "name": "Export: Vertex Groups",
    "author": "Daniel Grauer",
    "version": (1, 2, 3),
    "blender": (2, 6, 0),
    "category": "Import-Export",
    "category": "kromar",
    "location": "File > Export > Vertex Groups",
    "description": "exports all vertex groups to a xml file",
    "warning": '', # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
}

print(" ")
print("*------------------------------------------------------------------------------*")
print("*                          initializing VertexGroup export                     *")
print(" ")

def save_VertexGroup(filepath, amount):
    selected_objects = bpy.context.selected_objects
    for object in selected_objects:
        object_name = object.name
        export_name = object.name + "Labels.xml"
                   
        export_VertexGroup(object_name, filepath, amount, export_name)     
            
        print(export_name + " EXPORTED ")
        print("*-------------------------------------------------*")
        print(" ")

# ----------------------------------------------------------------------------#
     
#objects can be passed to this function
def export_VertexGroup(object_name, filepath, amount, export_name):
    
    if amount == 1:
        process_mesh(object_name, filepath, export_name)
    else:
        filepath = filepath + export_name
        process_mesh(object_name, filepath, export_name)
    
        
def process_mesh(object_name, filepath, export_name):  
    object = bpy.data.objects[object_name]
    
    #create document structure
    doc = Document()
    rootElement = doc.createElement("Group")
    doc.appendChild(rootElement)
    vertGroupElem = doc.createElement("VertexLabels")
    rootElement.appendChild(vertGroupElem)
    
    #get the groups
    for group in object.vertex_groups:
        print('LabelName:', group.name, group.index)
        
        vertCount = 0
        #exclude names
        ##if (group.name.startswith("Def_") or group.name.startswith("Decal_")):
        ##    continue
        
        #add elements to xml file
        elem = doc.createElement("VertexLabel")
        elem.setAttribute("LabelName", group.name)
                    
        verticesText = ""
        weightText = ""
        #get the verts
        for vert in object.data.vertices:
            #print(vert.index)
            for g in vert.groups:    #vertex groups of vertices
                #print(g.group)
                
                # exclude empty groups
                ## compare vertex group index with group index
                if g.weight > 0.0 and g.group == group.index:
                    verticesText += repr(vert.index) + " "
                    weightText += repr(g.weight) + " "
                    vertCount += 1
        
        if vertCount > 0:
            verticesElem = doc.createElement("Vertices")
            vertTextNode = doc.createTextNode(verticesText)
            verticesElem.appendChild(vertTextNode)
            elem.appendChild(verticesElem)

            weightElem = doc.createElement("Weights")
            weightTextNode = doc.createTextNode(weightText)
            weightElem.appendChild(weightTextNode)
            elem.appendChild(weightElem)
            
        #add new elements
        vertGroupElem.appendChild(elem)
        elem.setAttribute("Count", repr(vertCount))
        
        
        #print(doc.toprettyxml(indent="   "))
        
        f = open(filepath, 'w')
        print("Saving file to:", filepath)
        f.write(doc.toprettyxml(indent="   "))
        f.close()    
# ----------------------------------------------------------------------------#

class VertexGroupExporter(bpy.types.Operator):
    '''Export Vertex Groups'''
    bl_idname = "export.vertexgroup"
    bl_label = "export vertex groups"

    filepath = StringProperty(name="File Path", description="filepath", default="", maxlen=1024, options={'ANIMATABLE'}, subtype='NONE')
    
    def execute(self, context):
        ##save_VertexGroup(self.properties.filepath)
        
        #single selected
        if len(bpy.context.selected_objects) == 1:
            save_VertexGroup(self.properties.filepath, 1)
            return {'FINISHED'}    
            
        #multiple selected
        elif len(bpy.context.selected_objects) > 1:
            save_VertexGroup(self.properties.filepath, 2)
            return {'FINISHED'}
    
    '''
    #this generates options in the export helper
    def draw(self, context):
        layout = self.layout

        layout.operator("wm.open_mainfile")
        layout.operator("wm.save_as_mainfile").copy = True

        layout.operator("object.shade_smooth")

        layout.label(text="Hello world!", icon='WORLD_DATA')

        # use an operator enum property to populate a submenu
        layout.operator_menu_enum("object.select_by_type",
                                  property="type",
                                  text="Select All by Type...",
                                  )
        # call another menu
        layout.operator("wm.call_menu", text="Unwrap").name = "VIEW3D_MT_uv_map"
       '''
        
    #open the filemanager
    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}    

'''
class VertexGroupsTypeMenu(bpy.types.Menu):
    bl_label = "VertexGroups Types Menu"
    bl_idname = "OBJECT_MT_vertex_group_types_menu"

    def draw(self, context):
        layout = self.layout

        layout.operator("wm.open_mainfile")
        layout.operator("wm.save_as_mainfile")
        
    # The menu can also be called from scripts
    #bpy.ops.wm.call_menu(name=SimpleCustomMenu.bl_idname)
'''
   
# ----------------------------------------------------------------------------#
        
#defines the menu button (file>export)
def menu_func(self, context):
    #single selected
    if len(bpy.context.selected_objects) == 1:
        export_name = bpy.context.active_object.name + "Labels.xml"
        #export_name = bpy.context.selected_objects[0].name + "Labels.xml"
        self.layout.operator(VertexGroupExporter.bl_idname, text="Vertex Groups (.xml) - single object").filepath = export_name
    #multiple selected
    elif len(bpy.context.selected_objects) > 1:
        export_name = "" 
        self.layout.operator(VertexGroupExporter.bl_idname, text="Vertex Groups (.xml) - multiple objects").filepath = export_name
    
# ----------------------------------------------------------------------------#
    
def register():
    bpy.utils.register_module(__name__)    
    bpy.types.INFO_MT_file_export.append(menu_func)


def unregister():
    bpy.utils.unregister_module(__name__)    
    bpy.types.INFO_MT_file_export.remove(menu_func)

if __name__ == "__main__":
    register()
    

print(" ")
print("*                             initialized                                      *")
print("*------------------------------------------------------------------------------*")
print(" ")
