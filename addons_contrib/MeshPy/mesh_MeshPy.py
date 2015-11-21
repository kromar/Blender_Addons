# ##### BEGIN GPL LICENSE BLOCK #####
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
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8-80 compliant>


#======================================================================#
#      ***** Credits *****
#======================================================================#
'''
#
# thanks to Andreas Klöckner for MeshPy
#   http://mathema.tician.de/software/meshpy

# thanks to scorpin81 (irc#pythonblender) for linux lib compiling
'''

#======================================================================#
# binary downloads
#======================================================================#
'''
    http://www.lfd.uci.edu/~gohlke/pythonlibs/
'''

#======================================================================#
# TODO: main tasks
#======================================================================#
'''

MeshPy:

- V 1.30 figure out where the crash happens, i suspect it could happen while creating the mesh and using
    wrong data


    - voronoi:
    -no its not in, but if you have delauney triangulation,
    you can get voronoi by connecting the triangle's
    outer circles midpoints together (at least in 2d)

   - New output of Voronoi diagrams. The Voronoi diagram is the geometric dual of the Delaunay triangulation.
    By using the '-v' option, the Voronoi diagram will be saved in files:
    .v.node, .v.edge, .v.face, and .v.cell.
- For an example, the string '-q1.4q10' sets both a radius-edge ratio (<= 1.4)
    and a minimum dihedral angle (>= 10 degree) as the tetrahedral shape quality measure

- set softbody to split meshes
    - set collision to splits?

- add tetra amount preview option (skipp mesh calculations and just add tetamount to gui)

- add splits to new group
- copy material from source object

- custom name for new tetras
- human readable tooltips
- reset button resetting slider? separate reset for sliders?

switches
    - check intersection in meshes with -d switch
    - o2 switch
    (TetGen generates meshes with quadratic elements if the -o2 switch is specified.
    Quadratic elements have ten nodes per element, rather than four.
    The six extra nodes of a tetrahedron fall at the midpoints of its six edges)
    - C switch  to check the consistency of the mesh on finish.
    '-CC', TetGen also checks constrained Delaunay (for -p switch) or conforming Delaunay (for -q, -a, or -i) property for the mesh.
    - h switch for help output
- multiple intersecting meshes causes crash
- modifying a mesh crashes blender; find reason
- convert quality value to percentage, at the moment its inversed logic which is not user friendly

- monkey can not be generated, find reason
    Internal error in finddirectionsub():  Unable to find a subface leading from 73 to 97.
      Please report this bug to sihang@mail.berlios.de. Include the message above, your input data set, and the exact command line you used to run this program, thank you.
    Traceback (most recent call last):
      File "F:\BlenderSVN\cmake-blender\bin\Release\2.61\scripts\addons_contrib\mesh_MeshPy.py", line 423, in execute
- mesh output files?

MeshSlicer:
- cant hide vertices directly in edit mode which causes huge performance hit:(
    we have to switch back and forth to modes for every update.....
'''


#======================================================================#
#
#======================================================================#
from meshpy.tet import MeshInfo, build, Options
import bmesh
import bpy
import math
import mathutils


bl_info = {
    "name": "MeshPy",
    "author": "Daniel Grauer (kromar)",
    "version": (1, 3, 0),
    "blender": (2, 6, 7),
    "category": "Mesh",
    "category": "kromar",
    "location": "Properties space > Data > MeshPy",
    "description": "Quality triangular and tetrahedral mesh generation",
    "warning": "MeshPy modules are required!",    # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
    "resource_url": "http://www.lfd.uci.edu/~gohlke/pythonlibs/#meshpy"
    }


