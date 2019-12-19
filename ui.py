import bpy

class UE4ANIMTOOLS_PT_AnimationTools(bpy.types.Panel):
    bl_label = 'UE4 Animation Tools'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'UE4 Animation Tools'
    bl_order = 1

    # bpy.types.WindowsManager.UE4AnimTools.ui_toggles

    def draw(self, context):
        scn_props = context.scene.UE4AnimTools

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        col = layout.column(align=True)
        subcol = col.column()
        subcol.prop(scn_props, 'armature', icon='OBJECT_DATA')



class UE4ANIMTOOLS_PT_PinAnimation(bpy.types.Panel):
    bl_label = 'Pin Armature Animation'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'UE4 Animation Tools'
    bl_order = 2

    @classmethod
    def poll(cls, context):
        armature = context.scene.UE4AnimTools.armature
        return (armature is not None and armature.pose is not None)

    def draw(self, context):
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        col = layout.column(align=True)
        subcol = col.column()

        subcol.operator('ue4animtools.pin_animation')


class UE4ANIMTOOLS_PT_PinBatchFBXOperator(bpy.types.Panel):
    bl_label = 'Pin Batch FBX Operator'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'UE4 Animation Tools'
    bl_order = 3

    def draw(self, context):
        scn_props = context.scene.UE4AnimTools
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        col = layout.column(align=True)
        subcol = col.column()

        subcol.prop(scn_props, 'batch_filepath_src', text='Source Filepath')
        subcol.prop(scn_props, 'batch_filepath_bln', text='Blender Filepath')
        subcol.prop(scn_props, 'batch_filepath_dst', text='Destination Filepath')

        subcol.operator('ue4animtools.pin_batch_animation')


class UE4ANIMTOOLS_PT_CopyUE4MannequinBones(bpy.types.Panel):
    bl_label = 'Copy UE4 Mannequin Bones'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'UE4 Animation Tools'
    bl_order = 4

    @classmethod
    def poll(cls, context):
        armature = context.scene.UE4AnimTools.armature
        return (armature is not None and armature.pose is not None)

    def draw(self, context):
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        col = layout.column(align=True)
        subcol = col.column()

        subcol.operator('ue4animtools.copy_ue4_mannequin_bones')