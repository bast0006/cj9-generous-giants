import pygame

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 500

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

pygame.init()


class Button():
    """Creates a button to be drawn on the string

    Initialization takes x and y coordinates as arguments,
    as well as a scale argument for resizing.
    """

    def __init__(self, x, y, image, scale):
        """Initialization

        Creates instance of button class object
        """
        width = image.get_width()

        height = image.get_height()

        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))

        self.rect = self.image.get_rect()

        self.rect.topleft = (x, y)

    def draw(self):
        """Draw Method

        This method will draw the button on the screen
        """
        screen.blit(self.image, (self.rect.x, self.rect.y))
