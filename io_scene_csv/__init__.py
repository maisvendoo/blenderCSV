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

        from . import CSV

        # Load model from CSV file
        loader = CSV.CSVLoader()
        meshes_list = loader.loadCSV(path)

        print("Loaded " + str(len(meshes_list)) + " meshes")

        # Create all objects in Blender's editor
        for m_idx, m in enumerate(meshes_list):

            # Constract object name from file name
            obj_name = self.getFileName(path)

            # Create mesh from CSV geometry data
            me = bpy.data.meshes.new(obj_name + "-" + str(m_idx))
            me.from_pydata(m.vertex_list, [], m.faces_list)
            me.update(calc_edges=True)

            # Create object and link it to scene
            obj = bpy.data.objects.new(me.name, me)
            bpy.context.scene.objects.link(obj)

        return {'FINISHED'}

    # Select file for import
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

    def getSelectedMeshes(self):
        objs = bpy.context.selected_objects

        meshes_list = []

        for obj in objs:
            if obj.type == 'MESH':

                # CSV mesh creation
                from .CSV import CSVmesh
                mesh = CSVmesh()

                print("Process object: " + obj.name)

                # Get mesh data from object
                me = obj.data
                # Get verticies
                for i, v in enumerate(me.vertices):
                    mesh.vertex_list.append(list(v.co))
                    print(mesh.vertex_list[i])

                # Get faces
                for i, face in enumerate(me.polygons):

                    # Convert to CSV vertex order
                    tmp = list(face.vertices)
                    csv_face = []
                    csv_face.append(tmp[0])
                    for j in range(len(tmp) - 1, 0, -1):
                        csv_face.append(tmp[j])

                    mesh.faces_list.append(csv_face)
                    print(mesh.faces_list[i])

            meshes_list.append(mesh)

        return meshes_list

    def execute(self, context):

        path = self.filepath
        print("Export model to file: " + path)

        from .CSV import CSVLoader

        exporter = CSVLoader()
        exporter.export(path, self.getSelectedMeshes())

        return {'FINISHED'}

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
