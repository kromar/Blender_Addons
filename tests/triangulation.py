import bpy
import bmesh
import random
import math
import mathutils



#-----------------------------------------#
# check if mnesh is watertight
#-----------------------------------------#
def watertight(mesh):
    numVerts = len(mesh.vertices)
    numFaces = len(mesh.polygons)
    numEdges = len(mesh.edges)
    holes = numVerts - numEdges + numFaces
    
    if holes == 2:
        #print(mesh.name , " is watertight")
        euler = True
    else:
        #print(mesh.name , " has holes: " , watertight)
        euler = False

    return euler, holes

#-----------------------------------------#
# 
#-----------------------------------------#

# Get the active mesh
ob = bpy.context.object
me = ob.data

# Get a BMesh representation
euler, holes = watertight(me)
print("euler:" , euler, holes)

#-----------------------------------------#

# create an empty BMesh
bm = bmesh.new()   
if bpy.context.object.mode == 'EDIT':
    bpy.ops.object.mode_set(mode = 'OBJECT', toggle = False)
    #what did i do here? o_O
    bpy.ops.object.mode_set(mode = 'EDIT', toggle = False)
# fill it in from a Mesh
bm.from_mesh(me)   



    

#-----------------------------------------#
# Modify the BMesh, can do anything here...
#   create raster
#-----------------------------------------#
#   at a later point we want the raster to include 
#   only the bounding box of the object



    

   

# take the bounding box scales as raster size

def createRaster():
    #vector from pivot to corner
    #0 & 6 are needed for slice position
    bx0, by0, bz0 = ob.bound_box[0][0], ob.bound_box[0][1], ob.bound_box[0][2]
    bx6, by6, bz6 = ob.bound_box[6][0], ob.bound_box[6][1], ob.bound_box[6][2]
    #print("bbox: ", bx0, by0, bz0)
    
    #vector to pivot
    ox, oy, oz = ob.location[0], ob.location[1], ob.location[2]
    #print("pcor: " , ox,oy,oz)
        
    #world location of bounding box corner
    worldCorner0 = ((bx0 + ox), (by0 + oy), (bz0 + oz))
    worldCorner6 = ((bx6 + ox), (by6 + oy), (bz6 + oz))
    print("R0cor: ", worldCorner0)
    print("R6cor: ", worldCorner6)
    
    raster = [] 
    rasterSize = ob.dimensions
    
    rasterSegment = 0.1
    cellX   = rasterSize[0] * rasterSegment
    cellY   = rasterSize[1] * rasterSegment
    cellZ   = rasterSize[2] * rasterSegment
    
    
    #raster origin has to be in the bounding box corner
    x,y,z = worldCorner0[0], worldCorner0[1], worldCorner0[2]
        
    x = worldCorner0[0]
    while x <= rasterSize[0] * 0.5:         
        y = worldCorner0[1]
        while y <= rasterSize[1] * 0.5: 
            z = worldCorner0[2]
            while z <= rasterSize[2] * 0.5: 
                #print(x, y, z)                      
                raster.append([x, y, z])
                z += cellX        
            y += cellY
        x += cellX

    #create new vertices and update the index
    for v in raster:    
        bm.verts.new(v)
        bm.verts.index_update()

#-----------------------------------------#

createRaster()

#-----------------------------------------#
#   point inside mesh
#-----------------------------------------#
def pointInsideMesh(point, ob):
    
    axes = [mathutils.Vector((1,0,0))]
    inside = False
    
    for axis in axes:
        count = 0
        while True:
            location,normal,index = ob.ray_cast(point, (point + axis * 100.0)) 
            if index == -1: 
                break
            count += 1            
            if count%2 == 0:
                inside = True
                break
    return  inside, location, index            


#-----------------------------------------#
#   point mesh proximity
#-----------------------------------------#        
        
def pointMeshProximity(point, max):
     
    location,normal,index = closest_point_on_mesh(point, max_dist)
    
#-----------------------------------------#   
    
def removeOutside():
    #cast ray from each position to see if its inside the mesh
    for v in me.vertices:
        #print(v.co)
        point = mathutils.Vector(v.co)
        #print(point)
        inside, location, index = pointInsideMesh(point,ob)  
        #print(point, inside, index)
        
        #deselect all verts before exclud selection
        if not inside:
            v.select = True
        else:
            v.select = False   
#-----------------------------------------#   

# Finish up, write the bmesh back to the mesh
    
