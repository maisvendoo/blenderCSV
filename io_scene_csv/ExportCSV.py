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
from typing import List, Dict
from . import CSV
from . import logger
from . import Transform


class ExportCsv:
    def __init__(self):
        self.file_path = ""
        self.option = CSV.ExportOption()

    def copy_texture_separate_directory(self, model_dir: pathlib.PurePath, texture_path: pathlib.PurePath) -> str:
        rel_texture_dir = pathlib.Path(self.file_path).stem + "-textures"
        texture_dir = model_dir.joinpath(rel_texture_dir)

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

        return os.path.join(rel_texture_dir, texture_path.name)

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

            Transform.swap_coordinate_system(blender_mesh)

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
                blender_vertices = []  # type: List[bmesh.types.BMVert]

                for face in faces:
                    for vertex in face.verts:
                        if vertex not in blender_vertices:
                            blender_vertices.append(vertex)

                for vertex in blender_vertices:
                    mesh.vertex_list.append((vertex.co[0], vertex.co[1], vertex.co[2]))
                    mesh.normals_list.append((vertex.normal[0], vertex.normal[1], vertex.normal[2]))

                # Add faces to mesh
                for face in faces:
                    indices = []  # type: List[int]

                    for vertex in face.verts:
                        indices.append(blender_vertices.index(vertex))

                    mesh.faces_list.append(tuple(indices))

                # Add texcoords to mesh
                for face in faces:
                    for loop in face.loops:
                        vertex_index = blender_vertices.index(loop.vert)
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
                    if mat.active_texture_index < len(mat.texture_slots):
                        if mat.texture_slots[mat.active_texture_index] is not None and type(mat.texture_slots[mat.active_texture_index].texture) is bpy.types.ImageTexture:
                            texture_path = pathlib.Path(mat.texture_slots[mat.active_texture_index].texture.image.filepath).resolve()
                            model_dir = pathlib.Path(self.file_path).parent

                            if self.option.use_copy_texture_separate_directory:
                                mesh.texture_file = self.copy_texture_separate_directory(model_dir, texture_path)
                            else:
                                mesh.texture_file = os.path.relpath(str(texture_path), str(model_dir))

                else:
                    mesh.name += ", Material: Undefined"

                # Finalize
                meshes_list.append(mesh)

        CSV.CsvObject().export_csv(self.option, meshes_list, self.file_path)
