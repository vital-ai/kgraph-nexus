from PyInstaller.utils.hooks import copy_metadata, collect_data_files

# Include package metadata and data files
datas = copy_metadata('dash_cytoscape') + collect_data_files('dash_cytoscape')
