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
    
    - check where we spend so much time
    
    
#    mesuring time
time1 = time.time()
for x in search:
    method1(x)
print(time.time() - time1)



#    fastest wipe list:
del l[:]


---------------------------'''    

import bpy
import bmesh
import time
import mathutils
 
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
print("*                          Average Weights                                     *")
print(" ") 

lockedList = []
vertexList = []  

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

'''---------------------------'''  
def selectedVG(self, context):
    mesh =  bpy.context.active_object.data 
    config = bpy.data.scenes[0].CONFIG_AverageWeights
    print("selected group: ", config.selected_group)
   
    if config.selected_group == True:
        mesh.selected_group = True
    else:
        mesh.selected_group = False

    
'''---------------------------'''  
def enableModifiers(self, context):
    mesh =  bpy.context.active_object.data 
    config = bpy.data.scenes[0].CONFIG_AverageWeights
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
    config = bpy.data.scenes[0].CONFIG_AverageWeights
    print("vertexDistance enabled: ", config.vertex_distance)
    
    #enable debug mode, show indices
    #bpy.app.debug  to True while blender is running
    if config.vertex_distance == True:
        mesh.vertex_distance = True
    else:
        mesh.vertex_distance = False   
        
#mesh = objectApplyModifiers(scene, ob, apply_modifiers)
#mesh = ob.data
#activeVG = ob.vertex_groups.active

#print("active group: ", activeVG.name, "index: ", activeVG.index)

                
'''---------------------------
# check if vertex is in active group
---------------------------'''      
def populateLists(ob, mesh):   
    activeVG = ob.vertex_groups.active    
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
# get border verts
---------------------------'''   
def getBorderVerts(vertex, bm):      
    bmvert = bm.verts[vertex] 
    borderVerts = []  
        
    for loop in bmvert.link_loops:
        vec = mathutils.Vector(bmvert.co - loop.edge.other_vert(bmvert).co)     
        borderVerts.append(loop.edge.other_vert(bmvert).index)    
    return borderVerts, len(borderVerts), vec.length

 
'''---------------------------
# avarage border verts
    here we want to average the weight of our neighbour verts
        -loop over each vert, check if it is locked in our vertexList 
        -calculate sum
        -write new value to our vertexList

time mesured in this function:     (iteration time: 0.54003)
    0.53003


---------------------------'''  

def averageWeights(ob, mesh): 
    takeTIME = time.time()  
    #we need to be in edit mode to loop
    if not ob.mode == 'EDIT':
        bpy.ops.object.mode_set(mode = 'EDIT', toggle = False)
        print("set to edit mode for bmesh looping")        
       
    bm = bmesh.from_edit_mesh(mesh)    
                
    for v in vertexList:    #we go through all the vertices??? do we need this? 
        #print("v", v)
        #get those neighbour vertices  
        vIndex = v[0][0]      
        borderVerts, count, distance = getBorderVerts(vIndex, bm) #we only need vertex index for this function         
       
        # get average weight from border verts
        sumBorderWeights=0 
        
        #just add up border weights and assing to active vertex
        for i in borderVerts:
            #now add up the weights of these
            weight = vertexList[i][1][0]
            #print("borders", i, weight)
            #print(weight)
            sumBorderWeights = sumBorderWeights + weight
        
        avg = (sumBorderWeights / count) #add distance to this formula   
        if sumBorderWeights>0:  
            #print("avg:", avg)
            #print(verts.index, "sum:", sum,  "   count:", count,"    avg:",avg)   
            #print("lockedList: ", lockedList) 
            #print(vIndex)   
            if not vIndex in lockedList:
                #print("ROOT: ", verts.index, "children: ", borderVerts)
                #print("unlocked: ", verts.index)
                #print("before:", vertexList[vIndex][1][0], avg)
                vertexList[vIndex][1][0] = avg     #this creates doubles!! we dont want that             
                #print("after:", vertexList)      
    print("takeTIME:", time.time() - takeTIME) 
    
    
