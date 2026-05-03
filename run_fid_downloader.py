#!/usr/bin/env python
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
