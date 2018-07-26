import bpy

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
def invertVertexOrder(face):

    new_face = []
    new_face.append(face[0])

    for i in range(len(face) - 1, 0, -1):
        new_face.append(face[i])

    return new_face

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
def toLeftBasis(obj, mesh):

    import mathutils
    import math

    # Матрица поворота вокруг оси X
    mat_rot = mathutils.Matrix.Rotation(math.radians(-90.0), 4, 'X')

    # Матрица отражения вдоль оси Y
    mat_mirror_y = mathutils.Matrix()
    mat_mirror_y[0][0], mat_mirror_y[0][1], mat_mirror_y[0][2], mat_mirror_y[0][3] = 1, 0, 0, 0
    mat_mirror_y[1][0], mat_mirror_y[1][1], mat_mirror_y[1][2], mat_mirror_y[1][3] = 0, -1, 0, 0
    mat_mirror_y[2][0], mat_mirror_y[2][1], mat_mirror_y[2][2], mat_mirror_y[2][3] = 0, 0, 1, 0
    mat_mirror_y[3][0], mat_mirror_y[3][1], mat_mirror_y[3][2], mat_mirror_y[3][3] = 0, 0, 0, 1

    # Матрица перехода к мировым координатам
    mat_world = obj.matrix_world

    # Выделяем мтарицу поворота для мировых осей
    loc, world_rot, scale = obj.matrix_world.decompose()

    # Для каждой вершины
    for i, vertex in enumerate(mesh.vertex_list):

        loc_vert = mathutils.Vector(vertex)
        loc_norm = mathutils.Vector(mesh.normals_list[i])

        # Переходим к мировым координатам
        world_vert = mat_world * loc_vert
        # Переходим к левой системе координат
        new_vert = mat_rot * mat_mirror_y * world_vert
        mesh.vertex_list[i] = list(new_vert)

        # Поворачиваем нормаль
        world_norm = world_rot * loc_norm
        new_norm = mat_rot * mat_mirror_y * world_norm
        mesh.normals_list[i] = list(new_norm)

    # Перелицовываем грани
    for i, face in enumerate(mesh.faces_list):
        mesh.faces_list[i] = invertVertexOrder(face)

