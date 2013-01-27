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
    
    - include locked vertices
    - make init on every new group
---------------------------'''  



import bpy
import bmesh
import time
 
#addon description
bl_info = {
    "name": "Average Vertex Weights",
    "author": "Daniel Grauer",
    "version": (1, 0, 0),
    "blender": (2, 6, 5),
    "category": "Mesh",
    "category": "kromar",
    "location": "Properties space > Data > Average Vertex Weights",
    "description": "test",
    "warning": '', # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
}

print(" ")
print("*------------------------------------------------------------------------------*")
print("*                          initializing average vertex weights                 *")
print(" ")
''' 
ob = bpy.context.object
scene = bpy.context.scene  
apply_modifiers = True
'''   
'''---------------------------
# this function can be used to apply after modifiers
---------------------------'''  
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

def selectedVG():
    pass
    
def enableModifiers(self, context):
    mesh =  bpy.context.active_object.data 
    config = bpy.data.scenes[0].CONFIG_AverageWeights
    print("Show indices: ", config.modifiers_enabled)
    
    #enable debug mode, show indices
    #bpy.app.debug  to True while blender is running
    if config.modifiers_enabled == True:
        bpy.app.debug = True
        mesh.modifiers_enabled = True
    else:
        mesh = ob.data
        mesh.modifiers_enabled = False
        
    return mesh
        
        
        
#mesh = objectApplyModifiers(scene, ob, apply_modifiers)
#mesh = ob.data
#activeVG = ob.vertex_groups.active

print("active group: ", activeVG.name, "index: ", activeVG.index)

                
'''---------------------------
# check if vertex is in active group
---------------------------'''  
 
   
def populateLists():       
    #add vertices from vertex group in our list
    if activeVG.name in ob.vertex_groups:                    
        #check if vertex is in our group  
        for verts in mesh.vertices:                          
            for v in verts.groups:   #v defines the vertex of a group    
                if v.group == activeVG.index:
                    #print("locked vert: ", verts.index)
                    vertexList.append([[verts.index], [v.weight]])
                    lockedList.append(verts.index) 
    print("locked verts:", lockedList)              


    #add all vertices to our list that are not in the vertex group with weight 0.0
    for verts in mesh.vertices:  
        #print(lockedList)      
        if not verts.index in lockedList:  
            #print("unlocked:", verts.index)          
            vertexList.append([[verts.index], [0.0]]) 
    vertexList.sort()
    '''
    for i in vertexList:
        print(i)
     #'''
#we only need to run this once



'''---------------------------
# border verts
---------------------------'''  
def getBorderVerts(vertex, bm):     
         
    bmvert = bm.verts[vertex.index]    
    borderVerts = []
    
    for loop in bmvert.link_loops:
        borderVerts.append(loop.edge.other_vert(bmvert).index)
    
    return borderVerts, len(borderVerts)
 

 
'''---------------------------
# avarage border verts
    here we want to average the weight of our neighbour verts
        -loop over each vert, check if it is locked in our vertexList 
        -calculate sum
        -write new value to our vertexList
---------------------------'''  

def averageWeights(): 
    #we need to be in edit mode to loop
    if not ob.mode == 'EDIT':
        bpy.ops.object.mode_set(mode = 'EDIT', toggle = False)
        
    bm = bmesh.from_edit_mesh(mesh)

    for verts in mesh.vertices:    
        sum=0      
        #get those neighbour vertices
        borderVerts,count = getBorderVerts(verts, bm)
        
        #compare border verts with list and average weights    
        for i in borderVerts:                
            for v in vertexList:
                #print(v[0][0])                
                if i in v[0]:                    
                    #print(i,  "in our list")
                    #print("weights: ",v[1][0])
                    sum = sum + v[1][0]
        
        avg = (sum / count)   #we need to check if vertex is locked and adjust count  
        
        if sum>0: 
            #print(verts.index, "sum:", sum,  "   count:", count,"    avg:",avg)   
            #print("lockedList: ", lockedList)
    
            if not verts.index in lockedList:
                #print("ROOT: ", verts.index, "children: ", borderVerts)
                #print("unlocked: ", verts.index)
                #print("before:", vertexList[verts.index][1][0], avg)
                vertexList[verts.index][1][0] = avg     #this creates doubles!! we dont want that             
                #print("after:", vertexList)                     
                #print("------------------")   
                        

