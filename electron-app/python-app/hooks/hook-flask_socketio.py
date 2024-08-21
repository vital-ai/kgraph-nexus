from PyInstaller.utils.hooks import collect_submodules, collect_data_files

hiddenimports = collect_submodules('flask_socketio')
datas = collect_data_files('flask_socketio', include_py_files=True)
