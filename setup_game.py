import tcod

from engine.state import State  # Import-time requirement, so `from x import Y` is used.
import engine.save
import engine.world
import g
import procgen.dungeon

# Load the background image and remove the alpha channel.
background_image = tcod.image.load("menu_background.png")[:, :, :3]


class MainMenu(State):
    """Handle the main menu rendering and input."""

    # Handles the input options and maps them on the menu to functions.
    def __init__(self) -> None:
        super().__init__()
        self.cursor = 0
        self.menu = (
            ("Play a new game", self.playNew),
            ("Continue last game", self.load),
            ("Quit", self.quit),
        )

    # draws the UI elements.
    def on_draw(self, console: tcod.Console) -> None:
        """Render the main menu on a background image."""
        console.draw_semigraphics(background_image, 0, 0)

        console.print(
            console.width // 2,
            console.height // 2 - 4,
            "RayWizard",
            fg=(255, 255, 63),
            alignment=tcod.CENTER,
        )

        # menu_width = 100
        """
        for i, text in enumerate(
            [
                " ____,   ____, _  _,  _   _, __,   ___,    ____, ____,  ____,  ",
                "(-|__)  (-/_| (-\_/  (-|  | (-|   (- /    (-/_| (-|__) (-|  \  ",
                " _|  \, _/  |,  _|,   _|/\|, _|_,  _/__,  _/  |, _|  \, _|__/  ",
                "(      (       (     (      (     (      (      (      (       ",
            ]
        ):
            console.print(
                console.width // 2,
                console.height // 2 - 2 + i,
                text,
                fg=(255, 255, 63),
                # bg=(0, 0, 0),
                alignment=tcod.CENTER,
                bg_blend=tcod.BKGND_ALPHA(64),
            )
        """

        console.print(
            console.width // 2,
            console.height - 2,
            "By (High Tyrol and HexDecimal)",
            fg=(255, 255, 63),
            alignment=tcod.CENTER,
        )

        menu_width = 24
        for i, text in enumerate(["Play a new game", "Continue last game", "Quit"]):
            console.print(
                console.width // 2,
                console.height // 2 - 2 + i,
                text.ljust(menu_width),
                fg=(255, 255, 255),
                # bg=(0, 0, 0),
                alignment=tcod.CENTER,
                bg_blend=tcod.BKGND_ALPHA(64),
            )

        # states.InGame
        return None

    def cmd_move(self, x: int, y: int) -> None:
        if x:
            return
        self.cursor = (self.cursor + y) % len(self.menu)
        if y == 0:
            self.cmd_confirm()

    def cmd_confirm(self) -> None:
        self.menu[self.cursor][1]()

    def quit(self) -> None:
        raise SystemExit()

    def playNew(self) -> None:
        level = 1
        g.world = engine.world.World()
        g.world.map = procgen.dungeon.generate(g.world, level=level)
        g.states.pop()

    def load(self) -> None:
        engine.save.load()
        # Add code to return a number if it doesn't load.
        # then put an if statement that runs playNew() if the wrong thing is returned
