from abc import ABC, abstractmethod
from services.http.models.HttpResponse import HttpResponse

class IHttpService(ABC):
    '''An interface for HTTP methods.'''

    @abstractmethod
    def get(self, url: str, headers: dict[str, str] | None = None, params: dict[str, str] | None = None) -> HttpResponse:
        """
        Perform a GET request for the relative url specified.

        Parameters
        ----------
        relative_url : str, optional
            The partial web address that specifies the location of a resource relative to base_url. This can be passed with or without the leading forward slash.  
            Example: ``get("/users") or get("user")``

        headers : dict[str, str], optional
            Additional headers to combine with default_headers to be sent with the request.  
            Example: ``{"User-Agent": "Example"}``

        params : dict[str, str], optional
            Dictionary of query parameters to append to the URL.  
            Example: ``{"Name": "John"}``
        """
        pass