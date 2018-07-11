#-------------------------------------------------------------------------------
#
#       Plugin to import OpenBVE CSV models into Blender 3D editor
#       RGUPS, Virtual Railway 09/07/2018
#       Developer: Dmitry Pritykin
#
#-------------------------------------------------------------------------------
bl_info = {
    "name": "Importer OpenBVE CSV models",
    "category": "Import-Export",
    "author": "Dmitry Pritykin",
    "version": (0, 1, 0),
    "blender": (2, 78, 0)
}

import bpy
import bmesh
import os

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
class CSVImporter(bpy.types.Operator):
    """CSV models importer"""
    bl_idname = "import_scene.csv"
    bl_label = "OpenBVE CSV model (*.csv)"
    bl_options = {'REGISTER', 'UNDO'}

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    def getFileName(self, path):
        basename = os.path.basename(path)
        tmp = basename.split(".")
        return tmp[0]

    def execute(self, context):

        path = self.filepath
        print("Loading model from file: " + path)

        from . import CSVLoader
        # Load model from CSV file
        loader = CSVLoader.CSVLoader()
        meshes_list = loader.loadCSV(path)

        # Create object in Blender's editor
        for m in meshes_list:

            mesh_data = bpy.data.meshes.new(self.getFileName(path) + "_data")
            obj = bpy.data.objects.new(self.getFileName(path), mesh_data)
            scene = bpy.context.scene
            scene.objects.link(obj)
            obj.select = True

            bm = bmesh.new()
            bm.from_mesh(mesh_data)

            vert = []

            for v in m.getVerticies():
                vert.append(bm.verts.new(v))

            for fc in m.getFaces():
                face = []
                for idx in fc:
                    face.append(vert[idx])

                bm.faces.new(face)
                print(tuple(face))

            bm.to_mesh(mesh_data)

        return {'FINISHED'}

    def invoke(self, context, event):
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
def register():
       
    bpy.types.INFO_MT_file_import.append(menu_import)
    bpy.utils.register_class(CSVImporter)


#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
def unregister():
    bpy.types.INFO_MT_file_import.remove(menu_import)
    bpy.utils.register_class(CSVImporter)


#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
if __name__ == "__main__":
    register()