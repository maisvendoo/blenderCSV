from io_scene_csv import CSV

def load():
    loader = CSV.CSVLoader()
    meshes_list = loader.loadCSV("D:/work/vr/3D-graphics/Routes/FirstBrnoTrack/Object/FirstBrnoTrack/Track/400L.csv")

    for m in meshes_list:
        print(m)

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
if __name__ == "__main__":
    load()


