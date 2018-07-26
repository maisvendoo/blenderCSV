#-------------------------------------------------------------------------------
#
#       CSV models export module
#       (c) RGUPS, Virtual Railway 26/07/2018
#       Developer: Dmitry Pritykin
#
#-------------------------------------------------------------------------------
import bpy
import os

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
class ExportProps:

    def __init__(self):
        self.is_coord_transform = False
        self.scale = 1.0
        self.is_face2 = False
        self.use_transparent_decale_color = False
        self.decale_red = 0
        self.decale_green = 0
        self.decale_blue = 0
        self.is_copy_textures = False

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
class ExportCSV:

    #---------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------
    def __init__(self):
        self.filepath = ""
        self.export_props = ExportProps()

    #---------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------
    def addFaceToMesh(self, md, fc, mesh):

        face = []

        # Перебираем все вершины в данной грани по индексам и порядковым номерам
        for i, vert_idx in enumerate(fc.vertices):
            # Берем вершину из массива вершин всего меша
            loc_vertex = md.vertices[vert_idx]
            vertex = list(loc_vertex.co)

            # Проверяем, имеется ли уже такая вершина в CSV-сетке
            # if not (vertex in mesh.vertex_list):
            # Если имеется, до добаляем её как очередную
            mesh.vertex_list.append(vertex)
            mesh.normals_list.append(list(loc_vertex.normal))
            mesh.vertex_indices.append(vert_idx)
            v_idx = len(mesh.vertex_list) - 1
            face.append(v_idx)

        # Пытаемся работать с UV-разверткой
        for uv_layer in md.uv_layers:
            for i in fc.loop_indices:
                uvCoord = uv_layer.data[i].uv
                lookup_idx = mesh.vertex_indices.index(md.loops[i].vertex_index)
                texel = [lookup_idx, uvCoord[0], uvCoord[1]]
                mesh.texcoords_list.append(texel)

        mesh.faces_list.append(face)

    #---------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------
    def copyTexture(self, texture_path, model_dir):
        filename, file_ext = os.path.splitext(self.filepath)
        filename = os.path.basename(filename)

        texture_name = os.path.basename(texture_path)

        rel_tex_dir = filename + "-textures"
        texture_dir = os.path.join(model_dir, rel_tex_dir)

        if not os.path.exists(texture_dir):
            old_mask = os.umask(0)
            os.chdir(model_dir)
            os.makedirs(rel_tex_dir, mode=0o777)
            os.umask(old_mask)

        from shutil import copyfile
        try:
            dest_path = os.path.join(texture_dir, texture_name)

            if not os.path.exists(dest_path):
                copyfile(texture_path, dest_path)

        except Exception as ex:
            print(ex)
            return ""

        return os.path.join(rel_tex_dir, texture_name)

    #---------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------
    def getSelectedMeshes(self):

        from . import GeometryMath as gm

        # Получаем все выделеные объекты
        objs = bpy.context.selected_objects

        # Список CSV-сеток
        meshes_list = []

        # Перебираем все объекты
        for obj in objs:

            # Если текущий объект сеточный
            if obj.type == 'MESH':

                from .CSV import CSVmesh

                print("Process object: " + obj.name)

                # Берем данные о сетке текущего объекта
                md = obj.data

                # Сортируем полигоны по индексу используемого материала
                csv_meshes = {}
                for f in md.polygons:
                    csv_meshes[f.material_index] = []

                for f in md.polygons:
                    csv_meshes[f.material_index].append(f)

                print(csv_meshes)

                # Для кажой группы граней с одинаковым материалом
                for key, faces in csv_meshes.items():

                    # Создаем новую CSV-сетку
                    mesh = CSVmesh()
                    mesh.name = "Mesh: " + md.name + "-" + str(key)

                    # Перебираем все грани текущей сетки
                    for f in faces:
                        # Добавляем грань в сетку
                        self.addFaceToMesh(md, f, mesh)

                    # ---- Отладочная печать параметров меша в консоль ----
                    for i, v in enumerate(mesh.vertex_list):
                        print("Vertex: ", i, " ", v, " Normal: ", mesh.normals_list[i])

                    for i, fc in enumerate(mesh.faces_list):
                        print("Face: ", i, " ", fc)

                    for i, tx in enumerate(mesh.texcoords_list):
                        print("Tex. coords: ", i, " ", tx)

                    print("Vertex's indices: ", mesh.vertex_indices)
                    # ------------------------------------------------------

                    # Работаем с материалом
                    if obj.material_slots:
                        mat = obj.material_slots[key].material
                        mesh.name += " Material: " + mat.name

                        # Устанавливаем диффузный цвет
                        for c in mat.diffuse_color:
                            mesh.diffuse_color.append(round(c * 255))

                        # Устанавливаем альфа-канал
                        if mat.use_transparency:
                            mesh.diffuse_color.append(round(mat.alpha * 255))
                        else:
                            mesh.diffuse_color.append(255)

                        # Проверяем наличие текстур
                        if mat.texture_slots:

                            # Берем индекс активной текстуры
                            tex_idx = mat.active_texture_index
                            print("Texture index: ", tex_idx)

                            try:
                                texture_path = mat.texture_slots[tex_idx].texture.image.filepath
                                texture_path = bpy.path.abspath(texture_path)
                                model_dir = os.path.dirname(self.filepath)

                                if self.export_props.is_copy_textures:
                                    mesh.texture_file = self.copyTexture(texture_path, model_dir)
                                else:
                                    rel_path = os.path.relpath(texture_path, model_dir)
                                    mesh.texture_file = rel_path

                                print("Texture path: ", mesh.texture_file)
                            except Exception as ex:
                                print(ex)

                    else:
                        mesh.diffuse_color = [128, 128, 128, 255]
                        mesh.name += " Material: Undefined"
                        print("Material is't defined. Applied: ", mesh.diffuse_color)

                    # Устанавливаем декаль, если надо
                    mesh.is_decale = self.export_props.use_transparent_decale_color

                    if mesh.is_decale:
                        mesh.decale_color.append(self.export_props.decale_red)
                        mesh.decale_color.append(self.export_props.decale_green)
                        mesh.decale_color.append(self.export_props.decale_blue)

                    # Устанавливаем двойные грани, если надо
                    mesh.is_addFace2 = self.export_props.is_face2

                    # Переходим к координатам OpenBVE
                    if self.export_props.is_coord_transform:
                        print("Convertion to CSV coordinate system...")
                        gm.toLeftBasis(obj, mesh)

                    # Добавляем меш в список
                    meshes_list.append(mesh)

        return meshes_list

    #---------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------
    def exportModel(self, path):

        self.filepath = path

        from .CSV import CSVLoader

        exporter = CSVLoader()
        exporter.export(path, self.getSelectedMeshes(), self.export_props.is_coord_transform)
