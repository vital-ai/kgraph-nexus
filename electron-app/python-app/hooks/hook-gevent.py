from PyInstaller.utils.hooks import collect_submodules, collect_data_files

hiddenimports = collect_submodules('gevent')
datas = collect_data_files('gevent', include_py_files=True)
