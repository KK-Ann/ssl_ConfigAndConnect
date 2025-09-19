# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# 获取当前文件路径
spec_dir = os.path.abspath('.')

# 设置工作目录为当前目录
base_path = spec_dir

# 收集项目所需的数据文件
datas = [
    
    # 添加Vue前端构建后的文件
    (os.path.join(base_path, '..', 'ssl-ui', 'dist'), 'dist'),
]

# 添加额外的隐藏导入
hidden_imports = [
    'webview',
    'ClientAPI',
    'ServerAPI',
    'playwright.sync_api',
    'playwright._impl._api_types',
    'playwright._impl._errors',
    'playwright._impl._transport',
    'requests',
    'WMI',
]

# 添加运行时钩子
hookspath = []

# 分析项目的导入模块
a = Analysis(
    ['start.py'],
    pathex=[base_path],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=hookspath,
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 创建PYZ文件（Python字节码归档）
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# 创建可执行文件
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SSL连接程序',
    icon='logo.ico',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 设置为True可以显示控制台窗口，便于调试
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None

)

# 创建单文件打包（可选）
# 如果需要单个EXE文件而非文件夹，取消下面的注释
# coll = COLLECT(
#     exe,
#     a.binaries,
#     a.zipfiles,
#     a.datas,
#     strip=False,
#     upx=True,
#     upx_exclude=[],
#     name='SSL连接程序',
# )