import bpy
import pickle
from pathlib import Path

class UE4ANIMTOOLS_OT_CopyUE4MannequinBonesOperator(bpy.types.Operator):
    bl_idname = "ue4animtools.copy_ue4_mannequin_bones"
    bl_label = "Copy UE4 Mannequin Bones"

    @classmethod
    def poll(cls, context):
        armature = context.scene.UE4AnimTools.armature
        return (armature is not None and armature.pose is not None)

    def execute(self, context):
        return CopyUE4MannequinBones(context).run()


class CopyUE4MannequinBones():
    def __init__(self, context):
        self.context = context

        self.armature = context.scene.UE4AnimTools.armature
        self.bone_data = None
        self.mannequin_bone_data_filepath = Path(__file__).resolve() / '..' / '..' / 'data' / 'UE4_Mannequin_Bone_Data.pkl'

        with self.mannequin_bone_data_filepath.open('rb') as fd:
            self.bone_data = pickle.load(fd)

    def run(self):
        changed_bones = {}

        bpy.ops.object.mode_set(mode='EDIT')
        for edit_bone in self.armature.data.edit_bones:
            name = edit_bone.name
            data = self.bone_data.get(edit_bone.name)
            if data:
                for k, v in data.items():
                    if k != 'rotation' and k != 'parent' and k != 'vector' and k != 'basis' and 'use_' not in k:
                        if getattr(edit_bone, k) != v:
                            # bone will be modified
                            setattr(edit_bone, k, v)
                            changed_bones[name] = True
                    elif k == 'parent':
                        edit_bone.parent = self.armature.data.edit_bones[edit_bone.name]

        print("Bones changed: {}".format(', '.join(list(changed_bones.keys()))))
        return {'FINISHED'}