import bpy
from mathutils import *
import math
from pathlib import Path

from ..properties import Scene_UE4AnimToolProperties as UE4AnimToolProperties

class UE4ANIMTOOLS_OT_PinAnimation(bpy.types.Operator):
    bl_idname = 'ue4animtools.pin_animation'
    bl_label = 'Apply to Selected Armature'
    bl_category = 'UE4 Animation'
    bl_description =   (
        "Translates armature animation from the object root to the `pelvis` bone,"
        "pinning the armature root of the armature object to origin."
    )

    @classmethod
    def poll(cls, context):
        armature = context.scene.UE4AnimTools.armature
        return (armature is not None and armature.pose is not None)

    def execute(self, context):
        armature = context.scene.UE4AnimTools.armature
        return PinAnimation(context, armature).run()


class UE4ANIMTOOLS_OT_PinBatchFBXOperator(bpy.types.Operator):

    bl_idname = "ue4animtools.pin_batch_animation"
    bl_label = "Apply to FBX armatures in 'Source'"
    bl_category = 'UE4 Animation'
    bl_description =   (
        "Imports `*.fbx` files from a specified directory,"
        "translating the armature animation from the object root motion to the `pelvis` bone"
        "before pinning the armature root to the origin.\n"
        "The file is saved as a `*.blend` in a `./Blender` sibling directory be default, or an optionally specified directory,"
        "exporting a new `*.fbx` to a `./UE4` sibling directory by default, or an optionally specified directory.\n"
        "These directories are created if they do not exist."
    )

    @classmethod
    def poll(cls, context):
        batch_filepath_src = Path(context.scene.UE4AnimTools.batch_filepath_src)
        return (batch_filepath_src.exists())

    def execute(self, context):
        return PinBatchAnimation(context).run()


class PinAnimation:
    """
        Translates armature animation from entire armature object to the `pelvis` bone, pinning armature object to origin.
    """
    def __init__(self, context, armature):
        self.ctx = context
        self.initial_mode = bpy.context.object.mode
        self.scaling = 1

        self.armature = armature
        self.armature.name = 'Armature'
        self.armature.data.name = self.armature.name

        self.start_frame, self.end_frame = [int(i) for i in self.armature.animation_data.action.frame_range]

        self.ctx.scene.cursor.location = Vector((0, 0, 0))
        self.ctx.scene.frame_set(self.start_frame)
        self.ctx.scene.frame_end = self.end_frame

        self.new_pelvis_locs = []
        self.new_pelvis_rots = []

        if not self.armature.pose.bones[0].name in ('root', 'Root'):
            self.add_root_bone()

        self.armature.pose.bones[0].name = 'root'

        self.root_pose_bone = self.armature.pose.bones['root']
        self.pelvis_pose_bone = self.armature.pose.bones['pelvis']

        self.root_pose_bone.rotation_mode = 'QUATERNION'
        self.pelvis_pose_bone.rotation_mode = 'QUATERNION'

    def run(self):
        self.remove_end_bones()
        self.edit_pelvis_relations()
        self.set_root_to_origin()
        self.loop_all_frames(self.calculate_parameters)
        self.loop_all_frames(self.align_obj)
        # self.loop_all_frames(self.set_armature_to_origin)
        bpy.ops.object.mode_set(mode=(self.initial_mode))
        self.ctx.scene.frame_set(self.start_frame)
        return {'FINISHED'}

    def translate_vector_axes(self, coord):
        """Convert between world and pose space."""
        return Vector((
         coord.x,
         coord.z,
         -coord.y))

    def add_root_bone(self):
        """Add a root bone to the armature."""
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.armature.bone_primitive_add(name='root')
        root_edit = self.armature.data.edit_bones['root']
        pelvis_edit = self.armature.data.edit_bones['pelvis']
        root_edit.head = Vector((0, 0, 0))
        root_edit.tail = pelvis_edit.head
        bpy.ops.armature.select_all(action='DESELECT')
        self.armature.data.edit_bones.active = root_edit
        pelvis_edit.select = True
        bpy.ops.armature.parent_set(type='OFFSET')
        self.armature.update_from_editmode()

    def loop_all_frames(self, fns, verbose=False):
        for frame in range(self.start_frame - 1, self.end_frame + 1):
            self.ctx.scene.frame_set(frame)
            fns(frame)

    def remove_end_bones(self):
        bpy.ops.object.mode_set(mode='EDIT')
        for bone in self.armature.data.edit_bones:
            if '_end' in bone.name:
                self.armature.data.edit_bones.remove(bone)

        bpy.ops.object.mode_set(mode='POSE')
        self.armature.update_from_editmode()

    def set_root_to_origin(self):
        bpy.ops.object.mode_set(mode='EDIT')
        root_edit = self.armature.data.edit_bones['root']
        root_edit.head = Vector((0, 0, 0))
        tail_z = 0.5
        root_edit.tail = Vector((0, 0, tail_z))
        bpy.ops.object.mode_set(mode='POSE')
        self.armature.update_from_editmode()

    def set_armature_to_origin(self, frame):
        self.armature.location = Vector((0, 0, 0))
        self.armature.keyframe_insert(data_path='location', frame=frame)
        self.armature.rotation_euler = Euler((0, 0, 0))
        self.armature.keyframe_insert(data_path='rotation_euler', frame=frame)
        self.armature.rotation_quaternion = Quaternion((1, 0, 0, 0))
        self.armature.keyframe_insert(data_path='rotation_quaternion', frame=frame)

    def edit_pelvis_relations(self):
        bpy.ops.object.mode_set(mode='EDIT')
        pelvis_edit = self.armature.data.edit_bones['pelvis']
        pelvis_edit.use_connect = False
        pelvis_edit.use_inherit_rotation = False
        pelvis_edit.use_local_location = False
        pelvis_edit.use_inherit_scale = False
        bpy.ops.object.mode_set(mode='POSE')
        self.armature.update_from_editmode()

    def calculate_parameters(self, frame):
        self.pelvis_pose_bone.bone.select = True
        current_armature_basis = self.armature.matrix_basis.copy()

        wrt_current_origin = lambda x: current_armature_basis @ x

        new_pelvis_rot = wrt_current_origin(self.pelvis_pose_bone.matrix.copy()).to_quaternion()
        new_pelvis_rot.rotate(self.pelvis_pose_bone.matrix.to_quaternion().conjugated())

        # Get the difference between the world space and the scaled pose space
        # this is the offset
        pose_pelvis_loc = self.pelvis_pose_bone.matrix.to_translation()
        current_pelvis_loc = wrt_current_origin(pose_pelvis_loc)
        new_pelvis_loc = (current_pelvis_loc - (self.pelvis_pose_bone.matrix.to_translation() / self.scaling))

        self.new_pelvis_rots.append(new_pelvis_rot)
        self.new_pelvis_locs.append(self.translate_vector_axes(new_pelvis_loc) * self.scaling)

    def update_pelvis_location(self, frame):
        self.pelvis_pose_bone.bone.select = True
        self.pelvis_pose_bone.location = self.new_pelvis_locs[frame]
        self.pelvis_pose_bone.keyframe_insert(data_path='location', frame=frame)

    def update_pelvis_rotation(self, frame):
        self.pelvis_pose_bone.bone.select = True
        self.pelvis_pose_bone.rotation_quaternion = self.new_pelvis_rots[frame]
        self.pelvis_pose_bone.keyframe_insert(data_path='rotation_quaternion', frame=frame)

    def align_obj(self, frame):
        self.update_pelvis_rotation(frame)
        self.update_pelvis_location(frame)
        self.set_armature_to_origin(frame)


