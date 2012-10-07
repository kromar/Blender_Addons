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
