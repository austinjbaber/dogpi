"""Rotating wireframe icosahedron background animation for idle mode."""

import math


class IcosahedronBackground:
    def __init__(
        self,
        width,
        height,
        rng,
        camera_z=4.0,
        scale=24,
        margin=16,
        rot_x_spd=0.45,
        rot_y_spd=0.70,
        rot_z_spd=0.25,
    ):
        self.width = width
        self.height = height
        self.rng = rng

        # Golden ratio coordinates make an icosahedron in 3D
        phi = (1.0 + math.sqrt(5.0)) / 2.0
        verts = [
            (-1, phi, 0),
            (1, phi, 0),
            (-1, -phi, 0),
            (1, -phi, 0),
            (0, -1, phi),
            (0, 1, phi),
            (0, -1, -phi),
            (0, 1, -phi),
            (phi, 0, -1),
            (phi, 0, 1),
            (-phi, 0, -1),
            (-phi, 0, 1),
        ]
        self.edges = [
            (0, 11), (0, 5), (0, 1), (0, 7), (0, 10),
            (1, 5), (1, 9), (1, 8), (1, 7),
            (2, 3), (2, 4), (2, 6), (2, 10), (2, 11),
            (3, 4), (3, 9), (3, 8), (3, 6),
            (4, 5), (4, 9), (4, 11),
            (5, 9), (5, 11),
            (6, 7), (6, 8), (6, 10),
            (7, 8), (7, 10),
            (8, 9),
            (10, 11),
        ]

        max_r = max(math.sqrt(x * x + y * y + z * z) for x, y, z in verts)
        # Normalize to unit radius so scale and camera are predictable
        self.verts = [(x / max_r, y / max_r, z / max_r) for x, y, z in verts]

        self.camera_z = camera_z
        self.scale = scale
        self.margin = margin
        self.rot_x_spd = rot_x_spd
        self.rot_y_spd = rot_y_spd
        self.rot_z_spd = rot_z_spd

        self.ax = 0.0
        self.ay = 0.0
        self.az = 0.0
        self.cx = self.width / 2.0
        self.cy = self.height / 2.0
        self.vx = self.rng.uniform(6, 12) * self.rng.choice((-1, 1))
        self.vy = self.rng.uniform(4, 8) * self.rng.choice((-1, 1))

    def _rotate(self):
        sx, cx = math.sin(self.ax), math.cos(self.ax)
        sy, cy = math.sin(self.ay), math.cos(self.ay)
        sz, cz = math.sin(self.az), math.cos(self.az)
        out = []
        for x, y, z in self.verts:
            # Euler rotation sequence X -> Y -> Z for a stable tumbling wireframe.
            y, z = y * cx - z * sx, y * sx + z * cx
            x, z = x * cy + z * sy, -x * sy + z * cy
            x, y = x * cz - y * sz, x * sz + y * cz
            out.append((x, y, z))
        return out

    def _project(self, verts):
        points = []
        for x, y, z in verts:
            # Perspective divide: points with larger z are drawn closer to center/smaller.
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
        # Reflect center velocity at margins so the shape "bounces" around the screen.
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
