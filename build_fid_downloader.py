"""
打包脚本 - 将 fid_downloader.py 打包成独立的 exe 文件
使用方法: python build_fid_downloader.py
"""
import os
import sys
from pathlib import Path

# 检查是否安装了PyInstaller
try:
    import PyInstaller
except ImportError:
    print("请先安装 PyInstaller:")
    print("pip install pyinstaller")
    sys.exit(1)

# 确定项目路径
project_root = Path(__file__).parent
fid_downloader_script = project_root / "myself" / "down_all" / "fid_downloader.py"

if not fid_downloader_script.exists():
    print(f"错误: 找不到 {fid_downloader_script}")
    sys.exit(1)

# 创建打包入口脚本（统一入口）
entry_script = project_root / "run_fid_downloader.py"
entry_content = '''#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
百度照片批量下载器 - 统一入口
"""
import os
import sys

# 获取程序所在目录
if getattr(sys, 'frozen', False):
    # 打包后的路径
    program_dir = os.path.dirname(sys.executable)
else:
    # 开发环境路径
    program_dir = os.path.dirname(os.path.abspath(__file__))

# 将程序目录添加到路径
sys.path.insert(0, program_dir)

# 导入并运行主程序
from myself.down_all.fid_downloader import main

if __name__ == "__main__":
    main()
'''

with open(entry_script, 'w', encoding='utf-8') as f:
    f.write(entry_content)

print(f"已创建入口脚本: {entry_script}")

# 创建spec文件
spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    [{repr(str(entry_script))}],
    pathex=[{repr(str(project_root))}],
    binaries=[],
    datas=[
        # 包含配置文件
        ({repr(str(project_root / "settings.json"))}, "."),
        # 包含 pybaiduphoto 模块
        ({repr(str(project_root / "pybaiduphoto"))}, "pybaiduphoto"),
        # 包含 myself 模块
        ({repr(str(project_root / "myself"))}, "myself"),
    ],
    hiddenimports=[
        # pybaiduphoto 相关模块
        "pybaiduphoto",
        "pybaiduphoto.API",
        "pybaiduphoto.OnlineItem",
        "pybaiduphoto.Requests",
        "pybaiduphoto.apiObject",
        "pybaiduphoto.config",
        "pybaiduphoto.config.settings",
        "pybaiduphoto.config.constants",
        # myself 相关模块
        "myself",
        "myself.down_all",
        "myself.down_all.config_loader",
        "myself.down_all.fid_downloader",
        "myself.down_all.fid_list_manager",
        # 依赖库
        "requests",
        "urllib3",
        "charset_normalizer",
        "idna",
        "certifi",
        "tomli",
        "tomllib",
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        # 排除不需要的模块以减小体积
        "tkinter",
        "matplotlib",
        "numpy",
        "pandas",
        "PIL",
        "scipy",
        "IPython",
        "jupyter",
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
    name='BaiduPhotoDownloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # 命令行程序，显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 可以指定图标文件路径，如 "icon.ico"
)
'''

spec_file = project_root / "FidDownloader.spec"

with open(spec_file, 'w', encoding='utf-8') as f:
    f.write(spec_content)

print(f"已创建 spec 文件: {spec_file}")

# 运行PyInstaller
import subprocess

cmd = ["pyinstaller", "--clean", str(spec_file)]
print("\n正在运行 PyInstaller...")
print(" ".join(cmd))
print()

try:
    # 使用实时输出
    process = subprocess.Popen(
        cmd, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.STDOUT, 
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    
    for line in process.stdout:
        print(line, end='')
    
    process.wait()
    
    if process.returncode == 0:
        print("\n" + "=" * 50)
        print("打包成功！")
        print("=" * 50)
        print(f"输出目录: {project_root / 'dist' / 'BaiduPhotoDownloader'}")
        print(f"可执行文件: {project_root / 'dist' / 'BaiduPhotoDownloader' / 'BaiduPhotoDownloader.exe'}")
        print()
        print("使用说明:")
        print("1. 将 dist/BaiduPhotoDownloader 文件夹复制给对方")
        print("2. 对方需要有 settings.json 文件（包含 Cookie 配置）")
        print("3. 双击 BaiduPhotoDownloader.exe 即可运行")
    else:
        print("\n打包失败！")
        
except subprocess.CalledProcessError as e:
    print("打包失败:")
    print("错误输出:", e.stderr if hasattr(e, 'stderr') else str(e))
except Exception as e:
    print(f"打包过程中出错: {e}")

print("\n如果需要手动打包，请运行以下命令:")
print(f"pyinstaller {spec_file}")
