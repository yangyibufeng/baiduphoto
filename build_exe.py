"""
打包脚本 - 将GUI程序打包成exe文件
使用方法: python build_exe.py
"""
import os
import sys
from pathlib import Path

# 检查是否安装了PyInstaller
try:
    import PyInstaller
except ImportError:
    print("请先安装PyInstaller:")
    print("pip install pyinstaller")
    sys.exit(1)

# 确定项目路径
project_root = Path(__file__).parent
gui_script = project_root / "gui_downloader.py"

if not gui_script.exists():
    print(f"错误: 找不到 {gui_script}")
    sys.exit(1)

# 创建spec文件进行高级配置
spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    [{repr(str(gui_script))}],
    pathex=[{repr(str(project_root))}],
    binaries=[],
    datas=[
        # 包含必要的配置文件
        ({repr(str(project_root / "settings.json"))}, "."),
        ({repr(str(project_root / "myself" / "down_all"))}, "myself/down_all"),
    ],
    hiddenimports=[
        # 添加可能需要的隐藏导入
        "pybaiduphoto",
        "pybaiduphoto.API",
        "pybaiduphoto.OnlineItem",
        "pybaiduphoto.config.settings",
        "myself.down_all.config_loader",
        "myself.down_all.fid_downloader",
        "myself.down_all.fid_list_manager",
        "myself.down_all.visual_interface",
        "rich",
        "rich.console",
        "rich.progress",
        "rich.table",
        "rich.layout",
        "rich.panel",
        "rich.live",
        "rich.text",
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
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
    console=False,  # 设置为False以创建GUI应用（无控制台窗口）
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 可以指定图标文件路径
)
'''

spec_file = project_root / "BaiduPhotoDownloader.spec"

with open(spec_file, 'w', encoding='utf-8') as f:
    f.write(spec_content)

print("已创建spec文件:", spec_file)

# 运行PyInstaller
import subprocess

cmd = ["pyinstaller", "--clean", "--onedir", str(spec_file)]
print("正在运行PyInstaller...")
print(" ".join(cmd))

try:
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    print("打包成功！")
    print("输出目录: dist/BaiduPhotoDownloader/")
    print("可执行文件: dist/BaiduPhotoDownloader/BaiduPhotoDownloader.exe")
except subprocess.CalledProcessError as e:
    print("打包失败:")
    print("错误输出:", e.stderr)
    print("标准输出:", e.stdout)
except Exception as e:
    print(f"打包过程中出错: {e}")

print("\n如果需要手动打包，请运行以下命令:")
print(f"pyinstaller --onedir --windowed {gui_script}")
print("\n或者使用spec文件:")
print(f"pyinstaller {spec_file}")
