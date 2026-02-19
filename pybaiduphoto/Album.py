import logging
from typing import Union, List
from .OnlineItem import OnlineItem
from .apiObject import apiObject
from ..config.constants import API_ENDPOINTS, DEFAULT_CLIENT_TYPE


class Album(apiObject):
    """
    Represents a user-created album in Baidu Photo.
    
    Provides functionality for managing album contents, including:
    - Adding/removing items
    - Renaming and setting notices
    - Deleting the album
    - Listing album contents
    """
    
    @classmethod
    def get_self_1page(cls, req, cursor=None):
        """
        Get one page of albums.
        
        Args:
            req: Requests object for making API calls
            cursor: Pagination cursor (optional)
        
        Returns:
            Dictionary with keys: 'items', 'has_more', 'cursor'
        """
        url = API_ENDPOINTS["album_list"]
        params = {
            "cursor": cursor,
            "need_amount": "1",
            "need_member": "1",
            "field": "mtime",
        }
        pageInfo = req.getReqJson(url, params=params)
        if pageInfo["list"] is None:
            return {"items": [], "has_more": False, "cursor": None}
        return {
            "items": [cls(i, req) for i in pageInfo["list"]],
            "has_more": pageInfo["has_more"] == 1,
            "cursor": pageInfo["cursor"],
        }

    def append(self, itemObjs: Union[OnlineItem, List[OnlineItem]]):
        """
        Add one or more items to the album.
        
        Args:
            itemObjs: Single OnlineItem or list of OnlineItems to add
        
        Returns:
            API response dictionary
        """
        if type(itemObjs) is not list:
            itemObjlist = [itemObjs]
        else:
            itemObjlist = itemObjs

        url = API_ENDPOINTS["album_append"]
        params = {
            "clienttype": DEFAULT_CLIENT_TYPE,
            "album_id": self.getID(),
            "tid": self._getTID(),
            "list": "[{}]".format(
                ",".join(
                    ['{"fsid":{}}'.format(item.getID()) for item in itemObjlist]
                )
            ),
        }
        logging.debug("Album-append, getParams=[{}]".format(params))
        response = self.req.getReqJson(url, params=params)
        return response

    def deleteItem(self, items: Union[OnlineItem, List[OnlineItem]], isOrigin: bool = False):
        """
        Remove one or more items from the album.
        
        Args:
            items: Single OnlineItem or list of OnlineItems to remove
            isOrigin: If True, also delete the original file from cloud
        
        Returns:
            API response dictionary
        """
        if type(items) is not list:
            items = [items]
        uk = self.info["cover_info"]["uk"]
        data = {
            "album_id": self.getID(),
            "tid": self._getTID(),
            "list": "[{}]".format(
                ",".join(
                    ['{{"fsid":{},"uk":{}}}'.format(item.getID(), uk) for item in items]
                )
            ),
            "del_origin": "1" if isOrigin else "0",
        }
        url = API_ENDPOINTS["album_remove"]
        resDict = self.req.postReqJson(url, data=data)
        return resDict

    def delete(self, isWithItems: bool = True):
        """
        Delete the album.
        
        Args:
            isWithItems: If True, also delete all items in the album
        
        Returns:
            API response dictionary
        """
        data = {
            "album_id": self.getID(),
            "delete_origin_image": "1" if isWithItems else "0",
            "tid": self._getTID(),
        }
        url = API_ENDPOINTS["album_delete"]
        return self.req.postReqJson(url, data=data)

    def get_sub_1page(self, cursor=None):
        """
        Get one page of items in the album.
        
        Args:
            cursor: Pagination cursor (optional)
        
        Returns:
            Dictionary with keys: 'items', 'has_more', 'cursor'
        """
        url = API_ENDPOINTS["album_list_files"]
        data = {
            "cursor": cursor,
            "album_id": self.info["album_id"],
        }
        res = self.req.postReqJson(url=url, data=data)
        return {
            "items": [
                OnlineItem(info=itemInfo, req=self.req) for itemInfo in res["list"]
            ],
            "has_more": res["has_more"] == 1,
            "cursor": res["cursor"],
        }

    def getName(self) -> str:
        """Get the album name."""
        return self.info["title"]

    def getID(self) -> str:
        """Get the album ID."""
        return self.info["album_id"]

    def _getTID(self) -> str:
        """Get the album TID (internal identifier)."""
        return self.info["tid"]

    def rename(self, newName: str) -> None:
        """
        Rename the album.
        
        Args:
            newName: New album name
        """
        url = API_ENDPOINTS["album_rename"]
        data = {
            "album_id": self.getID(),
            "tid": self._getTID(),
            "title": newName,
        }
        r = self.req.postReqJson(url, data=data)
        if r["errno"] == 0:
            self.info["title"] = newName

    def setNotice(self, notice: str):
        """
        Set the album notice/announcement.
        
        Args:
            notice: Notice text to set
        
        Returns:
            Self for method chaining
        """
        url = API_ENDPOINTS["album_notice"]
        params = {
            'clienttype': DEFAULT_CLIENT_TYPE,
            'album_id': self.getID(),
            'tid': self._getTID(),
            'notice': notice,
        }
        r = self.req.getReqJson(url=url, params=params)
        return self

    def __repr__(self) -> str:
        """String representation of the album."""
        return f"Album({self.getName()},{self.getID()})"
