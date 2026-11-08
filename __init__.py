import os
import sys

APP_DIR = "/system/apps/metal_mona"
os.chdir(APP_DIR)
sys.path.insert(0, APP_DIR)

from badgeware import State
from level import Level, TILE, DOOR, KEY, EXIT, FLOOR
from player import Player
from guard import Guard
import level as level_data

TITLE, PLAY, CAUGHT, WIN = range(4)

BG = color.rgb(20, 14, 36)
WHITE = color.rgb(255, 255, 255)
YELLOW = color.rgb(255, 225, 90)
RED = color.rgb(255, 70, 70)

tiles = image.load("assets/tiles.png").spritesheet(6, 1)
mona_sprites = image.load("assets/mona.png").spritesheet(3, 3)
guard_sprites = image.load("assets/guard.png").spritesheet(3, 3)

big_font = font.ziplock
small_font = font.nope

save = {"best": 0}
State.load("metal_mona", save)

level = Level()
player = Player(mona_sprites)
guards = []

mode = TITLE
has_key = False
elapsed = 0.0
spotted_by = None
new_best = False
mode_time = 0


def shadow_text(text, x, y, pen=WHITE):
    screen.pen = color.rgb(0, 0, 0, 160)
    screen.text(text, x + 1, y + 1)
    screen.pen = pen
    screen.text(text, x, y)


def center_text(text, y, pen=WHITE):
    w, _ = screen.measure_text(text)
    shadow_text(text, (screen.width - w) / 2, y, pen)


def start_level():
    global mode, has_key, elapsed, spotted_by, mode_time
    level.reset()
    player.reset(*level.start)
    guards.clear()
    for waypoints in level_data.PATROLS:
        guards.append(Guard(guard_sprites, waypoints))
    has_key = False
    elapsed = 0.0
    spotted_by = None
    mode = PLAY
    mode_time = badge.ticks


def camera():
    cx = player.cx - screen.width / 2
    cy = player.cy - screen.height / 2
    cx = max(0, min(level.width - screen.width, cx))
    cy = max(0, min(level.height - screen.height, cy))
    return int(cx), int(cy)


def draw_world(cam_x, cam_y, alerted=None):
    screen.pen = BG
    screen.rectangle(screen.clip)
    tx0 = cam_x // TILE
    ty0 = cam_y // TILE
    tx1 = (cam_x + screen.width) // TILE + 1
    ty1 = (cam_y + screen.height) // TILE + 1
    for ty in range(ty0, ty1 + 1):
        for tx in range(tx0, tx1 + 1):
            if 0 <= tx < level.cols and 0 <= ty < level.rows:
                screen.blit(tiles.sprite(level.tiles[ty][tx], 0),
                            vec2(tx * TILE - cam_x, ty * TILE - cam_y))
    for g in guards:
        g.draw_cone(cam_x, cam_y, g is alerted)
    # Draw back-to-front so sprites overlap correctly.
    actors = [(g.y, g) for g in guards] + [(player.y, player)]
    actors.sort(key=lambda a: a[0])
    for _, a in actors:
        a.draw(cam_x, cam_y)
    if alerted:
        shadow_text("!", alerted.x - cam_x + 6, alerted.y - cam_y - 10, RED)


def draw_hud():
    screen.font = small_font
    shadow_text("%.1f" % elapsed, 3, 2)
    if has_key:
        screen.blit(tiles.sprite(5, 0), vec2(screen.width - 18, 0))


def update_play(dt):
    global has_key, elapsed, mode, spotted_by, new_best, mode_time
    elapsed += dt

    if badge.pressed(BUTTON_BACK):
        start_level()
        return

    dx = (1 if badge.held(BUTTON_RIGHT) else 0) - (1 if badge.held(BUTTON_LEFT) else 0)
    dy = (1 if badge.held(BUTTON_DOWN) else 0) - (1 if badge.held(BUTTON_UP) else 0)
    player.update(level, dx, dy, dt)

    # Doors open when Mona walks into them carrying the key.
    if has_key and player.moving:
        px, py = player.probe()
        tx, ty = int(px // TILE), int(py // TILE)
        if level.tile_at(tx, ty) == DOOR:
            level.set_tile(tx, ty, FLOOR)
            has_key = False

    # Key and exit pickups use the tile under Mona's center.
    tx, ty = int(player.cx // TILE), int(player.cy // TILE)
    t = level.tile_at(tx, ty)
    if t == KEY:
        level.set_tile(tx, ty, FLOOR)
        has_key = True
    elif t == EXIT:
        mode = WIN
        mode_time = badge.ticks
        best = save["best"]
        new_best = best == 0 or elapsed < best
        if new_best:
            save["best"] = round(elapsed, 1)
            State.save("metal_mona", save)
        return

    for g in guards:
        g.update(dt)
        g.build_cone(level)
    for g in guards:
        if g.sees(level, player.cx, player.cy):
            spotted_by = g
            mode = CAUGHT
            mode_time = badge.ticks
            return


def play():
    dt = min(badge.ticks_delta, 50) / 1000
    update_play(dt)
    cam_x, cam_y = camera()
    draw_world(cam_x, cam_y, spotted_by if mode == CAUGHT else None)
    draw_hud()


def title():
    screen.pen = BG
    screen.rectangle(screen.clip)
    # Slowly pulsing spotlight cone behind the title character.
    sway = 0.5 + 0.5 * ((badge.ticks % 2000) / 1000 - 1) ** 2
    screen.pen = color.rgb(255, 235, 90, int(30 + 30 * sway))
    screen.shape(shape.custom([vec2(80, 6), vec2(30, 118), vec2(130, 118)]))
    frame = 1 + int(badge.ticks / 200) % 2
    screen.blit(mona_sprites.sprite(frame, 0), rect(64, 56, 32, 32))
    screen.font = big_font
    center_text("METAL MONA", 14, YELLOW)
    screen.font = small_font
    if int(badge.ticks / 500) % 2:
        center_text("Press SELECT", 94)
    if save["best"]:
        center_text("Best %.1fs" % save["best"], 106)
    if badge.pressed(BUTTON_SELECT):
        start_level()


def end_screen(heading, pen):
    cam_x, cam_y = camera()
    draw_world(cam_x, cam_y, spotted_by if mode == CAUGHT else None)
    screen.pen = color.rgb(0, 0, 0, 150)
    screen.rectangle(rect(0, 28, screen.width, 64))
    screen.font = big_font
    center_text(heading, 34, pen)
    screen.font = small_font


def caught():
    end_screen("SPOTTED!", RED)
    center_text("SELECT to retry", 72)
    if badge.ticks - mode_time > 400 and badge.pressed(BUTTON_SELECT):
        start_level()


def win():
    end_screen("MISSION CLEAR", YELLOW)
    line = "Time %.1fs" % elapsed
    if new_best:
        line += "  NEW BEST!"
    center_text(line, 62)
    center_text("SELECT to play again", 74)
    if badge.ticks - mode_time > 400 and badge.pressed(BUTTON_SELECT):
        start_level()


def update():
    if mode == TITLE:
        title()
    elif mode == PLAY:
        play()
    elif mode == CAUGHT:
        caught()
    else:
        win()


run(update)