def toMesh():
    if bpy.context.object.mode == 'EDIT':
        bpy.ops.object.mode_set(mode = 'OBJECT', toggle = False)
        #to_mesh needs to be done in object mode
        bm.to_mesh(me)
        
        removeOutside()
        
        bpy.ops.object.mode_set(mode = 'EDIT', toggle = False)
    
        #bpy.ops.mesh.delete()
      
        '''
        if not index ==2:
            v.select = True
            #bm.verts.remove(v)
            #bm.verts.index_update()
            pass
        '''
        
              
        #bm.to_mesh(me)      
    else:  
        # will ned to redraw 3d view to update  
        bm.to_mesh(me)
        removeOutside()
        
        bpy.ops.object.mode_set(mode = 'EDIT', toggle = False)
    
        #bpy.ops.mesh.delete()

toMesh()









#-----------------------------------------#




#-----------------------------------------#
#   do some simple tests in 2d environment
#-----------------------------------------#
'''
1. get border region

2. place random vertices inside border

3. connect verts and try to generate "nice" triangles

'''

#-----------------------------------------#
#   write base mesh into borderlist for now; will expand this whenever needed
#-----------------------------------------#


border = []
def calculateBorder():
    global border
    for vert in me.vertices:
        border.append([vert.co[0],vert.co[1], vert.co[2]])

    print("----------------------------")
    print(border) 
    
   



#-----------------------------------------#
#   lets create some random vertices
#-----------------------------------------#

#add them to the existing border list and generate a new mesh? 
#that way we might already get around nasty border calculations?


def generateMesh(verts):

    bpy.ops.object.mode_set(mode = 'OBJECT', toggle = False)
    
    mesh_data = bpy.data.meshes.new("mesh_data") 
    mesh_data.from_pydata(verts, [], [])  
    mesh_data.update()#calc_edges=True) #not needed here 
    
    new_mesh = bpy.data.objects.new("triangle", mesh_data)  
    bpy.context.scene.objects.link(new_mesh)  
    
    #make new mesh active and selected; deselect old mesh
    print(new_mesh.name)
    ob.select = False   
    new_mesh.select = True   
    bpy.context.scene.objects.active = new_mesh
    
    #reset vertex selections on new mesh (probably not needed
    bpy.ops.object.mode_set(mode = 'EDIT', toggle = False)
    bpy.ops.mesh.reveal()
    bpy.ops.mesh.select_all(action='DESELECT')   
     

triangles = []
  
def generatePoints():
    

    if ob.name!='triangle':
        global triangles
        i=0
        vertcount = 20
        min,max = 0,2
        while i < vertcount:
            randX = random.uniform(min,max)-max*0.5
            randY = random.uniform(min,max)-max*0.5
            randZ = 0
            
            triangles.append([randX,randY,randZ])
            #print(i, ": ", randX,randY,randZ)
            i+=1   
            
        generateMesh(triangles)
    
    
    
    bpy.ops.object.mode_set(mode = 'OBJECT', toggle = False)
    i = 0
    n = 1
    points = len(ob.data.vertices)
    print(points)
    while i <= points:
        for v in ob.data.vertices:
            index = v.index
            
            if index==i:
                print(index)
                x1, y1, z1 = v.co[0], v.co[1], v.co[2]
                v.select = True
            
            if index==i+n:  
                print(index)          
                x2, y2, z2 = v.co[0], v.co[1], v.co[2]
                v.select = True
        
        lx = math.pow((x1-x2),2)
        ly = math.pow((y1-y2),2)
        lz = math.pow((z1-z2),2)
           
        radius = math.sqrt(lx+ly+lz)
        
        print("distance: ", radius)
        bpy.ops.object.mode_set(mode = 'EDIT', toggle = False)
        
        
        bpy.ops.mesh.edge_face_add()  
        
        bpy.ops.mesh.reveal()
        bpy.ops.mesh.select_all(action='DESELECT')  
        bpy.ops.object.mode_set(mode = 'OBJECT', toggle = False)
        
        i+=1
        
    
#calculateBorder()  
#generatePoints()
 
#-----------------------------------------#
#calculate distances to near vertices 
#-----------------------------------------#
 
#check distances between verts starting by first index

#print("testing", triangles)
#print("listsize: ", len(triangles))
#index = len(triangles)-1


#radius = x1-x2   
#print("radius: ",radius) 
#bpy.ops.mesh.edge_face_add()    


# if no vert in range, increase radius till we get 2
# on match generate edges/face on 3 verts
# check child verts with same radius to find verts in range 
 