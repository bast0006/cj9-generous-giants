from random import randint
from threading import Timer


class Character:
    """
    Class for player and NPC characters.

    Tracks character stats, inventory, etc.  Stats are generated randomly, but later can be passed from
    character creation process if desired.
    Base stats:  strength, vitality, intelligene, dexterity
    Derived stats:  health, health regen rate, mana, mana regen rate, base armor, damage multiplier
    """

    STAT_MIN, STAT_MAX = 3, 18  # As if they are 3d6 dice rolls
    REGEN_INTERVAL = 1.0  # health/mana regen interval in seconds

    def __init__(self,
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
        self.strength = strength if strength is not None else randint(self.STAT_MIN, self.STAT_MAX)
        self.vitality = vitality if vitality is not None else randint(self.STAT_MIN, self.STAT_MAX)
        self.intel = intel if intel is not None else randint(self.STAT_MIN, self.STAT_MAX)
        self.dexterity = dexterity if dexterity is not None else randint(self.STAT_MIN, self.STAT_MAX)
        self.items = items

        """
        Generate derived stats based on base stats.
        Health int 50-100, mana int 50-100, regen int 1-3, armor int 0-10, damage multiplier float 0-1
        """
        self.health = 50 + int(50 * (self.strength / self.STAT_MAX * self.vitality / self.STAT_MAX))
        self.base_health = self.health
        self.health_regen = 1 + int(2 * (self.strength / self.STAT_MAX + self.vitality / self.STAT_MAX))
        self.mana = 50 + int(50 * (self.intel / self.STAT_MAX * self.vitality / self.STAT_MAX))
        self.base_mana = self.mana
        self.mana_regen = 1 + int(2 * (self.intel / self.STAT_MAX + self.vitality / self.STAT_MAX))
        self.armor = int(10 * (self.strength / self.STAT_MAX * self.dexterity / self.STAT_MAX))
        self.damage_multiplier = 1 + self.strength / self.STAT_MAX * self.dexterity / self.STAT_MAX

        self.regen(True)  # Turn on health and mana regeneration by default

    def __str__(self):
        char_info = f"""
            strength     {self.strength}
            vitality     {self.vitality}
            intelligence {self.intel}
            dexterity    {self.dexterity}
            health       {self.health}
            health regen {self.health_regen}
            mana         {self.mana}
            mana regen   {self.mana_regen}
            armor        {self.armor}
            damage x     {self.damage_multiplier}
            items        {self.items}
        """
        return char_info

    def _regen_helper(self):
        """Regenerates health and mana."""
        self.health = min(self.health + self.health_regen, self.base_health)
        self.mana = min(self.mana + self.mana_regen, self.base_mana)

    def regen(self, active: bool = True):
        """Turns regeneration on (True) or off (False)"""
        if active:
            self.rt = RepeatedTimer(self.REGEN_INTERVAL, self._regen_helper)
        else:
            self.rt.stop()


class RepeatedTimer(object):
    """
    Used to automatically run a function at selected intervals.

    Taken from https://stackoverflow.com/a/13151299/19545063
    """

    def __init__(self, interval, function, *args, **kwargs):
        self._timer = None
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        """Start the timed function"""
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        """Stop the timed function"""
        self._timer.cancel()
        self.is_running = False


if __name__ == '__main__':
    from time import sleep

    player1 = Character()
    print(player1)

    # Test regeneration
    player1.health = 10
    player1.mana = 10
    print('regen is ON by default')
    for _ in range(10):
        print(f'health: {player1.health} mana: {player1.mana}')
        sleep(1.0)
    player1.regen(False)
    print('\nregen is now turned OFF')
    for _ in range(5):
        print(f'health: {player1.health} mana: {player1.mana}')
        sleep(1.0)
    player1.health = player1.base_health - 5
    player1.mana = player1.base_mana - 5
    player1.regen(True)
    print('\nregen ON and stops at full health/mana')
    for _ in range(7):
        print(f'health: {player1.health} mana: {player1.mana}')
        sleep(1.0)
    print('\nTurn regen OFF when finished to ensure clean exit')
    player1.regen(False)
