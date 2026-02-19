# 日志系统使用指南

pybaiduphoto 提供了完善的日志系统，帮助你在开发和生产环境中更好地跟踪和排查问题。

## 概览

日志系统支持：
- ✅ 控制台输出
- ✅ 文件输出
- ✅ 日志轮转（按大小或按时间）
- ✅ 多级别日志（DEBUG, INFO, WARNING, ERROR, CRITICAL）
- ✅ 详细格式（包含文件名和行号）
- ✅ 环境变量配置
- ✅ 多模块日志管理

## 快速开始

### 1. 基础使用

```python
from pybaiduphoto.config.settings import setup_logging, get_logger

# 设置日志
setup_logging(log_level="INFO", log_to_file=True)

# 获取 logger
logger = get_logger(__name__)

# 记录日志
logger.info("这是一条信息")
logger.warning("这是一条警告")
logger.error("这是一条错误")
```

### 2. 预设配置

#### 开发环境
```python
from pybaiduphoto.config.settings import setup_file_logging

# 文件 + 控制台，详细格式
setup_file_logging(log_level="DEBUG")
```

#### 生产环境
```python
from pybaiduphoto.config.settings import setup_production_logging

# 仅文件输出，按天轮转
setup_production_logging(log_level="WARNING")
```

#### 简单配置
```python
from pybaiduphoto.config.settings import setup_simple_logging

# 仅控制台输出
setup_simple_logging(log_level="INFO")
```

## 配置选项

### setup_logging 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `level` | int | WARNING | 日志级别 |
| `log_to_file` | bool | True | 是否输出到文件 |
| `log_file` | str | pybaiduphoto.log | 日志文件名 |
| `log_dir` | str | logs | 日志目录 |
| `console_output` | bool | True | 是否输出到控制台 |
| `detailed_format` | bool | False | 是否使用详细格式 |
| `rotation_mode` | str | size | 轮转模式：'size' 或 'time' |

### 日志级别

| 级别 | 值 | 用途 |
|------|-----|------|
| DEBUG | 10 | 最详细的信息，用于调试 |
| INFO | 20 | 一般信息 |
| WARNING | 30 | 警告信息（默认） |
| ERROR | 40 | 错误信息 |
| CRITICAL | 50 | 严重错误 |

## 环境变量配置

### 完整配置示例

```bash
# .env 文件

# 日志级别
PYBAIDUPHOTO_LOG_LEVEL=DEBUG

# 文件输出
PYBAIDUPHOTO_LOG_TO_FILE=true
PYBAIDUPHOTO_LOG_FILE=app.log
PYBAIDUPHOTO_LOG_DIR=logs

# 控制台输出
PYBAIDUPHOTO_CONSOLE_OUTPUT=true

# 详细格式
PYBAIDUPHOTO_DETAILED_FORMAT=true

# 轮转模式
PYBAIDUPHOTO_LOG_ROTATION=size
```

### 在代码中使用环境变量

```python
import os
from pybaiduphoto.config.settings import setup_logging

# 设置环境变量
os.environ["PYBAIDUPHOTO_LOG_LEVEL"] = "DEBUG"
os.environ["PYBAIDUPHOTO_LOG_TO_FILE"] = "true"

# 使用环境变量配置
setup_logging()
```

## 日志轮转

### 按大小轮转

当日志文件达到 10MB 时自动创建新文件。

```python
setup_logging(rotation_mode="size")
```

生成的文件：
- `pybaiduphoto.log` (当前日志)
- `pybaiduphoto.log.1` (第一个备份)
- `pybaiduphoto.log.2` (第二个备份)
- ... (最多保留 5 个备份)

### 按时间轮转

每天午夜创建新文件。

```python
setup_logging(rotation_mode="time")
```

生成的文件：
- `pybaiduphoto.log` (当前日志)
- `pybaiduphoto.log.2024-01-15` (昨天的日志)
- `pybaiduphoto.log.2024-01-14` (前天的日志)
- ... (最多保留 5 个备份)

## 日志格式

### 基本格式

```
2024-01-15 10:30:45 - pybaiduphoto.API - INFO - 这是一条信息
```

### 详细格式

```
2024-01-15 10:30:45 - pybaiduphoto.API - ERROR - API.py:123 - 这是一条错误
```

详细格式包含：
- 时间戳
- 模块名
- 日志级别
- 文件名和行号
- 日志消息

## 在不同模块中使用

### 使用模块名

