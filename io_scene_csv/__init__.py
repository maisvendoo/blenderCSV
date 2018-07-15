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
def toRightBasis(md):
    import mathutils
    import math
    mat_rot = mathutils.Matrix.Rotation(math.radians(90.0), 4, 'X')
    mat_mirror_y = mathutils.Matrix()
    mat_mirror_y[0][0], mat_mirror_y[0][1], mat_mirror_y[0][2], mat_mirror_y[0][3] = 1, 0, 0, 0
    mat_mirror_y[1][0], mat_mirror_y[1][1], mat_mirror_y[1][2], mat_mirror_y[1][3] = 0, -1, 0, 0
    mat_mirror_y[2][0], mat_mirror_y[2][1], mat_mirror_y[2][2], mat_mirror_y[2][3] = 0, 0, 1, 0
    mat_mirror_y[3][0], mat_mirror_y[3][1], mat_mirror_y[3][2], mat_mirror_y[3][3] = 0, 0, 0, 1

    for v in md.vertices:
        v.co = mat_mirror_y * mat_rot * v.co

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
def toLeftBasis(md):
    import mathutils
    import math
    mat_rot = mathutils.Matrix.Rotation(math.radians(-90.0), 4, 'X')
    mat_mirror_y = mathutils.Matrix()
    mat_mirror_y[0][0], mat_mirror_y[0][1], mat_mirror_y[0][2], mat_mirror_y[0][3] = 1, 0, 0, 0
    mat_mirror_y[1][0], mat_mirror_y[1][1], mat_mirror_y[1][2], mat_mirror_y[1][3] = 0, -1, 0, 0
    mat_mirror_y[2][0], mat_mirror_y[2][1], mat_mirror_y[2][2], mat_mirror_y[2][3] = 0, 0, 1, 0
    mat_mirror_y[3][0], mat_mirror_y[3][1], mat_mirror_y[3][2], mat_mirror_y[3][3] = 0, 0, 0, 1

    for v in md.vertices:
        v.co = mat_rot * mat_mirror_y * v.co

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
    #
    #---------------------------------------------------------------------------
    def getFileName(self, path):
        basename = os.path.basename(path)
        tmp = basename.split(".")
        return tmp[0]

    #---------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------
    def createMaterial(self, md, mesh):

        # Create new material for object
        if mesh.texture_file != "":
            matName = self.getFileName(mesh.texture_file)
        else:
            matName = md.name;

        # Check is material already exists
        mat = bpy.data.materials.get(matName)

        if mat is None:
            mat = bpy.data.materials.new(name=matName)

        # Add material to material's slot
        if md.materials:
            md.materials[0] = mat
        else:
            md.materials.append(mat)

        # Set solid color parametres
        for i in range(0, len(mesh.diffuse_color) - 1):
            c = mesh.diffuse_color[i]
            mat.diffuse_color[i] = float(c) / 255.0

        # Set alpha channel
        if len(mesh.diffuse_color) > 3:
            mat.alpha = float(mesh.diffuse_color[3]) / 255.0
            mat.use_transparency = True
            mat.transparency_method = 'Z_TRANSPARENCY'

        # Tune material texture
        if mesh.texture_file != "":

            modelDir = os.path.dirname(self.filepath)
            texImgPath = os.path.join(modelDir, mesh.texture_file)
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
        meshes_list = loader.loadCSV(path, self.use_left_coords_transform)

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

            if self.use_left_coords_transform:
                toRightBasis(me)

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

    # Left crew coordinat system transformation
    use_left_coords_transform = bpy.props.BoolProperty(
        name = "OpenBVE coordinate system",
        description = "Transformation to OpenBVE left crew coordinat system",
        default = False,
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

    #---------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------
    def addFaceToMesh(self, obj, md, f, mesh):

        face = []

        for i, v in enumerate(f.vertices):

            #Get local vertex coordinate
            loc_vert = md.vertices[v].co

            # Apply scale form user settings
            scaled_vert = self.use_mesh_scale * loc_vert

            # Transform local to world coordinates
            matrix = obj.matrix_world
            glob_vert = matrix * scaled_vert
            vertex = list(glob_vert)

            # Get face's UV-map
            uv_map = []
            if md.uv_layers.active:
                for loop_idx in f.loop_indices:
                    uv_coords = md.uv_layers.active.data[loop_idx].uv
                    uv_map.append(uv_coords)

            # Filter duplicated vertices
            if not (vertex in mesh.vertex_list):
                mesh.vertex_list.append(vertex)
                print("Append vertex: ", vertex)
                v_idx = len(mesh.vertex_list) - 1
                face.append(v_idx)
            else:
                v_idx = mesh.vertex_list.index(vertex)
                face.append(v_idx)


        # CSV format face creation (invert vertices order)
        csv_face = []
        csv_face.append(face[0])

        if md.uv_layers.active:
            mesh.texcoords_list.append([face[0], uv_map[0].x, uv_map[0].y])

        for i in range(len(face) - 1, 0, -1):
            csv_face.append(face[i])

            if md.uv_layers.active:
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
                if self.use_left_coords_transform:
                    toLeftBasis(md)

                # Sort faces by material index
                csv_meshes = {}
                for f in md.polygons:
                    csv_meshes[f.material_index] = []

                print(csv_meshes)

                # Check is exists meshes with material
                if len(csv_meshes) == 0:

                    # Single mesh without material
                    mesh = CSVmesh()

                    for f in md.polygons:
                        mesh.diffuse_color = [255, 255, 255, 255]
                        mesh.name = "Mesh: " + obj.name + " Material: None"
                        self.addFaceToMesh(obj, md, f, mesh)

                    mesh.is_addFace2 = bpy.types.Object.is_addFace2
                    meshes_list.append(mesh)
                else:

                    # Create mesh for each faces sets with same material
                    for f in md.polygons:
                        csv_meshes[f.material_index].append(f)

                    for key, faces in csv_meshes.items():

                        mat = obj.material_slots[key].material

                        mesh = CSVmesh()
                        mesh.name = "Mesh: " + obj.name + " Material: " + mat.name

                        # Diffuse color componets
                        for c in mat.diffuse_color:
                            mesh.diffuse_color.append(round(c * 255))

                        # Alpha channel
                        if mat.use_transparency:
                            mesh.diffuse_color.append(round(mat.alpha * 255))

                        # Texture settings
                        texture_idx = mat.active_texture_index
                        try:

                            # Get file path from texture's slot
                            texture_path = mat.texture_slots[texture_idx].texture.image.filepath
                            # Convert path to absolute OS path
                            texture_path = bpy.path.abspath(texture_path)
                            # Get directory of model file
                            modelDir = os.path.dirname(self.filepath)

                            # Set path for textures
                            if self.use_texture_separate_directory:
                                filename, file_ext = os.path.splitext(self.filepath)
                                filename = os.path.basename(filename)
                                textureName = os.path.basename(texture_path)

                                relTexDir = filename + "-textures"
                                textureDir = os.path.join(modelDir, relTexDir)

                                # Create directory for textures
                                if not os.path.exists(textureDir):
                                    oldmask = os.umask(0)
                                    print(oldmask)
                                    os.chdir(modelDir)
                                    os.makedirs(relTexDir, mode=0o777)
                                    os.umask(oldmask)

                                # Copy texture to directory
                                from shutil import copyfile
                                copyfile(texture_path, os.path.join(textureDir, textureName))

                                mesh.texture_file = os.path.join(relTexDir, textureName)
                                print("Texture path: " + mesh.texture_file)
                            else:
                                # Calcurate texture path
                                relPath = os.path.relpath(texture_path, modelDir)
                                print("Texture path: ", relPath)
                                mesh.texture_file = relPath

                        except Exception as ex:
                            print(ex)

                        for f in faces:
                            self.addFaceToMesh(obj, md, f, mesh)

                        mesh.is_addFace2 = self.use_add_face2
                        mesh.is_decale = self.use_transparent_decale_color

                        if mesh.is_decale:
                            mesh.decale_color.append(self.decale_color_red)
                            mesh.decale_color.append(self.decale_color_green)
                            mesh.decale_color.append(self.decale_color_blue)

                        meshes_list.append(mesh)

                if self.use_left_coords_transform:
                    toRightBasis(md)

        return meshes_list

    #-------------------------------------------------------------------------------
    #
    #-------------------------------------------------------------------------------
    def execute(self, context):

        path = self.filepath
        print("Export model to file: " + path)

        from .CSV import CSVLoader

        exporter = CSVLoader()
        exporter.export(path, self.getSelectedMeshes(), self.use_left_coords_transform)

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
