"""
高级批量下载工具

支持多种批量下载模式：
1. ZIP 批量下载（快速，一次性下载多个文件）
2. 逐个下载（可以控制并发数，支持断点续传）
3. 按相册下载
4. 按时间范围下载
5. 按条件筛选下载
"""

import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import List, Optional, Callable

from pybaiduphoto import API
from pybaiduphoto.config.settings import setup_file_logging, get_logger


class BatchDownloader:
    """批量下载器类"""
    
    def __init__(self, api: API, max_workers: int = 5):
        """
        初始化批量下载器
        
        Args:
            api: API 实例
            max_workers: 最大并发下载数
        """
        self.api = api
        self.max_workers = max_workers
        self.logger = get_logger(__name__)
        
        # 统计信息
        self.total = 0
        self.success = 0
        self.failed = 0
        self.skipped = 0
        self.start_time = None
    
    def download_by_zip(
        self,
        items: List,
        zip_name: str = "batch_download.zip",
        max_items: int = 100
    ) -> str:
        """
        使用 ZIP 方式批量下载（推荐）
        
        Args:
            items: 要下载的项目列表
            zip_name: ZIP 文件名
            max_items: 最大下载数量
        
        Returns:
            下载 URL
        """
        self.logger.info(f"准备 ZIP 批量下载: {len(items)} 个文件")
        
        # 限制下载数量
        items_to_download = items[:max_items]
        
        self.logger.info(f"创建下载链接: {len(items_to_download)} 个文件")
        download_url = self.api.get_batchDownloadLink(
            items=items_to_download,
            zipname=zip_name
        )
        
        self.logger.info(f"下载链接已生成")
        return download_url
    
    def download_by_individual(
        self,
        items: List,
        download_dir: str,
        max_items: Optional[int] = None,
        progress_callback: Optional[Callable] = None
    ) -> dict:
        """
        逐个下载文件（支持并发和进度回调）
        
        Args:
            items: 要下载的项目列表
            download_dir: 下载目录
            max_items: 最大下载数量
            progress_callback: 进度回调函数
        
        Returns:
            下载统计信息
        """
        # 创建下载目录
        os.makedirs(download_dir, exist_ok=True)
        
        # 限制下载数量
        if max_items:
            items = items[:max_items]
        
        self.total = len(items)
        self.success = 0
        self.failed = 0
        self.skipped = 0
        self.start_time = time.time()
        
        self.logger.info(f"开始批量下载: {self.total} 个文件")
        self.logger.info(f"下载目录: {download_dir}")
        self.logger.info(f"并发数: {self.max_workers}")
        
        # 使用线程池并发下载
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有下载任务
            future_to_item = {
                executor.submit(self._download_item, item, download_dir): item
                for item in items
            }
            
            # 处理完成的任务
            for i, future in enumerate(as_completed(future_to_item), 1):
                item = future_to_item[future]
                try:
                    result = future.result()
                    if result == 'success':
                        self.success += 1
                    elif result == 'skipped':
                        self.skipped += 1
                    else:
                        self.failed += 1
                    
                    # 调用进度回调
                    if progress_callback:
                        progress_callback(
                            completed=i,
                            total=self.total,
                            success=self.success,
                            failed=self.failed,
                            skipped=self.skipped,
                            item=item
                        )
                    
                except Exception as e:
                    self.failed += 1
                    self.logger.error(f"下载异常: {item} - {e}")
        
        # 打印统计信息
        elapsed = time.time() - self.start_time
        self._print_stats(elapsed)
        
        return {
            'total': self.total,
            'success': self.success,
            'failed': self.failed,
            'skipped': self.skipped,
            'elapsed': elapsed
        }
    
    def _download_item(self, item, download_dir: str) -> str:
        """
        下载单个文件
        
        Args:
            item: 要下载的项目
            download_dir: 下载目录
        
        Returns:
            'success', 'failed', 或 'skipped'
        """
        try:
            # 检查文件是否已存在
            file_path = os.path.join(download_dir, item.getName())
            if os.path.exists(file_path):
                self.logger.debug(f"文件已存在，跳过: {item.getName()}")
                return 'skipped'
            
            # 下载文件
            self.logger.debug(f"下载中: {item.getName()}")
            item.download(DirPath=download_dir)
            
            self.logger.debug(f"下载成功: {item.getName()}")
            return 'success'
            
        except Exception as e:
            self.logger.error(f"下载失败: {item.getName()} - {e}")
            return 'failed'
    
    def _print_stats(self, elapsed: float):
        """打印下载统计信息"""
        self.logger.info("=" * 60)
        self.logger.info("下载统计信息")
        self.logger.info("=" * 60)
        self.logger.info(f"总数: {self.total}")
        self.logger.info(f"成功: {self.success}")
        self.logger.info(f"失败: {self.failed}")
        self.logger.info(f"跳过: {self.skipped}")
        self.logger.info(f"耗时: {elapsed:.2f} 秒")
        if self.total > 0:
            self.logger.info(f"平均速度: {self.total/elapsed:.2f} 个/秒")
        self.logger.info("=" * 60)


