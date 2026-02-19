"""
Settings configuration for pybaiduphoto.

This module handles configuration settings, including proxy settings,
logging configuration, and other runtime settings.
"""

import os
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from typing import Optional, Dict
from datetime import datetime

# Logging configuration
DEFAULT_LOG_LEVEL = logging.WARNING
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DETAILED_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"

# Log file configuration
DEFAULT_LOG_DIR = "logs"
DEFAULT_LOG_FILE = "pybaiduphoto.log"
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB
BACKUP_COUNT = 5  # 保留5个备份文件


def get_log_file_path(log_file: Optional[str] = None, log_dir: Optional[str] = None) -> str:
    """
    获取日志文件的完整路径。
    
    Args:
        log_file: 日志文件名（默认：pybaiduphoto.log）
        log_dir: 日志目录（默认：logs）
    
    Returns:
        日志文件的完整路径
    """
    if log_file is None:
        log_file = os.getenv("PYBAIDUPHOTO_LOG_FILE", DEFAULT_LOG_FILE)
    
    if log_dir is None:
        log_dir = os.getenv("PYBAIDUPHOTO_LOG_DIR", DEFAULT_LOG_DIR)
    
    # 确保日志目录存在
    os.makedirs(log_dir, exist_ok=True)
    
    return os.path.join(log_dir, log_file)


