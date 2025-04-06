import random
import math

def compute_bullet_accuracy(dx, dy, accuracy):
    dx += random.uniform(-0.5, 0.5) * (1 - accuracy)
    dy += random.uniform(-0.5, 0.5) * (1 - accuracy)
    length = math.sqrt(dx * dx + dy * dy)
    return (dx / length), (dy / length)

def bullet_speed_multiplier(bullet_size):
    return max(0.5, 1.0 + (1.0 - bullet_size))  # Smaller bullets = faster

def bullet_reload_multiplier(bullet_size):
    return 0.7 + (bullet_size * 0.6)  # Larger bullets = longer cooldown
