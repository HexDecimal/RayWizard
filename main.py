#!/usr/bin/env python3
import tcod


def main() -> None:
    """Main entrypoint."""
    tileset = tcod.tileset.load_tilesheet(
        "Alloy_curses_12x12.png", 16, 16, tcod.tileset.CHARMAP_CP437
    )
    console = tcod.console.Console(1280 // 12, 720 // 12, order="C")
    with tcod.context.new(width=1280, height=720, tileset=tileset) as context:
        while True:
            console.print(0, 0, "Hello World")
            context.present(console, integer_scaling=True)
            for event in tcod.event.wait():
                if isinstance(event, tcod.event.Quit):
                    raise SystemExit()


if __name__ == "__main__":
    main()
