import json

import pygame

from entities import entity, projectile
from entities.dynamic import player, dynamic, enemy_melee
from maps import tile_map
import var
import data

"""
    @Santiago Barreiro Chapela

    ES - Dymond es la clase hecha para facilitar la creacion de elementos del juego facilitar herramientas como el 
    dibujado de texto, renderizado o carga de animaciones.
"""


def create_variables():
    """

    :return:

    """
    var.FRAME_SIZE = (480, 270)
    var.RES = (1600, 900)
    var.CAMERA_OFFSET = (224, 150)
    var.COLOR_KEY = (0, 255, 0)
    var.TIMER = 0
    var.CLK_TICKS = 60
    var.FONTS = {
        "SMALL": pygame.font.SysFont("impact", 12),
        "BIG": pygame.font.SysFont("impact", 16),
        "HUGE": pygame.font.SysFont("impact", 20),
        "GIGANTIC": pygame.font.SysFont("impact", 24)
    }


# ENTITY CREATORS BEGIN-------------------------------------------------------------------------------------------------


def create_entity(e_type: str, pos_x: int, pos_y: int, x: int, y: int, hp: int, god_mode=False):
    """

    :param god_mode:
    :param hp:
    :param e_type:
    :param pos_x:
    :param pos_y:
    :param x:
    :param y:
    :return:

    """
    return entity.Entity(e_type, pos_x, pos_y, x, y, hp, god_mode)


def create_dynamic_entity(e_type: str, pos: (int, int), size: (int, int), hp: int, max_speed: [int, int],
                          friction: [float, float], has_mass=True, god_mode=False):
    """

    :param e_type:
    :param pos:
    :param size:
    :param hp:
    :param max_speed:
    :param friction:
    :param has_mass:
    :param god_mode:
    :return:

    """
    return dynamic.Dynamic(e_type, pos, size, hp, max_speed, friction, has_mass, god_mode)


def create_projectile(p_type: str, pos_x: int, pos_y: int, x: int, y: int, damage: int, speed: int, angle: int):
    """

    :param p_type:
    :param pos_x:
    :param pos_y:
    :param x:
    :param y:
    :param damage:
    :param speed:
    :param angle:
    :return:

    """
    return projectile.Projectile(p_type, pos_x, pos_y, x, y, speed, angle, damage)


def create_player(pl_type: str, pos: [int, int], hp: int, max_speed: [int, int],
                  acc: float, friction: [float, float], j_strength: int, rof: int, has_mass=True, god_mode=False):
    """

    Creates a player entity (will be composed of multiple sprites) and returns it.
    :param pl_type: String to identify what sprite to be drawn
    :param pos: Tuple of the position of the player
    :param hp: Health points of the player
    :param max_speed: Tuple with the maximum speed on each axis for the player
    :param friction: Friction of the player (how fast it slows down)
    :param acc: Acceleration on the x axis
    :param j_strength: Strength of the jump
    :param rof: Rate of fire of the player (shots per second, might be changed if weapons are added)
    :param has_mass: Affected by gravity -> True
    :param god_mode: Can't take damage -> True
    :return:

    """
    return player.Player(pl_type, pos, hp, max_speed, acc, friction, j_strength, rof, has_mass, god_mode)


def create_enemy_melee(pl_type: str, pos: [int, int], hp: int, max_speed: [int, int], acc: float, friction: float,
                       j_strength: int, rof: int, m_range: int, points: int, has_mass=True, god_mode=False):
    """

    Creates a player entity (will be composed of multiple sprites) and returns it.
    :param m_range:
    :param points:
    :param pl_type: String to identify what sprite to be drawn
    :param pos: Tuple of the position of the player
    :param hp: Health points of the player
    :param max_speed: Tuple with the maximum speed on each axis for the player
    :param friction: Friction of the player (how fast it slows down)
    :param acc: Acceleration on the x axis
    :param j_strength: Strength of the jump
    :param rof: Rate of fire of the player (shots per second, might be changed if weapons are added)
    :param has_mass: Affected by gravity -> True
    :param god_mode: Can't take damage -> True
    :return:

    """
    return enemy_melee.Enemy_Melee(pl_type, pos, hp, max_speed, acc, friction, j_strength, rof, m_range, has_mass,
                                   god_mode, points)


