"""Starfield background animation for idle mode."""

import math


class StarfieldBackground:
    def __init__(
        self,
        width,
        height,
        rng,
        num_stars=90,
        max_depth=32.0,
        speed_min=20.0,
        speed_max=40.0,
        speed_drift=5.0,
    ):
        self.width = width
        self.height = height
        self.rng = rng

        self.num_stars = num_stars
        self.max_depth = max_depth
        self.speed_min = speed_min
        self.speed_max = speed_max
        self.speed_drift = speed_drift

        self.speed = self.speed_min
        self.speed_dir = 1.0

        self.stars = [self._new_star() for _ in range(self.num_stars)]

    def _new_star(self):
        angle = self.rng.uniform(0.0, 2.0 * math.pi)
        radius = self.rng.uniform(0.2, 1.0)
        return [
            math.cos(angle) * radius * (self.width / 2.0),
            math.sin(angle) * radius * (self.height / 2.0),
            self.rng.uniform(self.max_depth * 0.5, self.max_depth),
        ]

    def update_and_draw(self, draw, step, vp_x, vp_y):
        dt = step / 40.0

        self.speed += self.speed_drift * self.speed_dir * dt
        if self.speed > self.speed_max:
            self.speed = self.speed_max
            self.speed_dir = -1.0
        if self.speed < self.speed_min:
            self.speed = self.speed_min
            self.speed_dir = 1.0

        for star in self.stars:
            old_z = star[2]
            star[2] -= self.speed * dt

            if star[2] <= 0.3:
                star[:] = self._new_star()
                continue

            factor = self.max_depth / star[2]
            sx = int(vp_x + star[0] * factor)
            sy = int(vp_y + star[1] * factor)

            old_factor = self.max_depth / old_z
            sx_old = int(vp_x + star[0] * old_factor)
            sy_old = int(vp_y + star[1] * old_factor)

            if sx < -4 or sx >= self.width + 4 or sy < -4 or sy >= self.height + 4:
                star[:] = self._new_star()
                continue

            draw.line((sx_old, sy_old, sx, sy), fill=255)

            if star[2] < self.max_depth * 0.3:
                draw.rectangle((sx - 1, sy - 1, sx + 1, sy + 1), fill=255)
            elif star[2] < self.max_depth * 0.6:
                draw.point((sx, sy), fill=255)
                draw.point((sx + 1, sy), fill=255)
