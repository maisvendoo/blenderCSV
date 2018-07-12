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

    # Action by menu item selection
    def execute(self, context):

        path = self.filepath
        print("Loading model from file: " + path)

        from . import CSVLoader
        # Load model from CSV file
        loader = CSVLoader.CSVLoader()
        meshes_list = loader.loadCSV(path)

        print("Loaded " + str(len(meshes_list)) + " meshes")

        # Create object in Blender's editor
        m_idx = 0
        for m in meshes_list:

            obj_name = self.getFileName(path)

            me = bpy.data.meshes.new(obj_name + str(m_idx))
            me.from_pydata(m.vertex_list, [], m.faces_list)
            #me.update(calc_edges=True)

            obj = bpy.data.objects.new(me.name, me)
            bpy.context.scene.objects.link(obj)
            m_idx = m_idx + 1

        return {'FINISHED'}

    # Select file for import
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
