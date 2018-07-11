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

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
class CSVImporter(bpy.types.Operator):
    """CSV models importer"""
    bl_idname = "import_scene.csv"
    bl_label = "OpenBVE CSV model (*.csv)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):        

        from . import CSVLoader
        loader = CSVLoader.CSVLoader()
        path = "F:/work/vr/3D-graphics/obj2csv/models/csv/digits.csv"
        meshes_list = loader.loadCSV(path)

        for m in meshes_list:
            mesh_data = bpy.data.meshes.new("mesh data")
            mesh_data.from_pydata(m.getVerticies(), [], m.getFaces())
            mesh_data.update()

            obj = bpy.data.objects.new("DigitCube", mesh_data)
            scene = bpy.context.scene
            scene.objects.link(obj)
            obj.select = True

        return {'FINISHED'}

    

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

    #from src import CSVLoader

    #loader = CSVLoader.CSVLoader()
    #path = "../../obj2csv/models/csv/digits.csv"
    #loader.loadCSV(path)


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