#======================================================================#
#  args
#======================================================================#
'''
#   -p  Tetrahedralizes a piecewise linear complex (PLC).
#   -q   quality (shape) of tets 1.1 - 1.6    2.0(default)
#   -a   max tet size


::tetgen.exe -help

::  tetgen [-prq_a_AiMYS_T_dzo_fenvgGOJBNEFICQVh] input_file
::    -p  Tetrahedralizes a piecewise linear complex (PLC).
::    -r  Reconstructs a previously generated mesh.
::    -q  Refines mesh (to improve mesh quality).
::    -a  Applies a maximum tetrahedron volume constraint.
::    -A  Assigns attributes to tetrahedra in different regions.
::    -i  Inserts a list of additional points into mesh.
::    -M  No merge of coplanar facets.
::    -Y  No splitting of input boundaries (facets and segments).
::    -S  Specifies maximum number of added points.
::    -T  Sets a tolerance for coplanar test (default 1e-8).
::    -d  Detects self-intersections of facets of the PLC.
::    -z  Numbers all output items starting from zero.
::    -o2 Generates second-order subparametric elements.
::    -f  Outputs all faces to .face file.
::    -e  Outputs all edges to .edge file.
::    -n  Outputs tetrahedra neighbors to .neigh file.
::    -v  Outputs Voronoi diagram to files.
::    -g  Outputs mesh to .mesh file for viewing by Medit.
::    -G  Outputs mesh to .msh file for viewing by Gid.
::    -O  Outputs mesh to .off file for viewing by Geomview.
::    -K  Outputs mesh to .vtk file for viewing by Paraview.
::    -J  No jettison of unused vertices from output .node file.
::    -B  Suppresses output of boundary information.
::    -N  Suppresses output of .node file.
::    -E  Suppresses output of .ele file.
::    -F  Suppresses output of .face file.
::    -I  Suppresses mesh iteration numbers.
::    -C  Checks the consistency of the final mesh.
::    -Q  Quiet:  No terminal output except errors.
::    -V  Verbose:  Detailed information, more terminal output.
::    -h  Help:  A brief instruction for using TetGen.


'''
#======================================================================#
#   generate mesh
#======================================================================#

tetras = 0
debug = False

def generate_Preview():

    # toggle OBJECT mode
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode = 'OBJECT', toggle = False)


    config = bpy.context.scene.CONFIG_MeshPy

    vertList = []
    faceList = []
    meshPoints = []
    meshFacets = []
    split_faceList = []
    split_vertList = []
    ob = bpy.context.active_object
    obname = ob.name

    # compute mesh
    compute_vertices(ob, meshPoints)
    compute_polygones(ob, meshFacets)

    if config.make_subdivision == False:
        arg = "Y"
    else:
        arg = ""

    mesh_info = MeshInfo()
    mesh_info.set_points(meshPoints)
    mesh_info.set_facets(meshFacets)
    # args = ("pq" + str(config.ratio_quality) + "a" + str(config.ratio_maxsize) + str(arg))
    '''
    #args = ("VVv")
    args = ("pq")
    tetmesh = build(mesh_info, Options(args),
            verbose = True,
            attributes = False,
            volume_constraints = False,
            max_volume = None,
            diagnose = False,
            insert_points = None)

    #.v.node, .v.edge, .v.face, and .v.cell.
    tetmesh.save_nodes("test")
    tetmesh.save_faces("test")
    tetmesh.save_edges("test")
    tetmesh.save_elements("test")
    #compute_mesh(tetmesh, vertList, faceList)
    '''

def generate_TetMesh_BAK():

    # toggle OBJECT mode
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode = 'OBJECT', toggle = False)
        bpy.context.scene.update()
        config = bpy.context.scene.CONFIG_MeshPy

        tetIndex = 0
        vertList = []
        faceList = []
        meshPoints = []
        meshFacets = []
        split_faceList = []
        split_vertList = []

        ob = bpy.context.active_object
        obname = ob.name

        # lets try to catch the crash position


        # compute mesh
        compute_vertices(ob, meshPoints)
        compute_faces(ob, meshFacets)

        if config.make_subdivision == False:
            arg = "Y"
        else:
            arg = ""

        mesh_info = MeshInfo()
        mesh_info.set_points(meshPoints)
        mesh_info.set_facets(meshFacets)
        debugArg = ""
        # args = (debugArg + "pq" + str(config.ratio_quality) + "a" + str(config.ratio_maxsize) + str(arg))
        # args = ("o2" + str(arg))
        args = "pq"

        tetmesh = build(mesh_info, Options("pq"))
        compute_mesh(tetmesh, vertList, faceList)

        # #all this should only be executed when preview is disabled
        if config.make_split == True:
            # #add counter to iterate to iterate the loop through all tetras
            # print(len(tetmesh.elements))

            while tetIndex < len(tetmesh.elements):
                compute_mesh_split(tetmesh, split_faceList, split_vertList, vertList)
                # print("split_faceList ", tetIndex, ": ", split_faceList[tetIndex])
                # print("split_vertList ", tetIndex, ": ", split_vertList[tetIndex])

                # put this in a separate loop maybe bring some speed up
                # create mesh
                tetname = obname + "Tet"
                tet = create_mesh(tetname, split_vertList[tetIndex], split_faceList[tetIndex])
                # run configs
                enable_game(config, tet)
                enable_physics(config, tet, tetname)

                # bpy.ops.group.create(name='test')
                world_correction(config, ob, tet)

                tetIndex = tetIndex + 1
        else:
            # create mesh
            tetname = obname + "Tet"
            tetMesh = create_mesh(tetname, vertList, faceList)
            # run configs
            enable_game(config, tetMesh)
            enable_physics(config, tetMesh, tetname)
            world_correction(config, ob, tetMesh)


