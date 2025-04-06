from enum import IntEnum

class GeneIndex(IntEnum):
    # Behavior toggles (0–19)
    AGGRESSIVE = 0
    DEFENSIVE = 1
    TACTICAL = 3
    KAMIKAZE = 4
    ADAPTIVE = 5
    ZIGZAG = 10
    CIRCLE = 11
    STOP = 12
    SHOOT_STRAIGHT = 13
    SHOOT_SPREAD = 14
    SHOOT_BURST = 15
    DODGE = 16
    GROUP = 17
    AMBUSH = 18
    RETREAT = 19
    BEHAVIOR_START = 0
    BEHAVIOR_END = 19
    # Attributes
    SPEED = 40
    FIRE_RATE = 41
    ACCURACY = 42
    EVASION = 43
    BULLET_SPEED = 45
    DAMAGE = 46

    # Bullet size distribution weights (47–51)
    BULLET_SIZE_PROBABILITY = 47
    BULLET_WEIGHT_SMALL = 48
    BULLET_WEIGHT_MEDIUM = 49
    BULLET_WEIGHT_LARGE = 50
    BULLET_WEIGHT_VERY_LARGE = 51
    BULLET_WEIGHT_START = 47
    BULLET_WEIGHT_END = 51
    # Misc
    X_OFFSET = 52
    BEHAVIOR_VARIANCE = 53
    # Grouping and formation (54–58)
    GROUP_SIZE_PREFERENCE = 54
    OPTIMAL_PROXIMITY = 55
    FORMATION_ROLE = 56
    FORMATION_SYNC = 58
    # Fitness score (used post-simulation)
    FITNESS = 59
