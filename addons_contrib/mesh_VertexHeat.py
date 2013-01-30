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


'''---------------------------
TODO:
    - add distance influence value 
        multiplier so edge length has more impact on weight
    
    - include locked vertices
    
    
# mesuring time
time1 = time.time()
for x in search:
    method1(x)
print(time.time() - time1)



# fastest wipe list:
del l[:]
this is acctually slower than creating a new list on each cycle


---------------------------'''    

import bpy
import bmesh
import time
import mathutils
 
#addon description
bl_info = {
    "name": "Vertex Heat",
    "author": "Daniel Grauer (kromar)",
    "version": (1, 2, 1),
    "blender": (2, 6, 5),
    "category": "Mesh",
    "location": "Properties space > Object Data > Vertex Heat",
    "description": "vertex weight heat diffusion",
    "warning": '', # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "https://github.com/kromar/Blender_Addons/blob/master/addons_contrib/mesh_VertexHeat.py",
}

print(" ")
print("*------------------------------------------------------------------------------*")
print("*                          Vertex Heat                                         *")
print(" ") 

    
activeList = []    
lockedList = []
vertexList = []  

#[0]=index, [1]=weight, [2]=borderverts, [3]=borderDistance
'''---------------------------''' 
def populateLists(ob, mesh):   
    #write distanced and border verts to list
    if not ob.mode == 'EDIT':
        bpy.ops.object.mode_set(mode = 'EDIT', toggle = False)
        print("set to edit mode for bmesh looping")  
        
        
        
    activeVG = ob.vertex_groups.active    
    #add vertices from vertex group in our list
    #'''
    if activeVG.name in ob.vertex_groups:                    
        #check if vertex is in our group  
        for verts in mesh.vertices:                                                     #WE CAN SPEED THIS UP                     
            for v in verts.groups:   #v defines the vertex of a group    
                if v.group == activeVG.index:
                    #print("locked vert: ", verts.index)
                    vertexList.append([[verts.index],[v.weight]])           #[0]=index, [1]=weight
                    lockedList.append(verts.index)
    #print("locked verts:", lockedList)              
    #'''

    #add all vertices to our list that are not in the vertex group with weight 0.0
    for verts in mesh.vertices:  
        #print(lockedList)      
        if not verts.index in lockedList:  
            #print("unlocked:", verts.index)          
            vertexList.append([[verts.index], [0.0]])                       #[0]=index, [1]=weight
    vertexList.sort()
    
    bm = bmesh.from_edit_mesh(mesh)        
    
    for bmvert in bm.verts:    
        borderVerts = []  
        borderDistance = []        
        sumDistance = 0
        #add neighbours and distances to vertex list as sublist of vertex
        for edge in bmvert.link_edges:
            vertex = edge.other_vert(bmvert)         
            vec = mathutils.Vector(bmvert.co - vertex.co)   
            vDistance = vec.length 
            sumDistance = sumDistance + (1/vDistance)
            borderVerts.append(vertex.index)                  
            borderDistance.append(1/vDistance)                
        
        i=0
        for distance in borderDistance:   
            influence = 1 / distance * len(borderVerts)
            borderDistance[i] = distance / sumDistance   
            print(distance, influence)
            i = i + 1  
        
        vertexList[bmvert.index].append(borderVerts)            #[2]=borderverts
        vertexList[bmvert.index].append(borderDistance)         #[3]=borderDistance  
       
    
    '''
    
    #copy to active list and remove locked entries    
    print("activeList:", activeList)
    for i in vertexList:
        activeList.append(i)
   
    for v in activeList:
        #print(v)    
        if v[0][0] in lockedList:
            del activeList[v[0][0]]
            
    print("list after removal: ", len(lockedList), len(vertexList), len(activeList))
    '''
        
   
'''---------------------------'''              
def VertexHeat(ob, mesh):  
    for v in vertexList:
        vIndex = v[0][0]
        avgWeight = 0          
        if not vIndex in lockedList:        ##this causes lsow down when lockedList gets to big
            i = 0
            for distance in v[3]:
                weight = vertexList[v[2][i]][1][0]
                avgWeight = avgWeight + distance * weight
                i = i + 1
            #activeList[vIndex][1][0] = avgWeight 
            vertexList[vIndex][1][0] = avgWeight
            
            

'''---------------------------''' 
def assignVertexWeights(ob, mesh):   
    bpy.ops.object.mode_set(mode = 'OBJECT', toggle = False)   
    vg = ob.vertex_groups.new(name="Heat")        
    for i in vertexList:
        vg.add(i[0], i[1][0], 'ADD')   # LIST, weight, arg    
    bpy.ops.object.mode_set(mode = 'WEIGHT_PAINT', toggle = False)
   
               

'''---------------------------''' 
def computeHeat(iterations):
           
    timeCompute = time.time() 
    del vertexList[:]
    del lockedList[:]
    del activeList[:]
         
    ob = bpy.context.object
    mesh = ob.data        
    scene = bpy.context.scene      
    apply_modifiers = True  
    
    #compute weights
    i = 0
    max = iterations
    populateLists(ob, mesh) 
    
    for i in range(max):            
        time0 = time.time()
        print("iterration:", i)       
        VertexHeat(ob, mesh)
        print("iteration time:", time.time() - time0)                     
        print("------------------------------------") 
        
        if i == max-1:
            assignVertexWeights(ob, mesh)
            pass
        i = i + 1   
        
    print("timeCompute:", time.time() - timeCompute)       

        
#======================================================================# 
#         GUI                                                      
#======================================================================#     


