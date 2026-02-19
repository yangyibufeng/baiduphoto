import logging
from typing import Union
from .OnlineItem import OnlineItem
from .apiObject import apiObject
from .config.constants import API_ENDPOINTS


class PersonAlbum(apiObject):
    """
    Represents a person album (face recognition-based) in Baidu Photo.
    
    These albums are automatically created by Baidu's AI face recognition system.
    """
    
    @classmethod
    def get_self_1page(cls, req, cursor=None):
        """
        Get one page of person albums.
        
        Args:
            req: Requests object for making API calls
            cursor: Pagination cursor (optional)
        
        Returns:
            Dictionary with keys: 'items', 'has_more', 'cursor'
        """
        url = API_ENDPOINTS["person_list"]
        params = {
            "cursor": cursor,
            "ishidden": "0",
            "isrelation": "0",
        }
        res = req.getReqJson(url=url, params=params)
        return {
            "items": [cls(info=info, req=req) for info in res["list"]],
            "has_more": res["has_more"] == 1,
            "cursor": res["cursor"],
        }

    def get_sub_1page(self, cursor=None):
        """
        Get one page of photos in this person album.
        
        Args:
            cursor: Pagination cursor (optional)
        
        Returns:
            Dictionary with keys: 'items', 'has_more', 'cursor'
        """
        url = API_ENDPOINTS["person_list_files"]
        params = {
            "tag_id": self.getID(),
            "status": "0",
            "cursor": cursor,
        }
        resDict = self.req.getReqJson(url=url, params=params)
        return {
            "items": [OnlineItem(i, self.req) for i in resDict["list"]],
            "has_more": resDict["has_more"] == 1,
            "cursor": resDict["cursor"],
        }

    def getID(self) -> str:
        """Get the person ID."""
        return str(self.info["person_id"])

    def getName(self) -> str:
        """Get the person's name."""
        return self.info["name"]

    def setName(self, name: str) -> None:
        """
        Set the person's name.
        
        Args:
            name: New name for the person
        """
        params = {
            "person_id": self.getID(),
            "name": name,
        }
        resD = self.req.getReqJson(
            url=API_ENDPOINTS["person_rename"], params=params
        )
        if resD["errno"] == 0:
            self.info["name"] = name

    def rename(self, newName: str) -> None:
        """
        Rename the person (alias for setName).
        
        Args:
            newName: New name for the person
        """
        self.setName(newName)

    def getctime(self) -> int:
        """Get the creation timestamp."""
        return self.info["ctime"]

    def getmtime(self) -> int:
        """Get the modification timestamp."""
        return self.info["mtime"]

    def getCount(self) -> int:
        """Get the number of photos in this person album."""
        return self.info["pic_count"]

    def __repr__(self) -> str:
        """String representation of the person album."""
        return f'PersonAlbum({self.getName()},{self.getID()})'