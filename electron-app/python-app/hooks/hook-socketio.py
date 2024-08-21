from PyInstaller.utils.hooks import collect_submodules, collect_data_files

hiddenimports = collect_submodules('socketio')
datas = collect_data_files('socketio', include_py_files=True)
