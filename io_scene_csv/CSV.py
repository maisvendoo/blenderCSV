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

import math
from typing import List, Tuple
from .chardet import chardet
from . import logger


class CsvMesh:
    def __init__(self) -> None:
        self.name = ""
        self.vertex_list = []   # type: List[Tuple[float, float, float]]
        self.normals_list = []   # type: List[Tuple[float, float, float]]
        self.use_add_face2 = False
        self.faces_list = []  # type: List[Tuple[int, ...]]
        self.diffuse_color = (255, 255, 255, 255)  # type: Tuple[int, int, int, int]
        self.use_emissive_color = False
        self.emissive_color = (0, 0, 0)  # type: Tuple[int, int, int]
        self.blend_mode = "Normal"
        self.glow_half_distance = 0
        self.glow_attenuation_mode = "DivideExponent4"
        self.texture_file = ""
        self.use_transparent_color = False
        self.transparent_color = (0, 0, 0)  # type: Tuple[int, int, int]
        self.texcoords_list = []  # type: List[Tuple[int, float, float]]


class ExportOption:
    def __init__(self):
        self.use_transform_coords = True
        self.global_mesh_scale = 1.0
        self.use_normals = True
        self.use_copy_texture_separate_directory = True


class CsvObject:
    def is_potential_path(self, line: str) -> bool:
        images = [".bmp", ".gi", ".jpg", ".jpeg", ".png"]

        for image in images:
            try:
                i = line.index(image)
            except ValueError:
                i = -1

            if i >= 0:
                return True

        return False

    def create_cube(self, mesh: CsvMesh, sx: float, sy: float, sz: float) -> None:
        v = len(mesh.vertex_list)

        mesh.vertex_list.append((sx, sy, -sz))
        mesh.vertex_list.append((sx, -sy, -sz))
        mesh.vertex_list.append((-sx, -sy, -sz))
        mesh.vertex_list.append((-sx, sy, -sz))
        mesh.vertex_list.append((sx, sy, sz))
        mesh.vertex_list.append((sx, -sy, sz))
        mesh.vertex_list.append((-sx, -sy, sz))
        mesh.vertex_list.append((-sx, sy, sz))

        mesh.faces_list.append(tuple(reversed((v + 0, v + 1, v + 2, v + 3))))
        mesh.faces_list.append(tuple(reversed((v + 0, v + 4, v + 5, v + 1))))
        mesh.faces_list.append(tuple(reversed((v + 0, v + 3, v + 7, v + 4))))
        mesh.faces_list.append(tuple(reversed((v + 6, v + 5, v + 4, v + 7))))
        mesh.faces_list.append(tuple(reversed((v + 6, v + 7, v + 3, v + 2))))
        mesh.faces_list.append(tuple(reversed((v + 6, v + 2, v + 1, v + 5))))

    def create_cylinder(self, mesh: CsvMesh, n: int, r1: float, r2: float, h: float) -> None:
        # Parameters
        uppercap = r1 > 0.0
        lowercap = r2 > 0.0
        m = (1 if uppercap else 0) + (1 if lowercap else 0)
        r1 = abs(r1)
        r2 = abs(r2)

        # Initialization
        v = len(mesh.vertex_list)
        d = 2.0 * math.pi / float(n)
        g = 0.5 * h
        t = 0.0

        # Vertices
        for i in range(n):
            dx = math.cos(t)
            dz = math.sin(t)
            lx = dx * r2
            lz = dz * r2
            ux = dx * r1
            uz = dz * r1
            mesh.vertex_list.append((ux, g, uz))
            mesh.vertex_list.append((lx, -g, lz))
            t += d

        # Faces
        for i in range(n):
            i0 = (2 * i + 2) % (2 * n)
            i1 = (2 * i + 3) % (2 * n)
            i2 = 2 * i + 1
            i3 = 2 * i
            mesh.faces_list.append(tuple(reversed((v + i0, v + i1, v + i2, v + i3))))

        for i in range(m):
            face = []

            for j in range(n):
                if i == 0 and lowercap:
                    # lower cap
                    face.append(v + 2 * j + 1)
                else:
                    # upper cap
                    face.append(v + 2 * (n - j - 1))

            mesh.faces_list.append(tuple(reversed(face)))

    def apply_translation(self, mesh: CsvMesh, x: float, y: float, z: float) -> None:
        for i in range(len(mesh.vertex_list)):
            mesh.vertex_list[i] = (mesh.vertex_list[i][0] + x, mesh.vertex_list[i][1] + y, mesh.vertex_list[i][2] + z)

    def apply_scale(self, mesh: CsvMesh, x: float, y: float, z: float) -> None:
        for i in range(len(mesh.vertex_list)):
            mesh.vertex_list[i] = (mesh.vertex_list[i][0] * x, mesh.vertex_list[i][1] * y, mesh.vertex_list[i][2] * z)

        if x * y * z < 0.0:
            for i in range(len(mesh.faces_list)):
                mesh.faces_list[i] = tuple(reversed(mesh.faces_list[i]))

    def apply_rotation(self, mesh: CsvMesh, r: Tuple[float, float, float], angle: float) -> None:
        cosine_of_angle = math.cos(angle)
        sine_of_angle = math.sin(angle)
        cosine_complement = 1.0 - cosine_of_angle

        for i in range(len(mesh.vertex_list)):
            x = (cosine_of_angle + cosine_complement * r[0] * r[0]) * mesh.vertex_list[i][0] + (cosine_complement * r[0] * r[1] - sine_of_angle * r[2]) * mesh.vertex_list[i][1] + (cosine_complement * r[0] * r[2] + sine_of_angle * r[1]) * mesh.vertex_list[i][2]
            y = (cosine_of_angle + cosine_complement * r[1] * r[1]) * mesh.vertex_list[i][1] + (cosine_complement * r[0] * r[1] + sine_of_angle * r[2]) * mesh.vertex_list[i][0] + (cosine_complement * r[1] * r[2] - sine_of_angle * r[0]) * mesh.vertex_list[i][2]
            z = (cosine_of_angle + cosine_complement * r[2] * r[2]) * mesh.vertex_list[i][2] + (cosine_complement * r[0] * r[2] - sine_of_angle * r[1]) * mesh.vertex_list[i][0] + (cosine_complement * r[1] * r[2] + sine_of_angle * r[0]) * mesh.vertex_list[i][1]
            mesh.vertex_list[i] = (x, y, z)

    def apply_shear(self, mesh: CsvMesh, d: Tuple[float, float, float], s: Tuple[float, float, float], r: float) -> None:
        for i in range(len(mesh.vertex_list)):
            n = r * (d[0] * mesh.vertex_list[i][0] + d[1] * mesh.vertex_list[i][1] + d[2] * mesh.vertex_list[i][2])
            mesh.vertex_list[i] = (mesh.vertex_list[i][0] + s[0] * n, mesh.vertex_list[i][1] + s[1] * n, mesh.vertex_list[i][2] + s[2] * n)

    def apply_mirror(self, mesh: CsvMesh, vx: bool, vy: bool, vz: bool):
        for i in range(len(mesh.vertex_list)):
            x = mesh.vertex_list[i][0] * -1.0 if vx else mesh.vertex_list[i][0]
            y = mesh.vertex_list[i][1] * -1.0 if vx else mesh.vertex_list[i][1]
            z = mesh.vertex_list[i][2] * -1.0 if vx else mesh.vertex_list[i][2]
            mesh.vertex_list[i] = (x, y, z)

        num_flips = 0

        if vx:
            num_flips += 1

        if vy:
            num_flips += 1

        if vz:
            num_flips += 1

        if num_flips % 2 != 0:
            for i in range(len(mesh.faces_list)):
                mesh.faces_list[i] = tuple(reversed(mesh.faces_list[i]))

    def normalize(self, v: Tuple[float, float, float]) -> Tuple[float, float, float]:
        norm = v[0] * v[0] + v[1] * v[1] + v[2] * v[2]

        if norm == 0.0:
            return v

        factor = 1.0 / math.sqrt(norm)
        return (v[0] * factor, v[1] * factor, v[2] * factor)

    def load_csv(self, file_path: str) -> List[CsvMesh]:
        meshes_list = []  # type: List[CsvMesh]

        logger.info("Loading file: " + file_path)

        # Open CSV file
        try:
            with open(file_path, "rb") as f:
                binary = f.read()

            csv_text = binary.decode(chardet.detect(binary)["encoding"]).splitlines()
        except Exception as ex:
            logger.critical(ex)
            return meshes_list

        # Parse CSV file
        # Delete comments
        comment_started = False

        for i in range(len(csv_text)):
            # Strip OpenBVE original standard comments
            try:
                j = csv_text[i].index(";")
            except ValueError:
                j = -1

            if j >= 0:
                csv_text[i] = csv_text[i][:j]

            # Strip double backslash comments
            try:
                k = csv_text[i].index("//")
            except ValueError:
                k = -1

            if k >= 0:
                if self.is_potential_path(csv_text[i]):
                    # HACK: Handles malformed potential paths
                    continue

                csv_text[i] = csv_text[i][:k]

            # Strip star backslash comments
            if not comment_started:
                try:
                    m = csv_text[i].index("/*")
                except ValueError:
                    m = -1

                if m >= 0:
                    comment_started = True
                    part1 = csv_text[i][:1]
                    part2 = ""

                    try:
                        n = csv_text[i].index("*/")
                    except ValueError:
                        n = -1

                    if n >= 0:
                        part2 = csv_text[i][n + 2:]

                    csv_text[i] = part1 + part2
            else:
                try:
                    m = csv_text[i].index("*/")
                except ValueError:
                    m = -1

                if m >= 0:
                    comment_started = True

                    if m + 2 != len(csv_text[i]):
                        csv_text[i] = csv_text[i][m + 2:]
                    else:
                        csv_text[i] = ""
                else:
                    csv_text[i] = ""

        # Parse lines
        mesh = None

        for i in range(len(csv_text)):
            # Collect arguments
            arguments = csv_text[i].split(",")

            for j in range(len(arguments)):
                arguments[j] = arguments[j].strip()

            command = arguments.pop(0)

            if command == "":
                continue

            # Parse terms
            if command.lower() == "CreateMeshBuilder".lower():
                if len(arguments) > 0:
                    logger.warning("0 arguments are expected in " + command + " at line " + str(i + 1))

                if mesh is not None:
                    meshes_list.append(mesh)

                mesh = CsvMesh()

            elif mesh is None:
                logger.error(command + " before the first CreateMeshBuilder are ignored at line " + str(i + 1))

            elif command.lower() == "AddVertex".lower():
                if len(arguments) > 6:
                    logger.warning("At most 6 arguments are expected in " + command + " at line " + str(i + 1))

                try:
                    vx = float(arguments[0])
                except Exception:
                    logger.error("Invalid argument vX in " + command + " at line " + str(i + 1))
                    vx = 0.0

                try:
                    vy = float(arguments[1])
                except Exception:
                    logger.error("Invalid argument vY in " + command + " at line " + str(i + 1))
                    vy = 0.0

                try:
                    vz = float(arguments[2])
                except Exception:
                    logger.error("Invalid argument vZ in " + command + " at line " + str(i + 1))
                    vz = 0.0

                if len(arguments) >= 4:
                    logger.info("This add-on ignores nX, nY and nZ in " + command + " at line " + str(i + 1))

                mesh.vertex_list.append((vx, vy, vz))

            elif command.lower() == "AddFace".lower() or command.lower() == "AddFace2".lower():
                if len(arguments) < 3:
                    logger.error("At least 3 arguments are required in " + command + " at line " + str(i + 1))
                else:
                    q = True
                    a = []

                    for j in range(len(arguments)):
                        try:
                            a.append(int(arguments[j]))
                        except Exception:
                            logger.error("v" + str(j) + " is invalid in " + command + " at line " + str(i + 1))
                            q = False
                            break

                        if a[j] < 0 or a[j] >= len(mesh.vertex_list):
                            logger.error("v" + str(j) + " references a non-existing vertex in " + command + " at line " + str(i + 1))
                            q = False
                            break

                        if a[j] > 65535:
                            logger.error("v" + str(j) + " indexes a vertex above 65535 which is not currently supported in " + command + " at line " + str(i + 1))
                            q = False
                            break

                    if q:
                        mesh.faces_list.append(tuple(reversed(a)))

                        if command.lower() == "AddFace2".lower():
                            mesh.faces_list.append(tuple(a))

            elif command.lower() == "Cube".lower():
                if len(arguments) > 3:
                    logger.warning("At most 3 arguments are expected in " + command + " at line " + str(i + 1))

                try:
                    x = float(arguments[0])
                except Exception:
                    logger.error("Invalid argument HalfWidth in " + command + " at line " + str(i + 1))
                    x = 1.0

                try:
                    y = float(arguments[1])
                except Exception:
                    logger.error("Invalid argument HalfHeight in " + command + " at line " + str(i + 1))
                    y = 1.0

                try:
                    z = float(arguments[2])
                except Exception:
                    logger.error("Invalid argument HalfDepth in " + command + " at line " + str(i + 1))
                    z = 1.0

                self.create_cube(mesh, x, y, z)

            elif command.lower() == "Cylinder".lower():
                if len(arguments) > 4:
                    logger.warning("At most 4 arguments are expected in " + command + " at line " + str(i + 1))

                try:
                    n = int(arguments[0])
                except Exception:
                    logger.error("Invalid argument n in " + command + " at line " + str(i + 1))
                    n = 8

                if n < 2:
                    logger.error("n is expected to be at least 2 in " + command + " at line " + str(i + 1))
                    n = 8

                try:
                    r1 = float(arguments[1])
                except Exception:
                    logger.error("Invalid argument UpperRadius in " + command + " at line " + str(i + 1))
                    r1 = 1.0

                try:
                    r2 = float(arguments[2])
                except Exception:
                    logger.error("Invalid argument LowerRadius in " + command + " at line " + str(i + 1))
                    r2 = 1.0

                try:
                    h = float(arguments[3])
                except Exception:
                    logger.error("Invalid argument Height in " + command + " at line " + str(i + 1))
                    h = 1.0

                self.create_cylinder(mesh, n, r1, r2, h)

            elif command.lower() == "Translate".lower() or command.lower() == "TranslateAll".lower():
                if len(arguments) > 3:
                    logger.warning("At most 3 arguments are expected in " + command + " at line " + str(i + 1))

                try:
                    x = float(arguments[0])
                except Exception:
                    logger.error("Invalid argument X in " + command + " at line " + str(i + 1))
                    x = 0.0

                try:
                    y = float(arguments[1])
                except Exception:
                    logger.error("Invalid argument Y in " + command + " at line " + str(i + 1))
                    y = 0.0

                try:
                    z = float(arguments[2])
                except Exception:
                    logger.error("Invalid argument Z in " + command + " at line " + str(i + 1))
                    z = 0.0

                self.apply_translation(mesh, x, y, z)

                if command.lower() == "TranslateAll".lower():
                    for other_mesh in meshes_list:
                        self.apply_translation(other_mesh, x, y, z)

            elif command.lower() == "Scale".lower() or command.lower() == "ScaleAll".lower():
                if len(arguments) > 3:
                    logger.warning("At most 3 arguments are expected in " + command + " at line " + str(i + 1))

                try:
                    x = float(arguments[0])
                except Exception:
                    logger.error("Invalid argument X in " + command + " at line " + str(i + 1))
                    x = 1.0

                if x == 0.0:
                    logger.error("X is required to be different from zero in " + command + " at line " + str(i + 1))
                    x = 1.0

                try:
                    y = float(arguments[1])
                except Exception:
                    logger.error("Invalid argument Y in " + command + " at line " + str(i + 1))
                    y = 1.0

                if y == 0.0:
                    logger.error("Y is required to be different from zero in " + command + " at line " + str(i + 1))
                    y = 1.0

                try:
                    z = float(arguments[2])
                except Exception:
                    logger.error("Invalid argument Z in " + command + " at line " + str(i + 1))
                    z = 1.0

                if z == 0.0:
                    logger.error("Z is required to be different from zero in " + command + " at line " + str(i + 1))
                    z = 1.0

                self.apply_scale(mesh, x, y, z)

                if command.lower() == "ScaleAll".lower():
                    for other_mesh in meshes_list:
                        self.apply_scale(other_mesh, x, y, z)

            elif command.lower() == "Rotate".lower() or command.lower() == "RotateAll".lower():
                if len(arguments) > 4:
                    logger.warning("At most 4 arguments are expected in " + command + " at line " + str(i + 1))

                try:
                    rx = float(arguments[0])
                except Exception:
                    logger.error("Invalid argument X in " + command + " at line " + str(i + 1))
                    rx = 0.0

                try:
                    ry = float(arguments[1])
                except Exception:
                    logger.error("Invalid argument Y in " + command + " at line " + str(i + 1))
                    ry = 0.0

                try:
                    rz = float(arguments[2])
                except Exception:
                    logger.error("Invalid argument Z in " + command + " at line " + str(i + 1))
                    rz = 0.0

                try:
                    angle = float(arguments[3])
                except Exception:
                    logger.error("Invalid argument Angle in " + command + " at line " + str(i + 1))
                    angle = 0.0

                t = rx * rx + ry * ry + rz * rz

                if t == 0.0:
                    rz = 1.0
                    ry = rz = 0.0
                    t = 1.0

                if angle != 0.0:
                    t = 1.0 / math.sqrt(t)
                    rx *= t
                    ry *= t
                    rz *= t
                    angle *= math.pi / 180.0

                    self.apply_rotation(mesh, (rx, ry, rz), angle)

                    if command.lower() == "RotateAll".lower():
                        for other_mesh in meshes_list:
                            self.apply_rotation(other_mesh, (rx, ry, rz), angle)

            elif command.lower() == "Shear".lower() or command.lower() == "ShearAll".lower():
                if len(arguments) > 7:
                    logger.warning("At most 7 arguments are expected in " + command + " at line " + str(i + 1))

                try:
                    dx = float(arguments[0])
                except Exception:
                    logger.error("Invalid argument dX in " + command + " at line " + str(i + 1))
                    dx = 0.0

                try:
                    dy = float(arguments[1])
                except Exception:
                    logger.error("Invalid argument dY in " + command + " at line " + str(i + 1))
                    dy = 0.0

                try:
                    dz = float(arguments[2])
                except Exception:
                    logger.error("Invalid argument dZ in " + command + " at line " + str(i + 1))
                    dz = 0.0

                try:
                    sx = float(arguments[3])
                except Exception:
                    logger.error("Invalid argument sX in " + command + " at line " + str(i + 1))
                    sx = 0.0

                try:
                    sy = float(arguments[4])
                except Exception:
                    logger.error("Invalid argument sY in " + command + " at line " + str(i + 1))
                    sy = 0.0

                try:
                    sz = float(arguments[5])
                except Exception:
                    logger.error("Invalid argument sZ in " + command + " at line " + str(i + 1))
                    sz = 0.0

                try:
                    r = float(arguments[6])
                except Exception:
                    logger.error("Invalid argument Ratio in " + command + " at line " + str(i + 1))
                    r = 0.0

                d = self.normalize((dx, dy, dz))
                s = self.normalize((sx, sy, sz))
                self.apply_shear(mesh, d, s, r)

                if command.lower() == "ShearAll".lower():
                    for other_mesh in meshes_list:
                        self.apply_shear(other_mesh, d, s, r)

            elif command.lower() == "Mirror".lower() or command.lower() == "MirrorAll".lower():
                if len(arguments) > 6:
                    logger.warning("At most 6 arguments are expected in " + command + " at line " + str(i + 1))

                try:
                    vx = float(arguments[0])
                except Exception:
                    logger.error("Invalid argument vX in " + command + " at line " + str(i + 1))
                    vx = 0.0

                try:
                    vy = float(arguments[1])
                except Exception:
                    logger.error("Invalid argument vY in " + command + " at line " + str(i + 1))
                    vy = 0.0

                try:
                    vz = float(arguments[2])
                except Exception:
                    logger.error("Invalid argument vZ in " + command + " at line " + str(i + 1))
                    vz = 0.0

                if len(arguments) >= 4:
                    logger.info("This add-on ignores nX, nY and nZ in " + command + " at line " + str(i + 1))

                self.apply_mirror(mesh, vx != 0.0, vy != 0.0, vz != 0.0)

                if command.lower() == "MirrorAll".lower():
                    for other_mesh in meshes_list:
                        self.apply_mirror(other_mesh, vx != 0.0, vy != 0.0, vz != 0.0)

            elif command.lower() == "SetColor".lower():
                if len(arguments) > 4:
                    logger.warning("At most 4 arguments are expected in " + command + " at line " + str(i + 1))

                try:
                    red = int(arguments[0])
                except Exception:
                    logger.error("Invalid argument Red in " + command + " at line " + str(i + 1))
                    red = 0

                if red < 0 or red > 255:
                    logger.error("Red is required to be within the range from 0 to 255 in " + command + " at line " + str(i + 1))
                    red = 0 if red < 0 else 255

                try:
                    green = int(arguments[1])
                except Exception:
                    logger.error("Invalid argument Green in " + command + " at line " + str(i + 1))
                    green = 0

                if green < 0 or green > 255:
                    logger.error("Green is required to be within the range from 0 to 255 in " + command + " at line " + str(i + 1))
                    green = 0 if green < 0 else 255

                try:
                    blue = int(arguments[2])
                except Exception:
                    logger.error("Invalid argument Blue in " + command + " at line " + str(i + 1))
                    blue = 0

                if blue < 0 or blue > 255:
                    logger.error("Blue is required to be within the range from 0 to 255 in " + command + " at line " + str(i + 1))
                    blue = 0 if blue < 0 else 255

                try:
                    alpha = int(arguments[3])
                except Exception:
                    logger.error("Invalid argument Alpha in " + command + " at line " + str(i + 1))
                    alpha = 0

                if alpha < 0 or alpha > 255:
                    logger.error("Alpha is required to be within the range from 0 to 255 in " + command + " at line " + str(i + 1))
                    alpha = 0 if alpha < 0 else 255

                mesh.diffuse_color = (red, green, blue, alpha)

            elif command.lower() == "SetEmissiveColor".lower():
                if len(arguments) > 3:
                    logger.warning("At most 3 arguments are expected in " + command + " at line " + str(i + 1))

                try:
                    red = int(arguments[0])
                except Exception:
                    logger.error("Invalid argument Red in " + command + " at line " + str(i + 1))
                    red = 0

                if red < 0 or red > 255:
                    logger.error("Red is required to be within the range from 0 to 255 in " + command + " at line " + str(i + 1))
                    red = 0 if red < 0 else 255

                try:
                    green = int(arguments[1])
                except Exception:
                    logger.error("Invalid argument Green in " + command + " at line " + str(i + 1))
                    green = 0

                if green < 0 or green > 255:
                    logger.error("Green is required to be within the range from 0 to 255 in " + command + " at line " + str(i + 1))
                    green = 0 if green < 0 else 255

                try:
                    blue = int(arguments[2])
                except Exception:
                    logger.error("Invalid argument Blue in " + command + " at line " + str(i + 1))
                    blue = 0

                if blue < 0 or blue > 255:
                    logger.error("Blue is required to be within the range from 0 to 255 in " + command + " at line " + str(i + 1))
                    blue = 0 if blue < 0 else 255

                mesh.use_emissive_color = True
                mesh.emissive_color = (red, green, blue)

            elif command.lower() == "SetDecalTransparentColor".lower():
                if len(arguments) > 3:
                    logger.warning("At most 3 arguments are expected in " + command + " at line " + str(i + 1))

                try:
                    red = int(arguments[0])
                except Exception:
                    logger.error("Invalid argument Red in " + command + " at line " + str(i + 1))
                    red = 0

                if red < 0 or red > 255:
                    logger.error("Red is required to be within the range from 0 to 255 in " + command + " at line " + str(i + 1))
                    red = 0 if red < 0 else 255

                try:
                    green = int(arguments[1])
                except Exception:
                    logger.error("Invalid argument Green in " + command + " at line " + str(i + 1))
                    green = 0

                if green < 0 or green > 255:
                    logger.error("Green is required to be within the range from 0 to 255 in " + command + " at line " + str(i + 1))
                    green = 0 if green < 0 else 255

                try:
                    blue = int(arguments[2])
                except Exception:
                    logger.error("Invalid argument Blue in " + command + " at line " + str(i + 1))
                    blue = 0

                if blue < 0 or blue > 255:
                    logger.error("Blue is required to be within the range from 0 to 255 in " + command + " at line " + str(i + 1))
                    blue = 0 if blue < 0 else 255

                mesh.use_transparent_color = True
                mesh.transparent_color = (red, green, blue)

            elif command.lower() == "SetBlendMode".lower() or command.lower() == "SetBlendingMode".lower():
                if len(arguments) > 3:
                    logger.warning("At most 3 arguments are expected in " + command + " at line " + str(i + 1))

                try:
                    if arguments[0].lower() == "normal":
                        mesh.blend_mode = "Normal"
                    elif arguments[0].lower() == "additive" or arguments[0].lower() == "glow":
                        mesh.blend_mode = "Additive"
                    else:
                        logger.error("The given BlendMode is not supported in " + command + " at line " + str(i + 1))
                        mesh.blend_mode = "Normal"
                except Exception:
                    mesh.blend_mode = "Normal"

                try:
                    mesh.glow_half_distance = int(arguments[1])
                except Exception:
                    logger.error("Invalid argument GlowHalfDistance in " + command + " at line " + str(i + 1))
                    mesh.glow_half_distance = 0

                try:
                    if arguments[2].lower() == "DivideExponent2".lower():
                        mesh.glow_attenuation_mode = "DivideExponent2"
                    elif arguments[2].lower() == "DivideExponent4".lower():
                        mesh.glow_attenuation_mode = "DivideExponent4"
                    else:
                        logger.error("The given GlowAttenuationMode is not supported in " + command + " at line " + str(i + 1))
                        mesh.glow_attenuation_mode = "DivideExponent4"
                except Exception:
                    mesh.glow_attenuation_mode = "DivideExponent4"

            elif command.lower() == "LoadTexture".lower():
                if len(arguments) > 2:
                    logger.warning("At most 2 arguments are expected in " + command + " at line " + str(i + 1))

                try:
                    mesh.texture_file = arguments[0]
                except Exception:
                    logger.error("Invalid argument DaytimeTexture in " + command + " at line " + str(i + 1))

                if len(arguments) >= 2:
                    logger.info("This add-on ignores NighttimeTexture in " + command + " at line " + str(i + 1))

            elif command.lower() == "SetTextureCoordinates".lower():
                if len(arguments) > 3:
                    logger.warning("At most 3 arguments are expected in " + command + " at line " + str(i + 1))

                try:
                    j = int(arguments[0])
                except Exception:
                    logger.error("Invalid argument VertexIndex in " + command + " at line " + str(i + 1))
                    j = 0

                try:
                    x = float(arguments[1])
                except Exception:
                    logger.error("Invalid argument X in " + command + " at line " + str(i + 1))
                    x = 0.0

                try:
                    y = float(arguments[2])
                except Exception:
                    logger.error("Invalid argument Y in " + command + " at line " + str(i + 1))
                    y = 0.0

                if j >= 0 and j < len(mesh.vertex_list):
                    mesh.texcoords_list.append((j, x, y))
                else:
                    logger.error("VertexIndex references a non-existing vertex in " + command + " at line " + str(i + 1))

            else:
                logger.error("The command " + command + " is not supported at line " + str(i + 1))

        # Finalize
        if mesh is not None:
            meshes_list.append(mesh)

        return meshes_list

    def export_csv(self, option: ExportOption, meshes_list: List[CsvMesh], file_path: str) -> None:
        if len(meshes_list) == 0:
            logger.error("Select one or more objects to export.")
            return

        csv_text = []  # type: List[str]

        # Header
        csv_text.append(";---------------------------------------------------------------------------\n")
        csv_text.append("; This file was exported from Blender by blenderCSV.\n")
        csv_text.append("; https://github.com/maisvendoo/blenderCSV\n")
        csv_text.append("; The copyright of this file belongs to the creator of the original content.\n")
        csv_text.append(";---------------------------------------------------------------------------\n")

        # Export model
        for mesh in meshes_list:
            # Apply global scale
            self.apply_scale(mesh, option.global_mesh_scale, option.global_mesh_scale, option.global_mesh_scale)

            # New mesh
            csv_text.append("\n; " + mesh.name + "\n")
            csv_text.append("CreateMeshBuilder\n")

            # Vertices
            for vertex, normal in zip(mesh.vertex_list, mesh.normals_list):
                vertex_text = str(vertex[0]) + ", " + str(vertex[1]) + ", " + str(vertex[2])
                normal_text = str(normal[0]) + ", " + str(normal[1]) + ", " + str(normal[2])

                if option.use_normals:
                    csv_text.append("AddVertex, " + vertex_text + ", " + normal_text + "\n")
                else:
                    csv_text.append("AddVertex, " + vertex_text + "\n")

            # Faces
            for face in mesh.faces_list:
                face_text = ""

                for vertex_index in reversed(face):
                    face_text += ", " + str(vertex_index)

                if mesh.use_add_face2:
                    csv_text.append("AddFace2" + face_text + "\n")
                else:
                    csv_text.append("AddFace" + face_text + "\n")

            # Diffuse color
            csv_text.append("SetColor, " + str(mesh.diffuse_color[0]) + ", " + str(mesh.diffuse_color[1]) + ", " + str(mesh.diffuse_color[2]) + "\n")

            # Emissive color
            if mesh.use_emissive_color:
                csv_text.append("SetEmissiveColor, " + str(mesh.emissive_color[0]) + ", " + str(mesh.emissive_color[1]) + ", " + str(mesh.emissive_color[2]) + "\n")

            # Blend mode
            csv_text.append("SetBlendMode, " + mesh.blend_mode + ", " + str(mesh.glow_half_distance) + ", " + mesh.glow_attenuation_mode + "\n")

            # Texture
            if mesh.texture_file != "":
                csv_text.append("LoadTexture, " + mesh.texture_file + "\n")

            # Transparent color
            if mesh.use_transparent_color:
                csv_text.append("SetDecalTransparentColor, " + str(mesh.transparent_color[0]) + ", " + str(mesh.transparent_color[1]) + ", " + str(mesh.transparent_color[2]) + "\n")

            # Texture coordinates
            for texcoords in mesh.texcoords_list:
                csv_text.append("SetTextureCoordinates, " + str(texcoords[0]) + ", " + str(texcoords[1]) + ", " + str(texcoords[2]) + "\n")

        # Write file
        try:
            with open(file_path, "wt", encoding="utf-8") as f:
                f.writelines(csv_text)
        except Exception as ex:
            logger.critical(ex)