class PinBatchAnimation():
    """
        Imports  `*.fbx` files from a specified directory, pinning the root to the origin.

        The file is saved as a `*.blend` in a `./Blender` sibling directory or an optionally specified directory,
        exporting a new `*.fbx` to a `./UE4` sibling directory or an optionally specified directory.

        Directories are created if they do not exist.
    """
    def __init__(self, context):
        self.batch_filepath_src = Path(context.scene.UE4AnimTools.batch_filepath_src)
        self.batch_filepath_bln = Path(context.scene.UE4AnimTools.batch_filepath_bln or self.batch_filepath_src.parent / 'Blender').resolve()
        self.batch_filepath_dst = Path(context.scene.UE4AnimTools.batch_filepath_dst or self.batch_filepath_src.parent / 'UE4').resolve()

        self.batch_filepath_bln.mkdir(parents=True, exist_ok=True)
        self.batch_filepath_dst.mkdir(parents=True, exist_ok=True)

    def run(self):
        for filepath in self.batch_filepath_src.glob('**/*.fbx'):
            print('Working on {}'.format(filepath))
            for a in bpy.data.actions:
                bpy.data.actions.remove(a)

            for a in bpy.data.armatures:
                bpy.data.armatures.remove(a)

            if list(bpy.data.objects):
                if bpy.context.mode != 'OBJECT':
                    # BAD HACK
                    for _ in range(0xFFFFFF):
                        if bpy.ops.object.mode_set.poll():
                            break
                    bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.delete({'selected_objects': [obj for obj in bpy.data.objects]}, use_global=True)

            bpy.ops.import_scene.fbx(
                filepath=str(filepath)
                # automatic_bone_orientation=True,
                # axis_forward='-Y',
                # axis_up = 'Z'
            )

            armature_name = 'Armature'

            armature = bpy.context.scene.objects[armature_name]

            for child in armature.children:
                child.hide_set(state=True)

            if not armature:
                print('Something is wrong with {}'.format(filepath))
                break

            bpy.data.objects[armature_name].select_set(state=True)
            PinAnimation(bpy.context, armature).run()

            current_action = list(bpy.data.actions)[-1]

            current_action.name = filepath.stem

            bpy.ops.export_scene.fbx(
                filepath=str(self.batch_filepath_dst / filepath.name),
                object_types={'ARMATURE'},
                use_selection=True,
                add_leaf_bones=False
                # These screw up the import as of UE4.23
                # axis_forward='-Y',
                # axis_up = 'Z'
            )

            bpy.ops.wm.save_as_mainfile(filepath=str(self.batch_filepath_bln / (filepath.stem + '.blend')))

        bpy.ops.wm.read_homefile(app_template="")
        return {'FINISHED'}