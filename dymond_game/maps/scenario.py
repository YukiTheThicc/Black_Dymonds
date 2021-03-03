import random

import pygame

from dymond_game import game_data
from dymond_game.maps import parralax, tile


class Scenario:
    TILE_SIZE = [32, 32]

    def __init__(self):
        """

        Crea una instancia po defecto (sin datos) de la clase Scenario. El escenario en concreto se cargará a través de
        la función load().

        """
        self.id = None  # ID del escenario, para la busqueda interna de recursos
        self.name = None  # Nombre del escenario
        self.tile_set = {}  # Set the tiles que usa el escenario
        self.bkg_tile_set = {}  # Set de tiles que estan de fondo (no tienen colision nunca)
        self.enemies = {}  # Set de enemigos del mapa con sus posibilidades de aparicion
        self.maps = []  # Lista de los mapas de tiles que puede tener el escenario
        self.played_maps = []  # Lista de los mapas que ya se han seleccionado
        self.tile_map = []  # Mapa de tiles que tiene el escenario
        self.bkg_tile_map = []  # Tiles de fondo del escenario
        self.non_collision_group = []  # Lista de tiles que no tienen caja de colisiones (en el mapa de tiles normal)
        self.platform_group = []
        self.tiles = []  # Cajas de colision del escenario
        self.active_tiles = []  # Tiles activos
        self.background = None  # Fondo del escenario
        self.player_spawn = []  # Posicion de aparicion del jugador en el escenario
        self.music_tracks = []  # Pistas de musica que usa el escenario
        self.length = 0  # Longitud (en tiles) del escenario
        self.height = 0  # Altitud (en tiles) del escenario

    # CLASS METHODS BEGIN-----------------------------------------------------------------------------------------------

    @classmethod
    def get_tile_size(cls):
        """

        Recoge la tupla que indica el tamaño de los tiles del mapa

        :return:
        """
        return cls.TILE_SIZE

    @classmethod
    def set_tile_size(cls, size: [int, int]):
        """

        Pone el tamaño de tile del escenario al valor que se le pase

        :param size: Tupla de int con el tamaño nuevo de los tiles
        :return:
        """
        cls.TILE_SIZE = size

    # CLASS METHODS END ------------------------------------------------------------------------------------------------

    def load(self, map_info: {}):
        """

        Funcion que carga de un diccionario toda la información que el escenario necesita para funcionar. En el
        diccionario iran rutas a los recursos y datos como el set de tiles sin caja de colisiones, los posibles enemigos
        que aparecen en el mapa y sus posibilidades de aparición, además de la posicion de aparicion del avatar del
        jugador.

        :param map_info: Diccionario (sacado normalmente de un .json) con todos los datos para la creacion del mapa
        :return:
        """
        self.id = map_info["id"]
        self.name = map_info["name"]
        tile_info = map_info["tile_paths"]
        for tile_id in tile_info:
            tile = pygame.image.load(tile_info[tile_id]).convert()
            tile.set_colorkey(game_data.COLOR_KEY)
            self.tile_set[tile_id] = tile
        bkg_tile_info = map_info["bkg_tile_paths"]
        for tile_id in bkg_tile_info:
            tile = pygame.image.load(bkg_tile_info[tile_id]).convert()
            tile.set_colorkey(game_data.COLOR_KEY)
            self.bkg_tile_set[tile_id] = tile
        bck_info = map_info["background"]
        self.non_collision_group = map_info["non_collision_group"]
        self.platform_group = map_info["platform_group"]
        self.player_spawn = map_info["spawn_point"]
        self.enemies = map_info["enemies"]
        for music_track_path in map_info["music"]:
            self.music_tracks.append(music_track_path)
        if bck_info["type"] == "parallax":
            self.background = parralax.Parallax(bck_info["layers"])
        for map_name in map_info["maps"]:
            self.maps.append(map_name)

    def choose_tile_map(self, specific_map=None):
        """

        :param specific_map:
        :return:
        """
        self.tile_map.clear()
        self.bkg_tile_map.clear()
        self.tiles.clear()
        if specific_map is not None:
            map_name = specific_map
        else:
            if len(self.maps) == 0:
                self.maps = self.played_maps.copy()
                self.played_maps.clear()
            map_name = random.choice(self.maps)
            self.maps.remove(map_name)
            self.played_maps.append(map_name)
        f = open("res/scenarios/" + self.id + "/maps/" + map_name + "/tile_map.txt", 'r')
        data = f.read()
        f.close()
        data = data.split('\n')
        row = data[0]
        self.length = len(row) - 10
        y = 0
        for row in data:
            self.tile_map.append(row)
            x = 0
            for column in row:
                if column != '0':
                    new_tile = tile.Tile(column, (x * self.TILE_SIZE[0], y * self.TILE_SIZE[1]),
                                         (self.TILE_SIZE[0], self.TILE_SIZE[1]))
                    if new_tile.t_type in self.platform_group:
                        new_tile.is_platform = True
                    if column == 'f':
                        new_tile.does_damage = True
                        new_tile.damage = 10
                    self.tiles.append(new_tile)
                x += 1
            y += 1
        self.height = y
        f = open("res/scenarios/" + self.id + "/maps/" + map_name + "/bkg_tile_map.txt", 'r')
        data = f.read()
        f.close()
        data = data.split('\n')
        for row in data:
            self.bkg_tile_map.append(row)

    def check_collision(self, pos: [int, int], size: [int, int]):
        rect = pygame.Rect(pos, size)
        for tile in self.tiles:
            if rect.colliderect(tile.box):
                return True
        return False

    def render(self, frame: pygame.Surface, scroll: [int, int], player):
        self.active_tiles = []
        self.background.render(frame, scroll)
        y = 0
        for row in self.bkg_tile_map:
            x = 0
            for column in row:
                if column != '0':
                    frame.blit(self.bkg_tile_set[column],
                               (x * self.TILE_SIZE[0] - scroll[0], y * self.TILE_SIZE[1] - scroll[1]))
                x += 1
            y += 1
        for tile in self.tiles:
            if tile.t_type not in self.non_collision_group:
                self.active_tiles.append(tile)
            frame.blit(self.tile_set[tile.t_type], (tile.box.x - scroll[0],
                                                    tile.box.y - scroll[1]))
