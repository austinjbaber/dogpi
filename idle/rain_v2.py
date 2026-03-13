"""Rain v2 background animation for idle mode.

Adds subtle wind drift, layered depth, and occasional gust pulses while
keeping the original rain implementation untouched.
"""


class RainV2Background:
    def __init__(
        self,
        width,
        height,
        rng,
        far_count=24,
        near_count=18,
        far_len=(2, 5),
        near_len=(5, 11),
        far_spd=(28.0, 66.0),
        near_spd=(72.0, 140.0),
    ):
        self.width = width
        self.height = height
        self.rng = rng

        self.far_count = far_count
        self.near_count = near_count
        self.far_len = far_len
        self.near_len = near_len
        self.far_spd = far_spd
        self.near_spd = near_spd

        self.base_wind = self.rng.uniform(-6.0, 6.0)
        self.gust_wind = 0.0
        self.gust_speed_boost = 0.0
        self.gust_time_left = 0.0
        self.next_gust_in = self.rng.uniform(2.5, 5.5)

        self.frame_index = 0
        self.splashes = []
        self.drops = []

        for _ in range(self.far_count):
            self.drops.append(self._spawn_drop(layer="far", y_range=(-self.height, self.height)))
        for _ in range(self.near_count):
            self.drops.append(self._spawn_drop(layer="near", y_range=(-self.height, self.height)))

    def _spawn_drop(self, layer, y_range):
        y0, y1 = y_range
        if layer == "far":
            length = self.rng.randint(self.far_len[0], self.far_len[1])
            speed = self.rng.uniform(self.far_spd[0], self.far_spd[1])
            vx = self.rng.uniform(-3.5, 3.5)
            phase = self.rng.randrange(0, 2)
        else:
            length = self.rng.randint(self.near_len[0], self.near_len[1])
            speed = self.rng.uniform(self.near_spd[0], self.near_spd[1])
            vx = self.rng.uniform(-6.0, 6.0)
            phase = 0

        return {
            "layer": layer,
            "x": self.rng.uniform(0.0, float(self.width - 1)),
            "y": self.rng.uniform(float(y0), float(y1)),
            "len": length,
            "spd": speed,
            "vx": vx,
            "phase": phase,
        }

    def _update_gust(self, dt):
        self.next_gust_in -= dt
        if self.next_gust_in <= 0.0:
            self.gust_time_left = self.rng.uniform(0.45, 1.1)
            self.gust_wind = self.rng.uniform(-14.0, 14.0)
            self.gust_speed_boost = self.rng.uniform(0.25, 0.75)
            self.next_gust_in = self.rng.uniform(2.8, 6.0)

        active = self.gust_time_left > 0.0
        if active:
            self.gust_time_left = max(0.0, self.gust_time_left - dt)

        speed_mult = 1.0 + (self.gust_speed_boost if active else 0.0)
        wind = self.base_wind + (self.gust_wind if active else 0.0)
        return speed_mult, wind

    def update_and_draw(self, draw, dt):
        self.frame_index += 1
        speed_mult, wind = self._update_gust(dt)

        for drop in self.drops:
            drop["y"] += drop["spd"] * speed_mult * dt
            drop["x"] += (drop["vx"] + wind) * dt

            # Wrap sideways so wind does not starve one side of the screen.
            if drop["x"] < 0.0:
                drop["x"] += self.width
            elif drop["x"] >= self.width:
                drop["x"] -= self.width

            if drop["y"] - drop["len"] > self.height:
                if drop["layer"] == "near":
                    self.splashes.append({
                        "x": int(round(drop["x"])),
                        "y": self.height - 1,
                        "ttl": 0.055,
                        "half_w": 1,
                    })

                refreshed = self._spawn_drop(layer=drop["layer"], y_range=(-14, 0))
                drop["x"] = refreshed["x"]
                drop["y"] = refreshed["y"]
                drop["len"] = refreshed["len"]
                drop["spd"] = refreshed["spd"]
                drop["vx"] = refreshed["vx"]
                drop["phase"] = refreshed["phase"]

            x = int(round(drop["x"]))
            y1 = int(round(drop["y"]))
            seg_len = drop["len"] if drop["layer"] == "near" else max(1, drop["len"] - 1)
            y0 = y1 - seg_len

            # Far-layer drops are drawn every other frame to simulate dimmer depth.
            if drop["layer"] == "far" and ((self.frame_index + drop["phase"]) % 2 != 0):
                continue

            draw.line((x, y0, x, y1), fill=255)

        next_splashes = []
        for splash in self.splashes:
            splash["ttl"] -= dt
            if splash["ttl"] <= 0.0:
                continue

            x = splash["x"]
            y = splash["y"]
            half_w = splash["half_w"]
            x0 = max(0, x - half_w)
            x1 = min(self.width - 1, x + half_w)
            draw.line((x0, y, x1, y), fill=255)
            next_splashes.append(splash)

        self.splashes = next_splashes
