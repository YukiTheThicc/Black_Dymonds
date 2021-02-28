import random

import pygame

import var
from maps import parralax


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
        self.maps = []  # Lista de los mapas de tiles que puede tener el escenario
        self.tile_map = []  # Mapa de tiles que tiene el escenario
        self.bkg_tile_map = []  # Tiles de fondo del escenario
        self.non_collision_group = []  # Lista de tiles que no tienen caja de colisiones (en el mapa de tiles normal)
        self.collision_boxes = []  # Cajas de colision del escenario
        self.background = None  # Fondo del escenario
        self.player_spawn = []  # Posicion de aparicion del jugador en el escenario
        self.music_tracks = []  # Pistas de musica que usa el escenario
        self.length = 0  # Longitud (en tiles) del escenario

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
        if specific_map is not None:
            map_name = specific_map
        else:
            map_name = random.choice(self.maps)
        f = open("res/scenarios/" + self.id + "/maps/" + map_name + "/tile_map.txt", 'r')
        data = f.read()
        f.close()
        data = data.split('\n')
        row = data[0]
        self.length = len(row) - 16
        for row in data:
            self.tile_map.append(row)
        f = open("res/scenarios/" + self.id + "/maps/" + map_name + "/bkg_tile_map.txt", 'r')
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
