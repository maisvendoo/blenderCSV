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

    def triangulate(self, face):
        faces = []
        for i in range(1, len(face) - 1):
            faces.append([face[0], face[i], face[i+1]])

        print(faces)

        return faces

    def loadCSV(self, filePath):

        self.meshes_list.clear()

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
                try:
                    x = float(tmp[1])
                    y = float(tmp[2])
                    z = float(tmp[3])
                    vertex = (x, y, z)
                    mesh.addVertex(vertex)
                except ValueError:
                    pass


            # Face detection
            if tmp[0] == "AddFace":
                face = []
                for i in range(len(tmp)):
                    if i != 0:
                        try:
                            v = int(tmp[i])
                            face.append(v)
                        except ValueError:
                            pass

                if len(face) > 3:
                    faces = self.triangulate(face)
                    for fc in faces:
                        mesh.addFace(fc)
                else:
                    mesh.addFace(face)

        f.close()

        return self.meshes_list
