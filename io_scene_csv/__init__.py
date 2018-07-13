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
    "blender": (2, 79, 0)
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

    #---------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------
    def getFileName(self, path):
        basename = os.path.basename(path)
        tmp = basename.split(".")
        return tmp[0]

    def createMaterial(self, md, mesh):

        # Create new material for object
        if mesh.texture_file != "":
            matName = self.getFileName(mesh.texture_file)
        else:
            matName = md.name;

        mat = bpy.data.materials.get(matName)

        if mat is None:
            mat = bpy.data.materials.new(name=matName)

        if md.materials:
            md.materials[0] = mat
        else:
            md.materials.append(mat)

        if mesh.texture_file != "":

            modelDir = os.path.dirname(self.filepath)
            texImgPath = modelDir + os.path.sep + mesh.texture_file
            print(texImgPath)
            img = bpy.data.images.load(texImgPath)

            tex = bpy.data.textures.new("tex" + mat.name, 'IMAGE')
            tex.image = img
            slot = mat.texture_slots.add()
            slot.texture = tex
            slot.texture_coords = 'UV'
            slot.uv_layer = 'default'

    #---------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------
    def setUVcoords(self, md, mesh):
        bm = bmesh.new()
        bm.from_mesh(md)

        uv_layer = bm.loops.layers.uv.new()

        for f in bm.faces:
            for v, l in zip(f.verts, f.loops):
                luv = l[uv_layer]
                print(v.index)
                try:
                    tmp = mesh.texcoords_list[v.index]
                    print(tmp)

                    luv.uv[0] = tmp[1]
                    luv.uv[1] = tmp[2]

                except Exception as ex:
                    pass

        bm.to_mesh(md)


    #---------------------------------------------------------------------------
    # Action by menu item selection
    #---------------------------------------------------------------------------
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

            # Material creation
            self.createMaterial(me, m)

            # UV-map creation
            self.setUVcoords(me, m)

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

    def addFaceToMesh(self, obj, md, f, mesh):

        face = []

        for i, v in enumerate(f.vertices):
            loc_vert = md.vertices[v].co
            matrix = obj.matrix_world
            glob_vert = matrix * loc_vert
            vertex = list(glob_vert)

            uv_map = []
            if md.uv_layers.active:
                for loop_idx in f.loop_indices:
                    uv_coords = md.uv_layers.active.data[loop_idx].uv
                    uv_map.append(uv_coords)

            #print(list(uv_map))

            v_idx = -1

            if not (vertex in mesh.vertex_list):
                mesh.vertex_list.append(vertex)
                print("Append vertex: ", vertex)
                v_idx = len(mesh.vertex_list) - 1
                face.append(v_idx)
            else:
                v_idx = mesh.vertex_list.index(vertex)
                face.append(v_idx)

        csv_face = []
        csv_face.append(face[0])
        mesh.texcoords_list.append([face[0], uv_map[0].x, uv_map[0].y])

        for i in range(len(face) - 1, 0, -1):
            csv_face.append(face[i])
            mesh.texcoords_list.append([face[i], uv_map[i].x, uv_map[i].y])

        print("Append Face: ", csv_face)
        mesh.faces_list.append(csv_face)

    #---------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------
    def getSelectedMeshes(self):
        objs = bpy.context.selected_objects

        meshes_list = []

        for obj in objs:
            if obj.type == 'MESH':

                # CSV mesh creation
                from .CSV import CSVmesh

                print("Process object: " + obj.name)

                # Get mesh data from object
                md = obj.data

                csv_meshes = {}
                for f in md.polygons:
                    csv_meshes[f.material_index] = []

                print(csv_meshes)

                if len(csv_meshes) == 0:
                    # Single mesh without material
                    mesh = CSVmesh()

                    for f in md.polygons:
                        mesh.diffuse_color = [255, 255, 255, 255]
                        mesh.name = "Mesh: " + obj.name + " Material: None"
                        self.addFaceToMesh(obj, md, f, mesh)

                    meshes_list.append(mesh)
                else:

                    # Create mesh for each faces sets with same material
                    for f in md.polygons:
                        csv_meshes[f.material_index].append(f)

                    for key, faces in csv_meshes.items():

                        mat = obj.material_slots[key].material

                        mesh = CSVmesh()
                        mesh.name = "Mesh: " + obj.name + " Material: " + mat.name

                        for c in mat.diffuse_color:
                            mesh.diffuse_color.append(round(c * 255))

                        texture_idx = mat.active_texture_index
                        try:
                            texture_path = mat.texture_slots[texture_idx].texture.image.filepath
                            mesh.texture_file = texture_path

                            modelDir = os.path.dirname(self.filepath)
                            relPath = os.path.relpath(texture_path, modelDir)

                            print("Texture path: ", relPath)

                            mesh.texture_file = relPath

                        except Exception as ex:
                            pass

                        for f in faces:
                            self.addFaceToMesh(obj, md, f, mesh)

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
