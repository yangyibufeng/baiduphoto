"""
日志系统使用示例

演示如何使用 pybaiduphoto 的日志系统。
"""

import logging
from pybaiduphoto import API
from pybaiduphoto.config.settings import (
    setup_logging,
    setup_simple_logging,
    setup_file_logging,
    setup_production_logging,
    get_logger
)


def example_1_simple_logging():
    """示例 1：简单日志配置（仅控制台）"""
    print("=" * 60)
    print("示例 1：简单日志配置（仅控制台）")
    print("=" * 60)
    
    # 设置简单日志 - 仅控制台输出
    setup_simple_logging(log_level="INFO")
    
    logger = get_logger(__name__)
    logger.info("这是一条 INFO 日志")
    logger.warning("这是一条 WARNING 日志")
    logger.error("这是一条 ERROR 日志")
    print()


def example_2_file_logging():
    """示例 2：文件日志配置（文件 + 控制台）"""
    print("=" * 60)
    print("示例 2：文件日志配置（文件 + 控制台）")
    print("=" * 60)
    
    # 设置文件日志 - 同时输出到文件和控制台
    setup_file_logging(
        log_level="DEBUG",
        log_file="example.log",
        log_dir="logs"
    )
    
    logger = get_logger(__name__)
    logger.debug("这是一条 DEBUG 日志（仅在文件中）")
    logger.info("这是一条 INFO 日志")
    logger.warning("这是一条 WARNING 日志")
    logger.error("这是一条 ERROR 日志")
    
    print("日志已保存到 logs/example.log")
    print()


def example_3_production_logging():
    """示例 3：生产环境日志配置（仅文件，详细格式）"""
    print("=" * 60)
    print("示例 3：生产环境日志配置（仅文件，详细格式）")
    print("=" * 60)
    
    # 设置生产环境日志 - 仅文件输出，详细格式
    setup_production_logging(
        log_level="WARNING",
        log_file="production.log",
        log_dir="logs"
    )
    
    logger = get_logger(__name__)
    logger.info("这条 INFO 日志不会显示（级别低于 WARNING）")
    logger.warning("这是一条 WARNING 日志（仅在文件中）")
    logger.error("这是一条 ERROR 日志（仅在文件中）")
    
    print("日志已保存到 logs/production.log")
    print("注意：控制台不会显示日志（生产环境配置）")
    print()


def example_4_custom_logging():
    """示例 4：自定义日志配置"""
    print("=" * 60)
    print("示例 4：自定义日志配置")
    print("=" * 60)
    
    # 自定义日志配置
    setup_logging(
        level=logging.DEBUG,
        log_to_file=True,
        log_file="custom.log",
        log_dir="logs",
        console_output=True,
        detailed_format=True,
        rotation_mode="size"  # 按大小轮转
    )
    
    logger = get_logger(__name__)
    logger.debug("自定义日志配置 - DEBUG")
    logger.info("自定义日志配置 - INFO")
    logger.warning("自定义日志配置 - WARNING")
    logger.error("自定义日志配置 - ERROR")
    
    print("日志已保存到 logs/custom.log")
    print("使用详细格式（包含文件名和行号）")
    print()


def example_5_with_api():
    """示例 5：在实际 API 使用中启用日志"""
    print("=" * 60)
    print("示例 5：在实际 API 使用中启用日志")
    print("=" * 60)
    
    # 设置日志
    setup_file_logging(log_level="DEBUG", log_file="api_usage.log")
    
    logger = get_logger(__name__)
    logger.info("初始化 API...")
    
    # 模拟 API 调用（需要真实 cookies）
    try:
        # api = API(cookies=your_cookies)
        # logger.info("API 初始化成功")
        
        # 模拟操作
        logger.debug("开始获取照片列表...")
        # photos = api.get_self_All(typeName='Item')
        logger.info("获取到 0 张照片")
        
        logger.debug("开始下载照片...")
        # photos[0].download(DirPath='./downloads')
        logger.info("照片下载完成")
        
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
    
    print("日志已保存到 logs/api_usage.log")
    print()


def example_6_environment_variables():
    """示例 6：使用环境变量配置日志"""
    print("=" * 60)
    print("示例 6：使用环境变量配置日志")
    print("=" * 60)
    
    import os
    
    # 设置环境变量
    os.environ["PYBAIDUPHOTO_LOG_LEVEL"] = "DEBUG"
    os.environ["PYBAIDUPHOTO_LOG_TO_FILE"] = "true"
    os.environ["PYBAIDUPHOTO_LOG_FILE"] = "env_config.log"
    os.environ["PYBAIDUPHOTO_LOG_DIR"] = "logs"
    os.environ["PYBAIDUPHOTO_DETAILED_FORMAT"] = "true"
    
    # 使用环境变量配置
    setup_logging()
    
    logger = get_logger(__name__)
    logger.info("使用环境变量配置的日志")
    logger.warning("环境变量配置成功")
    
    print("日志已保存到 logs/env_config.log")
    print()


def example_7_different_loggers():
    """示例 7：使用不同模块的 logger"""
    print("=" * 60)
    print("示例 7：使用不同模块的 logger")
    print("=" * 60)
    
    setup_file_logging(log_level="DEBUG", log_file="multi_logger.log")
    
    # 不同模块使用不同的 logger
    api_logger = get_logger("pybaiduphoto.API")
    request_logger = get_logger("pybaiduphoto.Requests")
    album_logger = get_logger("pybaiduphoto.Album")
    
    api_logger.info("API 模块的日志")
    request_logger.debug("Requests 模块的日志")
    album_logger.warning("Album 模块的日志")
    
    print("所有模块的日志都保存到 logs/multi_logger.log")
    print()


def main():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("pybaiduphoto 日志系统使用示例")
    print("=" * 60 + "\n")
    
    # 运行各个示例
    example_1_simple_logging()
    example_2_file_logging()
    example_3_production_logging()
    example_4_custom_logging()
    example_5_with_api()
    example_6_environment_variables()
    example_7_different_loggers()
    
    print("=" * 60)
    print("所有示例运行完成！")
    print("请查看 logs/ 目录中的日志文件")
    print("=" * 60)


if __name__ == "__main__":
    main()