'''---------------------------
# assign our vertex weights to a new vertex group
---------------------------'''  

def assignVertexWeights():   
    bpy.ops.object.mode_set(mode = 'OBJECT', toggle = False)       
    vg = ob.vertex_groups.new(name="ALL")
    for verts in mesh.vertices:
        for i in vertexList:
            #print(i[0][0])
            if verts.index == i[0][0]:
                #print("compare:", verts.index, i[0][0])
                #print(i[0][0], i[1][0])
                #this only takes a list so i have to create sublist for every vertex with a weight
                vg.add(i[0], i[1][0], 'ADD')   # LIST, weight, arg
    
    bpy.ops.object.mode_set(mode = 'WEIGHT_PAINT', toggle = False)
    

    
    
print("------------------------------------------------------")   
                        
#assignVertexWeights()  

       
         
'''    #maybe some helpful stuff  

#mesuring time
time1 = time.time()
for x in search:
    method1(x)
print(time.time() - time1)

wipe list with  del l[:]


'''        
        
#======================================================================# 
#         GUI                                                      
#======================================================================#        
class UIElements(bpy.types.PropertyGroup):
    pass
    #text input
    #get_indices = bpy.props.StringProperty(name="index:", description="input vertex, face or edge indices here for selection. example: 1,2,3")
    #checkbox
    modifiers_enabled = bpy.props.BoolProperty(name="enable modifiers", default=False, description="apply modifiers before calculating weights", update= enableModifiers)
    selected_group = bpy.props.BoolProperty(name="selected VG only", default=True, description="only calculate weights from selected vertex group", update= selectedVG)
    slider_iterations = bpy.props.IntProperty(name="iterations", subtype='NONE', min=1, max=1000, default=10, step=1, description="iterations")
    
	
class OBJECT_PT_AverageWeights(bpy.types.Panel):
    bl_label = "AverageWeights"
    bl_idname = "OBJECT_PT_AverageWeights"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    bl_default_closed = True
    
    def draw(self, context):
    
        config = bpy.data.scenes[0].CONFIG_AverageWeights
        layout = self.layout
        
        ob = bpy.context.object
        mesh = ob.data        
        scene = bpy.context.scene  
        
        activeVG = ob.vertex_groups.active
        apply_modifiers = True        
                
        split = layout.split()
        col = split.column()
        box = col.box()
        box.prop(config, "modifiers_enabled")
        box.prop(config, "selected_group")
        box.column().prop(config, "slider_iterations")       
        row = layout.row() 
        row.operator("mesh.compute", text="compute")
        
        
        
class OBJECT_OP_AverageCompute(bpy.types.Operator):
    
    bl_idname = "mesh.compute"
    bl_label = "compute weights"
    bl_description = "compute weights"
    
    def execute(self, context):
        #get arguments from UIElemtnts
        config = bpy.data.scenes[0].CONFIG_AverageWeights
        
                       
            
        return {'FINISHED'} 
        
def compute():
    
    #compute weights
    i = 0
    max = 10
    lockedList = []
    vertexList = []  
    for i in range(max):            
        time0 = time.time()
        if i == 0:             
            populateLists()                      
        print("iterration:", i)
        averageWeights()
        print("iteration time:", time.time() - time0)              
        if i == max-1:
            assignVertexWeights() 
        i = i + 1   
       
#======================================================================# 
#         register                                                      
#======================================================================#
def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.CONFIG_AverageWeights = bpy.props.PointerProperty(type = UIElements)

    
def unregister():
    bpy.utils.unregister_module(__name__)

    if bpy.context.scene.get('CONFIG_AverageWeights') != None:
        del bpy.context.scene['CONFIG_AverageWeights']
    try:
        del bpy.types.Scene.CONFIG_AverageWeights
    except:
        pass 
        

print(" ")
print("*                             initialized                                      *")
print("*------------------------------------------------------------------------------*")
print(" ") 
    
