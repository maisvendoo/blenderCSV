#-------------------------------------------------------------------------------
#
#       CSV model loader
#       RGUPS, Virtual Railway 11/07/2018
#       Developer: Dmirty Pritykin
#
#-------------------------------------------------------------------------------
import math

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
class CSVmesh:

    def __init__(self):
        self.vertex_list = []
        self.faces_list = []
        self.texcoords_list = []

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
class CSVLoader:

    meshes_list = []

    def __init__(self):
        self.meshes_list.clear()

    #---------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------
    def parseLine(self, line):
        tmp = line.rstrip('\n').rstrip('\r').rstrip(' ').split(",")
        return tmp

    # ---------------------------------------------------------------------------
    #
    # ---------------------------------------------------------------------------
    def createCube(self, command, mesh):

        x = 0
        y = 0
        z = 0

        try:
            x = float(command[1])
            y = float(command[2])
            z = float(command[3])
        except Exception as ex:
            print(ex)
            return

        # Add vertices
        v = (x, y, -z)
        mesh.vertex_list.append(v)
        v = (x, -y, -z)
        mesh.vertex_list.append(v)
        v = (-x, -y, -z)
        mesh.vertex_list.append(v)
        v = (-x, y, -z)
        mesh.vertex_list.append(v)
        v = (x, y, z)
        mesh.vertex_list.append(v)
        v = (x, -y, z)
        mesh.vertex_list.append(v)
        v = (-x, -y, z)
        mesh.vertex_list.append(v)
        v = (-x, y, z)
        mesh.vertex_list.append(v)

        # Add faces
        face = (0, 1, 2, 3)
        mesh.faces_list.append(face)
        face = (0, 4, 5, 1)
        mesh.faces_list.append(face)
        face = (0, 3, 7, 4)
        mesh.faces_list.append(face)
        face = (6, 5, 4, 7)
        mesh.faces_list.append(face)
        face = (6, 7, 3, 2)
        mesh.faces_list.append(face)
        face = (6, 2, 1, 5)
        mesh.faces_list.append(face)

    # ---------------------------------------------------------------------------
    #
    # ---------------------------------------------------------------------------
    def createCylinder(self, command, mesh):

        n = 0
        r1 = 0.0
        r2 = 0.0
        h = 0.0

        try:
            n = int(command[1])
            r1 = float(command[2])
            r2 = float(command[3])
            h = float(command[4])
        except Exception as ex:
            print(ex)
            return

        # Vertices generation
        for i in range(0, n):
            x = round(r1 * math.cos(2 * math.pi * i / n), 6)
            y = round(h / 2.0, 4)
            z = round(r1 * math.sin(2 * math.pi * i / n), 6)
            mesh.vertex_list.append((x, y, z))

            x = round(r2 * math.cos(2 * math.pi * i / n), 6)
            y = round(-h / 2.0, 4)
            z = round(r2 * math.sin(2 * math.pi * i / n), 6)
            mesh.vertex_list.append((x, y, z))

        # Side faces generation
        for i in range(0, n - 1):
            face = (2 * (i + 1), 2 * (i + 1) + 1, 2 * (i + 1) - 1, 2 * i)
            mesh.faces_list.append(face)

        mesh.faces_list.append((0, 1, 2 * n - 1, 2 * n - 2))

        # Lower face generation

        if r2 > 0:
            face = []
            for i in range(n-1, -1, -1):
                face.append(2*i)
            mesh.faces_list.append(tuple(face))

        # Upper face generation
        if r1 > 0:
            face = []
            for i in range(0, n):
                face.append(2*i + 1)
            mesh.faces_list.append(tuple(face))

    #---------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------
    def Translate(self, command, mesh):

        try:
            x = float(command[1])
            y = float(command[2])
            z = float(command[3])
        except Exception as ex:
            print(ex)
            return

        for i, v in enumerate(mesh.vertex_list):
            tmp = list(v)
            tmp[0] = tmp[0] + x
            tmp[1] = tmp[1] + y
            tmp[2] = tmp[2] + z
            v = tuple(tmp)
            mesh.vertex_list[i] = v

    #---------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------
    def TranslateAll(self, command, meshes_list, mesh):
        for m in meshes_list:
            self.Translate(command, m)

        self.Translate(command, mesh)


    # ---------------------------------------------------------------------------
    #
    # ---------------------------------------------------------------------------
    def Rotate(self, command, mesh):
        try:
            ux = float(command[1])
            uy = float(command[2])
            uz = float(command[3])
            angle = -float(command[4]) * math.pi / 180.0

            len = math.sqrt(ux * ux + uy * uy + uz * uz)

            try:

                # Normalize axis vector
                ex = ux / len
                ey = uy / len
                ez = uz / len

                # Rotate vertex by Rodrigue's formula
                for i, v in enumerate(mesh.vertex_list):
                    tmp = list(v)

                    c = ex * tmp[0] + ey * tmp[1] + ez * tmp[2]

                    nx = ez * tmp[1] - ey * tmp[2]
                    ny = ex * tmp[2] - ez * tmp[0]
                    nz = ey * tmp[0] - ex * tmp[1]

                    tmp[0] = round(c * (1 - math.cos(angle)) * ex + nx * math.sin(angle) + tmp[0] * math.cos(angle), 4)
                    tmp[1] = round(c * (1 - math.cos(angle)) * ey + ny * math.sin(angle) + tmp[1] * math.cos(angle), 4)
                    tmp[2] = round(c * (1 - math.cos(angle)) * ez + nz * math.sin(angle) + tmp[2] * math.cos(angle), 4)
                    v = tuple(tmp)
                    mesh.vertex_list[i] = v

            except Exception as ex:
                print(ex)
                return

        except Exception as ex:
            print(ex)
            return

    #---------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------
    def RotateAll(self, command, meshes_list, mesh):
        for m in meshes_list:
            self.Rotate(command, m)

        self.Rotate(command, mesh)

    #---------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------
    def Scale(self, command, mesh):
        try:
            sx = float(command[1])
            sy = float(command[2])
            sz = float(command[3])
        except Exception as ex:
            print(ex)
            return

        for i, v in enumerate(mesh.vertex_list):
            tmp = list(v)
            tmp[0] = sx * tmp[0]
            tmp[1] = sy * tmp[1]
            tmp[2] = sx * tmp[2]
            v = tuple(tmp)
            mesh.vertex_list[i] = v

    #---------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------
    def ScaleAll(self, command, meshes_list, mesh):
        for m in meshes_list:
            self.Scale(command, m)

        self.Scale(command, mesh)

    #---------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------
    def Mirror(self, command, mesh):
        try:
            mx = int(command[1])
            my = int(command[2])
            mz = int(command[3])
        except Exception as ex:
            print(ex)
            return

        for i, v in enumerate(mesh.vertex_list):
            tmp = list(v)

            if mx != 0:
                tmp[0] = -tmp[0]

            if my != 0:
                tmp[1] = -tmp[1]

            if mz != 0:
                tmp[2] = -tmp[2]

            v = tuple(tmp)
            mesh.vertex_list[i] = v

    #---------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------
    def MirrorAll(self, command, meshes_list, mesh):
        for m in meshes_list:
            self.Mirror(command, m)

        self.Mirror(command, mesh)

    #---------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------
    def toRightBasis(self, meshes_list):
        for m in meshes_list:
            command = [None, '0', '0', '1']
            self.Mirror(command, m)
            command = [None, '1', '0', '0', '90']
            self.Rotate(command, m)

    #---------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------
    def toLeftBasis(self, meshes_list):
        for m in meshes_list:
            command = [None, '1', '0', '0', '-90']
            self.Rotate(command, m)
            command = [None, '0', '0', '1']
            self.Mirror(command, m)


    #---------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------
    def loadCSV(self, filePath):

        meshes_list = []

        # Open CSV file
        try:
            f = open(filePath, 'rt')
        except Exception as ex:
            print(ex)
            return meshes_list

        # Create temporary mesh

        # Read all file
        csv_text = f.read().split('\n')
        f.close()

        # Find first mesh
        idx = 0
        mesh_begin_idx = []

        for line in csv_text:
            command = self.parseLine(line)
            if command[0] == "CreateMeshBuilder":
               mesh_begin_idx.append(idx)
            idx = idx + 1

        for idx in range(0, len(mesh_begin_idx)):

            mesh = CSVmesh()

            a = mesh_begin_idx[idx]

            if idx + 1 >= len(mesh_begin_idx):
                b = len(csv_text)
            else:
                b = mesh_begin_idx[idx+1]

            for j in range(a, b):

                command = self.parseLine(csv_text[j])

                if command[0] == "AddVertex":
                    try:
                        x = float(command[1])
                        y = float(command[2])
                        z = float(command[3])
                        vertex = (x, y, z)
                        mesh.vertex_list.append(vertex)
                    except ValueError:
                        pass

                if command[0] == "AddFace":
                    face = []
                    for i in range(1, len(command)):
                        try:
                            v = int(command[i])
                            face.append(v)
                        except ValueError:
                            print("ERROR: invalid data in string: " + str(j) +
                                  " argument: " + command[i])

                    mesh.faces_list.append(tuple(face))

                if command[0] == "AddFace2":
                    face1 = []
                    for i in range(1, len(command)):
                        try:
                            v = int(command[i])
                            face1.append(v)
                        except ValueError:
                            print("ERROR!!! INVALID DATA")

                    mesh.faces_list.append(tuple(face1))

                    face2 = []
                    face2.append(face1[0])

                    for i in range(len(face1) - 1, 0, -1):
                        face2.append(face1[i])

                    mesh.faces_list.append(tuple(face2))

                # Create cube
                if command[0] == "Cube":
                    self.createCube(command, mesh)

                # Create cylinder
                if command[0] == "Cylinder":
                    self.createCylinder(command, mesh)

                # Translate mesh
                if command[0] == "Translate":
                    self.Translate(command, mesh)

                # Rotate mesh
                if command[0] == "Rotate":
                    self.Rotate(command, mesh)

                # Translate current mesh and all previos meshes
                if command[0] == "TranslateAll":
                    self.TranslateAll(command, meshes_list, mesh)

                # Rotate cureent mesh and all previos meshes
                if command[0] == "RotateAll":
                    self.RotateAll(command, meshes_list, mesh)

                # Scale meshes
                if command[0] == "Scale":
                    self.Scale(command, mesh)

                if command[0] == "ScaleAll":
                    self.ScaleAll(command, mesh)

                # Mirror meshes
                if command[0] == "Mirror":
                    self.Mirror(command, mesh)

                if command[0] == "MirrorAll":
                    self.MirrorAll(command, mesh)

            meshes_list.append(mesh)

        for m in meshes_list:
            print("v:" + str(len(m.vertex_list)) + "," +
                  "f:" + str(len(m.faces_list)))

        # Convertion to Blender basis
        self.toRightBasis(meshes_list)

        return meshes_list

    #---------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------
    def generateModel(self, csv_text, meshes_list):
        for mesh in meshes_list:

            # New mesh
            csv_text.append("CreateMeshBuilder,\n")

            # Vertices
            for v in mesh.vertex_list:

                addVertex = "AddVertex, "
                for coord in v:
                    addVertex = addVertex + str(coord) + ", "
                csv_text.append(addVertex + "\n")

            csv_text.append("\n")

            # Faces
            for face in mesh.faces_list:

                addFace = "AddFace, "
                for v_idx in face:
                    addFace = addFace + str(v_idx) + ", "
                csv_text.append(addFace + "\n")

    #---------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------
    def export(self, path, meshes_list):

        csv_text = []
        csv_text.append(";------------------------------------------------------\n")
        csv_text.append("; CSV exporter from Blender, RGUPS, Dmitry Pritykin\n")
        csv_text.append(";------------------------------------------------------\n")
        csv_text.append("\n")

        # Conversion to left basis
        self.toLeftBasis(meshes_list)
        # Generate mesh
        self.generateModel(csv_text, meshes_list)

        try:

            # Output in file
            f = open(path, "wt", encoding="utf-8")
            f.writelines(csv_text)
            f.close()

        except Exception as ex:
            print(ex)
            return

