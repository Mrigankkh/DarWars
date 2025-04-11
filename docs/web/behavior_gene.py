from enum import Enum

class BehaviorGene(Enum):
    AGGRESSIVE = 0       # Chase player aggressively
    DEFENSIVE = 1        # Keep distance from player
    ERRATIC = 2          # Move in unpredictable patterns
    TACTICAL = 3         # Try to flank the player
    KAMIKAZE = 4         # Rush towards player to crash
    ADAPTIVE = 5         # Change behavior based on health
    MOVE_LEFT = 6        # Move left
    MOVE_RIGHT = 7       # Move right
    MOVE_UP = 8          # Move up
    MOVE_DOWN = 9        # Move down
    ZIGZAG = 10          # Move in zigzag pattern
    CIRCLE = 11          # Move in a circular pattern
    STOP = 12            # Stop moving temporarily
    SHOOT_STRAIGHT = 13  # Shoot in current direction
    SHOOT_SPREAD = 14    # Shoot in multiple directions
    SHOOT_BURST = 15     # Fire multiple shots in quick succession
    DODGE = 16           # Try to dodge player bullets
    GROUP = 17           # Try to move near other enemies
    AMBUSH = 18          # Hide and wait for player approach
    RETREAT = 19         # Move away from player when close