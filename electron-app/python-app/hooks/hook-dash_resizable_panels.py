from PyInstaller.utils.hooks import copy_metadata, collect_data_files

# Include package metadata and data files
datas = copy_metadata('dash_resizable_panels') + collect_data_files('dash_resizable_panels')
