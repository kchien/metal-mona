import os
import sys
import unittest
from collections import deque

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import level as lv  # noqa: E402
from guard import Guard  # noqa: E402

KNOWN = set("#.DKES")


def find(grid, ch):
    return [(x, y) for y, row in enumerate(grid) for x, c in enumerate(row) if c == ch]


def reachable(grid, start, door_open):
    seen = {start}
    q = deque([start])
    while q:
        x, y = q.popleft()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if not (0 <= ny < len(grid) and 0 <= nx < len(grid[0])):
                continue
            c = grid[ny][nx]
            if c == "#" or (c == "D" and not door_open):
                continue
            if (nx, ny) not in seen:
                seen.add((nx, ny))
                q.append((nx, ny))
    return seen


class TestLevelData(unittest.TestCase):
    def test_has_multiple_levels(self):
        self.assertGreaterEqual(len(lv.LEVELS), 2)

    def test_level_structure(self):
        for i, d in enumerate(lv.LEVELS):
            with self.subTest(level=i):
                grid = d["map"]
                self.assertTrue(d["patrols"])
                self.assertEqual(len({len(r) for r in grid}), 1, "ragged rows")
                self.assertEqual(set("".join(grid)) - KNOWN, set())
                self.assertEqual(set(grid[0]), {"#"})
                self.assertEqual(set(grid[-1]), {"#"})
                for r in grid:
                    self.assertEqual((r[0], r[-1]), ("#", "#"))
                for ch in "SEKD":
                    self.assertEqual(len(find(grid, ch)), 1, ch)

    def test_patrols_on_walkable_tiles(self):
        for i, d in enumerate(lv.LEVELS):
            grid = d["map"]
            for p in d["patrols"]:
                self.assertGreaterEqual(len(p), 2)
                for x, y in p:
                    with self.subTest(level=i, point=(x, y)):
                        self.assertTrue(0 <= y < len(grid) and 0 <= x < len(grid[0]))
                        self.assertNotIn(grid[y][x], "#D")

    def test_solvable_only_through_door(self):
        for i, d in enumerate(lv.LEVELS):
            with self.subTest(level=i):
                g = d["map"]
                s, k, e = find(g, "S")[0], find(g, "K")[0], find(g, "E")[0]
                closed = reachable(g, s, False)
                self.assertIn(k, closed, "key unreachable")
                self.assertNotIn(e, closed, "exit reachable without door")
                self.assertIn(e, reachable(g, s, True))

    def test_guards_construct(self):
        for d in lv.LEVELS:
            for p in d["patrols"]:
                Guard(None, p)


class TestLevelClass(unittest.TestCase):
    def test_loads_by_index(self):
        for i, d in enumerate(lv.LEVELS):
            L = lv.Level(i)
            self.assertEqual(L.index, i)
            self.assertEqual(L.rows, len(d["map"]))
            self.assertEqual(L.cols, len(d["map"][0]))
            self.assertEqual(L.width, L.cols * lv.TILE)
            self.assertEqual(L.patrols, d["patrols"])
            self.assertEqual(L.start, find(d["map"], "S")[0])

    def test_default_is_first_level(self):
        self.assertEqual(lv.Level().index, 0)

    def test_levels_differ(self):
        self.assertNotEqual(lv.LEVELS[0]["map"], lv.LEVELS[1]["map"])

    def test_first_level_unchanged(self):
        m = lv.LEVELS[0]["map"]
        self.assertEqual((len(m), len(m[0])), (12, 32))
        self.assertEqual(find(m, "K")[0], (14, 7))
        self.assertEqual(find(m, "D")[0], (19, 6))
        self.assertEqual(find(m, "E")[0], (26, 3))

    def test_reset_restores_consumed_tiles(self):
        L = lv.Level(1)
        kx, ky = find(L.map, "K")[0]
        dx, dy = find(L.map, "D")[0]
        L.set_tile(kx, ky, lv.FLOOR)
        L.set_tile(dx, dy, lv.FLOOR)
        L.reset()
        self.assertEqual(L.tile_at(kx, ky), lv.KEY)
        self.assertEqual(L.tile_at(dx, dy), lv.DOOR)

    def test_out_of_bounds_is_wall(self):
        self.assertEqual(lv.Level().tile_at(-1, 0), lv.WALL)


if __name__ == "__main__":
    unittest.main()
