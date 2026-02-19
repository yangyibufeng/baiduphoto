#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试 WithTime 功能的脚本
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from pybaiduphoto import API
from pybaiduphoto.yybf.WithTime1 import WithTime1


def test_with_time():
    """测试从指定日期开始获取指定数量的items"""
    # 从 settings.json 加载配置
    import json
    with open("pybaiduphoto/yybf/settings.json", 'r') as f:
        json_data = json.load(f)
    
    # 将 Cookie 字符串转换为字典格式
    cookie_dict = {}
    for item in json_data["Cookie"].split('; '):
        if '=' in item:
            key, value = item.split('=', 1)
            cookie_dict[key] = value

    # 创建 API 实例
    api = API(cookies=cookie_dict)
    
    # 创建 WithTime 实例
    with_time = WithTime1(api)
    
    # 测试：从指定日期开始获取 5 个项目
    # 使用一个较早的日期进行测试，例如 2025-01-01
    begin_time = "2025-01-01 00:00:00"
    count = 5
    
    print(f"正在获取从 {begin_time} 开始的 {count} 个项目...")
    
    try:
        items = with_time._get_photo_with_begin_time_and_count(begin_time, count)
        
        print(f"获取到 {len(items)} 个项目:")
        for i, item in enumerate(items):
            item_time = with_time._get_item_time(item)
            from datetime import datetime
            time_str = datetime.fromtimestamp(item_time).strftime('%Y-%m-%d %H:%M:%S')
            print(f"  {i+1}: {item.getName()} - 时间: {time_str}")
            
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_with_time()