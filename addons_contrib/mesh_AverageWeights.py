

'''---------------------------
TODO:
    
    - include locked vertices
    - make init on every new group
---------------------------'''  



import bpy
import bmesh
import time
 
 
ob = bpy.context.object
scene = bpy.context.scene  
apply_modifiers = True
   
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

#mesh = objectApplyModifiers(scene, ob, apply_modifiers)
mesh = ob.data
activeVG = ob.vertex_groups.active

print("active group: ", activeVG.name, "index: ", activeVG.index)

                
'''---------------------------
# check if vertex is in active group
---------------------------'''  
 
   
def populateLists():       
    #add vertices from vertex group in our list
    print("len:", len(lockedList))  
    if len(lockedList) == 0:
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

def unlockedVerts():
    pass


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


i = 0
max = 1

try:
    lockedList
    print("try")
except:    
    print("except")
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
           
       
       
         
'''    #maybe some helpful stuff  

#mesuring time
time1 = time.time()
for x in search:
    method1(x)
print(time.time() - time1)

wipe list with  del l[:]


'''        
        

    
