# Architecture Documentation

## Overview

pybaiduphoto is a Python library that provides programmatic access to Baidu Photo (一刻相册) through reverse-engineered APIs. The library follows a layered architecture with clear separation of concerns.

## Architecture Layers

```
┌─────────────────────────────────────────────────────────┐
│                     Application Layer                    │
│                  (User Scripts/Examples)                 │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                        API Layer                         │
│                     (API.py - Main Entry)                │
│  - High-level operations (upload, search, create, etc.)  │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
┌───────▼──────┐ ┌────▼─────┐ ┌────▼─────────┐
│  Data Model  │ │ Network  │ │   Utility    │
│    Layer     │ │  Layer   │ │    Layer     │
│              │ │          │ │              │
│ - OnlineItem │ │Requests  │ │  General     │
│ - Album      │ │  .py     │ │  .py         │
│ - Person     │ │          │ │              │
│ - Location   │ │          │ │ - Upload     │
│ - Thing      │ │          │ │ - Encryption │
│ - apiObject  │ │          │ │ - File I/O   │
└──────────────┘ └──────────┘ └──────────────┘
        │              │              │
        └──────────────┼──────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                     Configuration Layer                 │
│                  (config/constants.py)                   │
│              (config/settings.py)                        │
└─────────────────────────────────────────────────────────┘
```

## Core Components

### 1. API Layer (`API.py`)

The main entry point for all operations. Provides high-level methods that orchestrate interactions with other layers.

**Key Responsibilities:**
- Object factory pattern for creating data objects
- High-level operations (upload, search, import)
- Cookie and proxy management
- Session handling

**Key Methods:**
- `get_self_1page()` - Get one page of objects
- `get_self_All()` - Get all objects (handles pagination)
- `upload_1file()` - Upload a single file
- `createNewAlbum()` - Create a new album
- `albumSearch()` - Search for albums
- `get_batchDownloadLink()` - Generate batch download URL
- `importFromPanDisk()` - Import from Baidu Netdisk

### 2. Data Model Layer

#### `apiObject.py` (Base Class)

Abstract base class for all data objects. Provides common functionality for pagination and object loading.

**Key Methods:**
- `get_self_1page()` - Abstract method for getting one page
- `get_self_All()` - Get all objects with pagination
- `get_sub_1page()` - Abstract method for getting sub-items
- `get_sub_All()` - Get all sub-items
- `_get_sub_items_common()` - Common pagination logic

#### `OnlineItem.py`

Represents photos or videos stored in Baidu Photo.

**Key Methods:**
- `download()` - Download the file to local directory
- `delete()` - Delete the file from cloud
- `getID()` - Get file ID (fsid)
- `getName()` - Get file name
- `getSize()` - Get file size
- `getMD5()` - Get MD5 hash

#### `Album.py`

Represents user-created albums.

**Key Methods:**
- `append()` - Add items to album
- `deleteItem()` - Remove items from album
- `delete()` - Delete the album
- `rename()` - Rename the album
- `setNotice()` - Set album announcement
- `get_sub_1page()` - Get one page of album items
- `get_sub_All()` - Get all album items

#### `Person.py`

Represents face-recognition based person albums.

**Key Methods:**
- `setName()` / `rename()` - Set person's name
- `getCount()` - Get number of photos
- `getctime()` - Get creation time
- `getmtime()` - Get modification time

#### `Location.py` and `Thing.py`

Similar to Person albums but for location and object recognition respectively.

### 3. Network Layer (`Requests.py`)

Handles all HTTP communications with Baidu's servers.

**Key Responsibilities:**
- Cookie management
- Request/response handling
- Automatic token refresh (`bdstoken`)
- Error handling and logging

**Key Methods:**
- `getReqJson()` - GET request returning JSON
- `postReqJson()` - POST request returning JSON

### 4. Utility Layer (`General.py`)

Provides utility functions for file operations and encryption.

**Key Responsibilities:**
- File upload process (3-step: preCreate -> superfile2 -> create)
- Batch download signature generation (RC4 encryption)
- MD5 calculation
- Media metadata extraction

### 5. Configuration Layer

#### `constants.py`

Centralized configuration for:
- API endpoints
- Default values
- Object type mappings
- Encryption keys

#### `settings.py`

Runtime configuration:
- Logging setup
- Proxy configuration
- Environment variable handling

## Design Patterns

### 1. Factory Pattern

The `API` class acts as a factory for creating data objects:

```python
def getObjectClass(self, typeName):
    return {
        'Item': OnlineItem,
        'Album': Album,
        'Person': PersonAlbum,
        'Location': Location,
        'Thing': Thing,
    }[typeName]
```

### 2. Template Method Pattern

The `apiObject` base class defines the template for pagination:

```python
def get_self_All(cls, req, max=-1):
    fun = lambda cursor=None: cls.get_self_1page(req=req, cursor=cursor)
    return getAllItemsBySinglePageFunction(SinglePageFunc=fun, max=max)
```

Subclasses implement `get_self_1page()` to provide specific functionality.

### 3. Strategy Pattern

Different object types (Album, Person, Location, Thing) implement the same interface but with different behaviors.

## Data Flow

### Example: Getting All Photos

```
User Code
    │
    ▼
api.get_self_All(typeName='Item')
    │
    ▼
API.getObjectClass('Item') → OnlineItem
    │
    ▼
OnlineItem.get_self_1page(cursor)
    │
    ▼
Requests.getReqJson(url, params)
    │
    ▼
HTTP Request to Baidu Servers
    │
    ▼
HTTP Response (JSON)
    │
    ▼
Create OnlineItem objects from JSON
    │
    ▼
Return list of OnlineItem objects
```

### Example: Uploading a File

```
User Code
    │
    ▼
api.upload_1file(filePath)
    │
    ▼
General.get_file_info() → Calculate MD5, size
    │
    ├───────────────────────────────────────────┐
    ▼                                           ▼
General.upload_preCreate()                 General.upload_superfile2()
    │                                           │
    ▼                                           ▼
Get upload URL and token                Upload file chunks
    │                                           │
    └─────────────────────┬─────────────────────┘
                          ▼
                   General.upload_create()
                          │
                          ▼
                   Complete upload
```

## Security Considerations

1. **Cookie Management**: Cookies are required for authentication and should be handled securely:
   - Never commit cookies to version control
   - Use environment variables or secure config files
   - Consider using `browser_cookie3` for convenience

2. **Encryption**: Batch download uses RC4 encryption for signature generation.

3. **Network Security**: All communications use HTTPS.

## Extension Points

### Adding New Object Types

To add a new object type:

1. Create a new class inheriting from `apiObject`
2. Implement `get_self_1page()` method
3. Implement `get_sub_1page()` method (if applicable)
4. Add the type to `API.getObjectClass()`
5. Add API endpoint to `constants.py`

### Custom Authentication

To implement custom authentication:

1. Extend `Requests` class
2. Override token management methods
3. Pass custom `Requests` instance to `API` class

## Known Limitations

1. **API Stability**: Uses reverse-engineered APIs that may change without notice
2. **Rate Limiting**: No built-in rate limiting, users must implement their own
3. **Error Recovery**: Limited retry logic for failed requests
4. **Concurrent Uploads**: Upload process is not thread-safe

## Future Improvements

1. Add async support for better performance
2. Implement retry logic with exponential backoff
3. Add comprehensive unit tests
4. Improve error messages and documentation
5. Add progress callbacks for long operations
6. Support for batch operations with better error handling