# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files, collect_submodules


binaries = [
    (r'disable_amsi\disable_amsi\disable_amsi.cp311-win_amd64.pyd', '.'),


]

# Collect data files from specific modules if needed
datas = collect_data_files('disable_amsi')  # Replace 'amsi' with actual module name if needed


a = Analysis(
    [r'C:\Users\User\statis\src\statis.py'],
    pathex=['.'],
    binaries=binaries,
    datas=datas,
    hiddenimports=[
],

    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='statis',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