def create_knifer(pos: [int, int], difficulty_multi: float):
    return enemy_melee.Enemy_Melee('knifer', pos, 50, (3, 12), 2, (0.2, 0), 8, 2, 24, 10, difficulty_multi, 100)


# ENTITY CREATORS END---------------------------------------------------------------------------------------------------


def load_animations(json_path: str):
    """

    Method that loads the animations into the animation database. This is done through a .json file that contains a dict
    with all the possible entity types; the entity types will index another dictionary, this time, the dict will contain
    indexed with the name of each action, a list; each element of the list is a tuple, whose first item is the number of
    frames that a frame will be shown, and the second element is the path of the frame image itself.

    This method iterates through said file and stores the loaded, converted and color keyed images onto the animation
    database, with the same format that the .json has, but this time containing in the lists the number of frames and
    the loaded image.
    :param json_path:
    :return:

    """
    animation_data = {}
    f = open(json_path, 'r')
    animations_loader_info = json.load(f)
    f.close()
    for entity_type in animations_loader_info:
        entity_animations_data = animations_loader_info[entity_type]
        loaded_animations = {}
        for animation in entity_animations_data:
            frames = entity_animations_data[animation]
            loaded_frames = []
            for frame in frames:
                image = pygame.image.load(frame[1]).convert()
                image.set_colorkey(var.COLOR_KEY)
                loaded_frames.append((frame[0], image))
            loaded_animations[animation] = loaded_frames
        animation_data[entity_type] = loaded_animations
    return animation_data


def load_audio():
    player_shot = pygame.mixer.Sound('res/sfx/player_gun.wav')
    player_shot.set_volume(0.5)
    player_hurt = pygame.mixer.Sound('res/sfx/player_hurt.wav')
    player_hurt.set_volume(0.5)
    knife_slash = pygame.mixer.Sound('res/sfx/knife_slash.wav')
    knife_slash.set_volume(0.3)
    ready = pygame.mixer.Sound('res/sfx/ready.wav')
    ready.set_volume(0.5)
    data.audio = {
        "player_shot": player_shot,
        "player_hurt": player_hurt,
        "knife_slash": knife_slash,
        "ready": ready
    }
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.mixer.set_num_channels(64)


def createMap(map_name: str):
    new_map = tile_map.TileMap()
    f = open("info/maps/" + map_name + ".json", 'r')
    map_info = json.load(f)
    f.close()
    new_map.load(map_info)
    return new_map


def text_data(to_text, font: str, color: str):
    scr = str(to_text)
    data_text = var.FONTS[font].render(scr, 1, pygame.Color(color))
    return data_text


def render_hud(frame: pygame.Surface, scroll, clock: pygame.time.Clock, time: float, points: int, player_health: int,
               show_fps: False, show_scroll: False):
    fps = str(int(clock.get_fps())) + " FPS"
    if show_fps:
        frame.blit(text_data(fps, "SMALL", "black"), (380, 250))
    if show_scroll:
        frame.blit(text_data(scroll, "SMALL", "black"), (420, 250))

    if time <= 0:
        time = 0
    frame.blit(text_data(round(time, 3), "BIG", "black"), (420, 4))
    frame.blit(text_data(str(points) + "p", "BIG", "black"), (420, 20))

    if player_health <= 0:
        player_health = 0
    pygame.draw.rect(frame, (10, 10, 10), pygame.Rect(6, 6, 204, 20))
    pygame.draw.rect(frame, (100, 10, 10), pygame.Rect(8, 8, 200, 16))
    pygame.draw.rect(frame, (20, 150, 20), pygame.Rect(8, 8, player_health * 2, 16))
    frame.blit(text_data(str(player_health) + " / 100", "BIG", "black"), (16, 24))


def render_frame(display: pygame.display, frame: pygame.Surface, scroll, clock: pygame.time.Clock, time, points: int,
                 player_health: int, show_fps: False, show_scroll: False):
    render_hud(frame, scroll, clock, time, points, player_health, show_fps, show_scroll)
    display.blit(pygame.transform.scale(frame, var.RES), (0, 0))
    pygame.display.update()
    return frame.copy()
