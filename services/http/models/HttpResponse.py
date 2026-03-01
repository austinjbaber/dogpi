from dataclasses import dataclass
import json

@dataclass
class HttpResponse():
    status_code: int
    headers: dict[str, str]
    body: str | bytes

    def text(self, encoding: str = "utf-8"):
        return self.body.encode(encoding)
    
    def json(self):
        return json.loads(self.body)