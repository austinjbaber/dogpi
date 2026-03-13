"""Rain background animation for idle mode."""


class RainBackground:
    def __init__(self, width, height, rng, num_drops=40, len_min=3, len_max=10, spd_min=32.0, spd_max=120.0):
        self.width = width
        self.height = height
        self.rng = rng
        self.num_drops = num_drops
        self.len_min = len_min
        self.len_max = len_max
        self.spd_min = spd_min
        self.spd_max = spd_max
        self.drops = [
            {
                "x": self.rng.randrange(0, self.width),
                "y": self.rng.uniform(-self.height, 0),
                "len": self.rng.randint(self.len_min, self.len_max),
                "spd": self.rng.uniform(self.spd_min, self.spd_max),
            }
            for _ in range(self.num_drops)
        ]

    def update_and_draw(self, draw, dt):
        for drop in self.drops:
            drop["y"] += drop["spd"] * dt
            if drop["y"] - drop["len"] > self.height:
                # Recycle drops above the frame with new length/speed for depth variation.
                drop["x"] = self.rng.randrange(0, self.width)
                drop["y"] = self.rng.uniform(-10, 0)
                drop["len"] = self.rng.randint(self.len_min, self.len_max)
                drop["spd"] = self.rng.uniform(self.spd_min, self.spd_max)
            x = int(drop["x"])
            y0 = int(drop["y"] - drop["len"])
            y1 = int(drop["y"])
            draw.line((x, y0, x, y1), fill=255)
