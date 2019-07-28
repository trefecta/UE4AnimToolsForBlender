import bpy

class UE4ANIMTOOLS_PT_AnimationTools(bpy.types.Panel):
    bl_label = 'UE4 Animation Tools'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'UE4 Animation'
    bl_order = 1

    # bpy.types.WindowsManager.UE4AnimTools.ui_toggles
    
    def draw(self, context):
        layout = self.layout
        wm_props = context.window_manager.UE4AnimTools

        colflow = layout.column_flow()
        colflow.row().prop(context.scene.UE4AnimTools, 'armature', icon='OBJECT_DATA')

        row = layout.row()
        row.prop(wm_props, 'pin_animation_toggle',
            icon='TRIA_DOWN' if wm_props.pin_animation_toggle else 'TRIA_RIGHT',
            icon_only=True,
            emboss=False
        )
        row.label(text='Pin Armature Animation')

        if wm_props.pin_animation_toggle:
            layout.row().operator('ue4animtools.pin_animation')

            layout.row().prop(context.scene.UE4AnimTools, 'batch_filepath_src', text='Source Filepath')
            layout.row().prop(context.scene.UE4AnimTools, 'batch_filepath_bln', text='Blender Filepath')
            layout.row().prop(context.scene.UE4AnimTools, 'batch_filepath_dst', text='Destination Filepath')

            layout.row().operator('ue4animtools.pin_batch_animation')