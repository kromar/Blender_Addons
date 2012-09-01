import bpy

# remove fake user from all image data
for tex in bpy.data.images:
	tex.use_fake_user = False
	print(tex)
	
for tex in bpy.data.textures:
	tex.use_fake_user = False
	print(tex)
	
for tex in bpy.data.brushes:
	tex.use_fake_user = False
	print(tex)