from dataclasses import dataclass, field
from helpers import try_round

@dataclass
class Temperature():
    """Represents temperature. Will automatically calculate celcius based on fahrenheit and rounds up to the nearest integer."""
    input_fahrenheit: float
    fahrenheit: int = field(init=False)
    celcius: int = field(init=False)

    def _farenheit_to_celcius(self, far: float) -> int | None:
        if not isinstance(far, float):
            return None
        
        return try_round((far - 32) * (5 / 9))
    
    def __post_init__(self):
        input_f = self.input_fahrenheit
        self.fahrenheit = try_round(input_f)
        self.celcius = self._farenheit_to_celcius(input_f)