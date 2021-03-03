import pygame


class Tile:
    def __init__(self, t_type: str, pos: [int, int], size: [int, int], is_platform=False, does_damage=False, damage=0):
        self.t_type = t_type
        self.box = pygame.rect.Rect(pos[0], pos[1], size[0], size[1])
        self.is_platform = is_platform
        self.does_damage = does_damage
        self.damage = damage
