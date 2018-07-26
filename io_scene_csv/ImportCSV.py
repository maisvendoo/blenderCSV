#-------------------------------------------------------------------------------
#
#       CSV models import module
#       (c) RGUPS, Virtual Railway 26/07/2018
#       Developer: Dmitry Pritykin
#
#-------------------------------------------------------------------------------
import bpy
import bmesh
import os

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
class ImportCSV:

    #---------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------
    def __init__(self):
        self.filepath = ""

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

        # Создаем материал. Если есть текстура, то используем имя
        # файла текстуры в качестве имени материала
        if mesh.texture_file != "":
            matName = self.getFileName(mesh.texture_file)
        else:
            matName = md.name;

        print("Creation of material: ", matName)

        # Проверяем, существует ли уже такой материал
        mat = bpy.data.materials.get(matName)

        # Если не существует, создаем его заново
        if mat is None:
            mat = bpy.data.materials.new(name=matName)
            print("New material ", matName, " created")
        else:
            print("Material ", matName, " already exists")
            # проверяем число текстурных слотов в материале
            if len(mat.texture_slots) == 18:
                print("WARNING: maximal number of texture slots 18. All textures will deleted")
                for i, slot in enumerate(mat.texture_slots):
                    mat.texture_slots.clear(i)

        # Добавляем материал в слот материалов
        print("Material slots number: ", len(md.materials))

        if md.materials:
            md.materials[0] = mat
        else:
            md.materials.append(mat)

        # Задаем параметры диффузного цвета
        if mesh.diffuse_color:
            mat.diffuse_color = (
            mesh.diffuse_color[0] / 255.0, mesh.diffuse_color[1] / 255.0, mesh.diffuse_color[2] / 255.0)

        # Задаем параметры альфа-канала
        if len(mesh.diffuse_color) > 3:
            mat.alpha = float(mesh.diffuse_color[3]) / 255.0
            mat.use_transparency = True
            mat.transparency_method = 'Z_TRANSPARENCY'

        # Настраиваем текстуру
        if mesh.texture_file != "":
            # Получаем имя каталога модели
            modelDir = os.path.dirname(self.filepath)
            # Вычисляем абсолютный путь к файлу текстуры
            texImgPath = os.path.join(modelDir, mesh.texture_file)
            # Грузим текстуру
            img = bpy.data.images.load(texImgPath)

            # Создаем новую текустуру
            tex = bpy.data.textures.new("tex-" + mat.name, 'IMAGE')
            tex.image = img

            print("Textures slots: ", len(mat.texture_slots))

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
    #
    #---------------------------------------------------------------------------
    def modelImport(self, path, is_coord_transform):

        from . import CSV
        from . import GeometryMath as gm

        self.filepath = path

        # Загружаем структуру модели из CSV-файла
        loader = CSV.CSVLoader()
        meshes_list = loader.loadCSV(path, is_coord_transform)

        print("Loaded " + str(len(meshes_list)) + " meshes")

        # Создаем все объекты, в соответсвии со списком мешей, полученом из CSV
        for m_idx, m in enumerate(meshes_list):

            # Берем имя объекта
            obj_name = self.getFileName(path)

            # Создаем меш объекта, в соответствии с загруженной геометрией
            md = bpy.data.meshes.new(obj_name + "-" + str(m_idx))
            md.from_pydata(m.vertex_list, [], m.faces_list)
            md.update(calc_edges=True)

            # Создаем материал
            self.createMaterial(md, m)

            # Создаем UV-развертку
            self.setUVcoords(md, m)

            # Если надо, выполняем трансформацию в правую СК
            if is_coord_transform:
                gm.toRightBasis(md)

            # Содаем объект и добавляем его в сцену
            obj = bpy.data.objects.new(md.name, md)
            bpy.context.scene.objects.link(obj)
            obj.select = True