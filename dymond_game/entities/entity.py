import random

import pygame
from dymond_game import dymond, game_data


class Entity:
    """

    """

    def __init__(self, e_type: str, pos_x: int, pos_y: int, x: int, y: int, hp: int, collides=True, god_mode=False):
        self.type = e_type  # Entity type; important for animations and state handlers
        self.box = pygame.Rect(pos_x, pos_y, x, y)  # Collider rectangle
        self.points = 0
        self.max_hp = hp
        self.hp = self.max_hp  # Entities health points
        self.god_mode = god_mode  # True if the entity can't take damage
        self.frame_timer = 0  # Time spent doing one action
        self.this_frame_index = 0  # Current frame inside an animation
        self.current_frame = None  # Current frame to blit
        self.action = "IDLE"  # Current state of the entity
        self.collides_with_projectiles = collides
        self.is_facing_left = False
        self.is_facing_up = False

    def take_damage(self, damage: int):
        random.choice(game_data.audio["hit"][self.type]).play()
        if not self.god_mode:
            self.hp -= damage

    def check_health(self, entity_list, pickable_list):
        if self.hp <= 0 and not self.god_mode:
            game_data.points += self.points
            entity_list.remove(self)
            random.choice(game_data.audio[self.type]["death"]).play()
            chance = random.randint(0, 100)
            pickable = ""
            for drop_item in game_data.drop_chances[self.type]:
                if chance <= game_data.drop_chances[self.type][drop_item]:
                    pickable = drop_item
            new_pickable = dymond.create_pickable(pickable, self.get_position())
            if new_pickable:
                pickable_list.append(new_pickable)

    def get_position(self):
        return self.box.x, self.box.y

    def get_box_size(self):
        return self.box.width, self.box.height

    def set_position(self, new_pos: [int, int]):
        self.box.x = new_pos[0]
        self.box.y = new_pos[1]

    def check_coll(self, box_list):
        """
        This function gets all the rects that the entity has collided with at a given moment.
        :param box_list:
        :return:
        """
        boxes_hit = []
        for box in box_list:
            if self.box.colliderect(box):
                boxes_hit.append(box)
        return boxes_hit

    def set_action(self, action):
        """
        If the previous action was different, it sets the new action and resets the animation.
        :param action:
        :return:
        """
        if self.action != action:
            self.action = action
            self.this_frame_index = 0
            self.frame_timer = 0

    def distance_to_point(self, point: [int, int]):
        my_pos = self.box.center
        return (((point[0] - my_pos[0]) ** 2) + ((point[1] - my_pos[1]) ** 2)) ** 0.5

    def animate(self, loop: bool):
        """

        :param loop:
        :return:
        """
        frame_data = game_data.animations[self.type][self.action]
        self.current_frame = frame_data[self.this_frame_index][1]
        self.frame_timer += 1
        if self.frame_timer == frame_data[self.this_frame_index][0]:
            self.frame_timer = 0
            self.this_frame_index += 1
        if self.this_frame_index == len(frame_data):
            if loop:
                self.this_frame_index = 0
            else:
                self.this_frame_index = len(frame_data) - 1
        self.current_frame = pygame.transform.flip(self.current_frame, self.is_facing_left, self.is_facing_up)

    def draw(self, frame, scroll):
        """

        :param frame:
        :param scroll:
        :return:
        """
        self.animate(True)
        frame.blit(self.current_frame, (self.box.x - scroll[0] - 8, self.box.y - scroll[1]))

    def update(self, player, tile_list, entity_list, proj_list, pickable_list):
        self.check_coll(tile_list)
        self.check_health(entity_list, pickable_list)
