"""Clock animation and drawing for idle mode."""

from datetime import datetime

from PIL import ImageFont


class ClockAnimator:
    def __init__(
        self,
        width,
        height,
        rng,
        font_paths,
        pad=3,
        border=2,
        min_spd=0.4,
        max_spd=0.7,
        edge_buf_x=8,
        edge_buf_y=4,
        starfield_buffer_ease=0.35,
    ):
        self.width = width
        self.height = height
        self.rng = rng

        self.pad = pad
        self.border = border
        self.min_spd = min_spd
        self.max_spd = max_spd
        self.edge_buf_x = edge_buf_x
        self.edge_buf_y = edge_buf_y
        self.starfield_buffer_ease = starfield_buffer_ease

        self.font_paths = list(font_paths)
        self.variant_index = 0

        self.tx = 0.0
        self.ty = 0.0
        self.vx = self._rand_speed()
        self.vy = self._rand_speed()

        self.last_time_str = None
        self.font = None
        self.tbx0 = 0
        self.tby0 = 0
        self.tw = 0
        self.th = 0

    def _rand_speed(self):
        return self.rng.uniform(self.min_spd, self.max_spd)

    def _load_font(self):
        try:
            return ImageFont.truetype(self.font_paths[self.font_index], 20)
        except Exception:
            return ImageFont.load_default()

    @property
    def font_index(self):
        return self.variant_index // 2

    @property
    def show_am_pm(self):
        return (self.variant_index % 2) == 0

    def _format_time(self, now):
        if self.show_am_pm:
            return now.strftime("%I:%M %p").lstrip("0")
        return now.strftime("%I:%M").lstrip("0")

    def cycle_font(self):
        variants = len(self.font_paths) * 2
        self.variant_index = (self.variant_index + 1) % variants
        self.last_time_str = None

    def prepare(self, draw):
        time_str = self._format_time(datetime.now())

        if time_str != self.last_time_str:
            self.last_time_str = time_str
            self.font = self._load_font()
            self.tbx0, self.tby0, tbx1, tby1 = draw.textbbox((0, 0), time_str, font=self.font)
            self.tw, self.th = (tbx1 - self.tbx0), (tby1 - self.tby0)

        return time_str

    @property
    def box_w(self):
        return self.tw + 2 * (self.pad + self.border)

    @property
    def box_h(self):
        return self.th + 2 * (self.pad + self.border)

    def update_position(self, step, use_starfield_buffer):
        self.tx += self.vx * step
        self.ty += self.vy * step

        hit_x = False
        hit_y = False

        if use_starfield_buffer:
            min_x = self.edge_buf_x
            max_x = self.width - self.box_w - self.edge_buf_x
            min_y = self.edge_buf_y
            max_y = self.height - self.box_h - self.edge_buf_y

            easing_x = False
            easing_y = False

            if self.tx < min_x:
                self.vx = abs(self.vx)
                self.tx += (min_x - self.tx) * self.starfield_buffer_ease
                if min_x - self.tx < 0.5:
                    self.tx = min_x
                easing_x = True
            elif self.tx > max_x:
                self.vx = -abs(self.vx)
                self.tx -= (self.tx - max_x) * self.starfield_buffer_ease
                if self.tx - max_x < 0.5:
                    self.tx = max_x
                easing_x = True

            if self.ty < min_y:
                self.vy = abs(self.vy)
                self.ty += (min_y - self.ty) * self.starfield_buffer_ease
                if min_y - self.ty < 0.5:
                    self.ty = min_y
                easing_y = True
            elif self.ty > max_y:
                self.vy = -abs(self.vy)
                self.ty -= (self.ty - max_y) * self.starfield_buffer_ease
                if self.ty - max_y < 0.5:
                    self.ty = max_y
                easing_y = True

            if not easing_x:
                if self.tx <= min_x:
                    self.tx = min_x
                    hit_x = True
                if self.tx >= max_x:
                    self.tx = max_x
                    hit_x = True

            if not easing_y:
                if self.ty <= min_y:
                    self.ty = min_y
                    hit_y = True
                if self.ty >= max_y:
                    self.ty = max_y
                    hit_y = True
        else:
            min_x = 0
            max_x = self.width - self.box_w
            min_y = 0
            max_y = self.height - self.box_h

            if self.tx <= min_x:
                self.tx = min_x
                hit_x = True
            if self.tx >= max_x:
                self.tx = max_x
                hit_x = True
            if self.ty <= min_y:
                self.ty = min_y
                hit_y = True
            if self.ty >= max_y:
                self.ty = max_y
                hit_y = True

        if hit_x:
            self.vx = -self.vx
            self.vx = (1 if self.vx > 0 else -1) * self._rand_speed()
        if hit_y:
            self.vy = -self.vy
            self.vy = (1 if self.vy > 0 else -1) * self._rand_speed()

    def draw(self, draw, time_str):
        ix, iy = int(self.tx), int(self.ty)
        box_w = self.box_w
        box_h = self.box_h

        draw.rectangle((ix, iy, ix + box_w - 1, iy + box_h - 1), fill=0)
        for i in range(self.border):
            draw.rectangle(
                (ix + i, iy + i, ix + box_w - 1 - i, iy + box_h - 1 - i),
                outline=255,
            )

        inner_x = ix + self.border + self.pad
        inner_y = iy + self.border + self.pad
        inner_w = box_w - 2 * (self.border + self.pad)
        inner_h = box_h - 2 * (self.border + self.pad)

        text_x = inner_x + (inner_w - self.tw) // 2 - self.tbx0
        text_y = inner_y + (inner_h - self.th) // 2 - self.tby0

        draw.text((text_x, text_y), time_str, font=self.font, fill=255)
