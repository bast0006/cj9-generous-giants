import random
from typing import Tuple

import noise
import numpy as np


class mapGen:
    """Generator for a map for the game to use.

    It first creates a noise map.
    It then uses this noise map to determine flower / water placement.
    It then can export the map to a text file
    """

    def __init__(self, shape: Tuple[int, int], seed: int = None):
        self.seed = seed
        random.seed(self.seed)
        self.shape = shape
        self.octaves = (random.random() * 0.5) + 0.5
        self.freq = 16 * self.octaves
        self.persistence = 0.5
        self.lacunarity = 2.0
        self.world = np.zeros(self.shape)

    def __str__(self) -> str:
        return "\n".join(
            ("".join("{:.0f}".format(j) for j in i) for i in mapGenerator.world)
        )

    def generateNoise(self):
        """Generates a noise map."""
        for i in range(self.shape[0]):
            for j in range(self.shape[1]):
                n = (
                    noise.pnoise2(
                        i / self.freq,
                        j / self.freq,
                    )
                    * 10
                    + 3
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
        flowerLevel = ((self.world.max() - self.world.mean()) * 0.5) + self.world.mean()
        waterLevel = ((self.world.min() - self.world.mean()) * 0.5) + self.world.mean()

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


if __name__ == "__main__":
    from os import remove

    width = 100
    heigth = 30
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

    remove(exportDir)
    print(f"\n{exportDir} removed\n")
