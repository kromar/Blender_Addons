# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8-80 compliant>




'''---------------------------
DONE:
v 1.25
    - increased iteration max to 10000 and lowered default to 100
    - added option and sliders for threshold weights to gui
    - implemented threshold values from sliders
    
v 1.24
    - use activeList to speed up iterations
    - change bmesh creation method to prevent mode switching
    

TODO:
    - make updates per iteration?
    
    - option to calculate heat over multiple vertex groups
    
    - option to define min/max weights and recalculate everything in between?
    
    - break if all weights == 1.00
    
    - add distance influence value 
        multiplier so edge length has more impact on weight
        
    - link with meshpy?
    
    - add a 3D diffusion, make vertex weights have a influence zone in addition to neighbors?
        - interaction on multiple meshes
    
    - a way to cancel the calculation
    
    

FIXME: 
     - 0 weights are not visible, is there a way to fix that?
        - and when weights are painted to 0 to remove the weight, can we unlock them? 
        can we even differentiate between the two?
        
        - can we use vertex colors to do the diffusion and then bake down to weights?
       
        http://www.blender.org/documentation/blender_python_api_2_64_1/bpy.ops.object.html#bpy.ops.object.vertex_group_clean
        bpy.ops.object.vertex_group_clean(limit=0.01, all_groups=False, keep_single=False)
   
   
    
    
HELP:

http://en.wikibooks.org/wiki/Blender_3D:_Blending_Into_Python

# measuring time
import time
time1 = time.time()
for x in search:
    method1(x)
print(time.time() - time1)



---------------------------'''    

import bpy
import bmesh
import time
import mathutils
 
#addon description
bl_info = {
    "name": "Vertex Heat",
    "author": "Daniel Grauer (kromar)",
    "version": (1, 2, 5),
    "blender": (2, 6, 5),
    "category": "Mesh",
    "location": "Properties space > Object Data > Vertex Heat",
    "description": "vertex weight heat diffusion",
    "warning": '', # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "https://github.com/kromar/Blender_Addons/blob/master/addons_contrib/mesh_VertexHeat.py",
}

    
activeList = []    
lockedList = []
vertexList = []  

    
#[0]=index, [1]=weight, [2]=borderverts, [3]=borderDistance
'''---------------------------''' 
def populateLists(ob, mesh):       
    bm = bmesh.new()
    bm.from_mesh(mesh)      
    activeVG = ob.vertex_groups.active   
     
    config = bpy.context.scene.CONFIG_VertexHeat
    
    #add vertices from vertex group in our list
    if config.use_threshold is True:    
        #print("threshold:", config.threshold_min, config.threshold_max)
        if activeVG.name in ob.vertex_groups:                    
            #check if vertex is in our group  
            for verts in mesh.vertices:  #FIXME: use if in instead of double for loop to speed up                     
                for v in verts.groups:   #v defines the vertex of a group    
                    if v.group is activeVG.index:
                        if v.weight >= config.threshold_max or v.weight <= config.threshold_min:
                            #print(v.weight)
                            vertexList.append([[verts.index],[v.weight]])           #[0]=index, [1]=weight
                            lockedList.append(verts.index)
                 
                if not verts.index in lockedList:  
                    #print("unlocked:", verts.index)          
                    vertexList.append([[verts.index], [0.0]])                       #[0]=index, [1]=weight
                    activeList.append(verts.index)

    else:
        if activeVG.name in ob.vertex_groups:                    
            #check if vertex is in our group  
            for verts in mesh.vertices:  #FIXME: use if in instead of double for loop to speed up                     
                for v in verts.groups:   #v defines the vertex of a group    
                    if v.group is activeVG.index:
                        #print("locked vert: ", verts.index)
                        vertexList.append([[verts.index],[v.weight]])           #[0]=index, [1]=weight
                        lockedList.append(verts.index)
        
            if not verts.index in lockedList:  
                #print("unlocked:", verts.index)          
                vertexList.append([[verts.index], [0.0]])                       #[0]=index, [1]=weight
                activeList.append(verts.index)
      
    vertexList.sort()
    activeList.sort()  
    
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
            #influence = 1 / distance * len(borderVerts)
            borderDistance[i] = distance / sumDistance   
            #print(distance, influence)
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
    #'''
        
  

