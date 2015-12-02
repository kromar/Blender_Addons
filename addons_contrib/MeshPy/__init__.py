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
# module binary downloads
#======================================================================#
'''
    http://www.lfd.uci.edu/~gohlke/pythonlibs/
'''


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
    
if "bpy" in locals():
    import importlib
    importlib.reload(mesh_Meshpy)
else:
    from . import mesh_Meshpy

import bpy


def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.CONFIG_MeshPy = bpy.props.PointerProperty(type = UIElements)
    #bpy.types.Scene.CONFIG_MeshSlicer = bpy.props.PointerProperty(type = UIElements)


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
    