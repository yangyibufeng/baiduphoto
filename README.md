# pybaiduphoto

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

百度相册（一刻相册）API 的 Python 库 - 非官方封装，用于程序化访问百度云相册服务。

## 功能特性

- **照片/视频管理**：上传、下载、删除照片和视频
- **相册操作**：创建、管理、重命名和组织相册
- **AI 分类相册**：访问自动生成的人物、地点和事物相册
- **批量操作**：支持批量下载并导出为 ZIP
- **网盘集成**：从百度网盘导入文件
- **代理支持**：自定义代理配置用于网络请求

## 安装

```bash
pip install pybaiduphoto
```

开发安装（包含浏览器 Cookie 支持）：

```bash
pip install pybaiduphoto[browser]
```

## 快速开始

### 初始化 API

```python
from pybaiduphoto import API

# 方式 1：使用 browser_cookie3（推荐）
import browser_cookie3
api = API(cookies=browser_cookie3.chrome())

# 方式 2：手动提供 Cookies
cookies = {
    'BAIDUID': 'YOUR_BAIDUID_HERE',
    'STOKEN': 'YOUR_STOKEN_HERE',
    'BDUSS_BFESS': 'YOUR_BDUSS_HERE',
}
api = API(cookies=cookies)
```

### 基本用法

```python
# 获取所有照片/视频
photos = api.get_self_All(typeName='Item')
print(f"找到 {len(photos)} 张照片")

# 下载第一张照片
photos[0].download(DirPath='./downloads')

# 创建新相册
album = api.createNewAlbum(Name='我的假期')

# 添加照片到相册
album.append(photos[:10])

# 重命名相册
album.rename('2024年暑假')

# 搜索相册
results = api.albumSearch(keyword='假期', limit=10)
for album in results['items']:
    print(album)
```

### AI 分类相册

```python
# 人物相册（人脸识别）
persons = api.get_self_All(typeName='Person')
for person in persons[:3]:
    print(f"{person.getName()}: {person.getCount()} 张照片")

# 地点相册
locations = api.get_self_All(typeName='Location')

# 事物相册（物体识别）
things = api.get_self_All(typeName='Thing')
```

### 上传文件

```python
# 上传到默认位置
api.upload_1file(filePath='photo.jpg')

# 上传到指定相册
album = api.get_self_1page(typeName='Album')['items'][0]
api.upload_1file(filePath='photo.jpg', album=album)
```

### 批量下载

```python
# 下载多张照片
photos = api.get_self_All(typeName='Item')
download_url = api.get_batchDownloadLink(photos[:20], zipname='my_photos.zip')

print(f"下载链接: {download_url}")
# 复制链接到浏览器下载 ZIP 文件
```

### 从百度网盘导入

```python
# 从百度网盘导入文件夹
api.importFromPanDisk(dirPath='/我的照片')
```

## 项目结构

```
pybaiduphoto/
├── pybaiduphoto/          # 主包
│   ├── config/            # 配置文件
│   │   ├── constants.py   # API 端点和常量
│   │   └── settings.py    # 运行时设置
│   ├── API.py             # 主 API 入口
│   ├── Requests.py        # HTTP 请求处理
│   ├── General.py         # 工具函数
│   ├── OnlineItem.py      # 照片/视频对象
│   ├── Album.py           # 相册对象
│   ├── Person.py          # 人物相册对象
│   ├── Location.py        # 地点相册对象
│   ├── Thing.py           # 事物相册对象
│   └── apiObject.py       # 所有对象的基类
├── examples/              # 示例脚本
│   ├── basic_usage.py
│   ├── upload_example.py
│   └── batch_download.py
├── docs/                  # 文档
│   ├── ARCHITECTURE.md
│   └── CONTRIBUTING.md
├── tests/                 # 测试文件
└── setup.py              # 包安装
```

## API 对象

### OnlineItem
表示百度相册中的照片或视频。

**方法：**
- `download(DirPath)` - 下载到本地目录
- `delete()` - 从云端删除
- `getID()` - 获取文件 ID
- `getName()` - 获取文件名
- `getSize()` - 获取文件大小
- `getMD5()` - 获取 MD5 哈希值

### Album
表示用户创建的相册。

**方法：**
- `append(itemObjs)` - 添加项目到相册
- `deleteItem(items)` - 从相册移除项目
- `delete(isWithItems)` - 删除相册
- `rename(newName)` - 重命名相册
- `setNotice(notice)` - 设置相册公告
- `get_sub_1page()` - 获取一页相册项目
- `get_sub_All()` - 获取所有相册项目

### PersonAlbum
表示基于人脸识别的人物相册。

**方法：**
- `setName(name)` - 设置人物姓名
- `rename(newName)` - setName 的别名
- `getCount()` - 获取照片数量
- `getctime()` - 获取创建时间
- `getmtime()` - 获取修改时间

### Location / Thing
与 PersonAlbum 类似，但用于地点和物体识别。

## 配置

### 环境变量

```bash
# 设置日志级别
export PYBAIDUPHOTO_LOG_LEVEL=DEBUG

# 设置代理
export PYBAIDUPHOTO_ALL_PROXY=socks5://127.0.0.1:1080
```

### 程序化配置

```python
# 初始化时设置代理
api = API(
    cookies=cookies,
    proxies={"https": "socks5://127.0.0.1:1080"}
)
```

## Cookie 管理

**重要提示**：永远不要将 Cookies 提交到版本控制。使用以下安全方法之一：

1. **browser_cookie3**（推荐）
```python
import browser_cookie3
api = API(cookies=browser_cookie3.chrome())
```

2. **环境变量**
```bash
export PYBAIDUPHOTO_COOKIES="BAIDUID=xxx;STOKEN=xxx;"
```

3. **安全配置文件**
```python
import json
with open('.env', 'r') as f:
    cookies = json.load(f)
api = API(cookies=cookies)
```

将 `.env` 添加到你的 `.gitignore` 文件中。

## 文档

- [架构文档](docs/ARCHITECTURE.md) - 内部设计和结构
- [贡献指南](docs/CONTRIBUTING.md) - 如何为项目做贡献

## 示例

查看 [examples](examples/) 目录获取完整的使用示例：

- `basic_usage.py` - 常用操作
- `upload_example.py` - 文件上传示例
- `batch_download.py` - 批量下载示例

## 依赖要求

- Python 3.8+
- requests >= 2.22.0
- rich >= 10.16.1

## 开发

```bash
# 克隆仓库
git clone https://github.com/HengyueLi/baiduphoto.git
cd baiduphoto

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 以开发模式安装
pip install -e .[dev]
```

## 测试

```bash
# 运行测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=pybaiduphoto
```

## 免责声明

本库仅供教育和个人使用。它是百度相册 API 的非官方封装，不隶属于百度也未获百度认可。

**使用风险自负。** 作者不对使用本库可能引起的任何问题负责，包括但不限于：
- 账户暂停或终止
- 数据丢失或损坏
- API 变更导致功能失效

在使用本库之前，请确保你已备份好你的数据。

## 许可证

MIT 许可证 - 详情见 [LICENSE](LICENSE) 文件。

## 贡献

欢迎贡献！请参阅 [CONTRIBUTING.md](docs/CONTRIBUTING.md) 获取指南。

## 致谢

- 感谢所有帮助改进本库的贡献者
- 基于 requests 和 rich 库构建

## 支持

- 通过 [GitHub Issues](https://github.com/HengyueLi/baiduphoto/issues) 报告错误
- 检查现有问题以了解常见问题
- 阅读文档获取详细用法

## 更新日志

查看 [CHANGES.txt](CHANGES.txt) 了解版本历史。