```python
from pybaiduphoto.config.settings import get_logger

# API 模块
api_logger = get_logger("pybaiduphoto.API")
api_logger.info("API 操作")

# Requests 模块
req_logger = get_logger("pybaiduphoto.Requests")
req_logger.debug("HTTP 请求")

# 自定义模块
my_logger = get_logger("myapp")
my_logger.info("应用日志")
```

### 使用 __name__

```python
import logging
from pybaiduphoto.config.settings import get_logger

logger = get_logger(__name__)

def my_function():
    logger.info("函数执行中")
    logger.debug("调试信息")
```

## 实际应用示例

### 示例 1：在 API 调用中使用日志

```python
from pybaiduphoto import API
from pybaiduphoto.config.settings import setup_file_logging, get_logger

# 设置日志
setup_file_logging(log_level="DEBUG")

logger = get_logger(__name__)

try:
    logger.info("初始化 API...")
    api = API(cookies=cookies)
    
    logger.info("获取照片列表...")
    photos = api.get_self_All(typeName='Item')
    logger.info(f"获取到 {len(photos)} 张照片")
    
    logger.debug("开始下载第一张照片...")
    photos[0].download(DirPath='./downloads')
    logger.info("下载完成")
    
except Exception as e:
    logger.error(f"操作失败: {e}", exc_info=True)
```

### 示例 2：批量操作日志

```python
from pybaiduphoto.config.settings import setup_logging, get_logger

setup_logging(log_level="INFO", log_to_file=True)
logger = get_logger(__name__)

def batch_download(photos):
    logger.info(f"开始批量下载 {len(photos)} 张照片")
    
    success = 0
    failed = 0
    
    for i, photo in enumerate(photos):
        try:
            logger.debug(f"下载 [{i+1}/{len(photos)}]: {photo.getName()}")
            photo.download(DirPath='./downloads')
            success += 1
        except Exception as e:
            logger.error(f"下载失败 [{i+1}/{len(photos)}]: {e}")
            failed += 1
    
    logger.info(f"批量下载完成 - 成功: {success}, 失败: {failed}")
```

### 示例 3：性能监控

```python
import time
from pybaiduphoto.config.settings import get_logger

logger = get_logger(__name__)

def timed_operation(operation, name):
    logger.info(f"开始 {name}...")
    start_time = time.time()
    
    try:
        result = operation()
        elapsed = time.time() - start_time
        logger.info(f"{name} 完成 - 耗时: {elapsed:.2f}秒")
        return result
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"{name} 失败 - 耗时: {elapsed:.2f}秒 - 错误: {e}")
        raise
```

## 最佳实践

### 1. 选择合适的日志级别

- **开发环境**：使用 DEBUG 级别
- **测试环境**：使用 INFO 级别
- **生产环境**：使用 WARNING 或 ERROR 级别

### 2. 合理使用日志格式

- **调试时**：使用详细格式（包含文件名和行号）
- **生产环境**：使用基本格式（减少日志大小）

### 3. 定期清理日志文件

```python
import os
import glob
from datetime import datetime, timedelta

def clean_old_logs(log_dir="logs", days=7):
    """清理 7 天前的日志文件"""
    cutoff = datetime.now() - timedelta(days=days)
    
    for log_file in glob.glob(f"{log_dir}/*.log*"):
        file_time = datetime.fromtimestamp(os.path.getmtime(log_file))
        if file_time < cutoff:
            os.remove(log_file)
            print(f"已删除: {log_file}")
```

### 4. 异常日志包含堆栈信息

```python
try:
    # 可能出错的代码
    pass
except Exception as e:
    logger.error(f"操作失败: {e}", exc_info=True)
```

### 5. 敏感信息不要记录日志

```python
# ❌ 错误：记录敏感信息
logger.info(f"用户登录: {username}:{password}")

# ✅ 正确：不记录敏感信息
logger.info(f"用户登录: {username}")
```

## 故障排查

### 问题：日志文件没有生成

**解决方案：**
1. 检查 `log_to_file` 是否为 `True`
2. 检查日志目录是否有写入权限
3. 检查磁盘空间是否充足

### 问题：日志没有输出到控制台

**解决方案：**
1. 检查 `console_output` 是否为 `True`
2. 检查日志级别设置是否过高

### 问题：日志文件过大

**解决方案：**
1. 启用日志轮转
2. 使用更高级别的日志（WARNING 而非 DEBUG）
3. 定期清理旧日志文件

## 更多示例

查看 [examples/logging_example.py](../examples/logging_example.py) 获取更多使用示例。