import bpy
from pathlib import Path

class UIToggleProperties(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name='Toggle', default='')
    value: bpy.props.BoolProperty(name='Toggle', default=False)

class WindowManager_UE4AnimToolProperties(bpy.types.PropertyGroup):
    # ui_toggles: bpy.props.CollectionProperty(name='UI Toggles', type=UIToggleProperties)
    pin_animation_toggle: bpy.props.BoolProperty(name='Pin Animation Toggle', default=False)
    copy_bone_roll_toggle: bpy.props.BoolProperty(name='Edit Bones Toggle', default=False)

class Scene_UE4AnimToolProperties(bpy.types.PropertyGroup):
    armature: bpy.props.PointerProperty(name='Armature', type=bpy.types.Object)
    batch_filepath_src: bpy.props.StringProperty(name='Batch Filepath: Source', subtype='FILE_PATH')
    batch_filepath_bln: bpy.props.StringProperty(name='Batch Filepath: Blender', subtype='FILE_PATH')
    batch_filepath_dst: bpy.props.StringProperty(name='Batch Filepath: Destination', subtype='FILE_PATH')