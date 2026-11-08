import math

from level import TILE

SPEED = 26  # pixels per second
PAUSE = 0.9  # seconds spent looking around at each waypoint
TURN = 4.0  # radians per second
HALF_ANGLE = 0.62  # half-width of the vision cone
RANGE = 58  # pixels
RAYS = 8

ROW = {"down": 0, "up": 1, "left": 2, "right": 2}
TWO_PI = math.pi * 2


class Guard:
    def __init__(self, sprites, waypoints):
        self.sprites = sprites
        self.points = [(tx * TILE, ty * TILE) for tx, ty in waypoints]
        self.x, self.y = self.points[0]
        self.target = 1
        self.pause = 0.0
        self.walked = 0.0
        self.moving = False
        self.ang = self._angle_to(self.points[1])
        self.want = self.ang
        self.cone = []

    def _angle_to(self, p):
        return math.atan2(p[1] - self.y, p[0] - self.x)

    @property
    def cx(self):
        return self.x + TILE / 2

    @property
    def cy(self):
        return self.y + TILE / 2

    @property
    def facing(self):
        c, s = math.cos(self.ang), math.sin(self.ang)
        if abs(c) > abs(s):
            return "right" if c > 0 else "left"
        return "down" if s > 0 else "up"

    def update(self, dt):
        # Turn smoothly toward the wanted angle.
        diff = (self.want - self.ang + math.pi) % TWO_PI - math.pi
        step = TURN * dt
        if abs(diff) <= step:
            self.ang = self.want
        else:
            self.ang += step if diff > 0 else -step

        self.moving = False
        if self.pause > 0:
            self.pause -= dt
            return
        tx, ty = self.points[self.target]
        dx, dy = tx - self.x, ty - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        move = SPEED * dt
        if dist <= move:
            self.x, self.y = tx, ty
            self.target = (self.target + 1) % len(self.points)
            self.pause = PAUSE
            self.want = self._angle_to(self.points[self.target])
            return
        self.x += dx / dist * move
        self.y += dy / dist * move
        self.want = math.atan2(dy, dx)
        self.moving = True
        self.walked += move

    def build_cone(self, level):
        """Cast rays so the cone is clipped by walls."""
        pts = [(self.cx, self.cy)]
        for i in range(RAYS + 1):
            a = self.ang - HALF_ANGLE + (2 * HALF_ANGLE) * i / RAYS
            ca, sa = math.cos(a), math.sin(a)
            d = 0
            while d < RANGE:
                nd = d + 4
                if level.blocks_sight_px(self.cx + ca * nd, self.cy + sa * nd):
                    break
                d = nd
            pts.append((self.cx + ca * d, self.cy + sa * d))
        self.cone = pts

    def sees(self, level, px, py):
        dx, dy = px - self.cx, py - self.cy
        d2 = dx * dx + dy * dy
        if d2 > RANGE * RANGE:
            return False
        if d2 < 36:  # too close to miss
            return level.line_of_sight(self.cx, self.cy, px, py)
        d = math.sqrt(d2)
        cos_a = (dx * math.cos(self.ang) + dy * math.sin(self.ang)) / d
        if cos_a < math.cos(HALF_ANGLE):
            return False
        return level.line_of_sight(self.cx, self.cy, px, py)

    def draw_cone(self, cam_x, cam_y, alerted):
        if len(self.cone) < 3:
            return
        pts = [vec2(x - cam_x, y - cam_y) for x, y in self.cone]
        if alerted:
            screen.pen = color.rgb(255, 60, 60, 110)
        else:
            screen.pen = color.rgb(255, 235, 90, 60)
        screen.shape(shape.custom(pts))

    def draw(self, cam_x, cam_y):
        frame = 1 + int(self.walked / 6) % 2 if self.moving else 0
        sprite = self.sprites.sprite(frame, ROW[self.facing])
        x = int(self.x - cam_x)
        y = int(self.y - cam_y)
        if self.facing == "right":
            screen.blit(sprite, rect(x + TILE, y, -TILE, TILE))
        else:
            screen.blit(sprite, vec2(x, y))
