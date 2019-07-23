import bpy
from mathutils import *
import math, numpy as np

from ..properties import Scene_UE4AnimToolProperties as UE4AnimToolProperties

class UE4ANIMTOOLS_OT_PinAnimation(bpy.types.Operator):
    bl_idname = 'ue4animtools.pin_animation'
    bl_label = 'Apply to Selected Armature'
    bl_category = 'UE4|Animation'
    bl_description = """Translates armature animation from armature to the `pelvis` bone, pinning armature object to origin."""

    @classmethod
    def poll(cls, context):
        armature = context.scene.UE4AnimTools.armature
        return (armature is not None and obj.pose is not None)

    def execute(self, context):
        armature = context.scene.UE4AnimTools.armature
        return PinAnimation(context, armature).run()

class PinAnimation:
    def __init__(self, context, armature):
        self.ctx = context
        self.initial_mode = bpy.context.object.mode
        self.scaling = 100

        self.armature = armature
        self.armature.name = 'armature'
        self.armature.data.name = self.armature.name

        self.start_frame, self.end_frame = [int(i) for i in self.armature.animation_data.action.frame_range]

        self.ctx.scene.cursor.location = Vector((0, 0, 0))
        self.ctx.scene.frame_set(self.start_frame)
        self.ctx.scene.frame_end = self.end_frame

        self.init_armature_basis = self.armature.matrix_basis.copy()
        self.wrt_init_origin = lambda x: self.init_armature_basis @ x
        self.wrt_init_armature = lambda x: self.init_armature_basis.inverted() @ x

        self.new_obj_locs = []
        self.new_root_locs = []
        self.new_pelvis_locs = []
        self.new_pelvis_rots = []

        has_root_bone = self.armature.pose.bones[0].name in ('Root', 'root')
        if not has_root_bone:
            self.add_root_bone()

        self.armature.pose.bones[0].name = 'Root'

        if 'hips' in self.armature.pose.bones:
            self.armature.pose.bones['hips'].name = 'pelvis'
         
        self.armature.pose.bones['Root'].rotation_mode = 'QUATERNION'
        self.armature.pose.bones['pelvis'].rotation_mode = 'QUATERNION'
        self.init_pelvis_loc = self.armature.pose.bones['pelvis'].matrix.copy().to_translation()


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

    def to_degrees(self, rot):
        """Convert a Euler from radians to degrees."""
        return Vector([math.degrees(a) for a in rot])

    def translate_vector_axes(self, coord):
        """Convert between world and pose space."""
        return Vector((
         coord.x,
         coord.z,
         -coord.y))


    def add_root_bone(self):
        """Add a root bone to the armature."""
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.armature.bone_primitive_add(name='Root')
        root_edit = self.armature.data.edit_bones['Root']
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
        root_edit = self.armature.data.edit_bones['Root']
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
        pelvis_pose = self.armature.pose.bones['pelvis']
        pelvis_bone = pelvis_pose.bone
        pelvis_bone.select = True
        current_armature_basis = self.armature.matrix_basis.copy()

        wrt_current_origin = lambda x: current_armature_basis @ x

        new_pelvis_rot = wrt_current_origin(pelvis_pose.matrix.copy()).to_quaternion()
        new_pelvis_rot.rotate(pelvis_pose.matrix.to_quaternion().conjugated())
        
        # Get the difference between the world space and the scaled pose space
        # this is the offset
        pose_pelvis_loc = pelvis_pose.matrix.to_translation()
        current_pelvis_loc = wrt_current_origin(pose_pelvis_loc)
        new_pelvis_loc = (current_pelvis_loc - pelvis_pose.matrix.to_translation() / 100)

        self.new_pelvis_rots.append(new_pelvis_rot)
        self.new_pelvis_locs.append(self.translate_vector_axes(new_pelvis_loc) * 100)

    def update_pelvis_location(self, frame):
        pelvis_pose = self.armature.pose.bones['pelvis']
        pelvis_pose.bone.select = True
        pelvis_pose.location = self.new_pelvis_locs[frame]
        pelvis_pose.keyframe_insert(data_path='location', frame=frame)

    def update_pelvis_rotation(self, frame):
        pelvis_pose = self.armature.pose.bones['pelvis']
        pelvis_pose.bone.select = True
        pelvis_pose.rotation_quaternion = self.new_pelvis_rots[frame]
        pelvis_pose.keyframe_insert(data_path='rotation_quaternion', frame=frame)

    def align_obj(self, frame):
        self.update_pelvis_rotation(frame)
        self.update_pelvis_location(frame)
        self.set_armature_to_origin(frame)