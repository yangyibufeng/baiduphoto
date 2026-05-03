"""
可视化界面演示脚本
在支持Rich库的终端中运行可看到真实界面
"""
import sys
import os
import time
import random
from datetime import datetime

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from myself.down_all.visual_interface import VisualInterface
from rich.live import Live


def show_visual_demo():
    """显示可视化界面演示"""
    print("百度照片批量下载器 - 可视化界面演示")
    print("注意：此界面仅在支持Rich库的终端中正常显示")
    print("请在命令提示符或PowerShell中运行此脚本以查看真实界面")
    print("="*50)
    
    # 创建可视化界面
    vis = VisualInterface()
    vis.set_total_count(25)  # 设置总数为25
    
    print(f"创建了包含 {vis.total_count} 个项目的可视化界面")
    print("界面包含以下组件：")
    print("1. 顶部进度条 - 显示整体下载进度")
    print("2. 当前下载显示 - 显示当前处理的文件")
    print("3. 状态面板 - 显示成功/失败/跳过统计")
    print("4. 成功列表 - 显示最近成功下载的文件")
    print("5. 失败列表 - 显示失败的文件及原因")
    print()
    print("暂停功能：")
    print("- 程序提供 toggle_pause() 方法控制暂停/继续")
    print("- 在下载循环中检查暂停状态")
    print("- 暂停时会等待直到继续或停止")
    
    # 创建布局（但不使用Live显示，因为可能在不支持的环境中）
    layout = vis.create_layout()
    vis.update_layout(layout)
    
    # 模拟一些进度
    print("\n以下是模拟的界面更新效果：")
    for i in range(10):
        item_info = {
            'name': f'photo_{i:03d}.jpg',
            'size': random.randint(1000000, 5000000),  # 1-5MB
            'fid': f'fid_{i:06d}'
        }
        
        # 随机成功或失败
        if random.random() < 0.85:  # 85% 成功率
            vis.update_progress(success=True, item_info=item_info)
            print(f"✓ 成功: {item_info['name']} ({item_info['size']//1024}KB)")
        else:
            vis.update_progress(success=False, item_info=item_info, error_msg="网络超时")
            print(f"✗ 失败: {item_info['name']} - 网络超时")
        
        vis.update_current_item(f"正在处理: {item_info['name']}")
        
        # 每2秒更新一次显示
        if i % 3 == 0:
            print(f"  进度: {vis.success_count} 成功 / {vis.failed_count} 失败 / {vis.total_count} 总计")
        
        time.sleep(0.1)
    
    print(f"\n最终状态: {vis.success_count} 成功 / {vis.failed_count} 失败 / {vis.skipped_count} 跳过")
    
    print("\n"+"="*50)
    print("要查看真实的可视化界面，请在命令提示符中执行以下命令：")
    print("cd D:\\resources\\pycharm_code\\baiduphoto")
    print("python -c \"from demo_real_visual import demo_real_time_visualization; demo_real_time_visualization()\"")


if __name__ == "__main__":
    show_visual_demo()
