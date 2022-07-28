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

    def __init__(self, x: int, y: int, image, scale: int):
        """Initialization

        Creates instance of button class object which then
        gets turned into a rect object for keeping track of
        different points on the surface
        """
        width = image.get_width()

        height = image.get_height()

        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))

        self.rect = self.image.get_rect()

        self.rect.topleft = (x, y)

        self.clicked = False

    def draw(self, target: pygame.Surface) -> list[pygame.Rect]:
        """Draw Method

        This method will draw the button onto the target param
        and return the changed pixels as a list
        """
        return self.image.blit(target, dest=(self.x, self.y))

    def update(self, event_list, redraw=False):
        """Update method

        This method will return True or False based on whether or
        not the button has been clicked.
        """
        mouse_pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(mouse_pos):
            if pygame.mouse.get_pressed()[0]:
                redraw = True
                return redraw
            else:
                return False
