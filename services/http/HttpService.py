from services.http.IHttpService import IHttpService
from services.http.models import HttpResponse
from urllib.parse import urlencode, urljoin, urlparse, ParseResult
from urllib.response import addinfourl
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

class HttpService(IHttpService):
    """
    HTTP service for a single server.

    Absolute URLs are built by combining the base URL with relative URLs.

    Parameters
    ----------
    base_url : str, required
        The base URL to be used with every request. Should be passed **without** a trailing forward slash.  
        Example: ``https://example.com``
    default_headers : dict, optional
        Default headers to include with every request.  
        Example: ``{"User-Agent": "Example"}``
    timeout : float, optional
        Timeout in seconds for blocking operations (e.g., connecting to the server, reading data). Defaults to 1.0
    """
    def __init__(
        self,
        base_url: str,
        default_headers: dict[str, str] | None = None,
        timeout: float = 1.0,
    ):
        self.base_url: str = base_url.rstrip("/")
        self.default_headers:dict[str, str] | None = default_headers
        self.timeout: float = timeout
    
    def _build_url(self, rel_url: str):
        if not self.base_url:
            raise ValueError("Base url not provided.")
        
        if not rel_url:
            return self.base_url
        
        return urljoin(self.base_url + "/", rel_url.lstrip("/"))
    
    def _build_headers(self, additional_headers: dict | None) -> dict:
        if not additional_headers and not self.default_headers:
            return {}
        
        if additional_headers and not self.default_headers:
            return additional_headers
        
        if self.default_headers and not additional_headers:
            return self.default_headers
        
        all_headers: dict = self.default_headers.copy()
        all_headers.update(additional_headers)
        
        return all_headers
    
    def _build_parameters(self, abs_url: str, parameters: dict[str, str]):
        # Add request parameters if exists
        if parameters:
            return abs_url + "?" + urlencode(parameters, safe=",")
        
        return abs_url
    
    def _is_valid_relative_url(self, rel_url: str):
        parsed: ParseResult = urlparse(rel_url)
        if parsed.scheme or parsed.netloc or parsed.query:
            return False
        
        return True
    
    def get(self, relative_url: str = None, headers: dict[str, str] | None = None, params: dict[str, str] | None = None) -> HttpResponse:
        # Hardening
        if not relative_url is None and not isinstance(relative_url, str):
            raise TypeError(f"Invalid 'url' parameter type. Received {type(relative_url)}, but expected str")
        
        if not headers is None:
            if not isinstance(headers, dict):
                raise TypeError(f"Invalid 'headers' parameter type. Received {type(headers)}, but expected dict[str, str]")
            
            # Enfore dict[str, str]
            for key, value in headers.items():
                if not isinstance(key, str):
                    raise ValueError(f"The header key {repr(key)} is an invalid type. Received {type(key)}, but expected str")
                
                if not isinstance(value, str):
                    raise ValueError(f"The header value {repr(value)} is an invalid type. Received {type(value)}, but expected str")
        
        if not params is None and not isinstance(params, dict):
            raise TypeError(f"Invalid 'params' parameter type. Received {type(params)}, but expected dict[str, str]")
        
        if not relative_url is None and not self._is_valid_relative_url(relative_url):
            raise ValueError("The relative URL cannot be absolute or contain query parameters")
        
        request_url = self._build_url(relative_url)
        request_url = self._build_parameters(request_url, params)
        headers = self._build_headers(headers)
        
        # Try to send the request
        request = Request(url=request_url, headers=headers, method="GET")
        response = None
        try:
            response: addinfourl = urlopen(request, timeout=self.timeout)
            return HttpResponse(
                status_code = response.status,
                headers = response.headers.__dict__,
                body = response.read()
            )
        except HTTPError as e:
            return HttpResponse(
                status_code = e.code,
                headers = e.headers.__dict__,
                body = e.msg
            )
        except URLError as e:
            # TODO: We need to implement logging and log these exceptions.
            print(f'Error: {repr(e)}')
        except Exception as e:
            print(f'Error: {repr(e)}')
        finally:
            if response:
                response.close()