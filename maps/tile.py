import pygame


class Tile:
    def __init__(self, t_type: str, pos: [int, int], size: [int, int]):
        self.type = t_type
        self.has_collision =
        self.box = pygame.rect.Rect(pos[0], pos[1], size[0], size[1])