#-----------------------------------------------------------------------------

def generate_TetMesh():

    # toggle OBJECT mode
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode = 'OBJECT', toggle = False)

        # bpy.context.scene.update()
        config = bpy.context.scene.CONFIG_MeshPy

        tetIndex = 0
        vertList = []
        faceList = []
        meshPoints = []
        meshFacets = []
        split_faceList = []
        split_vertList = []

        ob = bpy.context.active_object
        obname = ob.name

        # lets try to catch the crash position


        # compute mesh
        # using polygones instead of faces for bmesh
        # def compute_faces(ob, meshFacets):
        for p in ob.data.polygons:
            meshFacets.append(p.vertices[:])



        # def compute_vertices(ob, meshPoints):
        for v in ob.data.vertices:
            meshPoints.append([v.co[0], v.co[1], v.co[2]])



        mesh_info = MeshInfo()
        mesh_info.set_points(meshPoints)
        mesh_info.set_facets(meshFacets)

        args = "pqY"

        tetmesh = build(mesh_info, Options(args))
        compute_mesh(tetmesh, vertList, faceList)

        # create mesh
        tetname = obname + "Tet"
        # print("here we create the new mesh")
        tetMesh = create_mesh(tetname, vertList, faceList)

#-----------------------------------------------------------------------------

def create_mesh(name, vertList, faceList):
    # TODO: use bm = bmesh.new() bm.from_mesh(mesh)?
    # # maybe use to_mesh?
    me = bpy.data.meshes.new(name)
    me.from_pydata(vertList, [], faceList)
    me.validate(verbose = debug)
    me.update()
    me.update(calc_edges = True)
    tetMesh = bpy.data.objects.new(name, me)
    bpy.context.scene.objects.link(tetMesh)
    bpy.context.scene.update()

    # object display settings
    tetMesh.show_all_edges = True
    tetMesh.show_wire = True
    #    TODO: maybe this output causes the crash?
    #    # http://www.blender.org/documentation/blender_python_api_2_68_release/info_gotcha.html#edit-mode-memory-access
    return(tetMesh)



def compute_mesh(tetmesh, vertList, faceList):
    # print("Mesh Points:")
    for i, p in enumerate(tetmesh.points):
        vertList.append(p[:])
        # print(i, p)
    # print(len(vertList))
    # print(vertList)

    # print("Point numbers in tetrahedra:")
    for i, t in enumerate(tetmesh.elements):
        # print(i, t)
        e1 = [(t[0]), (t[1]), (t[2])]
        e2 = [(t[0]), (t[1]), (t[3])]
        e3 = [(t[0]), (t[2]), (t[3])]
        e4 = [(t[1]), (t[2]), (t[3])]
        faceList.append(e1)
        faceList.append(e2)
        faceList.append(e3)
        faceList.append(e4)
    tetras = len(faceList) * 0.25
    print(tetras)
    # print("tetras: ", len(faceList)*0.25)
    # print("faceList: ", faceList)


