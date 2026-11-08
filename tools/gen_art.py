"""Generate Metal Mona pixel art (pure python, no PIL). Usage: gen_art.py OUT_DIR"""
import struct
import sys
import zlib

T = None  # transparent
OUT = (27, 18, 48, 255)


def png(path, w, h, px):
    raw = b""
    for y in range(h):
        raw += b"\x00"
        for x in range(w):
            c = px[y][x]
            raw += bytes(c) if c else b"\x00\x00\x00\x00"

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    data = b"\x89PNG\r\n\x1a\n"
    data += chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
    data += chunk(b"IDAT", zlib.compress(raw, 9))
    data += chunk(b"IEND", b"")
    open(path, "wb").write(data)


class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.px = [[T] * w for _ in range(h)]

    def put(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.px[y][x] = c

    def rect(self, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.put(x, y, c)

    def outline(self, col=OUT):
        src = [row[:] for row in self.px]
        for y in range(self.h):
            for x in range(self.w):
                if src[y][x]:
                    continue
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.w and 0 <= ny < self.h and src[ny][nx]:
                        self.px[y][x] = col
                        break


def rgb(r, g, b):
    return (r, g, b, 255)


MONA = dict(
    body=rgb(118, 73, 214), light=rgb(166, 124, 240), face=rgb(247, 222, 186),
    eye=rgb(27, 18, 48), cheek=rgb(240, 150, 160), cap=None)
GUARD = dict(
    body=rgb(70, 110, 80), light=rgb(110, 150, 115), face=rgb(236, 190, 150),
    eye=rgb(27, 18, 48), cheek=rgb(220, 140, 120), cap=rgb(52, 84, 62))


def character(pal, facing, frame):
    """16x16 chibi: facing in down/up/left; frame 0 stand, 1/2 walk."""
    c = Canvas(16, 16)
    body, light, face, eye = pal["body"], pal["light"], pal["face"], pal["eye"]
    bob = 1 if frame in (1, 2) else 0
    # ears (hood)
    c.rect(2, 1 + bob, 4, 3 + bob, body)
    c.rect(11, 1 + bob, 13, 3 + bob, body)
    c.put(3, 2 + bob, light)
    c.put(12, 2 + bob, light)
    # head
    c.rect(2, 3 + bob, 13, 10 + bob, body)
    c.rect(3, 2 + bob, 12, 2 + bob, body)
    c.rect(3, 3 + bob, 6, 3 + bob, light)
    # body / tentacle skirt
    c.rect(4, 11 + bob, 11, 12 + bob, body)
    c.rect(5, 11 + bob, 7, 11 + bob, light)
    # legs / tentacles
    if frame == 0:
        c.rect(4, 13, 6, 15, body)
        c.rect(9, 13, 11, 15, body)
    elif frame == 1:
        c.rect(4, 13 + bob, 6, 14, body)
        c.rect(9, 13 + bob, 11, 15, body)
    else:
        c.rect(4, 13 + bob, 6, 15, body)
        c.rect(9, 13 + bob, 11, 14, body)
    if facing == "down":
        c.rect(4, 5 + bob, 11, 9 + bob, face)
        c.rect(5, 6 + bob, 5, 7 + bob, eye)
        c.rect(10, 6 + bob, 10, 7 + bob, eye)
        c.put(4, 8 + bob, pal["cheek"])
        c.put(11, 8 + bob, pal["cheek"])
    elif facing == "left":
        c.rect(2, 5 + bob, 9, 9 + bob, face)
        c.rect(3, 6 + bob, 3, 7 + bob, eye)
        c.rect(6, 6 + bob, 6, 7 + bob, eye)
        c.put(3, 8 + bob, pal["cheek"])
    else:  # up: back of the hood
        c.rect(4, 5 + bob, 11, 9 + bob, light)
        c.rect(6, 6 + bob, 9, 8 + bob, body)
    if pal["cap"]:
        cap = pal["cap"]
        c.rect(2, 3 + bob, 13, 4 + bob, cap)
        c.rect(3, 2 + bob, 12, 2 + bob, cap)
        if facing == "down":
            c.rect(3, 5 + bob, 12, 5 + bob, cap)
        elif facing == "left":
            c.rect(2, 5 + bob, 9, 5 + bob, cap)
    c.outline()
    return c


def sheet(pal):
    sh = Canvas(48, 48)
    for row, facing in enumerate(("down", "up", "left")):
        for frame in range(3):
            ch = character(pal, facing, frame)
            for y in range(16):
                for x in range(16):
                    sh.px[row * 16 + y][frame * 16 + x] = ch.px[y][x]
    return sh


def tiles():
    sh = Canvas(16 * 6, 16)

    def tile(i):
        return i * 16

    # 0 floor (checker with subtle panel lines)
    a, b = rgb(88, 94, 110), rgb(80, 86, 102)
    for y in range(16):
        for x in range(16):
            sh.put(tile(0) + x, y, a if ((x // 8) + (y // 8)) % 2 == 0 else b)
    for i in range(16):
        sh.put(tile(0) + i, 0, rgb(70, 76, 92))
        sh.put(tile(0) + 0, i, rgb(70, 76, 92))
    # 1 wall (brick)
    base, mortar, top = rgb(52, 40, 86), rgb(30, 22, 54), rgb(92, 72, 140)
    sh.rect(tile(1), 0, tile(1) + 15, 15, base)
    for y in (0, 5, 10, 15):
        sh.rect(tile(1), y, tile(1) + 15, y, mortar)
    for y0, offs in ((0, (0, 8)), (5, (4, 12)), (10, (0, 8))):
        for xo in offs:
            sh.rect(tile(1) + xo, y0, tile(1) + xo, y0 + 5, mortar)
    sh.rect(tile(1), 1, tile(1) + 15, 1, top)
    # 2 door (locked)
    sh.rect(tile(2), 0, tile(2) + 15, 15, rgb(60, 60, 70))
    sh.rect(tile(2) + 2, 0, tile(2) + 13, 15, rgb(170, 120, 40))
    sh.rect(tile(2) + 2, 0, tile(2) + 2, 15, rgb(110, 76, 24))
    sh.rect(tile(2) + 13, 0, tile(2) + 13, 15, rgb(110, 76, 24))
    sh.rect(tile(2) + 6, 6, tile(2) + 9, 10, rgb(240, 200, 60))
    sh.rect(tile(2) + 7, 7, tile(2) + 8, 8, rgb(40, 30, 10))
    # 3 key (on floor)
    for y in range(16):
        for x in range(16):
            sh.px[y][tile(3) + x] = sh.px[y][tile(0) + x]
    gold = rgb(250, 210, 60)
    sh.rect(tile(3) + 3, 5, tile(3) + 6, 8, gold)
    sh.rect(tile(3) + 4, 6, tile(3) + 5, 7, rgb(80, 80, 96))
    sh.rect(tile(3) + 7, 6, tile(3) + 12, 7, gold)
    sh.rect(tile(3) + 11, 8, tile(3) + 12, 10, gold)
    sh.rect(tile(3) + 9, 8, tile(3) + 9, 9, gold)
    # 4 exit pad
    for y in range(16):
        for x in range(16):
            sh.px[y][tile(4) + x] = sh.px[y][tile(0) + x]
    g1, g2 = rgb(70, 220, 110), rgb(30, 130, 70)
    sh.rect(tile(4) + 1, 1, tile(4) + 14, 14, g2)
    sh.rect(tile(4) + 2, 2, tile(4) + 13, 13, g1)
    sh.rect(tile(4) + 6, 4, tile(4) + 9, 11, g2)
    sh.rect(tile(4) + 4, 6, tile(4) + 11, 9, g2)
    # 5 key icon for HUD is same as 3 minus floor -> use transparent bg
    for y in range(16):
        for x in range(16):
            px = sh.px[y][tile(3) + x]
            sh.px[y][tile(5) + x] = px if px in (gold, rgb(80, 80, 96)) else T
    return sh


def icon():
    c = Canvas(24, 24)
    for y in range(24):
        for x in range(24):
            c.px[y][x] = rgb(40, 32, 70)
    ch = character(MONA, "down", 0)
    for y in range(16):
        for x in range(16):
            if ch.px[y][x]:
                c.px[y + 6][x + 4] = ch.px[y][x]
    # cone
    for i in range(6):
        c.rect(14 - i, 1 + i, 22, 1 + i, rgb(255, 230, 90)) if False else None
    c.rect(19, 3, 21, 3, rgb(255, 80, 80))
    c.rect(20, 4, 20, 6, rgb(255, 80, 80))
    c.rect(20, 8, 20, 8, rgb(255, 80, 80))
    return c


if __name__ == "__main__":
    out = sys.argv[1]
    s = sheet(MONA)
    png(out + "/mona.png", 48, 48, s.px)
    s = sheet(GUARD)
    png(out + "/guard.png", 48, 48, s.px)
    t = tiles()
    png(out + "/tiles.png", t.w, t.h, t.px)
    i = icon()
    png(out + "/../icon.png", 24, 24, i.px)
    print("ok")
