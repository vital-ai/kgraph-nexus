from PyInstaller.utils.hooks import collect_submodules, collect_data_files

hiddenimports = collect_submodules('geventwebsocket')
datas = collect_data_files('geventwebsocket', include_py_files=True)
