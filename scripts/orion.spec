# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller specification file for ORION Windows Executable
===========================================================
Bundles ORION into a single standalone Windows application directory with
local ML models, static web dashboard, and offline voice dependencies.
"""

import sys
import os
from pathlib import Path

block_cipher = None

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

datas = [
    (os.path.join(ROOT_DIR, "config"), "config"),
    (os.path.join(ROOT_DIR, "data"), "data"),
    (os.path.join(ROOT_DIR, "models"), "models"),
    (os.path.join(ROOT_DIR, "web"), "web"),
]

hiddenimports = [
    "sklearn",
    "sklearn.utils._typedefs",
    "sklearn.neighbors._typedefs",
    "whisper",
    "openwakeword",
    "fastapi",
    "uvicorn",
    "websockets",
    "customtkinter",
    "scipy",
    "scipy.signal",
    "sounddevice",
    "soundfile",
    "psutil",
    "pyautogui",
    "pyperclip",
    "pyttsx3",
    "pyttsx3.drivers",
    "pyttsx3.drivers.sapi5",
]

a = Analysis(
    [os.path.join(ROOT_DIR, "app.py")],
    pathex=[ROOT_DIR],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter.test", "pytest", "tests"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="ORION",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Launch as a windowed application without a persistent CMD window
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
    upx=True,
    upx_exclude=[],
    name="ORION",
)
