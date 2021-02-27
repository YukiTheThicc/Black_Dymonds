import random

import pygame

import data
from entities.dynamic.dynamic import Dynamic


class Enemy_Melee(Dynamic):
    """

    """
    HITBOX_SIZE = [24, 32]
    GRACE_FRAMES = 8

    def __init__(self, e_type: str, pos: [int, int], hp: int, max_speed: [int, int], acc: float,
                 friction: [float, float], j_strength: int, rof: int, m_range: int, damage: int, dif_multi: float,
                 points: [int], has_mass=True, god_mode=False):
        super().__init__(e_type, pos, self.HITBOX_SIZE, round(hp * dif_multi), max_speed, friction, has_mass, god_mode)
        self.acc = acc
        self.j_spd = j_strength
        self.rof = rof
        self.rof_timer = 0
        self.action_timer = 0
        self.range = m_range
        self.damage = round(damage * dif_multi)
        self.points = round(points * dif_multi)

    def internal_action_setter(self):
        if self.action_timer == 0:
            if abs(self.vel[0]) < 1 and abs(self.vel[1]) < 1:
                self.set_action("IDLE")
            elif abs(self.vel[1]) > 0.4:
                self.set_action("AIR_TIME")
            elif self.vel[0] > 0:
                self.set_action("MOVING_RIGHT")
            elif self.vel[0] < 0:
                self.set_action("MOVING_LEFT")

    def action_handler(self, player):
        self.follow_player(player)
        if self.action == "JUMPING":
            self.jump()
        elif self.action == "ATTACKING":
            self.attack()
        elif self.action == "AIR_TIME":
            self.fall()
        self.internal_action_setter()

    def start_jump(self):
        if self.action != "AIR_TIME" and self.action != "JUMPING" and self.action_timer == 0:
            self.set_action("JUMPING")
            self.action_timer = 8
            self.vel[1] = -self.j_spd

    def jump(self):
        self.action_timer -= 1

    def fall(self):
        self.air_time += 1

    def on_land(self):
        self.vel[1] = 0
        self.air_time = 0

    def collision_handler(self, coll):
        if coll[0] or coll[1]:
            self.vel[0] = 0
            if self.action != "AIR_TIME":
                self.start_jump()
        if coll[2]:
            self.on_land()
        if coll[3]:
            self.vel[1] = 0

    def follow_player(self, player):
        if self.action_timer == 0:
            player_pos = player.get_position()
            my_pos = self.get_position()
            dis_to_player = self.distance_to_point(player.box.center)
            if 10 < dis_to_player < 256:
                if player_pos[0] > my_pos[0]:
                    self.accelerate([2, 0])
                elif player_pos[0] < my_pos[0]:
                    self.accelerate([-2, 0])
            if dis_to_player < 128 and player_pos[1] < my_pos[1] - 64:
                self.start_jump()
            if dis_to_player <= self.range:
                self.start_attack(player)

    def start_attack(self, player):
        frames_halt = 60 / self.rof
        if self.rof_timer % frames_halt == 0:
            random.choice(data.audio[self.type]["slash"]).play()
            self.set_action("ATTACKING")
            self.action_timer = 60/self.rof
            player.take_damage(self.damage)
        if self.rof_timer % 60 == 0:
            self.rof_timer = 0

    def attack(self):
        self.action_timer -= 1
        self.rof_timer += 1

    def draw(self, frame, scroll):
        if self.action == "IDLE":
            pygame.draw.rect(frame, (0, 0, 0), pygame.Rect(self.box.x - scroll[0],
                                                           self.box.y - scroll[1], 32, 32))
        elif self.action == "MOVING_RIGHT":
            pygame.draw.rect(frame, (200, 0, 0), pygame.Rect(self.box.x - scroll[0],
                                                             self.box.y - scroll[1], 32, 32))
        elif self.action == "MOVING_LEFT":
            pygame.draw.rect(frame, (0, 0, 200), pygame.Rect(self.box.x - scroll[0],
                                                             self.box.y - scroll[1], 32, 32))
        elif self.action == "JUMPING":
            pygame.draw.rect(frame, (200, 200, 0), pygame.Rect(self.box.x - scroll[0],
                                                               self.box.y - scroll[1], 32, 32))
        elif self.action == "AIR_TIME":
            pygame.draw.rect(frame, (0, 200, 0), pygame.Rect(self.box.x - scroll[0],
                                                             self.box.y - scroll[1], 32, 32))
        elif self.action == "ATTACKING":
            pygame.draw.rect(frame, (200, 0, 200), pygame.Rect(self.box.x - scroll[0],
                                                               self.box.y - scroll[1], 32, 32))

    def update(self, player, tile_list, entity_list, proj_list):
        self.check_health(entity_list)
        coll = self.move(tile_list)
        self.collision_handler(coll)
        self.action_handler(player)


