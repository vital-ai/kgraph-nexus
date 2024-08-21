from PyInstaller.utils.hooks import collect_submodules, collect_data_files, copy_metadata

hiddenimports = collect_submodules('vital-ai-vitalsigns')
datas = copy_metadata('vital_ai_vitalsigns') + collect_data_files('vital_ai_vitalsigns', include_py_files=True)