def compute_mesh_split(tetmesh, split_faceList, split_vertList, vertList):
    for i, faceIndex in enumerate(tetmesh.elements):
        # print(i,faceIndex)
        # add to face list
        split_faceList.append(i)
        split_faceList[i] = []
        split_faceList[i].append([0, 1, 2])
        split_faceList[i].append([0, 1, 3])
        split_faceList[i].append([1, 2, 3])
        split_faceList[i].append([0, 2, 3])

        # add to vert list
        split_vertList.append(i)
        split_vertList[i] = []
        split_vertList[i].append(vertList[faceIndex[0]])
        split_vertList[i].append(vertList[faceIndex[1]])
        split_vertList[i].append(vertList[faceIndex[2]])
        split_vertList[i].append(vertList[faceIndex[3]])


# using polygones instead of faces for bmesh
def compute_faces(ob, meshFacets):
    for p in ob.data.polygons:
        meshFacets.append(p.vertices[:])

    if debug == True:
        print("meshFacets: ", meshFacets)


def compute_vertices(ob, meshPoints):
    for v in ob.data.vertices:
        vx, vy, vz = v.co[0] * ob.scale[0], v.co[1] * ob.scale[1], v.co[2] * ob.scale[2]
        # print("vcor: ", vx, vy, vz)

        # get origin location
        px, py, pz = ob.location[0], ob.location[1], ob.location[2]
        # print("ocor: ", px, py, pz)

        # world location
        ox, oy, oz = px + vx, py + vy, pz + vz
        # print("wcor: ", "[", ox, oy, oz, "]")

        meshPoints.append([ox, oy, oz])
    if debug == True:
        print("meshPoints: ", meshPoints)


def world_correction(config, ob, tet):
    if config.make_active == True:
        ob.select = False
        tet.select = True
        bpy.context.scene.objects.active = tet
        bpy.ops.object.origin_set(type = 'ORIGIN_GEOMETRY')

        # add object to group
        # #if config.make_split == True:
        # #bpy.ops.object.group_link(group='test')

        # apply source rotation to tet
        print(math.degrees(ob.rotation_euler[0]), math.degrees(ob.rotation_euler[1]), math.degrees(ob.rotation_euler[2]))
        tet.rotation_euler = ob.rotation_euler[0], ob.rotation_euler[1], ob.rotation_euler[2]
    else:
        ob.select = False
        tet.select = True
        bpy.context.scene.objects.active = tet
        bpy.ops.object.origin_set(type = 'ORIGIN_GEOMETRY')

        # add object to group
        # #if config.make_split == True:
        # #bpy.ops.object.group_link(group='test')

        # apply source rotation to tet
        print(math.degrees(ob.rotation_euler[0]), math.degrees(ob.rotation_euler[1]), math.degrees(ob.rotation_euler[2]))
        tet.rotation_euler = ob.rotation_euler[0], ob.rotation_euler[1], ob.rotation_euler[2]
        tet.select = False
        ob.select = True


def enable_physics(config, ob, name):
    if config.make_softbody == True:
        push = 0.999
        ob.modifiers.new(name, 'SOFT_BODY')
        # tet.modifiers.new(tetname, 'COLLISION')
        ob.modifiers[name].settings.use_goal = config.make_softbody_goal
        ob.modifiers[name].settings.push = push


def enable_game(config, ob):
    if config.make_game == True:
        if config.physics_type == '1':
            ob.game.physics_type = 'NAVMESH'
        elif config.physics_type == '2':
            ob.game.physics_type = 'SENSOR'
        elif config.physics_type == '3':
            ob.game.physics_type = 'OCCLUDE'
        elif config.physics_type == '4':
            ob.game.physics_type = 'SOFT_BODY'
        elif config.physics_type == '5':
            ob.game.physics_type = 'RIGID_BODY'
            ob.game.use_collision_bounds = True
            ob.game.use_collision_compound = True
            ob.game.collision_margin = 0.0
            ob.game.collision_bounds_type = 'TRIANGLE_MESH'
        elif config.physics_type == '6':
            ob.game.physics_type = 'DYNAMIC'
        elif config.physics_type == '7':
            ob.game.physics_type = 'STATIC'
        elif config.physics_type == '8':
            ob.game.physics_type = 'NO_COLLISION'


#======================================================================#
#   reset mesh
#======================================================================#
def reset_Mesh():
    # toggle to edit mode, reveal hidden and switch back to object mode for reset
    bpy.ops.object.mode_set(mode = 'EDIT', toggle = False)
    bpy.ops.mesh.reveal()
    bpy.ops.mesh.select_all(action = 'DESELECT')
    bpy.ops.object.mode_set(mode = 'OBJECT', toggle = False)