def progress_callback_console(completed, total, success, failed, skipped, item):
    """控制台进度回调"""
    progress = (completed / total) * 100
    print(f"\r进度: [{completed}/{total}] {progress:.1f}% | "
          f"成功: {success} | 失败: {failed} | 跳过: {skipped}", end="", flush=True)
    
    if completed == total:
        print()  # 换行


def main():
    """主函数 - 批量下载示例"""
    
    # 设置日志
    setup_file_logging(log_level="INFO", log_file="batch_download.log")
    logger = get_logger(__name__)
    
    # 初始化 API（请替换为你的 cookies）
    cookies = {
        'BAIDUID': 'YOUR_BAIDUID_HERE',
        'STOKEN': 'YOUR_STOKEN_HERE',
        'BDUSS_BFESS': 'YOUR_BDUSS_HERE',
    }
    api = API(cookies=cookies)
    
    # 创建批量下载器
    downloader = BatchDownloader(api, max_workers=5)
    
    print("\n" + "=" * 60)
    print("批量下载工具")
    print("=" * 60 + "\n")
    
    # 获取所有照片
    logger.info("获取照片列表...")
    items = api.get_self_All(typeName='Item')
    logger.info(f"找到 {len(items)} 张照片")
    
    print("\n请选择下载方式:")
    print("1. ZIP 批量下载（快速，推荐）")
    print("2. 逐个下载（可并发）")
    print("3. 下载指定相册")
    print("4. 按数量下载")
    
    choice = input("\n请输入选项 (1-4): ").strip()
    
    if choice == '1':
        # ZIP 批量下载
        print("\n=== ZIP 批量下载 ===")
        num = input("要下载多少张照片? (默认20): ").strip()
        num = int(num) if num else 20
        
        zip_name = input("ZIP 文件名 (默认: my_photos.zip): ").strip()
        zip_name = zip_name or "my_photos.zip"
        
        if not zip_name.endswith('.zip'):
            zip_name += '.zip'
        
        download_url = downloader.download_by_zip(
            items=items,
            zip_name=zip_name,
            max_items=num
        )
        
        print(f"\n✓ 下载链接已生成")
        print(f"  URL: {download_url}")
        print(f"  请复制链接到浏览器下载")
    
    elif choice == '2':
        # 逐个下载
        print("\n=== 逐个下载 ===")
        num = input("要下载多少张照片? (默认10): ").strip()
        num = int(num) if num else 10
        
        download_dir = input("下载目录 (默认: downloads): ").strip()
        download_dir = download_dir or "downloads"
        
        workers = input("并发数 (默认5): ").strip()
        workers = int(workers) if workers else 5
        
        downloader.max_workers = workers
        
        stats = downloader.download_by_individual(
            items=items,
            download_dir=download_dir,
            max_items=num,
            progress_callback=progress_callback_console
        )
        
        print(f"\n✓ 下载完成!")
        print(f"  成功: {stats['success']}")
        print(f"  失败: {stats['failed']}")
        print(f"  跳过: {stats['skipped']}")
    
    elif choice == '3':
        # 下载相册
        print("\n=== 下载相册 ===")
        
        # 获取相册列表
        albums = api.get_self_1page(typeName='Album')
        if not albums['items']:
            print("没有找到相册")
            return
        
        print("\n可用相册:")
        for i, album in enumerate(albums['items'][:10], 1):
            print(f"  {i}. {album.getName()}")
        
        album_choice = input("\n选择相册编号: ").strip()
        try:
            album_index = int(album_choice) - 1
            album = albums['items'][album_index]
            
            # 获取相册中的照片
            photos = album.get_sub_All()
            logger.info(f"相册 '{album.getName()}' 包含 {len(photos)} 张照片")
            
            download_dir = input(f"下载目录 (默认: {album.getName()}): ").strip()
            download_dir = download_dir or album.getName()
            
            stats = downloader.download_by_individual(
                items=photos,
                download_dir=download_dir,
                progress_callback=progress_callback_console
            )
            
            print(f"\n✓ 相册下载完成!")
            print(f"  成功: {stats['success']}")
            print(f"  失败: {stats['failed']}")
            
        except (ValueError, IndexError):
            print("无效的选择")
    
    elif choice == '4':
        # 按数量下载
        print("\n=== 按数量下载 ===")
        num = input("要下载多少张照片? (默认100): ").strip()
        num = int(num) if num else 100
        
        download_dir = input("下载目录 (默认: downloads): ").strip()
        download_dir = download_dir or "downloads"
        
        stats = downloader.download_by_individual(
            items=items,
            download_dir=download_dir,
            max_items=num,
            progress_callback=progress_callback_console
        )
        
        print(f"\n✓ 下载完成!")
        print(f"  成功: {stats['success']}")
        print(f"  失败: {stats['failed']}")
    
    else:
        print("无效的选择")


if __name__ == '__main__':
    main()
