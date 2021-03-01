import random

import pygame

import data
from entities.dynamic.dynamic import Dynamic
import dymond


class Player(Dynamic):
    """

    Clase del avatar que controla el jugador. Aviso para navegantes: se va a usar POO como base wde
    de todas las clases instanciables que hagamos.

    Constantes de la clase jugador:

    """
    HITBOX_SIZE = [20, 32]
    GRACE_FRAMES = 8
    IMMUNITY_FRAMES = 30

    def __init__(self, e_type: str, pos: [int, int], hp: int, max_speed: [int, int],
                 acc: float, friction: [float, float], j_strength: int, rof: int, has_mass=True, god_mode=False):
        super().__init__(e_type, pos, self.HITBOX_SIZE, hp, max_speed, friction, True, has_mass, god_mode)
        self.position_center = 0
        self.acc = acc
        self.j_spd = j_strength
        self.rof = rof
        self.rof_timer = 0
        self.action_delay = 0
        self.immunity_frames = 0
        self.step_timer = 0
        self.states = {"IDLE": True, "RUNNING_RIGHT": False, "RUNNING_LEFT": False, "JUMPING": False, "AIR_TIME": False,
                       "LANDING": False, "AIMING_UP": False, "SHOOTING": False, "IS_SHOOTING": False}
        self.flash = dymond.create_entity("flash", self.box.x, self.box.y, 8, 8, 0, True)

    def internal_action_setter(self):
        if abs(self.vel[0]) <= 0.2 and abs(self.vel[1]) <= 0.2:
            self.states["IDLE"] = True
            if self.states["AIMING_UP"]:
                self.set_action("IDLE_UP")
            else:
                self.set_action("IDLE")
        else:
            self.states["IDLE"] = False
        if abs(self.vel[0]) > 0.5 and not self.states["AIR_TIME"] and not self.states["JUMPING"]:
            if self.states["AIMING_UP"]:
                self.set_action("RUN_UP")
            else:
                self.set_action("RUN")
        if abs(self.vel[1]) > 0.5:
            self.states["AIR_TIME"] = True

    def state_handler(self, proj_list):
        """

        :return:

        """
        self.internal_action_setter()
        if self.states["IDLE"]:
            self.idle()
        if self.states["RUNNING_RIGHT"]:
            self.run_right()
        elif self.states["RUNNING_LEFT"]:
            self.run_left()
        if self.states["JUMPING"]:
            self.jump()
        elif self.states["AIR_TIME"]:
            self.fall()
        elif self.states["LANDING"]:
            self.recover()
        if self.states["SHOOTING"]:
            self.shoot(proj_list)

    def idle(self):
        pass

    def run_right(self):
        if self.is_facing_left:
            self.is_facing_left = False
        if self.vel[0] < self.max_speed[0]:
            self.vel[0] += self.acc

    def run_left(self):
        if not self.is_facing_left:
            self.is_facing_left = True
        if self.vel[0] > -self.max_speed[0]:
            self.vel[0] -= self.acc

    def start_jump(self):
        if self.air_time < self.GRACE_FRAMES and not self.states["AIR_TIME"]:
            self.states["JUMPING"] = True
            self.action_delay = 6

    def jump(self):
        if self.states["AIMING_UP"]:
            self.set_action("JUMPING_UP")
        else:
            self.set_action("JUMPING")
        self.action_delay -= 1
        if self.action_delay == 0:
            self.vel[1] = -self.j_spd
            self.states["JUMPING"] = False
            self.states["AIR_TIME"] = True
            self.set_action("AIR_TIME")

    def fall(self):
        if self.states["AIMING_UP"]:
            self.set_action("AIR_TIME_UP")
        else:
            self.set_action("AIR_TIME")
        self.air_time += 1

    def on_land(self):
        self.vel[1] = 0
        self.air_time = 0
        self.states["AIR_TIME"] = False
        if self.vel[1] > 8:
            self.states["LANDING"] = True
            self.action_delay = 8
            self.set_action("LANDING")

    def recover(self):
        self.action_delay -= 1
        if self.action_delay == 0:
            self.states["LANDING"] = False

    def shoot(self, proj_list):
        frames_halt = 60 / self.rof
        if self.rof_timer % frames_halt == 0:
            self.states["IS_SHOOTING"] = True
            self.flash.set_action("FIRING")
            self.flash.is_facing_up = False
            pos = self.get_position()
            if self.states["AIMING_UP"]:
                if self.is_facing_left:
                    off_pos = [pos[0] + 10, pos[1] - 16]
                    x_offset = 10
                else:
                    off_pos = [pos[0] + 6, pos[1] - 16]
                    x_offset = 6
                proj_list.append(dymond.create_projectile("bullet", pos[0] + x_offset, pos[1] + 8, 4, 4, 10, 20, 270))
                self.flash.set_position(off_pos)
            elif self.is_facing_left:
                off_pos = [pos[0] - 16, pos[1] + 4]
                self.flash.set_position(off_pos)
                self.flash.is_facing_left = True
                proj_list.append(dymond.create_projectile("bullet", pos[0], pos[1] + 10, 4, 4, 10, 20, 180))
            else:
                off_pos = [pos[0] + 32, pos[1] + 4]
                self.flash.set_position(off_pos)
                self.flash.is_facing_left = False
                proj_list.append(dymond.create_projectile("bullet", pos[0] + 8, pos[1] + 10, 4, 4, 10, 20, 0))
            random.choice(data.audio[self.type]["shot"]).play()

    def take_damage(self, damage: int):
        if not self.god_mode and self.immunity_frames == 0:
            self.hp -= damage
            random.choice(data.audio[self.type]["hurt"]).play()
            self.immunity_frames = self.IMMUNITY_FRAMES

    def collision_handler(self, coll):
        """

        :param coll:
        :return:

        """
        if coll[0]:
            self.vel[0] = 0
        if coll[1]:
            self.vel[0] = 0
        if coll[2]:
            self.on_land()
        if coll[3]:
            self.vel[1] = 0

    def draw(self, frame, scroll, player):
        self.animate(True)
        if self.states["IS_SHOOTING"]:
            self.flash.animate(True)
            if self.states["AIMING_UP"]:
                angle = 90
                if self.flash.is_facing_left:
                    angle = -90
                self.flash.current_frame = pygame.transform.rotate(self.flash.current_frame, angle)
            frame.blit(self.flash.current_frame, (self.flash.box.x - scroll[0] - 6, self.flash.box.y - scroll[1]))
        frame.blit(self.current_frame, (self.box.x - scroll[0] - 6, self.box.y - scroll[1]))

    def update(self, player, tile_list, entity_list, proj_list, pickable_list):
        """

        :param pickable_list:
        :param player:
        :param tile_list:
        :param entity_list:
        :param proj_list:
        :return:

        """
        self.states["IS_SHOOTING"] = False
        coll = self.move(tile_list)
        self.collision_handler(coll)
        self.internal_action_setter()
        self.state_handler(proj_list)
        self.rof_timer += 1
        if self.rof_timer % 60 == 0:
            self.rof_timer = 0
        if self.immunity_frames > 0:
            self.immunity_frames -= 1
        self.position_center = self.box.center