def setup_logging(
    level: int = None,
    log_to_file: bool = None,
    log_file: Optional[str] = None,
    log_dir: Optional[str] = None,
    console_output: bool = None,
    detailed_format: bool = None,
    rotation_mode: str = "size"
) -> logging.Logger:
    """
    设置日志配置，支持控制台和文件输出。
    
    Args:
        level: 日志级别（默认：WARNING）
        log_to_file: 是否输出到文件（默认：True）
        log_file: 日志文件名（默认：pybaiduphoto.log）
        log_dir: 日志目录（默认：logs）
        console_output: 是否输出到控制台（默认：True）
        detailed_format: 是否使用详细格式（包含文件名和行号）
        rotation_mode: 日志轮转模式（"size" 或 "time"）
    
    Returns:
        配置好的 logger 实例
    """
    # 从环境变量获取配置
    if level is None:
        env_level = os.getenv("PYBAIDUPHOTO_LOG_LEVEL", "WARNING").upper()
        level = getattr(logging, env_level, DEFAULT_LOG_LEVEL)
    
    if log_to_file is None:
        log_to_file = os.getenv("PYBAIDUPHOTO_LOG_TO_FILE", "true").lower() == "true"
    
    if console_output is None:
        console_output = os.getenv("PYBAIDUPHOTO_CONSOLE_OUTPUT", "true").lower() == "true"
    
    if detailed_format is None:
        detailed_format = os.getenv("PYBAIDUPHOTO_DETAILED_FORMAT", "false").lower() == "true"
    
    if rotation_mode is None:
        rotation_mode = os.getenv("PYBAIDUPHOTO_LOG_ROTATION", "size").lower()
    
    # 选择日志格式
    log_format = DETAILED_LOG_FORMAT if detailed_format else LOG_FORMAT
    
    # 创建根 logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # 清除已有的 handlers
    root_logger.handlers.clear()
    
    # 创建 formatter
    formatter = logging.Formatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")
    
    # 控制台输出
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # 文件输出
    if log_to_file:
        log_path = get_log_file_path(log_file, log_dir)
        
        if rotation_mode == "size":
            # 按大小轮转
            file_handler = RotatingFileHandler(
                log_path,
                maxBytes=MAX_LOG_SIZE,
                backupCount=BACKUP_COUNT,
                encoding='utf-8'
            )
        else:
            # 按时间轮转（每天一个文件）
            file_handler = TimedRotatingFileHandler(
                log_path,
                when='midnight',
                interval=1,
                backupCount=BACKUP_COUNT,
                encoding='utf-8'
            )
            # 设置轮转文件名后缀
            file_handler.suffix = "%Y-%m-%d"
        
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # 记录日志配置信息
    logger = logging.getLogger(__name__)
    logger.info(f"日志系统已初始化 - 级别: {logging.getLevelName(level)}")
    logger.info(f"日志文件: {get_log_file_path(log_file, log_dir) if log_to_file else '未启用文件输出'}")
    logger.info(f"控制台输出: {'启用' if console_output else '禁用'}")
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的 logger 实例。
    
    Args:
        name: logger 名称，通常使用 __name__
    
    Returns:
        Logger 实例
    """
    return logging.getLogger(name)


# 便捷函数：使用预设配置快速设置日志
def setup_simple_logging(log_level: str = "INFO") -> None:
    """
    快速设置简单日志配置（仅控制台输出）。
    
    Args:
        log_level: 日志级别字符串（DEBUG, INFO, WARNING, ERROR, CRITICAL）
    """
    setup_logging(
        level=getattr(logging, log_level.upper(), logging.INFO),
        log_to_file=False,
        console_output=True,
        detailed_format=False
    )


def setup_file_logging(
    log_level: str = "DEBUG",
    log_file: str = DEFAULT_LOG_FILE,
    log_dir: str = DEFAULT_LOG_DIR
) -> None:
    """
    快速设置文件日志配置（文件 + 控制台）。
    
    Args:
        log_level: 日志级别字符串
        log_file: 日志文件名
        log_dir: 日志目录
    """
    setup_logging(
        level=getattr(logging, log_level.upper(), logging.DEBUG),
        log_to_file=True,
        log_file=log_file,
        log_dir=log_dir,
        console_output=True,
        detailed_format=True
    )


def setup_production_logging(
    log_level: str = "WARNING",
    log_file: str = DEFAULT_LOG_FILE,
    log_dir: str = DEFAULT_LOG_DIR
) -> None:
    """
    快速设置生产环境日志配置（仅文件，详细格式）。
    
    Args:
        log_level: 日志级别字符串
        log_file: 日志文件名
        log_dir: 日志目录
    """
    setup_logging(
        level=getattr(logging, log_level.upper(), logging.WARNING),
        log_to_file=True,
        log_file=log_file,
        log_dir=log_dir,
        console_output=False,
        detailed_format=True,
        rotation_mode="time"
    )


# Proxy settings
def get_proxies() -> Optional[Dict[str, str]]:
    """
    Get proxy settings from environment variables.
    
    Returns:
        Dictionary with proxy settings or None if not configured.
        Supported environment variables:
        - PYBAIDUPHOTO_HTTP_PROXY: HTTP proxy URL
        - PYBAIDUPHOTO_HTTPS_PROXY: HTTPS proxy URL
        - PYBAIDUPHOTO_ALL_PROXY: Single proxy URL for both HTTP and HTTPS
    """
    proxies = {}
    
    # Check for single proxy
    all_proxy = os.getenv("PYBAIDUPHOTO_ALL_PROXY")
    if all_proxy:
        proxies["http"] = all_proxy
        proxies["https"] = all_proxy
        return proxies
    
    # Check for separate proxies
    http_proxy = os.getenv("PYBAIDUPHOTO_HTTP_PROXY")
    https_proxy = os.getenv("PYBAIDUPHOTO_HTTPS_PROXY")
    
    if http_proxy:
        proxies["http"] = http_proxy
    if https_proxy:
        proxies["https"] = https_proxy
    
    return proxies if proxies else None


# Cookie settings
def get_cookies_from_env() -> Optional[Dict[str, str]]:
    """
    Get cookies from environment variables.
    
    Note: For security reasons, it's recommended to use browser_cookie3
    or a secure configuration file instead of environment variables.
    
    Returns:
        Dictionary with cookies or None if not configured.
    """
    # This is a placeholder for future cookie management
    # Currently, cookies should be passed directly to the API class
    return None


# 注意：不再在模块导入时自动初始化日志
# 用户需要显式调用 setup_logging() 或使用便捷函数

# Proxy settings
def get_proxies() -> Optional[Dict[str, str]]:
    """
    Get proxy settings from environment variables.
    
    Returns:
        Dictionary with proxy settings or None if not configured.
        Supported environment variables:
        - PYBAIDUPHOTO_HTTP_PROXY: HTTP proxy URL
        - PYBAIDUPHOTO_HTTPS_PROXY: HTTPS proxy URL
        - PYBAIDUPHOTO_ALL_PROXY: Single proxy URL for both HTTP and HTTPS
    """
    proxies = {}
    
    # Check for single proxy
    all_proxy = os.getenv("PYBAIDUPHOTO_ALL_PROXY")
    if all_proxy:
        proxies["http"] = all_proxy
        proxies["https"] = all_proxy
        return proxies
    
    # Check for separate proxies
    http_proxy = os.getenv("PYBAIDUPHOTO_HTTP_PROXY")
    https_proxy = os.getenv("PYBAIDUPHOTO_HTTPS_PROXY")
    
    if http_proxy:
        proxies["http"] = http_proxy
    if https_proxy:
        proxies["https"] = https_proxy
    
    return proxies if proxies else None

# Cookie settings
def get_cookies_from_env() -> Optional[Dict[str, str]]:
    """
    Get cookies from environment variables.
    
    Note: For security reasons, it's recommended to use browser_cookie3
    or a secure configuration file instead of environment variables.
    
    Returns:
        Dictionary with cookies or None if not configured.
    """
    # This is a placeholder for future cookie management
    # Currently, cookies should be passed directly to the API class
    return None

# Initialize logging on module import
setup_logging()