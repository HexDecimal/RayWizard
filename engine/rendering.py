from __future__ import annotations

import tcod

import g

UI_SIZE = (12, 12)  # Area reserved for the UI.


def render_main(console: tcod.console.Console) -> None:
    """Rendeer the main view.  With the world tiles, any objects, and the UI."""
    # Render world tiles.
    map_ = g.world.map
    console_shape = (console.width - UI_SIZE[0], console.height - UI_SIZE[1])
    console.tiles_rgb[: console_shape[0], : console_shape[1]] = ord(" "), 0x40, 0x00  # Clear world area.
    screen_view, world_view = map_.camera.get_views((map_.width, map_.height), console_shape)
    console.tiles_rgb[screen_view] = g.world.map.tiles["dark"][world_view]

    # Render all actors.
    cam_x, cam_y = map_.camera.get_left_top_pos(console_shape)
    for actor in g.world.map.actors:
        x = actor.x - cam_x
        y = actor.y - cam_y
        if 0 <= x < console_shape[0] and 0 <= y < console_shape[1]:
            console.print(x, y, actor.ch, fg=actor.fg)
