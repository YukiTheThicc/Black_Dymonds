import random

import data
from entities.dynamic.dynamic import Dynamic


class Pickable(Dynamic):
    def __init__(self, e_type: str, pos: [int, int], size: [int, int], hp: int, max_speed: [int, int],
                 friction: [float, float], has_mass=True, god_mode=False):
        super().__init__(e_type, pos, size, hp, max_speed, friction, True, has_mass, god_mode)


class HP_boost(Pickable):
    def __init__(self, e_type: str, pos: [int, int], size: [int, int], hp: int, max_speed: [int, int],
                 friction: [float, float], has_mass=True, god_mode=False):
        super().__init__(e_type, pos, size, hp, max_speed, friction, has_mass, god_mode)

    def give_hp(self, player, pickable_list):
        if player.hp < player.max_hp:
            player.hp += self.hp
            if player.hp > player.max_hp:
                player.hp = player.max_hp
            random.choice(data.audio["game"]["hp_up"]).play()
            pickable_list.remove(self)

    def update(self, player, tile_list, entity_list, proj_list, pickable_list):
        if self.distance_to_point(player.box.center) < 320:
            self.check_coll(tile_list)
            if self.box.colliderect(player.box):
                self.give_hp(player, pickable_list)
