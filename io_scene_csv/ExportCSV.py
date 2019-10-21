#    Copyright 2018, 2019 Dmirty Pritykin, 2019 S520
#
#    This file is part of blenderCSV.
#
#    blenderCSV is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    blenderCSV is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with blenderCSV.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import bmesh
import filecmp
import pathlib
import os
import shutil
from typing import List, Tuple, Dict
from . import CSV
from . import logger
from . import Transform


class ExportCsv:
    def __init__(self):
        self.file_path = ""
        self.option = CSV.ExportOption()

    def copy_texture_separate_directory(self, model_dir: pathlib.PurePath, texture_path: pathlib.PurePath) -> str:
        texture_dir = model_dir.joinpath(pathlib.Path(self.file_path).stem + "-textures")

        try:
            os.makedirs(str(texture_dir), exist_ok=True)
        except Exception as ex:
            logger.critical(ex)
            return str(texture_path)

        try:
            dest_path = texture_dir.joinpath(texture_path.name)

            if not os.path.exists(str(dest_path)) or not filecmp.cmp(str(texture_path), str(dest_path)):
                shutil.copy2(str(texture_path), str(dest_path))

        except Exception as ex:
            logger.critical(ex)
            return str(texture_path)

        return str(dest_path)

    def export_model(self, file_path: str) -> None:
        self.file_path = file_path

        meshes_list = []  # type: List[CSV.CsvMesh]

        object_list = bpy.context.selected_objects

        for obj in object_list:
            if obj.type != "MESH":
                continue

            logger.info("Process object: " + obj.name)

            blender_mesh = bmesh.new()
            blender_mesh.from_mesh(obj.data)

            Transform.swap_coordinate_system(obj.matrix_world, blender_mesh, self.option.use_transform_coords)

            # Group faces by material index.
            blender_faces = {}  # type: Dict[int, List[bmesh.types.BMFace]]

            for face in blender_mesh.faces:
                if blender_faces.get(face.material_index) is None:
                    blender_faces[face.material_index] = []

                blender_faces[face.material_index].append(face)

            for m_idx, faces in blender_faces.items():
                # Create a new CsvMesh.
                mesh = CSV.CsvMesh()
                mesh.name = "Mesh: " + obj.data.name

                # Add vertices to mesh
                blender_vertices = []  # type: List[Tuple[bmesh.types.BMFace, bmesh.types.BMVert]]

                for face in faces:
                    for vertex in face.verts:
                        if (face, vertex) not in blender_vertices:
                            blender_vertices.append((face, vertex))

                for vertex in blender_vertices:
                    mesh.vertex_list.append((vertex[1].co[0], vertex[1].co[1], vertex[1].co[2]))
                    mesh.normals_list.append((vertex[1].normal[0], vertex[1].normal[1], vertex[1].normal[2]))

                # Add faces to mesh
                for face in faces:
                    indices = []  # type: List[int]

                    for vertex in face.verts:
                        indices.append(blender_vertices.index((face, vertex)))

                    mesh.faces_list.append(tuple(indices))

                # Add texcoords to mesh
                if blender_mesh.loops.layers.uv.active is not None:
                    for face in faces:
                        for loop in face.loops:
                            vertex_index = blender_vertices.index((face, loop.vert))
                            uv = loop[blender_mesh.loops.layers.uv.active].uv
                            texcoords = (vertex_index, uv[0], 1.0 - uv[1])

                            if texcoords not in mesh.texcoords_list:
                                mesh.texcoords_list.append(texcoords)

                # Add material to mesh
                if m_idx < len(obj.material_slots):
                    mat = obj.material_slots[m_idx].material
                    mesh.name += ", Material: " + mat.name

                    # Add diffuse color to mesh
                    mesh.diffuse_color = (round(mat.diffuse_color[0] * 255), round(mat.diffuse_color[1] * 255), round(mat.diffuse_color[2] * 255), round(mat.alpha * 255) if mat.use_transparency else 255)

                    # Add texture to mesh
                    model_dir = pathlib.Path(self.file_path).parent

                    if mat.active_texture_index < len(mat.texture_slots):
                        texture_slot = mat.texture_slots[mat.active_texture_index]

                        if texture_slot is not None and type(texture_slot.texture) is bpy.types.ImageTexture:
                            if texture_slot.texture.image.filepath != "":
                                texture_path = pathlib.Path(bpy.path.abspath(texture_slot.texture.image.filepath)).resolve()

                                if self.option.use_copy_texture_separate_directory:
                                    mesh.daytime_texture_file = self.copy_texture_separate_directory(model_dir, texture_path)
                                else:
                                    mesh.daytime_texture_file = str(texture_path)

                            mesh.diffuse_color = (mesh.diffuse_color[0], mesh.diffuse_color[1], mesh.diffuse_color[2], round(texture_slot.alpha_factor * 255))

                    if mat.csv_props.nighttime_texture_file != "":
                        texture_path = pathlib.Path(bpy.path.abspath(mat.csv_props.nighttime_texture_file)).resolve()

                        if self.option.use_copy_texture_separate_directory:
                            mesh.nighttime_texture_file = self.copy_texture_separate_directory(model_dir, texture_path)
                        else:
                            mesh.nighttime_texture_file = str(texture_path)
                else:
                    mesh.name += ", Material: Undefined"

                # Set options to mesh
                mesh.use_add_face2 = obj.csv_props.use_add_face2
                mesh.use_emissive_color = obj.csv_props.use_emissive_color
                mesh.emissive_color = (round(obj.csv_props.emissive_color[0] * 255), round(obj.csv_props.emissive_color[1] * 255), round(obj.csv_props.emissive_color[2] * 255))
                mesh.blend_mode = obj.csv_props.blend_mode
                mesh.glow_half_distance = obj.csv_props.glow_half_distance
                mesh.glow_attenuation_mode = obj.csv_props.glow_attenuation_mode
                mesh.use_transparent_color = obj.csv_props.use_transparent_color
                mesh.transparent_color = (round(obj.csv_props.transparent_color[0] * 255), round(obj.csv_props.transparent_color[1] * 255), round(obj.csv_props.transparent_color[2] * 255))

                # Finalize
                meshes_list.append(mesh)

        CSV.CsvObject().export_csv(self.option, meshes_list, self.file_path)
