#    Copyright 2018, 2019 Dmirty Pritykin, 2019 S520
#
#    This file is part of blenderCSV.
#
#    blenderCSV is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    blenderCSV is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with blenderCSV.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import bmesh
import mathutils
from typing import Union


def swap_coordinate_system(matrix_world: mathutils.Matrix, mesh: Union[bpy.types.Mesh, bmesh.types.BMesh], is_swap: bool) -> None:
    swap_mat = mathutils.Matrix.Identity(4)

    if is_swap:
        swap_mat[0][0], swap_mat[0][1], swap_mat[0][2], swap_mat[0][3] = 1, 0, 0, 0
        swap_mat[1][0], swap_mat[1][1], swap_mat[1][2], swap_mat[1][3] = 0, 0, 1, 0
        swap_mat[2][0], swap_mat[2][1], swap_mat[2][2], swap_mat[2][3] = 0, 1, 0, 0
        swap_mat[3][0], swap_mat[3][1], swap_mat[3][2], swap_mat[3][3] = 0, 0, 0, 1

    trans, rot, scale = matrix_world.decompose()

    if type(mesh) is bpy.types.Mesh:
        for vertex in mesh.vertices:
            vertex.co = swap_mat * matrix_world * vertex.co
            vertex.normal = (swap_mat * matrix_world).to_3x3().normalized() * vertex.normal

    if type(mesh) is bmesh.types.BMesh:
        for vertex in mesh.verts:
            vertex.co = swap_mat * matrix_world * vertex.co
            vertex.normal = (swap_mat * matrix_world).to_3x3().normalized() * vertex.normal
