from dataclasses import dataclass

@dataclass
class WindVector():
    speed_kph: int = None
    speed_mph: int = None
    direction: int = None