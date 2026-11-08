from level import TILE

SPEED = 52  # pixels per second
# Hitbox is Mona's feet/body, inset from the 16x16 sprite.
HB_X, HB_Y, HB_W, HB_H = 4, 8, 8, 7

ROW = {"down": 0, "up": 1, "left": 2, "right": 2}


class Player:
    def __init__(self, sprites):
        self.sprites = sprites
        self.reset(0, 0)

    def reset(self, tx, ty):
        self.x = tx * TILE
        self.y = ty * TILE
        self.facing = "down"
        self.moving = False
        self.walked = 0.0

    @property
    def cx(self):
        return self.x + TILE / 2

    @property
    def cy(self):
        return self.y + TILE / 2

    def _blocked(self, level, x, y):
        x0, y0 = x + HB_X, y + HB_Y
        x1, y1 = x0 + HB_W - 1, y0 + HB_H - 1
        return (level.solid_at_px(x0, y0) or level.solid_at_px(x1, y0)
                or level.solid_at_px(x0, y1) or level.solid_at_px(x1, y1))

    def update(self, level, dx, dy, dt):
        self.moving = dx != 0 or dy != 0
        if not self.moving:
            self.walked = 0.0
            return
        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071
        if abs(dx) > abs(dy):
            self.facing = "right" if dx > 0 else "left"
        else:
            self.facing = "down" if dy > 0 else "up"
        step = SPEED * dt
        nx = self.x + dx * step
        if not self._blocked(level, nx, self.y):
            self.x = nx
        ny = self.y + dy * step
        if not self._blocked(level, self.x, ny):
            self.y = ny
        self.walked += step

    def probe(self):
        """A point just in front of Mona, used to open doors."""
        px = self.x + HB_X + HB_W / 2
        py = self.y + HB_Y + HB_H / 2
        d = {"down": (0, 7), "up": (0, -7), "left": (-7, 0), "right": (7, 0)}[self.facing]
        return px + d[0], py + d[1]

    def draw(self, cam_x, cam_y):
        frame = 0
        if self.moving:
            frame = 1 + int(self.walked / 6) % 2
        sprite = self.sprites.sprite(frame, ROW[self.facing])
        x = int(self.x - cam_x)
        y = int(self.y - cam_y)
        if self.facing == "right":
            screen.blit(sprite, rect(x + TILE, y, -TILE, TILE))
        else:
            screen.blit(sprite, vec2(x, y))
