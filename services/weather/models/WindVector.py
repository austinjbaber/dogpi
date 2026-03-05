from dataclasses import dataclass, field
from helpers import try_round

@dataclass
class WindVector():
    input_speed_mph: float
    speed_kph: int = field(init=False)
    speed_mph: int = field(init=False)
    direction: int = None

    def __post_init__(self):
        self.speed_mph = try_round(self.input_speed_mph)
        self.speed_kph = try_round(self.speed_mph * 1.609344)