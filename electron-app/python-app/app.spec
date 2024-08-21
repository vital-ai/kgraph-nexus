# -*- mode: python ; coding: utf-8 -*-

import os
import subprocess
import re
import logging
from PyInstaller.utils.hooks import collect_submodules, collect_data_files, get_package_paths, collect_all

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info("starting...")

block_cipher = None



# testing inclusion of domain dependencies
dependencies={
    'vital-ai-vitalsigns',
    'vital-ai-domain',
    'vital-ai-social',
    'vital-ai-haley',
    'vital-ai-haley-taxonomy',
    'vital-ai-haley-kg',
    'vital-ai-haley-question',
    'vital-ai-aimp',
    'vital-ai-nlp'
}

packages = [
    'com_vitalai_aimp_domain',
    'com_vitalai_domain_nlp',
    'com_vitalai_domain_social',
    'com_vitalai_haley_domain',
    'com_vitalai_haley_taxonomy_domain',
    'com_vitalai_haleyai_question_domain',
    'vital_ai_domain',
    'vital_ai_vitalsigns_core',
    'ai_haley_kg_domain'
]

all_datas = []
all_binaries = []
all_hiddenimports = []

for package in packages:
    datas, binaries, hiddenimports = collect_all(package)
    all_datas.extend(datas)
    all_binaries.extend(binaries)
    all_hiddenimports.extend(hiddenimports)


all_datas.append(('assets', 'assets'))
all_datas.append(('src', 'src'))

# temp, to be removed:
all_datas.append(('app_config.yaml', '.'))
all_datas.append(('vital_env.env', '.'))
all_datas.append(('vitalhome', 'vitalhome'))



a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=all_binaries,
    datas=all_datas,
    hiddenimports=all_hiddenimports,
    hookspath=['hooks'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'test', 'unittest', 'distutils'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name='dist/app'
)
