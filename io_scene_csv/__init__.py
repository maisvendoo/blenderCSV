#    Copyright 2018, 2019 Dmirty Pritykin, 2018, 2019 S520
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
import logging
import pathlib

bl_info = {
    "name": "Importer/Exporter OpenBVE CSV models",
    "category": "Import-Export",
    "author": "Dmitry Pritykin",
    "version": (0, 6, 0),
    "blender": (2, 79, 0)
}

logger = logging.getLogger()
file_handler = logging.FileHandler(str(pathlib.Path.home().joinpath("io_scene_csv_log.txt")), "w")
file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s on %(funcName)s() at line %(lineno)d"))
logger.addHandler(file_handler)

loggingLevels = (
    ("NOTSET", "NOTSET", ""),
    ("DEBUG", "DEBUG", ""),
    ("INFO", "INFO", ""),
    ("WARNING", "WARNING", ""),
    ("ERROR", "ERROR", ""),
    ("CRITICAL", "CRITICAL", "")
)


class CsvImporter(bpy.types.Operator):
    bl_idname = "import_scene.csv"
    bl_label = "OpenBVE CSV model (*.csv)"
    bl_options = {"REGISTER", "UNDO"}

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    use_loggingLevel = bpy.props.EnumProperty(
        items=loggingLevels,
        name="Set logging level",
        description="Set logging level",
        default="INFO"
    )

    use_transform_coords = bpy.props.BoolProperty(
        name="Transform coordinates",
        description="Transformation from OpenBVE left crew coordinate system",
        default=True
    )

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        logger.setLevel(self.use_loggingLevel)
        logger.info("Import started.")
        from . import ImportCsv
        ImportCsv.ImportCsv().import_model(self.filepath, self.use_transform_coords)
        logger.info("Import completed.")
        return {"FINISHED"}


class CsvExporter(bpy.types.Operator):
    bl_idname = "export_scene.csv"
    bl_label = "OpenBVE CSV model (*.csv)"
    bl_options = {"REGISTER"}

    filename_ext = ".csv"

    filter_glob = bpy.props.StringProperty(
        default="*.csv",
        options={"HIDDEN"}
    )

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    use_loggingLevel = bpy.props.EnumProperty(
        items=loggingLevels,
        name="Set logging level",
        description="Set logging level",
        default="INFO"
    )

    use_transform_coords = bpy.props.BoolProperty(
        name="Transform coordinates",
        description="Transformation to OpenBVE left crew coordinate system",
        default=True
    )

    global_mesh_scale = bpy.props.FloatProperty(
        name="Set global scale",
        description="Global scale of the all scene objects",
        default=1.0,
        min=0.0001,
        max=10000.0,
    )

    use_normals = bpy.props.BoolProperty(
        name="Output Normals",
        description="Output normals",
        default=True
    )

    use_add_face2 = bpy.props.BoolProperty(
        name="Use AddFace2",
        description="Use AddFace2 command for generate faces in OpenBVE",
        default=False
    )

    use_emissive_color = bpy.props.BoolProperty(
        name="Use SetEmissiveColor",
        description="Use SetEmissiveColor command",
        default=False
    )

    emissive_color = bpy.props.IntVectorProperty(
        name="SetEmissiveColor's value",
        description="Set SetEmissiveColor command's Red, Green and Blue",
        default=(0, 0, 0),
        min=0,
        max=255,
        subtype="COLOR"
    )

    blend_mode = bpy.props.EnumProperty(
        items=(("Normal", "Normal", ""), ("Additive", "Additive", "")),
        name="Set BlendMode",
        description="Set SetBlendMode command's BlendMode",
        default="Normal"
    )

    glow_half_distance = bpy.props.IntProperty(
        name="Set GlowHalfDistance",
        description="Set SetBlendMode command's GlowHalfDistance",
        default=0,
        min=0,
        max=4095
    )

    glow_attenuation_mode = bpy.props.EnumProperty(
        items=(("DivideExponent2", "DivideExponent2", ""), ("DivideExponent4", "DivideExponent4", "")),
        name="Set GlowAttenuationMode",
        description="Set SetBlendMode command's GlowAttenuationMode",
        default="DivideExponent4"
    )

    use_copy_texture_separate_directory = bpy.props.BoolProperty(
        name="Copy textures in separate folder",
        description="Copied textures in directory near *.csv file. Directory name will be: <model name>-textures",
        default=True
    )

    use_transparent_color = bpy.props.BoolProperty(
        name="Use SetDecalTransparentColor",
        description="Use SetDecalTransparentColor command",
        default=False
    )

    transparent_color = bpy.props.IntVectorProperty(
        name="SetDecalTransparentColor's value",
        description="Set SetDecalTransparentColor command's Red, Green and Blue",
        default=(0, 0, 0),
        min=0,
        max=255,
        subtype="COLOR"
    )

    def invoke(self, context, event):
        self.filepath = "undefined" + self.filename_ext
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        if bpy.context.mode != "OBJECT":
            def draw_context(self, context):
                self.layout.label("Please switch to Object Mode.")

            bpy.context.window_manager.popup_menu(draw_context, title="Export CSV", icon="ERROR")
            return {"FINISHED"}

        logger.setLevel(self.use_loggingLevel)
        logger.info("Export started.")

        from . import ExportCsv
        exporter = ExportCsv.ExportCsv()

        exporter.option.use_transform_coords = self.use_transform_coords
        exporter.option.global_mesh_scale = self.global_mesh_scale
        exporter.option.use_normals = self.use_normals
        exporter.option.use_add_face2 = self.use_add_face2
        exporter.option.use_emissive_color = self.use_emissive_color
        exporter.option.emissive_color = self.emissive_color
        exporter.option.blend_mode = self.blend_mode
        exporter.option.glow_half_distance = self.glow_half_distance
        exporter.option.glow_attenuation_mode = self.glow_attenuation_mode
        exporter.option.use_copy_texture_separate_directory = self.use_copy_texture_separate_directory
        exporter.option.use_transparent_color = self.use_transparent_color
        exporter.option.transparent_color = self.transparent_color

        exporter.export_model(self.filepath)

        logger.info("Export completed.")
        return {"FINISHED"}


def menu_import(self, context):
    self.layout.operator(CsvImporter.bl_idname, text=CsvImporter.bl_label)


def menu_export(self, context):
    self.layout.operator(CsvExporter.bl_idname, text=CsvExporter.bl_label)


def register():
    bpy.types.INFO_MT_file_import.append(menu_import)
    bpy.utils.register_class(CsvImporter)

    bpy.types.INFO_MT_file_export.append(menu_export)
    bpy.utils.register_class(CsvExporter)


def unregister():
    bpy.types.INFO_MT_file_import.remove(menu_import)
    bpy.utils.unregister_class(CsvImporter)

    bpy.types.INFO_MT_file_export.remove(menu_export)
    bpy.utils.unregister_class(CsvExporter)


if __name__ == "__main__":
    register()
