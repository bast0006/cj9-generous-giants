from datetime import datetime
from enum import Enum
from typing import Tuple

import noise
import numpy as np
import pygame


class mapGen:
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
        self.seed = seed or int(str(datetime.now().time().microsecond)[:-4])
        self.shape = shape
        self.freq = freq
        self.world = np.zeros(self.shape)
        self.amplitude = amplitude
        self.resolution = resolution

    def __str__(self) -> str:
        return "\n".join(
            ("".join("{:.0f}".format(j) for j in i) for i in mapGenerator.world)
        )

    def generateNoise(self):
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

    def convert(self):
        """Convert to ints

        0 = Flower
        1 = Water
        2 = Grass

        Take anything past 1/2 of the way between mean and max and convert to 0
        Take anything past 1/2 of the way between mean and min and convert to 1
        Make the rest of the map 2
        """
        flowerLevel = ((self.world.max() - self.world.mean()) * 0.65) + self.world.mean()
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

    def _makeMap(self):
        """Make a new map."""
        self.generateNoise()
        self.convert()

    def newMap(self, seed: int = None):
        """Generate a new map."""
        self.seed = seed or int(str(datetime.now().time().microsecond)[:-4])
        print(self.seed)

        self._makeMap()


class mapLegend(Enum):
    """Enum for the map file's notation."""

    WATER = "W"
    GRASS = "G"
    FLOWER = "F"


class mapSprite:
    """Sprite for the map.

    It has a position and a sprite.
    It can be drawn to the screen.
    """

    def __init__(self, mapFileDir):
        self.registerNewMap(mapFileDir)

    def update(self, screen: pygame.Surface, _):
        """Draw the map out on the screen"""
        rects = []
        for indexY, row in enumerate(self._map):
            for indexX, collum in enumerate(row):
                rects.append(
                    pygame.draw.rect(
                        screen,
                        self.getKeyColor(collum),
                        (16 * indexY, 16 * indexX, 16, 16),
                    )
                )
        return rects

    def getKeyColor(self, key: mapLegend) -> pygame.Color:
        """Get the color of a key."""
        color = pygame.Color(0, 0, 0)
        match key:
            case mapLegend.WATER.value:
                color.b = 184
                color.g = 94
            case mapLegend.GRASS.value:
                color.g = 55
                color.r = 13
                color.b = 13
            case mapLegend.FLOWER.value:
                color.r = 255
                color.g = 3
                color.b = 62

        return color

    def registerNewMap(self, mapFileDir: str):
        """Change the map being used."""
        with open(mapFileDir, "r") as f:
            self._map = list(list(i) for i in (f.read().split("\n")))


if __name__ == "__main__":
    from os import remove

    from game import Game

    width = 100
    heigth = 100
    mapGenerator = mapGen((heigth, width))
    print(f"Map generator initialized for a {heigth}x{width} map.\n")

    mapGenerator.generateNoise()
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

    sprite = mapSprite(exportDir)
    print("\n\n" + str(sprite._map))

    game = Game()
    game.add_sprite(0, sprite)

    def newMap(evt: pygame.event.Event):
        """Render a new map when r is pressed."""
        if evt.key == pygame.K_r:
            mapGenerator.newMap()
            print(f"\n\n {mapGenerator}")
            mapGenerator.export(exportDir)
            sprite.registerNewMap(exportDir)

    game.add_handler(
        newMap,
        pygame.KEYDOWN,
    )
    game.start()

    remove(exportDir)
    print(f"\n{exportDir} removed\n")