def averageWeights_OLD(ob, mesh): 
    takeTIME = time.time()  
    #we need to be in edit mode to loop
    if not ob.mode == 'EDIT':
        bpy.ops.object.mode_set(mode = 'EDIT', toggle = False)
        print("set to edit mode for bmesh looping")
        
    bm = bmesh.from_edit_mesh(mesh)
   
    
    for verts in mesh.vertices:     # we should be able to remove this since we use our own vertex list?
        sum=0      
        #get those neighbour vertices
        borderVerts,count = getBorderVerts(verts, bm) #we only need vertex index for this function
        #compare border verts with list and average weights   
        #'''
        
        for i in borderVerts:   #we go through all border verts            
            for v in vertexList:    #we go through all the vertices??? do we need this?
                #print(v[0][0])                
                if i in v[0]:       # we check if border is in vertex list             
                    #print(i,  "in our list")
                    #print("weights: ",v[1][0])
                    sum = sum + v[1][0]
        
        avg = (sum / count) #add distance to this formula       
        
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
                        
        
    print("takeTIME:", time.time() - takeTIME) 
    
    
'''---------------------------
# assign our vertex weights to a new vertex group
---------------------------'''  
def assignVertexWeights(ob, mesh):   
    bpy.ops.object.mode_set(mode = 'OBJECT', toggle = False)       
    vg = ob.vertex_groups.new(name="Average")
    for verts in mesh.vertices:     #can probably be removed as well
        for i in vertexList:
            #print(i[0][0])
            if verts.index == i[0][0]:
                #print("compare:", verts.index, i[0][0])
                #print(i[0][0], i[1][0])
                #this only takes a list so i have to create sublist for every vertex with a weight
                vg.add(i[0], i[1][0], 'ADD')   # LIST, weight, arg
    
    bpy.ops.object.mode_set(mode = 'WEIGHT_PAINT', toggle = False)
    
               

def computeAverage(iterations):  
           
    timeCompute = time.time() 
    del vertexList[:]
    del lockedList[:]
         
    ob = bpy.context.object
    mesh = ob.data        
    scene = bpy.context.scene      
    apply_modifiers = True  
    
    time0 = time.time()
    #compute weights
    i = 0
    max = iterations
    for i in range(max):            
        time0 = time.time()
        if i == 0:             
            populateLists(ob, mesh)                      
        print("iterration:", i)       
        averageWeights(ob, mesh)
        print("iteration time:", time.time() - time0)                     
        print("------------------") 
                    
        if i == max-1:
            assignVertexWeights(ob, mesh) 
        i = i + 1   
        
    print("timeCompute:", time.time() - timeCompute)       

        
#======================================================================# 
#         GUI                                                      
#======================================================================#        
class UIElements(bpy.types.PropertyGroup):
    modifiers_enabled = bpy.props.BoolProperty(name="enable modifiers", default=False, description="apply modifiers before calculating weights", update= enableModifiers)
    selected_group = bpy.props.BoolProperty(name="selected VG only", default=True, description="only calculate weights from selected vertex group", update= selectedVG)
    vertex_distance = bpy.props.BoolProperty(name="vertex distance", default=False, description="take vertex distance into average calculation", update= vertexDistance)
    
    #slider_multiplier = bpy.props.IntProperty(name="weight multiplier", subtype='FACTOR', min=-1, max=1, default=1, step=0.1, description="multiplier")
    slider_iterations = bpy.props.IntProperty(name="Iterations", subtype='FACTOR', min=1, max=1000, default=10, step=1, description="iterations")
    slider_min = bpy.props.FloatProperty(name="min", subtype='FACTOR', min=0.0, max=1.0, default=0.0, step=0.01, description="min")
    slider_max = bpy.props.FloatProperty(name="max", subtype='FACTOR', min=0.0, max=1.0, default=1.0, step=0.01, description="max")

    
    
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
                
        
        
class OBJECT_OP_AverageCompute(bpy.types.Operator):    
    bl_idname = "mesh.compute_weights"
    bl_label = "compute weights"
    bl_description = "compute weights"
    
        
    def execute(self, context):
        #get arguments from UIElemtnts
        config = bpy.data.scenes[0].CONFIG_AverageWeights
        iterations = config.slider_iterations          
        computeAverage(iterations)            
        return {'FINISHED'} 
        
        
        

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
    
