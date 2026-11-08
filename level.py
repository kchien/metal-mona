TILE = 16

FLOOR, WALL, DOOR, KEY, EXIT = 0, 1, 2, 3, 4

# '#' wall, '.' floor, 'D' locked door, 'K' key, 'E' exit, 'S' Mona's start
MAP = [
    "################################",
    "#.......#..........#...........#",
    "#.......#..........#...........#",
    "#..S....#...##.....#......E....#",
    "#.......#...##.....#...........#",
    "#...............#..#...........#",
    "#...............#..D..###......#",
    "#..###..#.....K....#..###......#",
    "#.......#..........#...........#",
    "#.......#...###....#.......###.#",
    "#.......#..........#...........#",
    "################################",
]

# Guard patrols: (list of waypoints in tile coords, start facing is derived)
PATROLS = [
    [(2, 9), (6, 9)],
    [(10, 2), (17, 2)],
    [(10, 10), (17, 10)],
    [(21, 5), (30, 5)],
]

CHAR_TILE = {"#": WALL, "D": DOOR, "K": KEY, "E": EXIT}


class Level:
    def __init__(self):
        self.rows = len(MAP)
        self.cols = len(MAP[0])
        self.width = self.cols * TILE
        self.height = self.rows * TILE
        self.reset()

    def reset(self):
        self.tiles = []
        self.start = (1, 1)
        for ty, line in enumerate(MAP):
            row = []
            for tx, ch in enumerate(line):
                if ch == "S":
                    self.start = (tx, ty)
                row.append(CHAR_TILE.get(ch, FLOOR))
            self.tiles.append(row)

    def tile_at(self, tx, ty):
        if 0 <= tx < self.cols and 0 <= ty < self.rows:
            return self.tiles[ty][tx]
        return WALL

    def solid_at_px(self, x, y):
        t = self.tile_at(int(x // TILE), int(y // TILE))
        return t == WALL or t == DOOR

    def blocks_sight_px(self, x, y):
        return self.solid_at_px(x, y)

    def set_tile(self, tx, ty, t):
        self.tiles[ty][tx] = t

    def line_of_sight(self, x0, y0, x1, y1):
        dx, dy = x1 - x0, y1 - y0
        dist = (dx * dx + dy * dy) ** 0.5
        steps = int(dist / 4) + 1
        for i in range(1, steps):
            f = i / steps
            if self.blocks_sight_px(x0 + dx * f, y0 + dy * f):
                return False
        return True
