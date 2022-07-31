from datetime import datetime
from enum import Enum
from typing import Tuple

import noise
import numpy as np
import pygame

from character import Character
from sprites import ImportantSprites


class MapGen:
    """Generator for a map for the game to use.

    It first creates a noise map.
    It then uses this noise map to determine flower / water placement.
    It then can export the map to a text file
    """

    def __init__(
        self,
        shape: Tuple[int, int],
        seed: int = None,
        freq: int = 3,
        amplitude: int = 10,
        resolution: int = 50,
    ):
        """Initalizes all the important variables for map generation

        Args:
            shape (Tuple[int, int]): This determines the size of the map.
            seed (int, optional): This is the seed the map is generated based on. Defaults to None.
            freq (int, optional): This will ajust how often peaks and troughs show up. Defaults to 3.
            amplitude (int, optional): This will ajust the severity of said peaks and troughs. Defaults to 10.
            resolution (int, optional): This controls the "zoom" of map
            so a higher number will make bodies larger and a lower will do the inverse. Defaults to 50.
        """
        self.seed = seed or self._seed_generator()
        self.shape = shape
        self.freq = freq
        self.world = np.zeros(self.shape)
        self.amplitude = amplitude
        self.resolution = resolution

    def __str__(self) -> str:
        return "\n".join(
            ("".join("{:.0f}".format(j) for j in i) for i in self.world)
        )

    def generate_noise(self):
        """Generates a noise map."""
        for i in range(self.shape[0]):
            for j in range(self.shape[1]):
                n = (
                    noise.pnoise3(
                        i / self.resolution * self.freq,
                        j / self.resolution * self.freq,
                        self.seed / self.resolution * self.freq,
                    )
                    * self.amplitude
                )

                self.world[i][j] = n

    def _string_hashcode(self, s):
        h = 0
        for c in s:
            h = (31 * h + ord(c)) & 0xFFFFFFFF
        return ((h + 0x80000000) & 0xFFFFFFFF) - 0x80000000

    def _seed_generator(self):
        microsecond = str(datetime.now().time().microsecond)
        return int(self._string_hashcode(microsecond))

    def convert(self):
        """Convert to ints

        0 = Flower
        1 = Water
        2 = Grass

        Take anything past 1/2 of the way between mean and max and convert to 0
        Take anything past 1/2 of the way between mean and min and convert to 1
        Make the rest of the map 2
        """
        flowerLevel = (
            (self.world.max() - self.world.mean()) * 0.65
        ) + self.world.mean()
        waterLevel = ((self.world.min() - self.world.mean()) * 0.65) + self.world.mean()

        for i in range(self.shape[0]):
            for j in range(self.shape[1]):
                if self.world[i][j] > flowerLevel:
                    self.world[i][j] = 0
                elif self.world[i][j] < waterLevel:
                    self.world[i][j] = 1
                else:
                    self.world[i][j] = 2

    def export(self, filename: str):
        """Export the map to a text file."""
        with open(filename, "w") as f:
            f.write(str(self).replace("0", "F").replace("1", "W").replace("2", "G"))

    def export_to_string(self) -> str:
        """Export the map as a single-line string."""
        return str(self).replace("0", "F").replace("1", "W").replace("2", "G").replace("\n", "|")

    def _make_map(self):
        """Make a new map."""
        self.generate_noise()
        self.convert()

    def new_map(self, seed: int = None):
        """Generate a new map."""
        self.seed = seed or self._seed_generator()

        self._make_map()


class MapLegend(Enum):
    """Enum for the map file's notation."""

    WATER = "W"
    GRASS = "G"
    FLOWER = "F"


class MapSprite:
    """Sprite for the map.

    It has a position and a sprite.
    It can be drawn to the screen.
    """

    def __init__(self, mapFileDir):
        if mapFileDir:
            self.register_new_map(mapFileDir)

    def update(self, screen: pygame.Surface, _):
        """Draw the map out on the screen"""
        rects = []

        sprites = ImportantSprites()

        map_sprites = {
            MapLegend.WATER: sprites.get_water(),
            MapLegend.GRASS: sprites.get_grass(),
            MapLegend.FLOWER: sprites.get_flowers(),
        }

        for indexY, row in enumerate(self._map):
            for indexX, colum in enumerate(row):
                screen.blit(
                    map_sprites[MapLegend(colum)],
                    (16 * indexY, 16 * indexX, 16, 16),
                )
                rects.append(
                    pygame.Rect(
                        (16 * indexY, 16 * indexX, 16, 16),
                    )
                )
        return rects

    def get_key_color(self, key: MapLegend) -> pygame.Color:
        """Get the color of a key."""
        color = pygame.Color(0, 0, 0)
        match key:
            case MapLegend.WATER.value:
                color.b = 184
                color.g = 94
            case MapLegend.GRASS.value:
                color.g = 55
                color.r = 13
                color.b = 13
            case MapLegend.FLOWER.value:
                color.r = 255
                color.g = 3
                color.b = 62

        return color

    def register_new_map(self, mapFileDir: str):
        """Change the map being used."""
        with open(mapFileDir, "r") as f:
            self._map = list(list(i) for i in (f.read().split("\n")))

    def register_from_string(self, map_data: str):
        """Change the map being used to one provided as string data."""
        self._map = list(list(i) for i in (map_data.split("|")))


if __name__ == "__main__":
    from os import remove

    from game import Game

    width = 100
    heigth = 100
    mapGenerator = MapGen((heigth, width))
    print(f"Map generator initialized for a {heigth}x{width} map.\n")

    mapGenerator.generate_noise()
    print("Noise map generated.\n")
    print(
        "| "
        + " | \n| ".join(
            (" | ".join("{:.2f}".format(j) for j in i) for i in mapGenerator.world)
        )
        + " |\n"
    )

    mapGenerator.convert()
    print("noise map converted\n")
    print(str(mapGenerator) + "\n")

    exportDir = "./map.txt"
    mapGenerator.export(exportDir)
    print(f"exported to {exportDir}\n")
    with open(exportDir, "r") as f:
        print(f.read())

    sprite = MapSprite(exportDir)
    print("\n\n" + str(sprite._map))

    game = Game()
    game.add_sprite(0, sprite)

    def new_map(evt: pygame.event.Event):
        """Render a new map when r is pressed."""
        if evt.key == pygame.K_r:
            mapGenerator.new_map()
            print(f"\n\n {mapGenerator}")
            mapGenerator.export(exportDir)
            sprite.register_new_map(exportDir)

    game.add_handler(
        new_map,
        pygame.KEYDOWN,
    )

    player1 = Character(spawn_position=(50, 50), movement_speed=3)

    game.add_sprite(1, player1)

    game.start()

    remove(exportDir)
    print(f"\n{exportDir} removed\n")
