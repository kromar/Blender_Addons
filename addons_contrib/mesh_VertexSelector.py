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

"""
todo:
    - testing

changelog:
    "version": (1,1,0)
        - added option to toggle indices in viewport; enables debug mode
    
    "version": (1,0,0)
        - first version
""" 

# ----------------------------------------------------------------------------#    

import bpy

bl_info = {
    "name": "Vertex Selector",
    "author": "Daniel Grauer (kromar)",
    "version": (1, 1, 0),
    "blender": (2, 6, 3),
    "category": "Mesh",
    "category": "kromar",
    "location": "Properties space > Data > Vertex Selector",
    "description": "select vertices by index numbers",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": ""}

print(" ")
print("*------------------------------------------------------------------------------*")
print("*                          VertexSelector                      *")
print(" ")


def VS_select(indexList):
    #indices = [4608]    #add more indices: [0, 1, 4, 722]
    mesh =  bpy.context.active_object.data    
    bpy.ops.object.mode_set(mode = 'EDIT', toggle = False)
    bpy.ops.mesh.reveal()
    bpy.ops.mesh.select_all(action='DESELECT')    
    bpy.ops.object.mode_set(mode = 'OBJECT', toggle = False)
    
    for vert in mesh.vertices:
        #print(vert.index)
        for target in indexList:
            if vert.index == target:
                vert.select = True
                print(target, ' vertex selected')       
            
    
    bpy.ops.object.mode_set(mode = 'EDIT', toggle = False)

def VS_show_extra_indices(self, context):
    mesh =  bpy.context.active_object.data 
    config = bpy.data.scenes[0].CONFIG_VertexSelector
    print("Show indices: ", config.show_extra_indices)
    
    if config.show_extra_indices == True:
        #enable debug mode, show indices
        #bpy.app.debug  to True while blender is running
        bpy.app.debug = True
        mesh.show_extra_indices = True
    else:
        bpy.app.debug = False
        mesh.show_extra_indices = False
    
    
#======================================================================# 
#         GUI                                                      
#======================================================================#        
class UIElements(bpy.types.PropertyGroup):

    get_indices = bpy.props.StringProperty(name="vertex index:", description="input vertex indices here for selection. example: 1,2,3")
    show_extra_indices = bpy.props.BoolProperty(name="Show selected indices", default=False, description="Display the index numbers of selected vertices, edges, and faces. Note: enables debug mode", update=VS_show_extra_indices)


class OBJECT_PT_VertexSelector(bpy.types.Panel):
    bl_label = "VertexSelector"
    bl_idname = "OBJECT_PT_VertexSelector"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    bl_default_closed = True
    
    def draw(self, context):
    
        config = bpy.data.scenes[0].CONFIG_VertexSelector
        layout = self.layout
        ob = context.object
        type = ob.type.capitalize()
        objects = bpy.context.selected_objects
        game = ob.game
        
        #make sure a object is selected, otherwise hide settings and display warning
        if not objects: 
            row = layout.row()
            row.label(text="No Active Object", icon='ERROR')
            return      
        if type == 'Mesh':
            row = layout.column()            
            row.prop(config, "show_extra_indices")
            row.prop(config, "get_indices")
            row.operator("mesh.vertexselector_select", text="select vertices")

            
class OBJECT_OP_Select(bpy.types.Operator):
    bl_idname = "mesh.vertexselector_select"
    bl_label = "Select"
    bl_description = "select vertices"
            
    def execute(self, context):
        #get arguments from UIElemtnts
        config = bpy.data.scenes[0].CONFIG_VertexSelector
        
        #lets convert the values to int and pass the list to the select function
        indexList=[]
        detectList = config.get_indices.split(',')
        for i in detectList:
            indexList.append(int(i))
            
        #print(indexList)
        VS_select(indexList)
        return {'FINISHED'} 
        


#======================================================================# 
#         register                                                      
#======================================================================#
def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.CONFIG_VertexSelector = bpy.props.PointerProperty(type = UIElements)

    
def unregister():
    bpy.utils.unregister_module(__name__)
    if bpy.context.scene.get('CONFIG_VertexSelector') != None:
        del bpy.context.scene['CONFIG_VertexSelector']
    try:
        del bpy.types.Scene.CONFIG_VertexSelector
    except:
        pass

print(" ")
print("*                             initialized                                      *")
print("*------------------------------------------------------------------------------*")
print(" ")  