'''---------------------------'''              
def VertexHeat(ob, mesh, aL, lL):  
    for v in vertexList:    #TODO: check if its possible to use activeList instead of full list
        vIndex = v[0][0]
        avgWeight = 0
        
        #depending on list size we change the index check because this is the most expensive part
        if aL < lL:
            if vIndex in activeList:
                i = 0
                for distance in v[3]:
                    weight = vertexList[v[2][i]][1][0]
                    avgWeight = avgWeight + distance * weight
                    i = i + 1
                #activeList[vIndex][1][0] = avgWeight 
                vertexList[vIndex][1][0] = avgWeight
        else:   
            if not vIndex in lockedList:
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
    #apply_modifiers = True      #TODO: do we need this? or will it be solved when apllied from export?
    
    #compute weights
    i = 0
    bpy.ops.wm.modal_timer_operator()
    populateLists(ob, mesh) 
    
    aL = len(activeList)
    lL = len(lockedList) 
    
    for i in range(iterations):            
        time0 = time.time()      
        VertexHeat(ob, mesh, aL, lL)
        print("iteration:", i+1, "time:", time.time() - time0,"sec")
        
        if i == iterations-1:
            assignVertexWeights(ob, mesh)
        i = i + 1   
                      
    print("------------------------------------") 
    print("total VertexHeat:", time.time() - timeCompute,"sec")   
    print("------------------------------------")     

        
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
    config = bpy.context.scene.CONFIG_VertexHeat
    print("selected group: ", config.selected_group)
   
    if config.selected_group == True:
        mesh.selected_group = True
    else:
        mesh.selected_group = False

    
'''---------------------------'''  
def enableModifiers(self, context):
    mesh =  bpy.context.active_object.data 
    config = bpy.context.scene.CONFIG_VertexHeat
    print("modifier enabled: ", config.modifiers_enabled)
    
    if config.modifiers_enabled == True:
        mesh.modifiers_enabled = True
    else:
        mesh.modifiers_enabled = False        
    return mesh
        
        
'''---------------------------'''  
def vertexDistance(self, context):
    mesh =  bpy.context.active_object.data 
    config = bpy.context.scene.CONFIG_VertexHeat
    print("vertexDistance enabled: ", config.vertex_distance)
    
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
    slider_iterations = bpy.props.IntProperty(name="Iterations", subtype='FACTOR', min=1, max=10000, default=100, step=1, description="iterations")
    
    use_threshold = bpy.props.BoolProperty(name="Use threshold", default=True, description="use weight threshold", update=None)
    threshold_min = bpy.props.FloatProperty(name="min", subtype='FACTOR', min=0.0, max=1.0, default=0.0, step=0.01, description="min")
    threshold_max = bpy.props.FloatProperty(name="max", subtype='FACTOR', min=0.0, max=1.0, default=1.0, step=0.01, description="max")

    slider_progress = bpy.props.IntProperty(name="progress", subtype='PERCENTAGE', min=0, max=100, default=0, step=1, description="iteration progress")
 

'''---------------------------'''    
class OBJECT_PT_VertexHeat(bpy.types.Panel):
    bl_label = "VertexHeat"
    bl_idname = "OBJECT_PT_VertexHeat"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    bl_default_closed = True
    
    def draw(self, context):        
        config = bpy.context.scene.CONFIG_VertexHeat
        layout = self.layout  
        ob = context.object
        activeVG = ob.vertex_groups.active 
        objects = bpy.context.selected_objects 
        type = ob.type.capitalize()       
        
        #make sure a object is selected, otherwise hide settings and display warning           
        if type == 'Mesh':  
            if not objects: 
                row = layout.row()
                row.label(text="No Active Object", icon='ERROR') 
        
            else:
                if activeVG:      
                    row = layout.row()
                    row.label(text="Active Vertex Group: " + str(activeVG.name), icon='GROUP_VCOL')
                            
                    #row.prop(config, "slider_progress")
                    
                    #col = layout.column()     
                    #col.prop(config, "vertex_distance")                
                    #col.prop(config, "modifiers_enabled")
                    #col.prop(config, "selected_group") 
                    
                    
                    row = layout.row() 
                    row.prop(config, "use_threshold")
                    if config.use_threshold is True:
                        box = layout.split().column().box()
                        box.prop(config, "threshold_min")  
                        box.prop(config, "threshold_max") 
                        row = layout.row() 
                    
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
        config = bpy.context.scene.CONFIG_VertexHeat
        iterations = config.slider_iterations 
                 
        computeHeat(iterations)            
        return {'FINISHED'} 
        
        
'''---------------------------''' 
class ModalTimerOperator(bpy.types.Operator):
    """Operator which runs its self from a timer"""
    bl_idname = "wm.modal_timer_operator"
    bl_label = "Modal Timer Operator"

    _timer = None

    def modal(self, context, event):
        if event.type == 'ESC':
            return self.cancel(context)

        if event.type == 'TIMER':
            # change theme color, silly!
            config = bpy.context.scene.CONFIG_VertexHeat
            config.slider_progress +=1
            #context.scene.slider += 1
            for area in context.screen.areas:
                if area.type == 'PROPERTIES':
                    area.tag_redraw()
            

        return {'PASS_THROUGH'}

    def execute(self, context):
        self._timer = context.window_manager.event_timer_add(0.1, context.window)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        context.window_manager.event_timer_remove(self._timer)
        return {'CANCELLED'}        

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

