# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.win32.versioninfo import VSVersionInfo, FixedFileInfo, StringFileInfo, StringTable, StringStruct

version_info = VSVersionInfo(
                    ffi=FixedFileInfo(
                        filevers=(1, 0, 0, 0),
                        prodvers=(1, 0, 0, 0),
                        mask=0x3f,
                        flags=0x0,
                        OS=0x40004,
                        fileType=0x1,
                        subtype=0x0,
                        date=(0, 0)
                    ),
                    kids=[
                        StringFileInfo([
                            StringTable(
                                '040904B0',
                                [StringStruct('CompanyName', 'Venoryk'),
                                StringStruct('FileDescription', 'Project Lazarus Gear Comparison Tool'),
                                StringStruct('FileVersion', '1.0.0.0'),
                                StringStruct('InternalName', 'LazGearCompare'),
                                StringStruct('LegalCopyright', 'Copyright (c) 2024 Joshua Quillin (Venoryk)'),
                                StringStruct('OriginalFilename', 'LazGearCompare.exe'),
                                StringStruct('ProductName', 'LazGearCompare'),
                                StringStruct('ProductVersion', '1.0.0.0')])
                        ])
                    ]
                )

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('ui', 'ui'),
        ('ui/CTkXYFrame', 'ui/CTkXYFrame'),
        ('utils', 'utils'),
        ('config', 'config'),
        ('core', 'core'),
        ('assets/LazGearCompare.ico', 'assets'),
    ],
    hiddenimports=[
        'customtkinter', 
        'CTkMessagebox',
        'ui.CTkXYFrame.CTkXYFrame',
        'logging',
        'logging.handlers',
        'os',
        'ui',
        'utils',
        'config',
        'assets',
        'core'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='LazGearCompare',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.abspath(os.path.join(os.getcwd(), 'assets', 'LazGearCompare.ico')),
    uac_admin=False,
    uac_uiaccess=False,
    version_info=version_info,
    manifest='app.manifest',
)