import numpy as np


class PowerUp:
    """Defines all information for the Power-up"""

    def __init__(self,
                 name: str = None,
                 damage: int = None,
                 damage_area: int = None,
                 damage_range: int = None,
                 w_type: str = None,
                 strength_boost: int = None,
                 vitality_boost: int = None,
                 intel_boost: int = None,
                 dexterity_boost: int = None,
                 avoid_area: list = None,
                 ):
        self.name = name
        self.damage = damage
        self.damage_area = damage_area
        self.damage_range = damage_range
        self.w_type = w_type
        self.strength_boost = strength_boost
        self.vitality_boost = vitality_boost
        self.intel_boost = intel_boost
        self.dexterity_boost = dexterity_boost
        self.avoid_area = avoid_area

    def __str__(self):
        powerup_info = f"""
        Name            | {self.name}
        Damage          | {self.damage}
        Damage area     | {self.damage_area}
        Damage range    | {self.damage_range}
        Weapon type     | {self.w_type}
        Strength boost  | {self.strength_boost}
        Vitality boost  | {self.vitality_boost}
        Intel boost     | {self.intel_boost}
        Dexterity boost | {self.dexterity_boost}
        """
        return powerup_info

    @classmethod
    def generate(cls,
                 world_map
                 ):
        """Returns coordinates for a random powerup spawn on map"""
        powerup_class = cls.get_random_powerup()

        actual_powerup = powerup_class()      # Create powerup instance

        if actual_powerup.avoid_area is None or 0 == len(actual_powerup.avoid_area):
            filtered_map = np.random.uniform(1, 100, world_map.shape)
        else:
            filtered_map = np.isin(actual_powerup.avoid_area, world_map) * np.random.uniform(1, 100, world_map.shape)
            # filter map to avoid certain areas and give a random performance rating for every tile in map

        width = world_map.shape[-1]

        temp = np.argmax(filtered_map)      # get index of highest value in filtered map to place the weapon

        place_x = temp // width
        place_y = temp % width

        # cls.powerup = powerup
        # cls.x = place_x
        # cls.y = place_y
        return actual_powerup, place_x, place_y

    @staticmethod
    def get_random_powerup():
        """Return a random PowerUp class"""
        return np.random.choice(PowerUp.__subclasses__())

    def activate(self):
        """Activate the powerup"""
        pass

# The reason to include strength_boost > 0 for almost every powerup is that showing off a powerup
# despite it not increasing any stat does in fact lead to a psychological doubt in enemy's mind


class PumpUpPistol(PowerUp):
    """It's a pistol not a shotgun. This is not a drill!"""

    def __init__(self):
        super(PumpUpPistol, self).__init__('PumpUp Pistol', 5, 1, 5, 'Ranged', 1, 0, 0, 0, [0])


class MagureleLaser(PowerUp):
    """Strongest laser in the world"""

    def __init__(self):
        super(MagureleLaser, self).__init__('Magurele\'s Laser', 10, 1, 3, 'Ranged', 5, 0, 0, 0, [0])


class TysonGlove(PowerUp):
    """Just an ordinary glove from an ordinary Mike Tyson"""

    def __init__(self):
        super(TysonGlove, self).__init__('Tyson\'s Glove', 3, 3, 1, 'Melee', 2, 0, 0, 0, [0])


class DakuwaquCharm(PowerUp):
    """Swarm of sharks, you control"""

    def __init__(self):
        super(DakuwaquCharm, self).__init__('Dakuwaqu\'s Charm', 5, 1, 10, 'Unknown', 3, 0, 0, 0, [1, 2])
        # The 'Unknown' powerup type can be used as feature, not a bug. For instance an if elif condition where
        # we check whether we can stack multiple Melee powerups but do not include a check for 'Unknown'


class WreckingBomb(PowerUp):
    """She came in like a wrecking Bomb"""

    def __init__(self):
        super(WreckingBomb, self).__init__('Wrecking Bomb', 3, 3, 10, 'Catastrophic', 2, 0, 0, 0, [0])


class DefenderGrit(PowerUp):
    """Raises defensive stats"""

    def __init__(self):
        super(DefenderGrit, self).__init__('Defender\'s Grit', 0, 0, 0, 'Self', 0, 5, 0, 0, [0])


class MagicalMist(PowerUp):
    """Grants mist protection that harms nearby enemies"""

    def __init__(self):
        super(MagicalMist, self).__init__('Magical Mist', 2, 1, 4, 'Magic', 5, 2, 0, 0, [0])


class JokerSmile(PowerUp):
    """Why So Silly"""

    def __init__(self):
        super(JokerSmile, self).__init__('Joker\'s Smile', 0, 0, 0, 'Unknown', 1, -1, 0, 0, [])


class RickRoll(PowerUp):
    """Doesn't do shit instead of enraging your enemies more. Was the laugh worth it?"""

    def __init__(self):
        super(RickRoll, self).__init__('Rick roll', 0, 0, 0, 'Unknown', -5, -5, -5, -5, [])


if __name__ == '__main__':

    world_map = np.random.randint(0, 3, (10, 10))
    powerup, x, y = PowerUp.generate(world_map=world_map)
    powerup_repr = world_map.tolist()
    powerup_repr[x][y] = '+'

    print('World_map')
    print(np.array(world_map, dtype=str))
    print('\nWeapon on map indicated by +')
    print(np.array(powerup_repr, dtype=str))
    print(powerup)