#======================================================================#
#  update slicer
#======================================================================#
def update_Slicer(self, context):
    config = bpy.context.scene.CONFIG_MeshPy

    # slice distance based on slider percentages
    # #actions performed when in object mode
    ob = bpy.context.active_object
    obname = ob.name
    if ob.mode == 'OBJECT':
        # apply rotation and scale
        applyScale = config.apply_scale
        applyRrotation = config.apply_rotation
        # print("Scale: ", applyScale, "Rotation: ", applyRrotation)
        bpy.ops.object.transform_apply(location = False, rotation = applyRrotation, scale = applyScale)

    # get slice dimensions
    dX, dY, dZ = ob.dimensions[0], ob.dimensions[1], ob.dimensions[2]
    # enable dsiplay settings
    ob.show_all_edges = True

    # vector from pivot to corner
    # 0 & 6 are needed for slice position
    bx0, by0, bz0 = ob.bound_box[0][0], ob.bound_box[0][1], ob.bound_box[0][2]
    bx6, by6, bz6 = ob.bound_box[6][0], ob.bound_box[6][1], ob.bound_box[6][2]
    # print("bbox: ", bx, by, bz)

    # vector to pivot
    ox, oy, oz = ob.location[0], ob.location[1], ob.location[2]
    # print("pcor: " , ox,oy,oz)

    # world location of bounding box corner
    wx0, wy0, wz0 = bx0 + ox, by0 + oy, bz0 + oz
    wx6, wy6, wz6 = bx6 + ox, by6 + oy, bz6 + oz
    # print("Rcor: ", wx, wy, wz)

    # calculate new slice positions
    xSlice0 = dX * 0.01 * config.ratio_xSlice0
    ySlice0 = dY * 0.01 * config.ratio_ySlice0
    zSlice0 = dZ * 0.01 * config.ratio_zSlice0
    # print("slice result: ", xSlice0, ySlice0, zSlice0)

    xSlice6 = dX * 0.01 * config.ratio_xSlice6
    ySlice6 = dY * 0.01 * config.ratio_ySlice6
    zSlice6 = dZ * 0.01 * config.ratio_zSlice6
    # print("slice result: ", xSlice6, ySlice6, zSlice6)

    slice_Mesh(ob, obname, xSlice0, ySlice0, zSlice0, xSlice6, ySlice6, zSlice6, wx0, wy0, wz0, wx6, wy6, wz6)


#======================================================================#
#   Slice mesh
#======================================================================#
def slice_Mesh(ob, obname, xSlice0, ySlice0, zSlice0, xSlice6, ySlice6, zSlice6, wx0, wy0, wz0, wx6, wy6, wz6):

    reset_Mesh()

    for vert in ob.data.vertices:
        index = vert.index
        # vertex coordinates
        vx, vy, vz = vert.co[0], vert.co[1], vert.co[2]
        # print("vcor: ", vx, vy, vz)

        # get origin location
        px, py, pz = ob.location[0], ob.location[1], ob.location[2]
        # print("ocor: ", px, py, pz)

        # world location
        ox, oy, oz = px + vx, py + vy, pz + vz
        # print("wcor: ", ox, oy, oz)

        # when vertex coordinate is bigger than slice position then select them to hide
        if ox < wx0 + xSlice0:
            # print(index, "ox: ", ox, ":", wx0+xSlice0)
            vert.select = True
        if oy < wy0 + ySlice0:
            # print(index, "vy: ",vy)
            vert.select = True
        if oz < wz0 + zSlice0:
            # print(index, "vz: ",vz)
            vert.select = True
        if ox > wx6 - xSlice6:
            # print(index, "vx: ",vx)
            vert.select = True
        if oy > wy6 - ySlice6:
            # print(index, "vy: ",vy)
            vert.select = True
        if oz > wz6 - zSlice6:
            # print(index, "vz: ",vz)
            vert.select = True

    bpy.ops.object.mode_set(mode = 'EDIT', toggle = False)
    bpy.context.scene.tool_settings.mesh_select_mode = (True, False, False)

    # hide selected
    bpy.ops.mesh.hide(unselected = False)


