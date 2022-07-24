from random import randint


class Character:
    """
    Class for player and NPC characters.

    Tracks character stats, inventory, etc.  Stats are generated randomly, but later can be passed from
    character creation process if desired.
    Base stats:  strength, vitality, intelligene, dexterity
    Derived stats:  health, health regen rate, mana, mana regen rate, base armor, damage multiplier
    """

    REGEN_INTERVAL = 1.0  # health/mana regen interval in seconds
    STAT_MAX = 18  # as if rolling 3d6 for stats

    def __init__(self,
                 x: int = 0,
                 y: int = 0,
                 dx: int = 0,
                 dy: int = 0,
                 strength: int = None,
                 vitality: int = None,
                 intel: int = None,
                 dexterity: int = None,
                 items: list = []
                 ):
        """
        Character initialization.  Generates random base stats if not provided upon creating the class instance.

        Base stats should be integers between 3 and 18 (3d6).
        """
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.__strength = self.roll_stat(strength)
        self.__vitality = self.roll_stat(vitality)
        self.__intel = self.roll_stat(intel)
        self.__dexterity = self.roll_stat(dexterity)
        self.__items = items
        self.update_derived_stats()
        self._regen = True  # Health and mana regeneration are on by default

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

    def roll_stat(self, stat):
        """Rolls 3d6 stat value if none is provided"""
        return stat if stat is not None else randint(1, 6) + randint(1, 6) + randint(1, 6)

    @property
    def strength(self):
        """Returns strength"""
        return self.__strength

    @strength.setter
    def strength(self, value):
        self.__strength = value
        self.update_derived_stats()

    @property
    def vitality(self):
        """Returns vitality"""
        return self.__vitality

    @vitality.setter
    def vitality(self, value):
        self.__vitality = value
        self.update_derived_stats()

    @property
    def intel(self):
        """Returns intelligence"""
        return self.__intel

    @intel.setter
    def intel(self, value):
        self.__intel = value
        self.update_derived_stats()

    @property
    def dexterity(self):
        """Returns dexterity"""
        return self.__dexterity

    @dexterity.setter
    def dexterity(self, value):
        self.__dexterity = value
        self.update_derived_stats()

    @property
    def items(self):
        """Returns list of character's items"""
        return self.__items

    def add_item(self, item):
        """Adds item to player inventory if not already there (should we allow multiples?)"""
        if item not in self.items:
            self.items.append(item)

    def remove_item(self, item):
        """Removes item from player inventory"""
        if item in self.items:
            self.items.remove(item)

    def update_derived_stats(self):
        """
        Generate derived stats based on base stats.

        Health int 50-100, mana int 50-100, regen int 1-3, armor int 0-10, damage multiplier float 0-1
        """
        self.health = 50 + int(50 * (self.strength / self.STAT_MAX * self.vitality / self.STAT_MAX))
        self.base_health = self.health
        self.health_regen = 1 + int(self.strength / self.STAT_MAX + self.vitality / self.STAT_MAX)
        self.mana = 50 + int(50 * (self.intel / self.STAT_MAX * self.vitality / self.STAT_MAX))
        self.base_mana = self.mana
        self.mana_regen = 1 + int(self.intel / self.STAT_MAX + self.vitality / self.STAT_MAX)
        self.armor = int(10 * (self.strength / self.STAT_MAX * self.dexterity / self.STAT_MAX))
        self.base_armor = self.armor
        self.damage_multiplier = 1 + self.strength / self.STAT_MAX * self.intel / self.STAT_MAX

    def toggle_regen(self, state: bool = None):
        """Turns regeneration on or off (True/False) or toggles current value with no parameter"""
        if state is None:
            self._regen = not self._regen
        elif state:
            self._regen = True
        else:
            self._regen = False

    def regen(self):
        """Update health and mana if regen is active"""
        if self._regen:
            self.health = min(self.health + self.health_regen, self.base_health)
            self.mana = min(self.mana + self.mana_regen, self.base_mana)

    def update(self):
        """Update character stats and position"""
        self.regen()
        self.x += self.dx
        self.y += self.dy


if __name__ == '__main__':
    player = Character()
    print('Initial character stats')
    print(player)

    # Test player property and stat manipulation
    print('Adding +5 strength and recalculating attributes')
    player.strength += 5
    print(player)

    # Test regen
    player.health, player.mana = 10, 10
    print(f'Player health {player.health} mana {player.mana} before update')
    player.update()
    print(f'Player health {player.health} mana {player.mana} after update with regen {player._regen}')
    player.toggle_regen()
    print(f'Player health {player.health} mana {player.mana} after update with regen {player._regen}')

    # Test adding and removing items
    print(f'Current items {player.items}')
    player.add_item('rusty dagger')
    player.add_item('wooden shield')
    print(f'Updated items {player.items}')
    player.remove_item('rusty dagger')
    print(f'Items after disarming the player {player.items}')
