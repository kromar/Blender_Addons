import bpy
from bpy.props import IntProperty


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
            context.scene.slider += 1
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


def register():
    bpy.types.Scene.slider = IntProperty(default=0,min=0,max=1000)
    bpy.utils.register_class(ModalTimerOperator)


def unregister():
    bpy.utils.unregister_class(ModalTimerOperator)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.wm.modal_timer_operator()