import pygame


class SpriteSheet:
    """Class for loading and parsing spritesheets."""

    def __init__(self, filename):
        """Load the spritesheet."""
        self.sheet = pygame.image.load(filename).convert()

    def image_at(self, rectangle):
        """Load a single image from the spritesheet.

        rectangle: (x, y, x + offset, y + offset)
        """
        x, y, x1, y1 = rectangle
        rect = pygame.Rect(x, y, x1-x, y1-y)
        image = pygame.Surface(rect.size).convert_alpha()
        image.blit(self.sheet, (0, 0), rect)
        return image


class ImportantSprites:
    """Class including some important sprites

    Note all sprits are 1x1 tile (16x16 pixels)
    """

    def __init__(self) -> None:
        self._miniRougelike = SpriteSheet("sprites/colored_tilemap.png")
        self._modernCity = SpriteSheet("sprites/roguelikeSheet_transparent.png")

    def get_flowers(self) -> pygame.Surface:
        """Get the image for flowers"""
        x = (16 * 3) + 3
        y = (16 * 7) + 7
        return self._modernCity.image_at((x, y, x + 16, y + 16))

    def get_water(self) -> pygame.Surface:
        """Get the image for water"""
        x = (16 * 3) + 3
        y = (16 * 1) + 1
        return self._modernCity.image_at((x, y, x + 16, y + 16))

    def get_grass(self) -> pygame.Surface:
        """Get the image for grass"""
        x = (16 * 3) + 3
        y = (16 * 16) + 16
        return self._modernCity.image_at((x, y, x + 16, y + 16))

    def get_potion(self) -> pygame.Surface:
        """Get the image of a potion"""
        x = (8 * 7) + 7
        y = (8 * 8) + 8
        return pygame.transform.scale2x(
            (self._miniRougelike.image_at((x, y, x + 8, y + 8)))
        )

    def get_sword(self) -> pygame.Surface:
        """Get the image of a sword"""
        x = (8 * 6) + 6
        y = (8 * 4) + 4
        return pygame.transform.scale2x(
            (self._miniRougelike.image_at((x, y, x + 8, y + 8)))
        )

    def get_axe(self) -> pygame.Surface:
        """Get the image of an axe"""
        x = (8 * 7) + 7
        y = (8 * 4) + 4
        return pygame.transform.scale2x(
            (self._miniRougelike.image_at((x, y, x + 8, y + 8)))
        )

    def get_crossbow(self) -> pygame.Surface:
        """Get the image of a crossbow"""
        x = (8 * 8) + 8
        y = (8 * 4) + 4
        return pygame.transform.scale2x(
            (self._miniRougelike.image_at((x, y, x + 8, y + 8)))
        )

    def get_arrow(self) -> pygame.Surface:
        """Get the image of an arrow"""
        x = (8 * 9) + 9
        y = (8 * 4) + 4
        return pygame.transform.scale2x(
            (self._miniRougelike.image_at((x, y, x + 8, y + 8)))
        )

    def get_trident(self) -> pygame.Surface:
        """Get the image of a trident"""
        x = (8 * 10) + 10
        y = (8 * 4) + 4
        return pygame.transform.scale2x(
            (self._miniRougelike.image_at((x, y, x + 8, y + 8)))
        )

    def get_club(self) -> pygame.Surface:
        """Get the image of a club"""
        x = (8 * 10) + 10
        y = (8 * 3) + 3
        return pygame.transform.scale2x(
            (self._miniRougelike.image_at((x, y, x + 8, y + 8)))
        )

    def get_chest(self) -> pygame.Surface:
        """Get the image of a chest"""
        x = (8 * 9) + 9
        y = (8 * 3) + 3
        return pygame.transform.scale2x(
            (self._miniRougelike.image_at((x, y, x + 8, y + 8)))
        )

    def get_empty_heart(self) -> pygame.Surface:
        """Get the image of an empty heart"""
        x = (8 * 7) + 7
        y = (8 * 5) + 5
        return pygame.transform.scale2x(
            (self._miniRougelike.image_at((x, y, x + 8, y + 8)))
        )

    def get_half_heart(self) -> pygame.Surface:
        """Get the image of a half heart"""
        x = (8 * 8) + 8
        y = (8 * 5) + 5
        return pygame.transform.scale2x(
            (self._miniRougelike.image_at((x, y, x + 8, y + 8)))
        )

    def get_full_heart(self) -> pygame.Surface:
        """Get the image of a full heart"""
        x = (8 * 9) + 9
        y = (8 * 5) + 5
        return pygame.transform.scale2x(
            (self._miniRougelike.image_at((x, y, x + 8, y + 8)))
        )

    def get_character1(self) -> pygame.Surface:
        """Get the image of a character"""
        x = (8 * 4) + 4
        y = 0
        return pygame.transform.scale2x(
            (self._miniRougelike.image_at((x, y, x + 8, y + 8)))
        )

    def get_character2(self) -> pygame.Surface:
        """Get the image of a character"""
        x = (8 * 5) + 5
        y = 0
        return pygame.transform.scale2x(
            (self._miniRougelike.image_at((x, y, x + 8, y + 8)))
        )

    def get_character3(self) -> pygame.Surface:
        """Get the image of a character"""
        x = (8 * 6) + 6
        y = 0
        return pygame.transform.scale2x(
            (self._miniRougelike.image_at((x, y, x + 8, y + 8)))
        )

    def get_character4(self) -> pygame.Surface:
        """Get the image of a character"""
        x = (8 * 7) + 7
        y = 0
        return pygame.transform.scale2x(
            (self._miniRougelike.image_at((x, y, x + 8, y + 8)))
        )

    def get_character5(self) -> pygame.Surface:
        """Get the image of a character"""
        x = (8 * 10) + 10
        y = 0
        return pygame.transform.scale2x(
            (self._miniRougelike.image_at((x, y, x + 8, y + 8)))
        )

    def get_character6(self) -> pygame.Surface:
        """Get the image of a character"""
        x = (8 * 11) + 11
        y = 0
        return pygame.transform.scale2x(
            (self._miniRougelike.image_at((x, y, x + 8, y + 8)))
        )
