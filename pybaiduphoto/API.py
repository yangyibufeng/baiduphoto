from __future__ import annotations
import os
import logging


from .Requests import Requests
from .OnlineItem import OnlineItem
from .Album import Album
from .General import General

# from .General import getAllItemsBySinglePageFunction
from .Person import PersonAlbum
from .Location import Location
from .Thing import Thing




class ImportFromNDisk:
    """
    Handler for importing files from Baidu Netdisk to Baidu Photo.
    """
    
    def __init__(self, req: Requests):
        """
        Initialize the NetDisk importer.
        
        Args:
            req: Requests object for making API calls
        """
        self.req = req

    def listPath(self, path: str):
        """
        List directories in Baidu NetDisk.

        Args:
            path: Path to list

        Returns:
            List of directory information

        Raises:
            Exception: If API call fails
        """
        from .config.constants import API_ENDPOINTS

        url = API_ENDPOINTS["netdisk_list"]
        params = {"path": path}
        res = self.req.getReqJson(url=url, params=params)
        if res['errno'] == 0:
            return res['list']
        else:
            logging.error(str(res))
            raise Exception("error @listPath")

    def importDirByfsid(self, fsid):
        """
        Import directory by fsid.

        Args:
            fsid: File system ID of the directory

        Returns:
            API response
        """
        from .config.constants import API_ENDPOINTS

        url = API_ENDPOINTS["netdisk_import"]
        params = {
            "type": 2,
            "time_range": 10,
            "category": 13,
            "fsid_list": f"[{fsid}]"
        }
        res = self.req.getReqJson(url=url, params=params)
        return res

    def recursiveImportDir(self, dirPath: str):
        """
        Recursively import a directory from Baidu NetDisk.
        
        Args:
            dirPath: Path of the directory to import
        
        Returns:
            API response
        
        Raises:
            Exception: If directory format is invalid or directory not found
        """
        segs = [seg for seg in dirPath.split("/") if len(seg) > 0]
        if len(segs) == 0:
            logging.error(f"illegal format of dirPath={dirPath}")
            raise Exception("error @recursiveImportDir")
        fatherDir = "/" + "/".join(segs[:-1])
        listdir = self.listPath(path=fatherDir)
        fs_id = None
        for item in listdir:
            if item['path'] == dirPath:
                fs_id = item['fs_id']
                isdir = item['isdir']
                break
        if fs_id is None:
            raise Exception(f"cannot find dirPath = {dirPath} error @recursiveImportDir")
        if isdir != 1:
            raise Exception(f"only support importing directory. error @recursiveImportDir")
        return self.importDirByfsid(fsid=fs_id)


















