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



from meshpy.tet import MeshInfo, build, Options
import bmesh
import bpy
import math
import mathutils


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


class UIElements(bpy.types.PropertyGroup):

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
    bl_label = "MeshSlicer"
    bl_idname = "OBJECT_PT_MeshSlicer"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    bl_default_closed = True

    def draw(self, context):

        config = bpy.context.scene.CONFIG_MeshSlicer
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


class OBJECT_OP_MeshSlicer_Reset(bpy.types.Operator):
    bl_idname = "mesh.mesh_slicer_reset"
    bl_label = "reset mesh"
    bl_description = "resets mesh"


    def execute(self, context):
        config = bpy.context.scene.CONFIG_MeshSlicer
        reset_Mesh()
        return {'FINISHED'}

