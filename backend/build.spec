# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Pencil Draw Backend
Build command: pyinstaller build.spec
"""

import os
import sys
from pathlib import Path

# Get the backend directory
backend_dir = Path(SPECPATH)

block_cipher = None

# Collect all application files
added_files = [
    # Hand assets
    (str(backend_dir / 'assets' / 'hands'), 'assets/hands'),
    # App modules
    (str(backend_dir / 'app'), 'app'),
]

# Hidden imports required by FastAPI/Uvicorn
hidden_imports = [
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'fastapi',
    'starlette',
    'pydantic',
    'cv2',
    'numpy',
    'PIL',
    'PIL.Image',
    'multipart',
    'python_multipart',
    'anyio',
    'anyio._backends',
    'anyio._backends._asyncio',
    'email_validator',
]

a = Analysis(
    ['server.py'],
    pathex=[str(backend_dir)],
    binaries=[],
    datas=added_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'scipy',
        'pandas',
        'IPython',
        'jupyter',
        'notebook',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PencilDraw',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Keep console for logs
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path if you have one
)
