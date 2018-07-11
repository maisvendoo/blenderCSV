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

    def __init__(self):
        self.meshes_list = []

    def parseLine(self, line):
        tmp = line.rstrip('\n').rstrip('\r').rstrip(' ').split(",")
        return tmp

    def loadCSV(self, filePath):

        # Open CSV file
        f = open(filePath, 'r')
        # Create temporary mesh
        mesh = CSVmesh()

        # Scan all lines of file
        for line in f.readlines():

            # Parse line to command list
            tmp = self.parseLine(line)

            # Mesh detection
            if tmp[0] == "CreateMeshBuilder":
                self.meshes_list.append(mesh)
                mesh = CSVmesh()

            # Vertex detection
            if tmp[0] == "AddVertex":
                mesh.addVertex((float(tmp[1]), float(tmp[2]), float(tmp[3])))

            # Face detection
            if tmp[0] == "AddFace":
                face = []
                for i in range(len(tmp)):
                    if i != 0:
                        face.append(int(tmp[i]))

                mesh.addFace(tuple(face))


        f.close()

        return self.meshes_list
