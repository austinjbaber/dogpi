"""Rain v2 background animation for idle mode.

Adds subtle wind drift, layered depth, and occasional gust"""


class RainV2Background:
    def __init__(
        self,
        width,
        height,
        rng,
        far_count=24,
        near_count=18,
        far_len=(4, 8),
        near_len=(10, 18),
        far_spd=(30.0, 60.0),
        near_spd=(90.0, 150.0),
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

        self.base_wind = self.rng.uniform(-2.0, 2.0)
        self.gust_wind = 0.0
        self.gust_time_left = 0.0
        self.next_gust_in = self.rng.uniform(1.4, 2.8)
        self.lightning_time_left = 0.0
        self.lightning_flash_time = 0.0
        self.next_lightning_in = self.rng.uniform(9.0, 18.0)
        self.lightning_segments = []
        self.lightning_branch_segments = []

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
            phase = self.rng.randrange(0, 2)
        else:
            length = self.rng.randint(self.near_len[0], self.near_len[1])
            speed = self.rng.uniform(self.near_spd[0], self.near_spd[1])
            phase = 0

        return {
            "layer": layer,
            "x": self.rng.uniform(0.0, float(self.width - 1)),
            "y": self.rng.uniform(float(y0), float(y1)),
            "len": length,
            "spd": speed,
            "phase": phase,
        }

    def _update_gust(self, dt):
        self.next_gust_in -= dt
        if self.next_gust_in <= 0.0:
            self.gust_time_left = self.rng.uniform(1.5, 3.0)
            gust_mag = self.rng.uniform(20.0, 30.0)
            self.gust_wind = gust_mag * self.rng.choice((-1.0, 1.0))
            self.next_gust_in = self.rng.uniform(4, 6)

        active = self.gust_time_left > 0.0
        if active:
            self.gust_time_left = max(0.0, self.gust_time_left - dt)

        wind = self.base_wind + (self.gust_wind if active else 0.0)
        return wind

    def _build_lightning_path(self, start_x, start_y, max_height, horizontal_step, vertical_step):
        points = [(start_x, start_y)]
        x = start_x
        y = start_y
        while y < max_height:
            x += self.rng.randint(-horizontal_step, horizontal_step)
            x = max(2, min(self.width - 3, x))
            y += self.rng.randint(max(5, vertical_step - 3), vertical_step + 4)
            points.append((x, min(max_height, y)))
        return points

    def _points_to_segments(self, points):
        return list(zip(points, points[1:]))

    def _start_lightning(self):
        start_x = self.rng.randint(self.width // 5, (self.width * 4) // 5)
        max_height = self.rng.randint(self.height // 2, self.height - 10)
        main_points = self._build_lightning_path(
            start_x=start_x,
            start_y=0,
            max_height=max_height,
            horizontal_step=8,
            vertical_step=10,
        )
        self.lightning_segments = self._points_to_segments(main_points)

        self.lightning_branch_segments = []
        if len(main_points) >= 4:
            branch_origin = self.rng.randint(1, len(main_points) - 2)
            bx, by = main_points[branch_origin]
            branch_points = self._build_lightning_path(
                start_x=bx,
                start_y=by,
                max_height=min(self.height - 6, by + self.rng.randint(10, 22)),
                horizontal_step=7,
                vertical_step=7,
            )
            if len(branch_points) >= 2:
                self.lightning_branch_segments = self._points_to_segments(branch_points)

        self.lightning_time_left = self.rng.uniform(0.10, 0.18)
        self.lightning_flash_time = self.rng.uniform(0.14, 0.24)
        self.next_lightning_in = self.rng.uniform(12.0, 24.0)

    def _update_lightning(self, dt):
        if self.lightning_time_left > 0.0:
            self.lightning_time_left = max(0.0, self.lightning_time_left - dt)
        else:
            self.lightning_segments = []
            self.lightning_branch_segments = []

        if self.lightning_flash_time > 0.0:
            self.lightning_flash_time = max(0.0, self.lightning_flash_time - dt)

        self.next_lightning_in -= dt
        if self.next_lightning_in <= 0.0 and self.lightning_flash_time <= 0.0:
            self._start_lightning()

    def _draw_lightning(self, draw):
        if self.lightning_flash_time > 0.0:
            flash_h = self.rng.randint(10, 18)
            draw.rectangle((0, 0, self.width - 1, flash_h), outline=255, fill=255)

        if self.lightning_time_left <= 0.0:
            return

        for (x0, y0), (x1, y1) in self.lightning_segments:
            draw.line((x0, y0, x1, y1), fill=255)
            if x0 + 1 < self.width and x1 + 1 < self.width:
                draw.line((x0 + 1, y0, x1 + 1, y1), fill=255)

        for (x0, y0), (x1, y1) in self.lightning_branch_segments:
            draw.line((x0, y0, x1, y1), fill=255)

    def update_and_draw(self, draw, dt):
        self.frame_index += 1
        wind = self._update_gust(dt)
        self._update_lightning(dt)

        for drop in self.drops:
            horizontal_v = wind
            drop["y"] += drop["spd"] * dt
            drop["x"] += horizontal_v * dt

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
                        "ttl": 0.085,
                        "half_w": self.rng.randint(1, 2),
                    })

                refreshed = self._spawn_drop(layer=drop["layer"], y_range=(-14, 0))
                drop["x"] = refreshed["x"]
                drop["y"] = refreshed["y"]
                drop["len"] = refreshed["len"]
                drop["spd"] = refreshed["spd"]
                drop["phase"] = refreshed["phase"]

            x = int(round(drop["x"]))
            y1 = int(round(drop["y"]))
            seg_len = drop["len"] if drop["layer"] == "near" else max(1, drop["len"] - 1)
            y0 = y1 - seg_len
            slant = int(round((horizontal_v / max(drop["spd"], 1.0)) * seg_len * 1.35))
            x0 = x - slant

            # Far-layer drops are drawn every other frame to simulate dimmer depth.
            if drop["layer"] == "far" and ((self.frame_index + drop["phase"]) % 2 != 0):
                continue

            draw.line((x0, y0, x, y1), fill=255)

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
        self._draw_lightning(draw)
