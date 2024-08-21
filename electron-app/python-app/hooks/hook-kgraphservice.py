from PyInstaller.utils.hooks import collect_submodules, collect_data_files, copy_metadata

hiddenimports = collect_submodules('kgraphservice')
datas = copy_metadata('kgraphservice') + collect_data_files('kgraphservice', include_py_files=True)
