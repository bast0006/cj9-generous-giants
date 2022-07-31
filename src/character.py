from random import randint

import pygame

from sprites import ImportantSprites


class Character(pygame.sprite.Sprite):
    """
    Class for player and NPC characters.

    Tracks character stats, inventory, etc.  Stats are generated randomly, but later can be passed from
    character creation process if desired.
    Base stats:  strength, vitality, intelligene, dexterity
    Derived stats:  health, health regen rate, mana, mana regen rate, base armor, damage multiplier
    """

    REGEN_INTERVAL = 1.0  # health/mana regen interval in seconds
    STAT_MAX = 18  # as if rolling 3d6 for stats

    def __init__(
        self,
        spawn_position: tuple = (0, 0),
        character_index: int = 1,
        x: int = 0,
        y: int = 0,
        dx: float = 0,
        dy: float = 0,
        strength: int = None,
        vitality: int = None,
        intel: int = None,
        dexterity: int = None,
        movement_speed: int = 5,
        regen: int = 1.5,
        items: list = []
    ) -> None:
        """
        Character initialization.  Generates random base stats if not provided upon creating the class instance.

        Base stats should be integers between 3 and 18 (3d6).
        """
        self.__x = x
        self.__y = y
        self.__dx = dx
        self.__dy = dy
        self.__strength = self.roll_stat(strength)
        self.__vitality = self.roll_stat(vitality)
        self.__intel = self.roll_stat(intel)
        self.__dexterity = self.roll_stat(dexterity)
        self.__items = items
        self.update_derived_stats()
        self._regen = True  # Health and mana regeneration are on by default
        self.regen_speed = regen

        self.sprites = ImportantSprites()
        self.image = self.sprites.get_character1()
        self.rect = self.image.get_rect(topleft=spawn_position)
        self.direction = pygame.math.Vector2()
        self.character_index = character_index
        self.movement_speed = movement_speed

    def input(self) -> None:
        """
        Input handler

        handles the key event
        """
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            self.direction.y = -1
        elif keys[pygame.K_s]:
            self.direction.y = 1
        else:
            self.direction.y = 0

        if keys[pygame.K_a]:
            self.direction.x = -1
        elif keys[pygame.K_d]:
            self.direction.x = 1
        else:
            self.direction.x = 0

    def move(self, speed: int):
        """
        Manages the move

        It moves the sprite to certain direction based on key input and speed
        """
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()
        self.rect.center += self.direction * speed

    def update(self, screen: pygame.Surface, _) -> None:
        """
        Update character stats and position.

        Parameter dt is elapsed time since last update, in seconds.
        Returns True if health <= 0
        """
        self.regen(self.regen_speed)

        self.input()
        self.move(self.movement_speed)
        screen.blit(self.image, self.rect, (self.character_index * 1,
                                            self.character_index * 1,
                                            16, 16))
        return [self.rect]

    def __str__(self):
        char_info = f"""
            x {self.x} y {self.y}
            str {self.strength} vit {self.vitality} int {self.intel} dex {self.dexterity}
            health {self.health} health regen {self.health_regen}
            mana {self.mana} mana regen {self.mana_regen}
            armor {self.armor} damage mult {self.damage_multiplier}
            regen state {self._regen}
            items {self.items}
        """
        return char_info

    def roll_stat(self, stat: int) -> int:
        """Rolls 3d6 stat value if none is provided"""
        return stat if stat is not None else randint(1, 6) + randint(1, 6) + randint(1, 6)

    @property
    def x(self) -> int:
        """Returns x coordinate as integer"""
        return int(self.__x)

    @x.setter
    def x(self, value: int) -> None:
        """Set x coordinate"""
        self.__x = value

    @property
    def y(self) -> int:
        """Returns y coordinate as integer"""
        return int(self.__y)

    @y.setter
    def y(self, value: int) -> None:
        """Set y coordinate"""
        self.__y = value

    @property
    def dx(self) -> float:
        """Returns dx"""
        return self.__dx

    @dx.setter
    def dx(self, value: float) -> None:
        """Set dx"""
        self.__dx = value

    @property
    def dy(self) -> float:
        """Returns dy"""
        return self.__dy

    @dy.setter
    def dy(self, value: float) -> None:
        """Set dy"""
        self.__dy = value

    @property
    def strength(self) -> int:
        """Returns strength"""
        return self.__strength

    @strength.setter
    def strength(self, value: int) -> None:
        """Sets strength"""
        self.__strength = value
        self.update_derived_stats()

    @property
    def vitality(self) -> int:
        """Returns vitality"""
        return self.__vitality

    @vitality.setter
    def vitality(self, value: int) -> None:
        """Sets vitality"""
        self.__vitality = value
        self.update_derived_stats()

    @property
    def intel(self) -> int:
        """Returns intelligence"""
        return self.__intel

    @intel.setter
    def intel(self, value: int) -> None:
        """Sets intelligence"""
        self.__intel = value
        self.update_derived_stats()

    @property
    def dexterity(self) -> int:
        """Returns dexterity"""
        return self.__dexterity

    @dexterity.setter
    def dexterity(self, value: int) -> None:
        """Sets dexterity"""
        self.__dexterity = value
        self.update_derived_stats()

    @property
    def items(self) -> list:
        """Returns list of character's items"""
        return self.__items

    def add_item(self, item: object) -> bool:
        """Adds item to player inventory if not already there, returns True if added, False if already there"""
        if item not in self.items:
            self.items.append(item)
            return True
        return False

    def remove_item(self, item: object) -> bool:
        """Removes item from player inventory, returns True if successful, False if item not in inventory"""
        if item in self.items:
            self.items.remove(item)
            return True
        return False

    def update_derived_stats(self) -> None:
        """
        Generate derived stats based on base stats.

        Health float 50-100, mana float 50-100, regen float 1-3, armor float 0-10, damage multiplier float 0-1
        """
        self.health = 50 + 50 * (self.strength / self.STAT_MAX * self.vitality / self.STAT_MAX)
        self.base_health = self.health
        self.health_regen = 1 + self.strength / self.STAT_MAX + self.vitality / self.STAT_MAX
        self.mana = 50 + 50 * (self.intel / self.STAT_MAX * self.vitality / self.STAT_MAX)
        self.base_mana = self.mana
        self.mana_regen = 1 + self.intel / self.STAT_MAX + self.vitality / self.STAT_MAX
        self.armor = 10 * (self.strength / self.STAT_MAX * self.dexterity / self.STAT_MAX)
        self.base_armor = self.armor
        self.damage_multiplier = 1 + self.strength / self.STAT_MAX * self.intel / self.STAT_MAX

    def toggle_regen(self, state: bool = None) -> None:
        """Turns regeneration on or off (True/False), or toggles current value with no parameter"""
        self._regen = not self._regen if state is None else state

    def regen(self, dt: float) -> None:
        """Update health and mana if regen is active"""
        if self._regen:
            self.health = min(self.health + dt * self.health_regen, self.base_health)
            self.mana = min(self.mana + dt * self.mana_regen, self.base_mana)
