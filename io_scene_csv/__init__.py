#-------------------------------------------------------------------------------
#
#       Plugin to import OpenBVE CSV models into Blender 3D editor
#       RGUPS, Virtual Railway 09/07/2018
#       Developer: Dmitry Pritykin
#
#-------------------------------------------------------------------------------

bl_info = {
    "name": "Importer/Exporter OpenBVE CSV models",
    "category": "Import-Export",
    "author": "Dmitry Pritykin",
    "version": (0, 5, 0),
    "blender": (2, 79, 0)
}

import bpy

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
class CSVImporter(bpy.types.Operator):
    """CSV models importer"""
    bl_idname = "import_scene.csv"
    bl_label = "OpenBVE CSV model (*.csv)"
    bl_options = {'REGISTER', 'UNDO'}

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    use_left_coords_transform = bpy.props.BoolProperty(
        name="Transform coordinates",
        description="Transformation from OpenBVE left crew coordinat system",
        default=True,
    )

    #---------------------------------------------------------------------------
    # Action by menu item selection
    #---------------------------------------------------------------------------
    def execute(self, context):

        path = self.filepath
        print("Loading model from file: " + path)

        from . import ImportCSV
        importer = ImportCSV.ImportCSV()

        importer.modelImport(path, self.use_left_coords_transform)

        return {'FINISHED'}

    #---------------------------------------------------------------------------
    # Select file for import
    #---------------------------------------------------------------------------
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
class CSVExporter(bpy.types.Operator):
    """CSV models exporter"""
    bl_idname = "export_scene.csv"
    bl_label = "OpenBVE CSV model (*.csv)"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = ".csv"
    filter_glob = bpy.props.StringProperty(
        default = "*.csv",
        options={'HIDDEN'},
    )

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    # Left crew coordinat system transformation
    use_left_coords_transform = bpy.props.BoolProperty(
        name = "OpenBVE coordinate system",
        description = "Transformation to OpenBVE left crew coordinat system",
        default = True,
    )

    # Global scale form exported geometry
    use_mesh_scale = bpy.props.FloatProperty(
        name = "Scale",
        description = "Global scale of the all scene objects",
        default = 1.0,
        min = 0.0001,
        max = 10000.0,
    )

    use_add_face2 = bpy.props.BoolProperty(
        name="Use AddFace2 command",
        description="Use AddFace2 command for generate faces in OpenBVE",
        default=False,
    )

    use_transparent_decale_color = bpy.props.BoolProperty(
        name="Use transparent decale color",
        description="Texture color, which will transparent in OpenBVE",
        default=False,
    )

    decale_color_red = bpy.props.IntProperty(
        name="R",
        default=0,
        min = 0,
        max = 255
    )

    decale_color_green = bpy.props.IntProperty(
        name="G",
        default=0,
        min=0,
        max=255
    )

    decale_color_blue = bpy.props.IntProperty(
        name="B",
        default=0,
        min=0,
        max=255
    )

    use_texture_separate_directory = bpy.props.BoolProperty(
        name = "Copy textures in separate folder",
        description = "Copied textures in directory near *.csv file. Directory name will be: <model name>-textures",
        default = True,
    )

    #-------------------------------------------------------------------------------
    #
    #-------------------------------------------------------------------------------
    def execute(self, context):

        path = self.filepath
        print("Export model to file: " + path)

        from . import ExportCSV
        exporter = ExportCSV.ExportCSV()



        exporter.export_props.is_coord_transform = self.use_left_coords_transform
        exporter.export_props.is_copy_textures = self.use_texture_separate_directory
        exporter.export_props.use_transparent_decale_color = self.use_transparent_decale_color
        exporter.export_props.decale_red = self.decale_color_red
        exporter.export_props.decale_green = self.decale_color_green
        exporter.export_props.decale_blue = self.decale_color_blue
        exporter.export_props.is_face2 = self.use_add_face2
        exporter.export_props.scale = self.use_mesh_scale

        exporter.exportModel(path)

        return {'FINISHED'}

    #-------------------------------------------------------------------------------
    #
    #-------------------------------------------------------------------------------
    def invoke(self, context, event):
        self.filepath = "undefined" + self.filename_ext
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
def menu_import(self, context):
    self.layout.operator(CSVImporter.bl_idname, text=CSVImporter.bl_label)

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
def menu_export(self, context):
    self.layout.operator(CSVExporter.bl_idname, text=CSVExporter.bl_label)

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
def register():
    bpy.types.INFO_MT_file_import.append(menu_import)
    bpy.utils.register_class(CSVImporter)

    bpy.types.INFO_MT_file_export.append(menu_export)
    bpy.utils.register_class(CSVExporter)

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
def unregister():
    bpy.types.INFO_MT_file_import.remove(menu_import)
    bpy.utils.unregister_class(CSVImporter)

    bpy.types.INFO_MT_file_export.remove(menu_export)
    bpy.utils.unregister_class(CSVExporter)

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
if __name__ == "__main__":
    register()
