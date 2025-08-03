# -*- mode: python ; coding: utf-8 -*-
import os
env_hook = os.path.abspath("env.py")

a = Analysis(
    ['bootstrapper.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=["pyzipper", "cryptography"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=["env.py"],
    excludes=[],
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
    name='bootstrapper',
    icon="sdk_icon.png",
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
)
