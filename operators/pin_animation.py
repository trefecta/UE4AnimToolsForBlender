import bpy

from properties import UE4AnimToolProperties

class UE4ANIMTOOLS_OT_PinAnimation(bpy.types.Operator):
    bl_idname = 'ue4animtools.pin_animation'
    bl_label = 'Apply to Selected Armature'
    bl_category = 'UE4|Animation'
    bl_description = """Translates armature animation from armature to the `pelvis` bone, pinning armature object to origin."""

    @classmethod
    def poll(cls, context):
        obj = context.object.UE4AnimTools.armature
        return (obj is not None and obj.pose is not None)

    def execute(self, context):
        obj = context.object.UE4AnimTools.armature
        return {'FINISHED'}