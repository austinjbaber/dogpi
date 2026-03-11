"""Rotating wireframe tesseract background animation for idle mode."""

import math


class TesseractBackground:
    def __init__(
        self,
        width,
        height,
        rng,
        camera_z=7.0,
        scale=36.0,
        margin=24,
        rot_x_spd=0.45,
        rot_y_spd=0.70,
        rot_z_spd=0.25,
    ):
        self.width = width
        self.height = height
        self.rng = rng

        self.camera_z = camera_z
        self.scale = scale
        self.margin = margin
        self.rot_x_spd = rot_x_spd
        self.rot_y_spd = rot_y_spd
        self.rot_z_spd = rot_z_spd

        self.ax = 0.0
        self.ay = 0.0
        self.az = 0.0
        self.cx = self.width * 0.5
        self.cy = self.height * 0.5
        self.vx = self.rng.uniform(4.0, 8.0) * self.rng.choice((-1, 1))
        self.vy = self.rng.uniform(3.0, 7.0) * self.rng.choice((-1, 1))

        cube_verts = [
            (-1, -1, -1), (-1, -1, 1),
            (-1, 1, -1), (-1, 1, 1),
            (1, -1, -1), (1, -1, 1),
            (1, 1, -1), (1, 1, 1),
        ]
        cube_edges = [
            (0, 1), (0, 2), (0, 4),
            (1, 3), (1, 5),
            (2, 3), (2, 6),
            (3, 7),
            (4, 5), (4, 6),
            (5, 7),
            (6, 7),
        ]

        base_cube = self._normalize_vertices(cube_verts)
        # A smaller, concentric cube plus connector edges makes a tesseract wireframe.
        inner_scale = 0.5
        inner_cube = [(x * inner_scale, y * inner_scale, z * inner_scale) for x, y, z in base_cube]

        self.vertices = base_cube + inner_cube
        self.edges = cube_edges + [(a + 8, b + 8) for a, b in cube_edges] + [(i, i + 8) for i in range(8)]

    def _normalize_vertices(self, verts):
        # Normalize to a unit-radius shape so scale/camera settings behave consistently.
        max_r = max(math.sqrt(x * x + y * y + z * z) for x, y, z in verts)
        return [(x / max_r, y / max_r, z / max_r) for x, y, z in verts]

    def _rotate(self):
        sx, cx = math.sin(self.ax), math.cos(self.ax)
        sy, cy = math.sin(self.ay), math.cos(self.ay)
        sz, cz = math.sin(self.az), math.cos(self.az)

        out = []
        for x, y, z in self.vertices:
            # Euler rotation sequence X -> Y -> Z for a stable tumbling wireframe.
            y, z = y * cx - z * sx, y * sx + z * cx
            x, z = x * cy + z * sy, -x * sy + z * cy
            x, y = x * cz - y * sz, x * sz + y * cz
            out.append((x, y, z))
        return out

    def _project(self, verts):
        points = []
        for x, y, z in verts:
            # Perspective projection: nearer points (smaller camera_z + z) appear larger.
            factor = self.camera_z / (self.camera_z + z)
            px = int(self.cx + x * self.scale * factor)
            py = int(self.cy + y * self.scale * factor)
            points.append((px, py))
        return points

    def update_and_draw(self, draw, dt):
        self.ax += self.rot_x_spd * dt
        self.ay += self.rot_y_spd * dt
        self.az += self.rot_z_spd * dt

        self.cx += self.vx * dt
        self.cy += self.vy * dt

        # Bounce the model center inside a safety margin so geometry stays on-screen.
        if self.cx < self.margin:
            self.cx = self.margin
            self.vx = abs(self.vx)
        if self.cx > self.width - self.margin:
            self.cx = self.width - self.margin
            self.vx = -abs(self.vx)
        if self.cy < self.margin:
            self.cy = self.margin
            self.vy = abs(self.vy)
        if self.cy > self.height - self.margin:
            self.cy = self.height - self.margin
            self.vy = -abs(self.vy)

        projected = self._project(self._rotate())

        for a, b in self.edges:
            draw.line((projected[a], projected[b]), fill=255)
        for px, py in projected:
            if 0 <= px < self.width and 0 <= py < self.height:
                draw.point((px, py), fill=255)
