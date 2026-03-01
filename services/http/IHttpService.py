from abc import ABC, abstractmethod

class IHttpService(ABC):
    '''An interface for HTTP methods.'''

    @abstractmethod
    def get(self, url: str, headers: dict[str, str] | None = None, params: dict[str, str] | None = None):
        pass