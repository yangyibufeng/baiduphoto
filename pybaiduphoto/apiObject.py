from abc import abstractmethod
from typing import Dict, List, Optional, Callable, Any, TYPE_CHECKING
from .General import getAllItemsBySinglePageFunction

if TYPE_CHECKING:
    from .OnlineItem import OnlineItem


class apiObject:
    """
    Abstract base class for all API objects (Album, Person, Location, Thing).
    
    Provides common functionality for pagination and object loading.
    """
    
    def __init__(self, info: Dict[str, Any], req):
        """
        Initialize an API object.
        
        Args:
            info: Dictionary containing object information
            req: Requests object for making API calls
        """
        self.info = info
        self.req = req

    def getInfo(self) -> Dict[str, Any]:
        """
        Get the raw info dictionary.
        
        Returns:
            Dictionary containing object information
        """
        return self.info

    @classmethod
    @abstractmethod
    def get_self_1page(cls, req, cursor: Optional[str] = None) -> Dict[str, Any]:
        """
        Get one page of objects of this type.
        
        Args:
            req: Requests object for making API calls
            cursor: Pagination cursor (optional)
        
        Returns:
            Dictionary with keys: 'items', 'has_more', 'cursor'
        """
        pass

    @classmethod
    def get_self_All(cls, req, max: int = -1) -> List:
        """
        Get all objects of this type.
        
        Args:
            req: Requests object for making API calls
            max: Maximum number of items to retrieve (-1 for all)
        
        Returns:
            List of objects
        """
        fun = lambda cursor=None: cls.get_self_1page(req=req, cursor=cursor)
        return getAllItemsBySinglePageFunction(SinglePageFunc=fun, max=max)

    @abstractmethod
    def get_sub_1page(self, cursor: Optional[str] = None) -> Dict[str, Any]:
        """
        Get one page of items in this container.
        
        Args:
            cursor: Pagination cursor (optional)
        
        Returns:
            Dictionary with keys: 'items', 'has_more', 'cursor'
        """
        pass

    def get_sub_All(self, max: int = -1) -> List:
        """
        Get all items in this container.
        
        Args:
            max: Maximum number of items to retrieve (-1 for all)
        
        Returns:
            List of OnlineItem objects
        """
        fun = self.get_sub_1page
        return getAllItemsBySinglePageFunction(SinglePageFunc=fun, max=max)

    @classmethod
    def _get_sub_items_common(
        cls,
        url: str,
        params: Dict[str, Any],
        req,
        cursor: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Common method for getting sub-items with pagination.

        This eliminates code duplication across Album, Person, Location, Thing classes.

        Args:
            url: API endpoint URL
            params: Query parameters (will have cursor added if provided)
            req: Requests object for making API calls
            cursor: Pagination cursor (optional)

        Returns:
            Dictionary with keys: 'items', 'has_more', 'cursor'
        """
        # 延迟导入以避免循环依赖
        from .OnlineItem import OnlineItem

        if cursor:
            params["cursor"] = cursor

        resD = req.getReqJson(url=url, params=params)

        return {
            "has_more": resD["has_more"] == 1,
            "cursor": resD.get("cursor", ""),
            "items": [OnlineItem(info=i, req=req) for i in resD["list"]],
        }

    @classmethod
    def loadSelfByInfo(cls, info: Dict[str, Any], req):
        """
        Load an object from info dictionary.
        
        Args:
            info: Dictionary containing object information
            req: Requests object for making API calls
        
        Returns:
            Instance of the class
        """
        return cls(info=info, req=req)