def objectApplyModifiers(scene, ob, apply_modifiers):  
    mesh = ob.data
    for modifier in ob.modifiers:
        #we only want visible modifiers to be processed
        if modifier.show_viewport==True:
            print("detected modifiers, will apply before exporting")
            print(modifier.type, "modifier: ", modifier.show_viewport)           
            mesh = ob.to_mesh(scene, apply_modifiers, 'RENDER')       
            #mesh = ob.to_mesh(scene, apply_modifiers, 'PREVIEW')
            print(mesh)        
    return mesh  

#mesh = objectApplyModifiers(scene, ob, apply_modifiers)


'''---------------------------'''  
def selectedVG(self, context):
    mesh =  bpy.context.active_object.data 
    config = bpy.data.scenes[0].CONFIG_VertexHeat
    print("selected group: ", config.selected_group)
   
    if config.selected_group == True:
        mesh.selected_group = True
    else:
        mesh.selected_group = False

    
'''---------------------------'''  
def enableModifiers(self, context):
    mesh =  bpy.context.active_object.data 
    config = bpy.data.scenes[0].CONFIG_VertexHeat
    print("modifier enabled: ", config.modifiers_enabled)
    
    #enable debug mode, show indices
    #bpy.app.debug  to True while blender is running
    if config.modifiers_enabled == True:
        mesh.modifiers_enabled = True
    else:
        mesh.modifiers_enabled = False        
    return mesh
        
'''---------------------------'''  
def vertexDistance(self, context):
    mesh =  bpy.context.active_object.data 
    config = bpy.data.scenes[0].CONFIG_VertexHeat
    print("vertexDistance enabled: ", config.vertex_distance)
    
    #enable debug mode, show indices
    #bpy.app.debug  to True while blender is running
    if config.vertex_distance == True:
        mesh.vertex_distance = True
    else:
        mesh.vertex_distance = False  
     
'''---------------------------'''    
class UIElements(bpy.types.PropertyGroup):
    modifiers_enabled = bpy.props.BoolProperty(name="enable modifiers", default=False, description="apply modifiers before calculating weights", update= enableModifiers)
    selected_group = bpy.props.BoolProperty(name="selected VG only", default=True, description="only calculate weights from selected vertex group", update= selectedVG)
    vertex_distance = bpy.props.BoolProperty(name="vertex distance", default=False, description="take vertex distance into heat calculation", update= vertexDistance)
    
    #slider_multiplier = bpy.props.IntProperty(name="weight multiplier", subtype='FACTOR', min=-1, max=1, default=1, step=0.1, description="multiplier")
    slider_iterations = bpy.props.IntProperty(name="Iterations", subtype='FACTOR', min=1, max=100000, default=10, step=1, description="iterations")
    slider_min = bpy.props.FloatProperty(name="min", subtype='FACTOR', min=0.0, max=1.0, default=0.0, step=0.01, description="min")
    slider_max = bpy.props.FloatProperty(name="max", subtype='FACTOR', min=0.0, max=1.0, default=1.0, step=0.01, description="max")


'''---------------------------'''    
class OBJECT_PT_VertexHeat(bpy.types.Panel):
    bl_label = "VertexHeat"
    bl_idname = "OBJECT_PT_VertexHeat"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    bl_default_closed = True
    
    def draw(self, context):        
        config = bpy.data.scenes[0].CONFIG_VertexHeat
        layout = self.layout  
        ob = context.object  
        activeVG = ob.vertex_groups.active 
        objects = bpy.context.selected_objects 
        type = ob.type.capitalize()       
        
        #make sure a object is selected, otherwise hide settings and display warning
        if not objects: 
            row = layout.row()
            row.label(text="No Active Object", icon='ERROR')
            return      
        if type == 'Mesh':  
            if activeVG:      
                row = layout.row()
                row.label(text="Active Vertex Group: " + str(activeVG.name), icon='GROUP_VCOL')
                        
                col = layout.column()     
                col.prop(config, "vertex_distance")                
                #col.prop(config, "modifiers_enabled")
                #col.prop(config, "selected_group") 
                
                '''
                row = layout.row() 
                row.prop(config, "slider_min")   
                row.prop(config, "slider_max")  
                '''
                
                col = layout.column()
                #col.prop(config, "slider_multiplier")  
                col.prop(config, "slider_iterations")   
                    
                row = layout.row() 
                row.operator("mesh.compute_weights", text="Calculate")
            else:
                row = layout.row()
                row.label(text="No Active Vertex Group", icon='ERROR')
                

'''---------------------------'''       
class OBJECT_OP_HeatCompute(bpy.types.Operator):    
    bl_idname = "mesh.compute_weights"
    bl_label = "compute weights"
    bl_description = "compute weights"
    
        
    def execute(self, context):
        #get arguments from UIElemtnts
        config = bpy.data.scenes[0].CONFIG_VertexHeat
        iterations = config.slider_iterations          
        computeHeat(iterations)            
        return {'FINISHED'} 
        
        
        

#======================================================================# 
#         register                                                      
#======================================================================#
def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.CONFIG_VertexHeat = bpy.props.PointerProperty(type = UIElements)

    
def unregister():
    bpy.utils.unregister_module(__name__)

    if bpy.context.scene.get('CONFIG_VertexHeat') != None:
        del bpy.context.scene['CONFIG_VertexHeat']
    try:
        del bpy.types.Scene.CONFIG_VertexHeat
    except:
        pass 
        

print(" ")
print("*                             initialized                                      *")
print("*------------------------------------------------------------------------------*")
print(" ") 
    