# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None

# Diretório do projeto
projeto_root = os.path.abspath('.')

# Coletar todos os arquivos da pasta tools
tools_datas = []
for f in os.listdir('tools'):
    if f.endswith('.py'):
        tools_datas.append((os.path.join('tools', f), 'tools'))

# Coletar arquivos de imagem
img_datas = []
if os.path.exists('img'):
    for f in os.listdir('img'):
        img_datas.append((os.path.join('img', f), 'img'))

a = Analysis(
    ['main.py'],
    pathex=[projeto_root],
    binaries=[],
    datas=[
        ('i18n.py', '.'),
        *tools_datas,
        *img_datas,
    ],
    hiddenimports=[
        # CustomTkinter
        'customtkinter',
        'customtkinter.windows',
        'customtkinter.windows.widgets',
        # Pandas e dependências
        'pandas',
        'pandas._libs',
        'pandas._libs.tslibs.timedeltas',
        'pandas._libs.tslibs.nattype',
        'pandas._libs.tslibs.np_datetime',
        'pandas.core.frame',
        'pandas.io.formats.style',
        # Excel
        'openpyxl',
        'openpyxl.cell',
        'openpyxl.workbook',
        'xlrd',
        'pyxlsb',
        # Outros
        'chardet',
        'PIL',
        'PIL._tkinter_finder',
        'PIL.Image',
        'PIL.ImageTk',
        # Tkinter
        'tkinter',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.ttk',
        # Standard library
        'xml.etree.ElementTree',
        'json',
        'csv',
        're',
        'pathlib',
        'datetime',
        'subprocess',
        'ctypes',
        'locale',
        # Numpy (usado pelo pandas)
        'numpy',
        'numpy.core._methods',
        'numpy.lib.format',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'pytest',
        'IPython',
        'notebook',
        'jupyter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='CSVToolBox',
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
    icon='img/logo.ico',
    version='version_info.py',
)
