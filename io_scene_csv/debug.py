from io_scene_csv import CSVLoader

def load():
    loader = CSVLoader.CSVLoader()
    meshes_list = loader.loadCSV("C:/Users/maisvendoo/Brevna.csv")

    for m in meshes_list:
        print(m)

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
if __name__ == "__main__":
    load()


