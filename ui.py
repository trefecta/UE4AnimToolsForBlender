import bpy

class UE4ANIMTOOLS_Mixin:
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'UE4 Animation Tools'

    @classmethod
    def poll(cls, context):
        return (context.object is not None)

class UE4ANIMTOOLS_PT_PinAnimation(UE4ANIMTOOLS_Mixin, bpy.types.Panel):
    bl_label = 'Pin To Root'
    bl_order = 2

    @classmethod
    def poll(cls, context):
        if context.object.select_get() and context.object.type == 'ARMATURE':
            context.scene.UE4AnimTools.armature = context.object
            return True

    def draw(self, context):
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        col = layout.column(align=True)
        subcol = col.column()

        subcol.operator('ue4animtools.pin_animation')
        subcol.separator()


class UE4ANIMTOOLS_PT_PinBatchFBXOperator(UE4ANIMTOOLS_Mixin, bpy.types.Panel):
    bl_label = 'Batch Pin To Root'
    bl_order = 3

    def draw(self, context):
        scn_props = context.scene.UE4AnimTools
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        col = layout.column(align=False)
        subcol = col.column()

        subcol.prop(scn_props, 'batch_filepath_src', text='Source Filepath')
        subcol.prop(scn_props, 'batch_filepath_bln', text='Blender Filepath')
        subcol.prop(scn_props, 'batch_filepath_dst', text='Destination Filepath')
        subcol.separator()
        subcol.operator('ue4animtools.pin_batch_animation')


class UE4ANIMTOOLS_PT_CopyUE4MannequinBones(UE4ANIMTOOLS_Mixin, bpy.types.Panel):
    bl_label = 'Copy UE4 Mannequin Bones'
    bl_order = 4

    @classmethod
    def poll(cls, context):
        if context.object.select_get() and context.object.type == 'ARMATURE':
            context.scene.UE4AnimTools.armature = context.object
            return True

    def draw(self, context):
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        col = layout.column(align=True)
        subcol = col.column()

        subcol.operator('ue4animtools.copy_ue4_mannequin_bones')