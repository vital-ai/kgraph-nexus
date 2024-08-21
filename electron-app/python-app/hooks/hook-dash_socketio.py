from PyInstaller.utils.hooks import collect_submodules, collect_data_files

hiddenimports = collect_submodules('dash_socketio')
datas = collect_data_files('dash_socketio', include_py_files=True)
