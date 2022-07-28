import bisect
from collections import defaultdict

import pygame


class Game:
    """
    A management class that maintains pygame-specific application-wide details

    Such as a sorted sprite render/update list, the mainloop, and event handling.
    """

    running: bool = False
    framerate: int = 60

    def __init__(self):
        if not pygame.get_init():
            pygame.init()

        self.screen = pygame.display.set_mode(self.get_nice_display_mode())

        self.event_handlers = defaultdict(list)
        self.sprites = []
        self.add_handler(self.quit_on_esc, pygame.KEYDOWN)

    def get_nice_display_mode(self):
        """
        Select a pleasant, non-fullscreen display mode of reasonable size

        Matches the display aspect ratio.
        Handles dpi awareness issues.
        """
        # Display info is required because .list_modes() returns _native_ modes,
        # matching the display's actual pixel values, however on high dpi systems
        # with scaling set, pygame does not current have a way to indicate that it is
        # high dpi aware, so setting something matching the full display resolution
        # will break unless we do fullscreen. This function is solely for non-fullscreen
        # use, so we carefully select a mode using the nonscaled display resolution.
        display_info = pygame.display.Info()
        native_mode = display_info.current_w, display_info.current_h
        aspect_ratio = native_mode[0] / native_mode[1]
        available_modes = pygame.display.list_modes()

        print(f"{native_mode=} {aspect_ratio=}")
        nice_modes = [(width, height) for width, height in available_modes if ((width/height) - aspect_ratio) < 0.01]
        print(F"{nice_modes=}")

        for mode in nice_modes:
            if mode[0] < 0.7*native_mode[0]:
                print("Selected display mode:", mode)
                return mode

    def add_handler(self, func: callable, *event_types) -> None:
        """Register an event handler, which will be called on all events of a matching type."""
        for event_type in event_types:
            self.event_handlers[event_type].append(func)

    def remove_handler(self, func: callable, *event_types) -> None:
        """Remove an event handler from the given event types so that it will no longer be called."""
        for event_type in event_types:
            self.event_handlers[event_type].remove(func)

    def add_sprite(self, layer: int, sprite: object) -> None:
        """Add a sprite to the game, where it will be rendered and updated each frame."""
        # Hash is used here so sprites are never directly compared.
        # Order shouldn't matter (provided layer ordering is preseved)
        # although python does guarantee consistency.
        bisect.insort(self.sprites, (layer, hash(sprite), sprite))

    def remove_sprite(self, layer: int, sprite: object):
        """Remove a sprite from the game."""
        self.sprites.remove((layer, hash(sprite), sprite))

    def quit_on_esc(self, event: pygame.event.EventType):
        """Exit if the event is an escape keypress."""
        if event.key == pygame.K_ESCAPE:
            self.running = False

    def start(self):
        """Begin the Mainloop, managing framerate, sprites, and window events."""
        self.running = True
        clock = pygame.time.Clock()

        while self.running:
            tick_time = clock.tick(self.framerate) / 1000
            events = pygame.event.get()
            changed_rects = []
            for event in events:
                handlers = self.event_handlers[event.type]
                for handler in handlers:
                    if handler(event):
                        break

                if event.type == pygame.QUIT:
                    self.running = False
                    break

            for layer, _, sprite in self.sprites:
                changed_rects.extend(sprite.update(self.screen, tick_time))

            pygame.display.update(changed_rects)

        pygame.quit()


if __name__ == "__main__":
    print("Testing Game class")
    game = Game()

    class TestSprite:
        """A quick and dirty class used to test basic Game functionality."""

        x, y = 0, 0
        dx, dy = 10, 10

        def update(self, screen: pygame.Surface, dt: float) -> list[pygame.Rect]:
            """Move and redraw our test square on each tick."""
            self.x += self.dx * dt % screen.get_width()
            self.y += self.dy * dt % screen.get_height()

            return [
                pygame.draw.rect(
                    screen,
                    (0xff, 0, 0xff),
                    (int(self.x), int(self.y), 10, 10),
                )
            ]

    sprite = TestSprite()
    game.add_sprite(1, sprite)
    game.add_handler(print, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN)

    game.start()
