from dataclasses import dataclass
import json

@dataclass
class HttpResponse():
    status_code: int
    headers: dict[str, str]
    body: str | bytes

    def body_to_text(self, encoding: str = "utf-8"):
        """Returns the raw text of the response body"""
        return self.body.encode(encoding)
    
    def body_to_json_object(self) -> dict:
        """Returns a subscriptable json object from the response body"""
        return json.loads(self.body)
    
    def body_to_json_text(self) -> str:
        """Returns a JSON formatted string from the response body"""
        return json.dumps(json.loads(self.body))