"""
Constants and API endpoints configuration for pybaiduphoto.

This module contains all API endpoints, default values, and constants
used throughout the library.
"""

# API Base URL
BASE_URL = "https://photo.baidu.com/youai"

# API Endpoints
API_ENDPOINTS = {
    # File operations
    "file_list": f"{BASE_URL}/file/v1/list",
    "file_download": f"{BASE_URL}/file/v1/download",
    "file_delete": f"{BASE_URL}/file/v1/delete",
    "file_mediainfo": f"{BASE_URL}/file/v1/mediainfo",
    
    # Album operations
    "album_list": f"{BASE_URL}/album/v1/list",
    "album_create": f"{BASE_URL}/album/v1/create",
    "album_delete": f"{BASE_URL}/album/v1/delete",
    "album_append": f"{BASE_URL}/album/v1/add",
    "album_remove": f"{BASE_URL}/album/v1/remove",
    "album_rename": f"{BASE_URL}/album/v1/rename",
    "album_notice": f"{BASE_URL}/album/v1/notice",
    "album_list_files": f"{BASE_URL}/album/v1/listfile",
    "album_search": f"{BASE_URL}/album/v1/search",
    
    # Person albums
    "person_list": f"{BASE_URL}/face/v1/list",
    "person_list_files": f"{BASE_URL}/face/v1/listfile",
    "person_rename": f"{BASE_URL}/face/v1/rename",
    
    # Location albums
    "location_list": f"{BASE_URL}/place/v1/list",
    "location_list_files": f"{BASE_URL}/place/v1/listfile",
    
    # Thing albums
    "thing_list": f"{BASE_URL}/thing/v1/list",
    "thing_list_files": f"{BASE_URL}/thing/v1/listfile",
    
    # Upload operations
    "upload_precreate": f"{BASE_URL}/file/v1/upload/precreate",
    "upload_superfile2": f"{BASE_URL}/file/v1/upload/superfile2",
    "upload_create": f"{BASE_URL}/file/v1/upload/create",
    
    # Batch download
    "batch_download": f"{BASE_URL}/file/v1/batchdownload",
    
    # Netdisk import
    "netdisk_list": f"{BASE_URL}/import/v1/ndpathlist",
    "netdisk_import": f"{BASE_URL}/import/v1/create",
    
    # Token
    "token_query": f"{BASE_URL}/user/query",
}

# Default values
DEFAULT_CLIENT_TYPE = "70"
DEFAULT_PAGE_SIZE = 100
DEFAULT_MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30

# Object type names
OBJECT_TYPES = {
    "Item": "photo/video",
    "Album": "album",
    "Person": "person",
    "Location": "location",
    "Thing": "thing",
}

# ID field names for different object types
ID_FIELDS = {
    "Album": "album_id",
    "Person": "person_id",
    "Location": "tag_id",
    "Thing": "tag_id",
}

# Encryption key for batch download (DO NOT CHANGE)
BATCH_DOWNLOAD_KEY = "4f26a5c7d4e6b8a2"