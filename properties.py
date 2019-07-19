import bpy

class UE4AnimToolProperties(bpy.types.PropertyGroup):
    armature: bpy.props.PointerProperty(name='Armature', type=(bpy.types.Object))