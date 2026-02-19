"""
pybaiduphoto - A Python library for Baidu Photo (一刻相册) API.

This library provides programmatic access to Baidu Photo services including:
- Managing photos and videos
- Creating and managing albums
- Accessing AI-categorized albums (person, location, thing)
- Uploading and downloading files
- Batch operations

Example:
    >>> from pybaiduphoto import API
    >>> api = API(cookies=your_cookies)
    >>> photos = api.get_self_All(typeName='Item')
    >>> photos[0].download(DirPath='./downloads')
"""

__version__ = '0.3.0'
__author__ = 'yangyibufeng'
__license__ = 'MIT'

from .API import *
