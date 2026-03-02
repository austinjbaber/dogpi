from dataclasses import dataclass
import json
from typing import Any

@dataclass
class HttpResponse():
    status_code: int
    headers: dict[str, str]
    body: str | bytes

    def body_to_text(self, encoding: str = "utf-8"):
        """Returns the raw text of the response body"""
        return self.body.decode(encoding)
    
    def body_to_json_object(self) -> dict[str, Any] | None:
        """Returns a subscriptable json object from the response body if it exists, or None"""
        return json.loads(self.body) if self.body else None
    
    def body_to_json_text(self) -> str | None:
        """Returns a JSON formatted string from the response body if it exists, or None"""
        return json.dumps(json.loads(self.body)) if self.body else None