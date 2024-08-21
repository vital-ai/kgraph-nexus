from PyInstaller.utils.hooks import collect_data_files
import owlready2

# Collect all data files, including the pellet reasoner
datas = collect_data_files('owlready2', subdir='pellet')
