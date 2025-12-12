# Version info for Windows executable
# This creates the version resource for the EXE

VSVersionInfo(
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
        StringFileInfo(
            [
                StringTable(
                    '041604B0',  # Portuguese Brazil
                    [
                        StringStruct('CompanyName', 'Guilherme Pinheiro'),
                        StringStruct('FileDescription', 'CSVToolBox - CSV Toolkit / Caixa de Ferramentas CSV'),
                        StringStruct('FileVersion', '1.0.0.0'),
                        StringStruct('InternalName', 'CSVToolBox'),
                        StringStruct('LegalCopyright', '© 2025 Guilherme Pinheiro - MIT License'),
                        StringStruct('OriginalFilename', 'CSVToolBox.exe'),
                        StringStruct('ProductName', 'CSVToolBox'),
                        StringStruct('ProductVersion', '1.0.0.0'),
                    ]
                )
            ]
        ),
        VarFileInfo([VarStruct('Translation', [0x0416, 1200])])
    ]
)
