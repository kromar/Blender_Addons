# ##### BEGIN GPL LICENSE BLOCK #####
#
#This program is free software; you can redistribute it and/or
#modify it under the terms of the GNU General Public License
#as published by the Free Software Foundation; either version 2
#of the License, or (at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software Foundation,
#Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

#<pep8-80 compliant>

#======================================================================#
#     todo
#======================================================================#

'''
 - import helper options to check name
 - import helper option to choose wether to overwrite existing groups or skip them
'''


import bpy
from os.path import *
from bpy.props import *
from bpy_extras.io_utils import ImportHelper
from xml.dom.minidom import parse
import xml.dom.minidom
import time

filename_ext = ".xml"

#addon description
bl_info = {
    "name": "Import: Vertex Groups",
    "author": "Daniel Grauer",
    "version": (1, 1, 2),
    "blender": (2, 7, 1),
    "category": "Import-Export",
    "category": "VirtaMed",
    "location": "File > Import > Vertex Groups",
    "description": "import vertex groups from xml file and assign them to active mesh",
    "warning": '',    #used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
}

print(80 * "-")
print("initializing VertexGroup import")

#------------------------------------------------------------------------------ 


vertexList = []
weightList = []
labelList = []

def import_VertexGroup(file):
    timeCompute = time.time()
       
    ob = bpy.context.active_object 

    # parse the xml file
    DOMTree = xml.dom.minidom.parse(file)
    virtamed = DOMTree.documentElement
    VertexLabels = virtamed.getElementsByTagName("VertexLabels")
    VertexLabel = virtamed.getElementsByTagName("VertexLabel")

    # parse vertex groups
    
    for tag in VertexLabels:
        print(20 * "-", "Mesh Infos", 20 * "-")
        meshName = tag.getAttribute("MeshName")
        meshVertices = tag.getAttribute("MeshVertices")
        print("MeshName: %s" % meshName, "\nMeshVertices: %s" % meshVertices)
        
        if meshName:
            print("new format with mesh details")
            # check if we get matching mesh names
            if ob.name == meshName:
                print("Matching mesh name: %s" % meshName)

                # check if the vertex count has changed
                vertexCount = str(len(ob.data.vertices))
                if vertexCount == meshVertices:        
                    print("Matching vertex count: %s" % meshVertices)
                    
                    parseVertices(ob, VertexLabel) 
                    
                    print(80 * "-")
                    print("Vertex Group import finished in %s" % (time.time() - timeCompute), "sec")
                    print(80 * "-")
                    
                elif vertexCount < meshVertices:
                    print("WARNING: %s" % vertexCount, "lower than Mesh vertices %s" % meshVertices)
                               
                else:
                    print("WARNING: %s" % vertexCount, "is not %s" % meshVertices)
                    break
                
            else:
                print("WARNING name mismatch: %s" % ob.name, "is not %s" % meshName)
                break
                
        else:
            print("WARNING: old format without mesh details!")
            parseVertices(ob, VertexLabel)
        
            print(80 * "-")
            print("Vertex Group import finished in %s" % (time.time() - timeCompute), "sec")
            print(80 * "-")
        
 
def parseVertices(ob, VertexLabel):
    # parse vertices and weights
    for tag in VertexLabel:        
        
        # clean the list and continue                    
        del vertexList[:]
        del labelList[:]
        del weightList[:]  
        
        print(20 * "-", "VertexGroup Infos", 20 * "-")
        
        labelCount = int(tag.getAttribute("Count"))
        labelName = tag.getAttribute("LabelName")
        print("LabelName: %s" % labelName, ": ", labelCount)    
        if labelCount > 0:    
            vertices = tag.getElementsByTagName('Vertices')[0]
            vertexIndex = vertices.childNodes[0].data   
            weights = tag.getElementsByTagName('Weights')[0]
            vertexWeight = weights.childNodes[0].data    
            
            for i in vertexIndex.split():
                vertexList.append(int(i))
                
            for i in vertexWeight.split():
                weightList.append(float(i))

            i = 0
            while i < labelCount: 
                labelList.append([[vertexList[i]], [weightList[i]]])  
                i += 1
        
        # here we create the groups and assign the weights  
        assignVertexWeights(ob, labelName) 

  
#------------------------------------------------------------------------------ 

def assignVertexWeights(ob, vertexGroup):        
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    
    if not vertexGroup in ob.vertex_groups:
        vg = ob.vertex_groups.new(name=vertexGroup)
        for i in labelList:
            vg.add(i[0], i[1][0], 'ADD')
        print("added: ", vertexGroup)
              
    else:
        print("alr4eady exists:", vertexGroup)
        '''
        vg = ob.vertex_groups[vertexGroup]
        for i in labelList:
            vg.add(i[0], i[1][0], 'REPLACE')  # http://www.blender.org/documentation/blender_python_api_2_64_1/bpy.types.VertexGroup.html?highlight=vertex%20group#bpy.types.VertexGroup.add
        '''
    bpy.ops.object.mode_set(mode='WEIGHT_PAINT', toggle=False)
    
    

# ----------------------------------------------------------------------------#

class VertexGroupImporter(bpy.types.Operator, ImportHelper):
    '''Import Vertex Groups'''
    bl_idname = "import.vertexgroup"
    bl_label = "import vertex groups"

    filename_ext = filename_ext
    filter_glob = StringProperty(
            default="*.xml",
            options={'HIDDEN'},
            )
    
    
    filepath = StringProperty(name = "File Path",
                              description = "filepath",
                              default = "",
                              maxlen = 1024,
                              options = {'ANIMATABLE'},
                              subtype = 'NONE')
    check_extension = True
    
    def execute(self, context):
        ##save_VertexGroup(self.properties.filepath)
        import_VertexGroup(self.properties.filepath)
        return {'FINISHED'}

    #open the filemanager
    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}


# ----------------------------------------------------------------------------#

#defines the menu button (file>import)
def menu_func(self, context):
    #check for active and list in import menu
    if bpy.context.active_object:
        export_name = bpy.context.active_object.name + "Labels.xml"
        #export_name = bpy.context.selected_objects[0].name + "Labels.xml"
        self.layout.operator(VertexGroupImporter.bl_idname, text = "Vertex Group (.xml)").filepath = export_name

# ----------------------------------------------------------------------------#

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_func)


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_func)

if __name__ == "__main__":
    register()



print("initialized")
print(80 * "-")


