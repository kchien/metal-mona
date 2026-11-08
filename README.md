# Metal Mona

Sneak Mona past patrolling guards, grab the key and reach the exit in this top-down stealth game.

## Usage

- **D-pad**: move Mona.
- **Select**: start, retry after being spotted, or advance to the next level after clearing a mission. Levels play in order and loop back to level 1 after the last.
- **Back**: restart the level.

Stay out of the yellow vision cones. Walls block a guard's view, so use them for cover. Pick up the key, walk into the locked door to open it, then step onto the green pad to finish. Your best time for each level is saved on the badge.

## Installing on the badge

This repo is the app folder itself. Copy its contents into `/system/apps/metal_mona/` on a Universe 2026 badge (see the badge's `hardware/USB_SERIAL.md` for the USB mass-storage steps), or open the folder in the Badge Simulator as `apps/metal_mona`.

## Regenerating the art

The sprites are generated with a dependency-free script: `python3 tools/gen_art.py assets` rewrites `assets/*.png` and `icon.png`.

## Adding levels

Append a `{"map": [...], "patrols": [...]}` entry to `LEVELS` in `level.py`. Each map needs one each of `S`, `K`, `D`, `E`, a wall border, and must only be solvable through the door.

## Tests

`python3 -m unittest discover -s tests` checks level data (including solvability) and progression logic. The tests need only CPython.