class API:
    """
    Main API class for Baidu Photo operations.
    
    This class provides the main entry point for all Baidu Photo operations
    including file management, album operations, and uploads/downloads.
    """
    
    def __init__(self, cookies, proxies=None):
        """
        Initialize the API.
        
        Args:
            cookies: Dictionary of cookies for authentication
            proxies: Optional dictionary of proxy settings
        """
        self.req = Requests(cookies=cookies, proxies=proxies)
        self.g = General(self.req)

    @staticmethod
    def getObjectClass(name):
        """
        Get the class for a given object type.

        Args:
            name: Object type name ('Item', 'Album', 'Person', 'Location', 'Thing')

        Returns:
            Corresponding class or None if not found
        """
        from .config.constants import OBJECT_TYPES

        table = {
            "Item": OnlineItem,
            "Album": Album,
            "Person": PersonAlbum,
            "Location": Location,
            "Thing": Thing,
        }
        if name not in table:
            logging.error("not registered class by name = [{}]".format(name))
            return None
        return table[name]

    def get_self_1page(self, typeName, cursor=None) -> dict:
        """
        Get one page of objects of the specified type.
        
        Args:
            typeName: Type of objects ('Item', 'Album', 'Person', 'Location', 'Thing')
            cursor: Pagination cursor (optional)
        
        Returns:
            Dictionary with keys: 'items', 'has_more', 'cursor'
        """
        cls = self.getObjectClass(typeName)
        return cls.get_self_1page(req=self.req, cursor=cursor)

    def get_SinglePage(self, cursor=None) -> dict:
        """
        Deprecated: Use get_self_1page instead.
        
        Args:
            cursor: Pagination cursor (optional)
        
        Returns:
            Dictionary with keys: 'items', 'has_more', 'cursor'
        """
        logging.warning("Deprecated method!!! use get_self_1page instead!")
        return self.get_self_1page(typeName="Item", cursor=cursor)

    def get_self_All(self, typeName, max=-1) -> list:
        """
        Get all objects of the specified type.
        
        Args:
            typeName: Type of objects ('Item', 'Album', 'Person', 'Location', 'Thing')
            max: Maximum number of items to retrieve (-1 for all)
        
        Returns:
            List of objects
        """
        cls = self.getObjectClass(typeName)
        if cls is None:
            return None
        return cls.get_self_All(req=self.req, max=max)

    def getAllItems(self, max=-1) -> list:
        """
        Deprecated: Use get_self_All instead.
        
        Args:
            max: Maximum number of items to retrieve
        
        Returns:
            List of items
        """
        logging.warning("Deprecated method!!! use get_self_All instead!")
        return self.get_self_All(typeName="Item", max=max)

    def getAlbumList(self, limit=30, cursor=None):
        """
        Get a list of albums.

        Args:
            limit: Maximum number of albums to retrieve
            cursor: Pagination cursor (optional)

        Returns:
            Dictionary with keys: 'items', 'has_more', 'cursor'
        """
        from .config.constants import API_ENDPOINTS, DEFAULT_CLIENT_TYPE

        url = API_ENDPOINTS["album_list"]
        params = {
            "clienttype": DEFAULT_CLIENT_TYPE,
            "limit": limit,
            "need_amount": "1",
            "need_member": "1",
            "field": "mtime",
        }
        if cursor is not None:
            params["cursor"] = cursor
        pageInfo = self.req.getReqJson(url, params=params)
        if pageInfo["list"] is None:
            return {"items": [], "has_more": False, "cursor": None}
        return {
            "items": [Album(i, self.req) for i in pageInfo["list"]],
            "has_more": pageInfo["has_more"] == 1,
            "cursor": pageInfo["cursor"],
        }

    def getAlbumList_All(self, max=-1):
        """
        Get all albums.
        
        Args:
            max: Maximum number of albums to retrieve (-1 for all)
        
        Returns:
            List of Album objects
        """
        r = []
        cursor = None
        while True:
            albs = self.getAlbumList(cursor=cursor)
            r += albs["items"]
            if albs["has_more"]:
                cursor = albs["cursor"]
            else:
                return r

    def upload_1file_directly(self, filePath):
        preC, reqJson1, reqJson2 = self.g.upload_1file(filePath)
        logging.debug(
            "upload file: preC=\n{}\n,reqJson1=\n{}\n, reqJson2=\n{}\n ".format(
                preC, reqJson1, reqJson2
            )
        )
        if preC["return_type"] == 1:  # new upload
            # if reqJson2 is not None:
            info = reqJson2["data"]
            if "fsid" not in info:
                info["fsid"] = info["fs_id"]
            return OnlineItem(info, self.req)
        elif preC["return_type"] == 3:  # already exist
            logging.warning("upload item already exist on remote")
            return self.getOnlineItem_ByInfo(info=preC["data"])
        else:
            logging.error(
                "unknow return_type ={} @upload_1file_directly".format(
                    preC["return_type"]
                )
            )
            logging.error("full response = [{}]".format(str(preC)))
            return

    def upload_1file(self, filePath, album=None):
        # consider upload into alumb
        item = self.upload_1file_directly(filePath=filePath)
        if album is not None and item is not None:
            logging.debug(
                "append item into album. item=[{}],album=[{}]".format(
                    item.info, album.info
                )
            )
            album.append(item)
        return item

    def createNewAlbum(self, Name, tid=None):
        res = self.g.createNewAlbum(Name, tid)
        return Album(res["info"], req=self.req)

    def get_batchDownloadLink(self, items, zipname=None):
        return self.g.getdlLink_batchDonwload(items=items, zipname=zipname)

    def getOnlineItem_ByInfo(self, info):
        return OnlineItem(info=info, req=self.req)

    def getAlbum_ByInfo(self, info):
        return Album(info=info, req=self.req)

    def getPerson_ByInfo(self, info):
        return PersonAlbum(info=info, req=self.req)

    def getAlbum_ByID(self, ID):
        """
        Get an album by its ID.

        Args:
            ID: Album ID

        Returns:
            Album object or None if not found
        """
        from .config.constants import API_ENDPOINTS

        params = {
            "album_id": str(ID),
        }
        data = self.req.getReqJson(
            url=API_ENDPOINTS["album_list"] + "/detail",
            params=params,
        )
        if data["errno"] == 0:
            return self.getAlbum_ByInfo(info=data)
        else:
            logging.error("return error in getAlbum_ByID")

    def getPersonList_Onepage(self):
        """
        Get one page of person albums.

        Note: Currently kept as internal function. Cursor may be needed
        when number of persons increases.

        Returns:
            List of PersonAlbum objects
        """
        from .config.constants import API_ENDPOINTS

        url = API_ENDPOINTS["person_list"]
        params = {
            "ishidden": "0",
            "isrelation": "0",
        }
        res = self.req.getReqJson(url=url, params=params)
        PersonList = [PersonAlbum(info=info, req=self.req) for info in res["list"]]
        return PersonList

    def getAllPersonList(self, max=-1):
        return self.getPersonList_Onepage()

    def loadSelfByInfo(self, typeName, info):
        cls = self.getObjectClass(typeName)
        return cls.loadSelfByInfo(info=info, req=self.req)

    def albumSearch(self, keyword, limit=30, start=0):
        """
        Search for albums by keyword.

        Args:
            keyword: Search keyword
            limit: Maximum number of results (default: 30)
            start: Starting offset (default: 0)

        Returns:
            Dictionary with keys: 'items', 'has_more'
        """
        from .config.constants import API_ENDPOINTS

        R = {"items": [], "has_more": False}
        params = {
            "keyword": keyword,
            "limit": limit,
            "start": start,
        }
        req = self.g.req
        res = req.getReqJson(
            url=API_ENDPOINTS["album_search"],
            params=params,
        )
        abList = []
        for info in res["list"]:
            abList.append(self.getAlbum_ByInfo(info=info))
        R["items"] = abList
        R["has_more"] = res["has_more"] == 1
        return R
    

    def importFromPanDisk(self, dirPath: str):
        """
        Import items from Baidu Netdisk.

        Args:
            dirPath: The path in Baidu Netdisk. Example: dirPath="/我的资源"
        
        Returns:
            API response
        """
        return ImportFromNDisk(req=self.req).recursiveImportDir(dirPath=dirPath)
     

