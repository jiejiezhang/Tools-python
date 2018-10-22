# -*- mode: python -*-

block_cipher = None


a = Analysis(['vid_tool.py'],
             pathex=['ecfile=vid_tool.spec', 'ui.py', '/home/cody/yuneec/pycv/pyqt/VID_tool'],
             binaries=[],
             datas=[],
             hiddenimports=[
                            'pymavlink.dialects.v20',
                            'pymavlink.dialects.v20.ardupilotmega',
                            ],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='vid_tool',
          debug=False,
          strip=True,
          upx=True,
          runtime_tmpdir=None,
          console=True )
