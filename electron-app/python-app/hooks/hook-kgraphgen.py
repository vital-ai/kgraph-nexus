from PyInstaller.utils.hooks import collect_submodules, collect_data_files, copy_metadata

hiddenimports = collect_submodules('kgraphgen')
datas = copy_metadata('kgraphgen') + collect_data_files('kgraphgen', include_py_files=True)
