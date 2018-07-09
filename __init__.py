#-----------------------------------------------------------------------------------------------------------------------
#
#       Plugin to import OpenBVE CSV models into Blender 3D editor
#       RGUPS, Virtual Railway 09/07/2018
#       Developer: Dmitry Pritykin
#
#-----------------------------------------------------------------------------------------------------------------------
bl_info = {
    "name": "Importer OpenBVE CSV models",
    "category": "Import-Export",
    "author": "Dmitry Pritykin",
    "version": (0, 1, 0),
    "blender": (2, 78, 0)
}

import bpy
import bmesh

class CSVImporter(bpy.types.Operator):
    """CSV models importer"""
    bl_idname = "import_scene.csv"
    bl_label = "OpenBVE CSV model (*.csv)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        verts = [(1, 1, 0), (-1, 1, 0), (-1, -1, 0), (1, -1, 0)]
        mesh = bpy.data.meshes.new("square")
        obj = bpy.data.objects.new("Square", mesh)

        scene = bpy.context.scene
        scene.objects.link(obj)
        scene.objects.active = obj
        obj.select = True

        mesh = bpy.context.object.data
        bm = bmesh.new()

        for v in verts:
            bm.verts.new(v)

        bm.to_mesh(mesh)
        bm.free()

        return {'FINISHED'}

def menu_import(self, context):
    self.layout.operator(CSVImporter.bl_idname, text=CSVImporter.bl_label)

def register():
    bpy.types.INFO_MT_file_import.append(menu_import)
    bpy.utils.register_class(CSVImporter)


def unregister():
    bpy.types.INFO_MT_file_import.remove(menu_import)
    bpy.utils.register_class(CSVImporter)


if __name__ == "__main__":
    register()