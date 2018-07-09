




bl_info = {
    "name": "OpenBVE CSV format",
    "author": "Dmitry Pritykin",
    "version": (0, 1, 0),
    "blender": (2, 78, 0),
    "location": "File > Import-Export",
    "description": "Import CSV mesh, UV's, materials and textures",
    "warning": "",
    "wiki_url": "https://vk.com/maisvendoo",
    "support": 'OFFICIAL',
    "category": "Import-Export"}
	
import bpy

class CSVImporter(bpy.types.Operator):
	"""Load CSV mesh data"""
	bl_idname = "import_mesh.csv"
	bl_label = "Import CSV"
	bl_options = {'UNDO'}
	
	def execute(self, context):
		return {'FINISHED'}

def menu_import(self, context):
	self.layout.operator(CSVImporter.bl_idname, text="OpenBVE CSV (.csv)")
	
def register():
	bpy.types.INFO_MT_file_import.append(menu_import)
	
def unregister():
	bpy.types.INFO_MT_file_import.remove(menu_import)

if __name__ == "__main__":
	register()