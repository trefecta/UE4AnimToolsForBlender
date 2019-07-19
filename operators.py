import bpy

from .properties import UE4AnimToolProperties

class OBJECT_OT_PinAnimation(bpy.types.Operator):
    bl_idname = 'object.pin_animation'
    bl_label = 'Pin Animation'

    @classmethod
    def poll(cls, context):
        return (context.scene.UE4AnimTools.armature is not None)

    def execute(self, context):
        obj = context.scene.UE4AnimTools.armature
        return {'FINISHED'}