#======================================================================#
#     GUI
#======================================================================#
class UIElements(bpy.types.PropertyGroup):

    # tetgen checkboxes
    make_subdivision = bpy.props.BoolProperty(name="Subdivide Surface",
                                              default=True,
                                              description="Boundary facets/segments splitting.")
    
    make_active = bpy.props.BoolProperty(name="Make active",
                                         default=True,
                                         description="make generated mesh active")
    
    make_split = bpy.props.BoolProperty(name="Split",
                                        default=False,
                                        description="generate each tetrahedron as new object")
    
    make_softbody = bpy.props.BoolProperty(name="Softbody",
                                           default=False,
                                           description="new tetras will become softbodys")
    
    make_softbody_goal = bpy.props.BoolProperty(name="Softbody Goal",
                                                default=False,
                                                description="new tetras will become softbodys")
    
    make_game = bpy.props.BoolProperty(name="Game Physics",
                                       default=False,
                                       description="new tetras will become game objects")

    # tetgen sliders
    ratio_quality = bpy.props.FloatProperty(name="quality",
                                            subtype='FACTOR',
                                            min=1.01,
                                            max=2.5,
                                            default=2.0,
                                            step=0.01,
                                            description="")
    
    ratio_maxsize = bpy.props.FloatProperty(name="max size",
                                            subtype='NONE',
                                            min=0.000001,
                                            max=10.000000,
                                            default=5.000000,
                                            step=0.01,
                                            description="")

    # tetgen dropdown
    itemlist = [('1', 'Navigation Mesh', 'test1'),
                ('2', 'Sensor', 'test2'),
                ('3', 'Occlude', 'test3'),
                ('4', 'Soft Body', 'test4'),
                ('5', 'Rigid Body', 'test5'),
                ('6', 'Dynamic', 'test6'),
                ('7', 'Static', 'test7'),
                ('8', 'None', 'test8')
                ]
    physics_type = bpy.props.EnumProperty(name="Physics Type",
                                          items=itemlist,
                                          default='5')

    # mesh slicer checkboxes
    apply_scale = bpy.props.BoolProperty(name="Apply scale",
                                         default=True,
                                         description="apply scale to object before slicing")
    
    apply_rotation = bpy.props.BoolProperty(name="Apply rotation",
                                            default=False,
                                            description="apply rotation to object before slicing")
    # mesh slicer sliders
    ratio_xSlice0 = bpy.props.FloatProperty(name="+ X ",
                                            subtype='PERCENTAGE',
                                            min=0,
                                            max=100,
                                            default=0,
                                            description="+ X axis slicer",
                                            update=update_Slicer)
    
    ratio_ySlice0 = bpy.props.FloatProperty(name="+ Y ",
                                            subtype='PERCENTAGE',
                                            min=0,
                                            max=100,
                                            default=0,
                                            description="+ Y axis slicer",
                                            update=update_Slicer)
    
    ratio_zSlice0 = bpy.props.FloatProperty(name="+ Z ",
                                            subtype='PERCENTAGE',
                                            min=0,
                                            max=100,
                                            default=0,
                                            description="+ Z axis slicer",
                                            update=update_Slicer)
    
    ratio_xSlice6 = bpy.props.FloatProperty(name="- X ",
                                            subtype='PERCENTAGE',
                                            min=0,
                                            max=100,
                                            default=0,
                                            description="- X axis slicer",
                                            update=update_Slicer)
    
    ratio_ySlice6 = bpy.props.FloatProperty(name="- Y ",
                                            subtype='PERCENTAGE',
                                            min=0,
                                            max=100,
                                            default=0,
                                            description="- Y axis slicer",
                                            update=update_Slicer)
    
    ratio_zSlice6 = bpy.props.FloatProperty(name="- Z ",
                                            subtype='PERCENTAGE',
                                            min=0,
                                            max=100,
                                            default=0,
                                            description="- Z axis slicer",
                                            update=update_Slicer)


