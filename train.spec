# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['train.py'],
    pathex=[],
    binaries=[],
    datas=[('map.png', '.'), ('trains.txt', '.'),
           ('train.exe', '.'), ('geo.json', '.'), ('train.ico', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['altgraph', 'importlib_metadata', 'packaging', 'pefile', 'pip', 'pyinstaller',
              'pyinstaller-hooks-contrib', 'pywin32-ctypes', 'setuptools', 'wheel', 'zipp'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='train',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['train.ico'],
)
