import bpy

class MoveOperator(bpy.types.Operator):
    bl_name = "object.move_oberator"
    bl_label = "Move Operator"
    
    def execute(self, context):
        context.active_object.location.x += 1.0
        return{'FINISHED'}

def register():
    bpy.utils.register_class(MoveOperator)
    
if __name__ == "__main__":
    register()