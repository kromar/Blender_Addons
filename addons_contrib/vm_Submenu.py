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

'''
todo:
    
bugs:

changelog:
    "version": 1.0.0
        -initial release
    
        
'''

# ----------------------------------------------------------------------------#

import bpy
import os
from bpy.props import *

#import ExportOBJ

#addon description
bl_info = {
    "name": "Export: Submenu",
    "author": "Daniel Grauer (kromar)",
    "version": (1, 0, 0),
    "blender": (2, 6, 0),
    "category": "Import-Export",
    "category": "kromar",
    "location": "File > Export",
    "description": "adds an extra submenu in th export section",
    "warning": '', # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": ""
    }

print(" ")
print("*------------------------------------------------------------------------------*")
print("*                          initializing ExportSubmenu                     *")
print(" ")


# ----------------------------------------------------------------------------#
#    menus
# ----------------------------------------------------------------------------#

#this draws the new menu in FILE>EXPORT
def My_Menu(self, context):
    bl_label = "export menu"
    bl_idname = "OBJECT_MT_menu"
    
    #try to generate menu with our menu class 
    self.layout.menu(My_Menu_Content.bl_idname, text = "Content")
       
# ----------------------------------------------------------------------------#

#draw content in export menus
class My_Menu_Content(bpy.types.Menu):
    bl_label = "Content export menu"
    bl_idname = "OBJECT_MT_Content"
    
    def draw(self, context):
        pass


# ----------------------------------------------------------------------------#   
    
def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_export.append(My_Menu)


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_export.remove(My_Menu)

if __name__ == "__main__":
    register()
    

print(" ")
print("*                             initialized                                      *")
print("*------------------------------------------------------------------------------*")
print(" ")
