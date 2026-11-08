TILE = 16

FLOOR, WALL, DOOR, KEY, EXIT = 0, 1, 2, 3, 4

# '#' wall, '.' floor, 'D' locked door, 'K' key, 'E' exit, 'S' Mona's start
# Guard patrols are lists of waypoints in tile coords; each guard walks A -> B -> A.
LEVELS = [
    {
        "map": [
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
        ],
        "patrols": [
            [(2, 9), (6, 9)],
            [(10, 2), (17, 2)],
            [(10, 10), (17, 10)],
            [(21, 5), (30, 5)],
        ],
    },
    {
        "map": [
            "################################",
            "#S.....#...........#...........#",
            "#......#.....##....#.......E...#",
            "#..##..#.....##....#...........#",
            "#..##..#...........#..####.....#",
            "#..................#..####.....#",
            "#...........K......#...........#",
            "#......#..###......D...........#",
            "#......#...........#....###....#",
            "#..##..#......##...#...........#",
            "#..##.........##...#...........#",
            "#......#...........#......####.#",
            "#......#...........#...........#",
            "################################",
        ],
        "patrols": [
            [(2, 12), (6, 12)],
            [(9, 1), (17, 1)],
            [(9, 11), (17, 11)],
            [(9, 8), (17, 8)],
            [(21, 9), (29, 9)],
            [(21, 3), (29, 3)],
        ],
    },
]

CHAR_TILE = {"#": WALL, "D": DOOR, "K": KEY, "E": EXIT}


class Level:
    def __init__(self, index=0):
        self.index = index
        self.map = LEVELS[index]["map"]
        self.patrols = LEVELS[index]["patrols"]
        self.rows = len(self.map)
        self.cols = len(self.map[0])
        self.width = self.cols * TILE
        self.height = self.rows * TILE
        self.reset()

    def reset(self):
        self.tiles = []
        self.start = (1, 1)
        for ty, line in enumerate(self.map):
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
