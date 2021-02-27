import pygame

import var
from maps import parralax


class TileMap:
    TILE_SIZE = [32, 32]

    def __init__(self):
        self.tile_map = []  # Tile map
        self.bkg_tile_map = []  # Tiles de fondo
        self.tile_set = {}  # Tile set (not the actual map)
        self.bkg_tile_set = {}
        self.non_collision_group = []  # List of tile ids that do not have a collision box
        self.collision_boxes = []  # Collider rectangles at any single point in a frame, gets recalculated every frame
        self.background = None  # Background of the map
        self.player_spawn = []  # Position of the player spawn point
        self.length = 0

    # CLASS METHODS BEGIN-----------------------------------------------------------------------------------------------

    @classmethod
    def get_size(cls):
        return cls.TILE_SIZE

    @classmethod
    def set_size(cls, size: [int, int]):
        cls.TILE_SIZE = size

    @classmethod
    def set_chunk_size(cls, size: [int, int]):
        cls.TILE_SIZE = size

    # CLASS METHODS END ------------------------------------------------------------------------------------------------

    def load(self, map_info: {}):
        tile_info = map_info["tile_paths"]
        for tile_id in tile_info:
            tile = pygame.image.load(tile_info[tile_id]).convert()
            tile.set_colorkey(var.COLOR_KEY)
            self.tile_set[tile_id] = tile
        bkg_tile_info = map_info["bkg_tile_paths"]
        for tile_id in bkg_tile_info:
            tile = pygame.image.load(bkg_tile_info[tile_id]).convert()
            tile.set_colorkey(var.COLOR_KEY)
            self.bkg_tile_set[tile_id] = tile
        bck_info = map_info["background"]
        self.non_collision_group = map_info["non_collision_group"]
        self.player_spawn = map_info["spawn_point"]
        if bck_info["type"] == "parallax_4":
            self.background = parralax.Parallax4(bck_info["layers"])
        f = open(map_info["tile_map"], 'r')
        data = f.read()
        f.close()
        data = data.split('\n')
        row = data[0]
        self.length = len(row) - 16
        for row in data:
            self.tile_map.append(row)
        f = open(map_info["bkg_tile_map"], 'r')
        data = f.read()
        f.close()
        data = data.split('\n')
        for row in data:
            self.bkg_tile_map.append(row)

    def check_collision(self, pos: [int, int], size: [int, int]):
        self.collision_boxes = []
        y = 0
        for row in self.tile_map:
            x = 0
            for column in row:
                if column in self.non_collision_group:
                    self.collision_boxes.append(pygame.Rect(x * self.TILE_SIZE[0],
                                                            y * self.TILE_SIZE[1],
                                                            self.TILE_SIZE[0],
                                                            self.TILE_SIZE[1]))
                x += 1
            y += 1
        rect = pygame.Rect(pos, size)
        for box in self.collision_boxes:
            if rect.colliderect(box):
                return True
        self.collision_boxes = []
        return False

    def render(self, frame: pygame.Surface, scroll: [int, int]):
        self.collision_boxes = []
        self.background.render(frame, scroll)
        y = 0
        for row in self.bkg_tile_map:
            x = 0
            for column in row:
                if column != '0':
                    frame.blit(self.bkg_tile_set[column],
                               (x * self.TILE_SIZE[0] - scroll[0],
                                y * self.TILE_SIZE[1] - scroll[1]))
                x += 1
            y += 1
        y = 0
        for row in self.tile_map:
            x = 0
            for column in row:
                # Si el valor en la columna actual del mapa de tiles es distinto de 0,
                # el tile no es 'aire', y se transforma en un int para transformarlo
                # directamente en un indice del set de tiles
                if column != '0':
                    # Dibujamos el tile correspondiente (-1 porque el set de tiles empieza en
                    # 0 pero en el archivo el valor 0 se reserva para el aire)
                    if column != 'w':
                        frame.blit(self.tile_set[column],
                                   (x * self.TILE_SIZE[0] - scroll[0],
                                    y * self.TILE_SIZE[1] - scroll[1]))
                    # Le asignamos una hitbox al tile
                    if column not in self.non_collision_group:
                        self.collision_boxes.append(pygame.Rect(x * self.TILE_SIZE[0],
                                                                y * self.TILE_SIZE[1],
                                                                self.TILE_SIZE[0],
                                                                self.TILE_SIZE[1]))
                x += 1
            y += 1
