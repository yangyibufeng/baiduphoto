"""
可视化界面演示脚本
使用模拟数据展示真实的可视化界面效果
"""
import sys
import os
import time
from datetime import datetime
import threading

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from myself.down_all.visual_interface import VisualInterface
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn


def demo_visual_interface():
    """演示可视化界面"""
    print("启动可视化界面演示...")
    print("按 Ctrl+C 退出演示")
    
    # 创建可视化界面
    vis = VisualInterface()
    vis.set_total_count(100)  # 设置总数为100
    
    # 创建布局
    layout = vis.create_layout()
    vis.update_layout(layout)
    
    # 模拟下载过程
    try:
        with Live(layout, refresh_per_second=4) as live:
            for i in range(100):
                # 随机模拟成功、失败或跳过
                import random
                action = random.choices(['success', 'fail', 'skip'], weights=[0.8, 0.05, 0.15])[0]
                
                item_info = {
                    'name': f'photo_{i:03d}.jpg',
                    'size': random.randint(100000, 5000000),  # 100KB - 5MB
                    'fid': f'fid_{i:05d}'
                }
                
                if action == 'success':
                    vis.update_progress(success=True, item_info=item_info)
                elif action == 'fail':
                    error_msg = random.choice([
                        "网络超时",
                        "文件损坏",
                        "权限不足",
                        "API限制"
                    ])
                    vis.update_progress(success=False, item_info=item_info, error_msg=error_msg)
                else:  # skip
                    vis.skip_item()
                
                # 更新当前项目
                vis.update_current_item(f"正在处理: {item_info['name']}")
                
                # 更新布局
                vis.update_layout(layout)
                live.update(layout)
                
                # 模拟处理时间
                time.sleep(0.1)
                
                # 每20个更新一次显示信息
                if (i + 1) % 20 == 0:
                    print(f"已处理 {i + 1}/100 个项目")
    
    except KeyboardInterrupt:
        print("\n演示已停止")
    
    # 显示最终报告
    print("\n" + "="*50)
    print("模拟下载完成！以下是最终报告：")
    vis.display_final_report()


def show_simple_demo():
    """简单的演示"""
    print("可视化界面演示")
    print("=" * 50)
    
    # 创建一个简单的进度展示
    vis = VisualInterface()
    vis.set_total_count(50)
    
    # 手动更新一些数据
    for i in range(10):
        item_info = {
            'name': f'test_photo_{i:02d}.jpg',
            'size': 2048576,  # 2MB
            'fid': f'fid_{i:05d}'
        }
        vis.update_progress(success=True, item_info=item_info)
        vis.update_current_item(f"当前: test_photo_{i:02d}.jpg")
        time.sleep(0.1)
    
    # 添加一些失败的项目
    for i in range(3):
        item_info = {
            'name': f'failed_photo_{i:02d}.png',
            'size': 1024576,  # 1MB
            'fid': f'fid_fail_{i:05d}'
        }
        vis.update_progress(success=False, item_info=item_info, error_msg="网络错误")
    
    print("当前状态:")
    print(f"总数量: {vis.total_count}")
    print(f"成功: {vis.success_count}")
    print(f"失败: {vis.failed_count}")
    print(f"跳过: {vis.skipped_count}")
    
    # 创建并显示布局
    layout = vis.create_layout()
    vis.update_layout(layout)
    
    print("\n完整可视化界面布局:")
    print("注意：要看到完整的实时界面效果，需要使用Live组件")
    
    # 显示最终报告
    print("\n最终报告:")
    vis.display_final_report()


if __name__ == "__main__":
    print("请选择演示模式:")
    print("1. 简单数据演示")
    print("2. 完整实时界面演示")
    
    choice = input("请选择 (1/2): ").strip()
    
    if choice == "2":
        demo_visual_interface()
    else:
        show_simple_demo()
        print("\n如需查看完整的实时界面演示，请运行: python demo_visual_interface.py")
        print("然后选择选项 2")