class OBJECT_PT_MeshPy(bpy.types.Panel):
    bl_label = "MeshPy"
    bl_idname = "OBJECT_PT_MeshPy"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    bl_default_closed = True

    def draw(self, context):

        config = bpy.context.scene.CONFIG_MeshPy
        layout = self.layout
        ob = context.object
        ob_type = ob.type.capitalize()
        objects = bpy.context.selected_objects
        game = ob.game

        if not objects:
            row = layout.row()
            row.label(text = "No Active Object", icon = 'ERROR')
            return

        if ob_type == 'Mesh':
            #=====================================#
            #   tetgen
            #=====================================#

            row = layout.row()
            row.label(text = "TetGen", icon = 'MESH_ICOSPHERE')

            # checkboxes
            split = layout.split()
            col = split.column()
            row = col.row()
            row.prop(config, "make_subdivision")
            row.prop(config, "make_split")
            row.prop(config, "make_active")

            row = col.row()
            row.prop(config, "make_softbody")
            if config.make_softbody == True:
                row.prop(config, "make_softbody_goal")

            row = col.row()
            row.prop(config, "make_game")
            if config.make_game == True:
                row.prop(config, "physics_type")

            # slice sliders
            box = col.box()
            box.column().prop(config, "ratio_quality")
            box.column().prop(config, "ratio_maxsize")

            # tetgen button
            # box = col.box()
            row = col.row()
            row.operator("mesh.meshpy_preview", text = "Generate Preview")
            row.label(text = "tetras: " + str(tetras))
            col.operator("mesh.meshpy_tetgen", text = "Generate Tetmesh")


            #=====================================#
            #     mesh slicer
            #=====================================#
            # checkboxes
            row = layout.row()
            row = layout.row()
            row.label(text = "Mesh Slicer", icon = 'EDITMODE_HLT')

            split = layout.split()
            # col = split.column().box()
            col = split.column()
            row = col.row()
            row.prop(config, "apply_scale")
            row.prop(config, "apply_rotation")

            # slice sliders
            split = layout.split()
            col = split.column().box()
            col.column().prop(config, "ratio_xSlice0")
            col.column().prop(config, "ratio_ySlice0")
            col.column().prop(config, "ratio_zSlice0")

            col = split.column().box()
            col.column().prop(config, "ratio_xSlice6")
            col.column().prop(config, "ratio_ySlice6")
            col.column().prop(config, "ratio_zSlice6")

            # slice button
            # row = layout.row().box()
            # row.operator("mesh.mesh_slicer", text="Update Mesh")

            # reset button
            row.operator("mesh.mesh_slicer_reset", text = "Reset Mesh")

        else:
            row = layout.row()
            row.label(text = "Object is no mesh", icon = 'ERROR')
            return


#======================================================================#
# tetgen button
#======================================================================#
class OBJECT_OP_MeshPy_TetGen(bpy.types.Operator):
    bl_idname = "mesh.meshpy_tetgen"
    bl_label = "generate tetmesh"
    bl_description = "generates tetmesh"

    def execute(self, context):
        config = bpy.context.scene.CONFIG_MeshPy
        generate_TetMesh()
        return {'FINISHED'}

class OBJECT_OP_MeshPy_Preview(bpy.types.Operator):
    bl_idname = "mesh.meshpy_preview"
    bl_label = "generate preview"
    bl_description = "generates preview"

    def execute(self, context):
        config = bpy.context.scene.CONFIG_MeshPy
        generate_Preview()
        return {'FINISHED'}

#======================================================================#
#   mesh reset button
#======================================================================#
class OBJECT_OP_MeshSlicer_Reset(bpy.types.Operator):
    bl_idname = "mesh.mesh_slicer_reset"
    bl_label = "reset mesh"
    bl_description = "resets mesh"


    def execute(self, context):
        config = bpy.context.scene.CONFIG_MeshPy
        reset_Mesh()
        return {'FINISHED'}

#======================================================================#
#     register
#======================================================================#
def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.CONFIG_MeshPy = bpy.props.PointerProperty(type = UIElements)


def unregister():
    bpy.utils.unregister_module(__name__)
    if bpy.context.scene.get('CONFIG_MeshPy') != None:
        del bpy.context.scene['CONFIG_MeshPy']
    try:
        del bpy.types.Scene.CONFIG_MeshPy
    except:
        pass


if __name__ == "__main__":
    register()

print(" ")
print("*                             initialized                                      *")
print("*------------------------------------------------------------------------------*")
print(" ")
