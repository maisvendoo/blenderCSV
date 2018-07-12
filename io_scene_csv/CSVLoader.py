#-------------------------------------------------------------------------------
#
#       CSV model loader
#       RGUPS, Virtual Railway 11/07/2018
#       Developer: Dmirty Pritykin
#
#-------------------------------------------------------------------------------

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

                if command[0] == "AddFace" or command[0] == "AddFace2":
                    face = []
                    for i in range(1, len(command)):
                        try:
                            v = int(command[i])
                            face.append(v)
                        except ValueError:
                            print("ERROR!!! INVALID DATA")

                    mesh.faces_list.append(tuple(face))

                if command[0] == "Cube":
                    self.createCube(command, mesh)

            meshes_list.append(mesh)

        for m in meshes_list:
            print("v:" + str(len(m.vertex_list)) + "," +
                  "f:" + str(len(m.faces_list)))

        return meshes_list