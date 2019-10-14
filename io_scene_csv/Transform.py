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


def swap_coordinate_system(mesh: Union[bpy.types.Mesh, bmesh.types.BMesh]) -> None:
    mat = mathutils.Matrix()
    mat[0][0], mat[0][1], mat[0][2], mat[0][3] = 1, 0, 0, 0
    mat[1][0], mat[1][1], mat[1][2], mat[1][3] = 0, 0, 1, 0
    mat[2][0], mat[2][1], mat[2][2], mat[2][3] = 0, 1, 0, 0
    mat[3][0], mat[3][1], mat[3][2], mat[3][3] = 0, 0, 0, 1

    mesh.transform(mat)
