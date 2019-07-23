import bpy

class UIToggleProperties(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name='Toggle', default='')
    value: bpy.props.BoolProperty(name='Toggle', default=False)

class WindowManager_UE4AnimToolProperties(bpy.types.PropertyGroup):
    # ui_toggles: bpy.props.CollectionProperty(name='UI Toggles', type=UIToggleProperties)
    pin_animation_toggle: bpy.props.BoolProperty(name='Pin Animation Toggle', default=False)

class Scene_UE4AnimToolProperties(bpy.types.PropertyGroup):
    armature: bpy.props.PointerProperty(name='Armature', type=bpy.types.Object)