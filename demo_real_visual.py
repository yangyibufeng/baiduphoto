"""
实时可视化界面演示
展示完整的可视化界面效果
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
from rich.panel import Panel


def demo_real_time_visualization():
    """实时可视化界面演示"""
    print("实时可视化界面演示")
    print("按 Ctrl+C 停止演示")
    print("=" * 50)
    
    # 创建可视化界面
    vis = VisualInterface()
    vis.set_total_count(50)  # 设置总数为50
    
    # 创建布局
    layout = vis.create_layout()
    vis.update_layout(layout)
    
    try:
        with Live(layout, refresh_per_second=4) as live:
            for i in range(50):
                # 随机模拟成功、失败或跳过
                action = random.choices(['success', 'fail', 'skip'], weights=[0.85, 0.05, 0.1])[0]
                
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
                        "API限制",
                        "服务器错误"
                    ])
                    vis.update_progress(success=False, item_info=item_info, error_msg=error_msg)
                else:  # skip
                    vis.skip_item()
                
                # 更新当前项目
                vis.update_current_item(f"正在处理: {item_info['name']} (ID: {item_info['fid']})")
                
                # 更新布局
                vis.update_layout(layout)
                live.update(layout)
                
                # 每10个打印一次进度
                if (i + 1) % 10 == 0:
                    print(f"  进度: {i + 1}/50")
                
                # 模拟处理时间
                time.sleep(0.05)
    
    except KeyboardInterrupt:
        print("\n\n演示已停止")
    
    print(f"\n演示完成！最终统计:")
    print(f"  总数量: {vis.total_count}")
    print(f"  成功: {vis.success_count}")
    print(f"  失败: {vis.failed_count}")
    print(f"  跳过: {vis.skipped_count}")


def demo_pause_functionality():
    """演示暂停功能"""
    print("暂停功能演示")
    print("=" * 30)
    
    # 创建可视化界面
    vis = VisualInterface()
    vis.set_total_count(20)
    
    # 模拟暂停状态
    print("当前暂停状态:", vis.is_paused())
    
    # 模拟一些进度
    for i in range(5):
        item_info = {
            'name': f'test_photo_{i:02d}.jpg',
            'size': 2048576,
            'fid': f'fid_{i:05d}'
        }
        vis.update_progress(success=True, item_info=item_info)
        vis.update_current_item(f"正在处理: test_photo_{i:02d}.jpg")
        time.sleep(0.1)
    
    # 暂停
    is_now_paused = vis.toggle_pause()
    print(f"切换暂停状态 -> {is_now_paused}")
    print("当前暂停状态:", vis.is_paused())
    
    # 继续处理
    for i in range(5, 10):
        item_info = {
            'name': f'test_photo_{i:02d}.jpg',
            'size': 2048576,
            'fid': f'fid_{i:05d}'
        }
        vis.update_progress(success=True, item_info=item_info)
        vis.update_current_item(f"正在处理: test_photo_{i:02d}.jpg")
        time.sleep(0.1)
    
    # 再次暂停
    is_now_paused = vis.toggle_pause()
    print(f"再次切换暂停状态 -> {is_now_paused}")
    print("当前暂停状态:", vis.is_paused())


if __name__ == "__main__":
    print("可视化界面功能演示")
    print("1. 实时界面演示")
    print("2. 暂停功能演示")
    
    # 运行实时界面演示
    demo_real_time_visualization()
    
    print("\n" + "="*50)
    
    # 运行暂停功能演示
    demo_pause_functionality()
    
    print("\n演示完成！")
