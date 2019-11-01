#    Copyright 2018, 2019 Dmirty Pritykin, 2019 S520
#
#    This file is part of blenderCSV.
#
#    blenderCSV is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 2 of the License, or
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
import pathlib
import mathutils
from . import CSV
from . import logger
from . import Transform


class ImportCsv:
    INV255 = 1.0 / 255.0

    def __init__(self):
        self.file_path = ""
        self.option = CSV.ImportOption()

    def get_same_material(self, csv_mesh: CSV.CsvMesh, mat_name: str) -> bpy.types.Material:
        mat = bpy.data.materials.get(mat_name)

        if mat is None:
            return None

        if mat.diffuse_color[0] != csv_mesh.diffuse_color[0] * self.INV255 or mat.diffuse_color[1] != csv_mesh.diffuse_color[1] * self.INV255 or mat.diffuse_color[2] != csv_mesh.diffuse_color[2] * self.INV255:
            return None

        if csv_mesh.daytime_texture_file == "" and mat.alpha != csv_mesh.diffuse_color[3] * self.INV255:
            return None

        if mat.active_texture_index < len(mat.texture_slots):
            slot = mat.texture_slots[mat.active_texture_index]

            if slot is None:
                return None

            if type(slot.texture) is not bpy.types.ImageTexture:
                return None

            if slot.texture.image.filepath != csv_mesh.daytime_texture_file:
                return None

            if slot.alpha_factor != csv_mesh.diffuse_color[3] * self.INV255:
                return None

        if mat.csv_props.use_add_face2 != csv_mesh.use_add_face2:
            return None

        if mat.csv_props.nighttime_texture_file != csv_mesh.nighttime_texture_file:
            return None

        return mat

    def create_material(self, csv_mesh: CSV.CsvMesh, blender_mesh: bpy.types.Mesh) -> None:
        # Decide the name of the material. If a texture file exists, use that file name.
        if csv_mesh.daytime_texture_file != "":
            mat_name = pathlib.Path(csv_mesh.daytime_texture_file).stem
        else:
            mat_name = blender_mesh.name

        # Check if the same material already exists.
        mat = self.get_same_material(csv_mesh, mat_name)

        # Since the same material does not exist, create a new one.
        if mat is None:
            logger.debug("Create new material: " + mat_name)
            mat = bpy.data.materials.new(mat_name)
            mat.diffuse_color = (csv_mesh.diffuse_color[0] * self.INV255, csv_mesh.diffuse_color[1] * self.INV255, csv_mesh.diffuse_color[2] * self.INV255)
            mat.alpha = csv_mesh.diffuse_color[3] * self.INV255
            mat.transparency_method = "Z_TRANSPARENCY"
            mat.use_transparency = csv_mesh.diffuse_color[3] != 255

            # Set the texture on the material.
            if csv_mesh.daytime_texture_file != "":
                texture = bpy.data.textures.get(mat_name)

                if texture is None:
                    texture = bpy.data.textures.new(mat_name, "IMAGE")
                    texture.image = bpy.data.images.load(csv_mesh.daytime_texture_file)

                slot = mat.texture_slots.add()
                slot.texture = texture
                slot.texture_coords = "UV"
                slot.uv_layer = "default"
                slot.use_map_color_diffuse = True
                slot.use_map_alpha = True
                slot.alpha_factor = mat.alpha
                mat.alpha = 0.0
                mat.use_transparency = True

            mat.csv_props.use_add_face2 = csv_mesh.use_add_face2
            mat.csv_props.nighttime_texture_file = csv_mesh.nighttime_texture_file

        # Set the material on the mesh.
        blender_mesh.materials.append(mat)

    def set_texcoords(self, csv_mesh: CSV.CsvMesh, blender_mesh: bpy.types.Mesh) -> None:
        blender_mesh.uv_textures.new("default")

        for face in blender_mesh.polygons:
            for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
                try:
                    texcoords = [j for j in csv_mesh.texcoords_list if j[0] == vert_idx][0]
                except Exception:
                    logger.error("VertexIndex: " + str(vert_idx) + " is not defined with the SetTextureCoordinates command.")
                    continue

                blender_mesh.uv_layers["default"].data[loop_idx].uv = [texcoords[1], 1.0 - texcoords[2]]

    def import_model(self, file_path: str) -> None:
        self.file_path = file_path

        meshes_list = CSV.CsvObject().load_csv(self.option, file_path)

        logger.info("Loaded meshes: " + str(len(meshes_list)))

        for i in range(len(meshes_list)):
            logger.info("Loaded mesh" + str(i) + ": (Vertex: " + str(len(meshes_list[i].vertex_list)) + ", Face: " + str(len(meshes_list[i].faces_list)) + ")")

            for j in range(len(meshes_list[i].vertex_list)):
                logger.debug("Vertex" + str(j) + ": " + str(meshes_list[i].vertex_list[j]))

            for j in range(len(meshes_list[i].faces_list)):
                logger.debug("Face" + str(j) + ": " + str(meshes_list[i].faces_list[j]))
                pass

        obj_base_name = pathlib.Path(self.file_path).stem

        for i in range(len(meshes_list)):
            blender_mesh = bpy.data.meshes.new(str(obj_base_name) + " - " + str(i))
            blender_mesh.from_pydata(meshes_list[i].vertex_list, [], meshes_list[i].faces_list)
            blender_mesh.update(True)

            self.create_material(meshes_list[i], blender_mesh)

            self.set_texcoords(meshes_list[i], blender_mesh)

            Transform.swap_coordinate_system(mathutils.Matrix.Identity(4), blender_mesh, self.option.use_transform_coords)

            blender_mesh.calc_normals()

            obj = bpy.data.objects.new(blender_mesh.name, blender_mesh)
            obj.select = True

            obj.csv_props.use_emissive_color = meshes_list[i].use_emissive_color
            obj.csv_props.emissive_color = (meshes_list[i].emissive_color[0] * self.INV255, meshes_list[i].emissive_color[1] * self.INV255, meshes_list[i].emissive_color[2] * self.INV255)
            obj.csv_props.blend_mode = meshes_list[i].blend_mode
            obj.csv_props.glow_half_distance = meshes_list[i].glow_half_distance
            obj.csv_props.glow_attenuation_mode = meshes_list[i].glow_attenuation_mode
            obj.csv_props.use_transparent_color = meshes_list[i].use_transparent_color
            obj.csv_props.transparent_color = (meshes_list[i].transparent_color[0] * self.INV255, meshes_list[i].transparent_color[1] * self.INV255, meshes_list[i].transparent_color[2] * self.INV255)

            bpy.context.scene.objects.link(obj)
