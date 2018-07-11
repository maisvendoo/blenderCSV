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


    vertex_list = []
    faces_list = []
    texcoords_list = []

    def __init__(self):
        self.vertex_list.clear()
        self.faces_list.clear()
        self.texcoords_list.clear()


    def addVertex(self, vertex):
        self.vertex_list.append(vertex)

    def addFace(self, face):
        self.faces_list.append(face)

    def getVerticies(self):
        return self.vertex_list

    def getFaces(self):
        return self.faces_list

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
class CSVLoader:

    meshes_list = []

    def __init__(self):
        self.meshes_list.clear()

    def parseLine(self, line):
        tmp = line.rstrip('\n').rstrip('\r').rstrip(' ').split(",")
        return tmp

    def triangulate(self, face):
        faces = []
        for i in range(1, len(face) - 1):
            faces.append([face[0], face[i], face[i+1]])

        print(faces)

        return faces

    def loadCSV(self, filePath):

        meshes_list = list()

        # Open CSV file
        f = open(filePath, 'r')
        # Create temporary mesh

        # Read all file
        csv_text = f.read().split('\n')
        f.close()

        # Create add meshes in list
        for line in csv_text:
            command = self.parseLine(line)
            if command[0] == "CreateMeshBuilder":
                import copy
                mesh = CSVmesh()
                print(mesh)
                meshes_list.append(copy.deepcopy(mesh))

        m_idx = -1
        for line in csv_text:
            command = self.parseLine(line)

            if command[0] == "CreateMeshBuilder":
                m_idx = m_idx + 1

            if command[0] == "AddVertex":
                try:
                    x = float(command[1])
                    y = float(command[2])
                    z = float(command[3])
                    vertex = (x, y, z)
                    meshes_list[m_idx].addVertex(vertex)
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

                meshes_list[m_idx].addFace(tuple(face))

        for m in meshes_list:
            print("v:" + str(len(m.getVerticies())) + "," +
                  "f:" + str(len(m.getFaces())))

        '''
        # Scan all lines of file
        for line in f.readlines():

            

            # Parse line to command list
            tmp = self.parseLine(line)

            # Mesh detection
            if tmp[0] == "CreateMeshBuilder":
                if len(meshes_list) == 0:
                    meshes_list.append(mesh)
                else:
                    tmp_mesh = mesh.copy()
                    meshes_list.append(tmp_mesh)
                    mesh = CSVmesh()


            # Vertex detection
            if tmp[0] == "AddVertex":
                try:
                    x = float(tmp[1])
                    y = float(tmp[2])
                    z = float(tmp[3])
                    vertex = (x, y, z)
                    mesh.addVertex(vertex)
                except ValueError:
                    pass


            # Face detection
            if tmp[0] == "AddFace" or tmp[0] == "AddFace2":
                face = []
                for i in range(1, len(tmp)):
                    try:
                        v = int(tmp[i])
                        face.append(v)
                    except ValueError:
                        print("ERROR!!! INVALID DATA")


                mesh.addFace(tuple(face))
        '''

        return meshes_list
