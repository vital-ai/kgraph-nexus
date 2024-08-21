from PyInstaller.utils.hooks import collect_submodules, collect_data_files

hiddenimports = collect_submodules('engineio')
datas = collect_data_files('engineio', include_py_files=True)
