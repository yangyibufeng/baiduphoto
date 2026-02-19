import logging
from .OnlineItem import OnlineItem
from .apiObject import apiObject
from .config.constants import API_ENDPOINTS


class Location(apiObject):
    """
    Represents a location-based album in Baidu Photo.
    
    These albums are automatically created by Baidu's location recognition system.
    """
    
    @classmethod
    def get_self_1page(cls, req, cursor=None):
        """
        Get one page of location albums.
        
        Args:
            req: Requests object for making API calls
            cursor: Pagination cursor (optional)
        
        Returns:
            Dictionary with keys: 'items', 'has_more', 'cursor'
        """
        url = API_ENDPOINTS["location_list"]
        params = {"type": "2", "cursor": cursor}
        resD = req.getReqJson(url=url, params=params)
        return {
            "has_more": resD["has_more"] == 1,
            "cursor": resD["cursor"],
            "items": [cls(info=i, req=req) for i in resD["list"]],
        }

    def get_sub_1page(self, cursor=None):
        """
        Get one page of photos in this location album.
        
        Args:
            cursor: Pagination cursor (optional)
        
        Returns:
            Dictionary with keys: 'items', 'has_more', 'cursor'
        """
        url = API_ENDPOINTS["location_list_files"]
        params = {
            "cursor": cursor,
            "tag_id": self.getID(),
        }
        resD = self.req.getReqJson(url=url, params=params)
        return {
            "has_more": resD["has_more"] == 1,
            "cursor": resD["cursor"],
            "items": [OnlineItem(info=i, req=self.req) for i in resD["list"]],
        }

    def getID(self) -> str:
        """Get the location ID."""
        return str(self.info["tag_id"])

    def getName(self) -> str:
        """Get the location name."""
        return self.info["tag_name"]

    def __repr__(self) -> str:
        """String representation of the location album."""
        return f'Location({self.getName()},{self.getID()})'
