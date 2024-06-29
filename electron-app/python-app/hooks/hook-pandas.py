from PyInstaller.utils.hooks import collect_submodules, collect_data_files

hiddenimports = collect_submodules('pandas')
datas = collect_data_files('pandas', include_py_files=True)
