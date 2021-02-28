from entities.entity import *
from data_types import Vector2


class Projectile:
    """
    """
    def __init__(self, p_type: str, pos_x: int, pos_y: int, x: int, y: int, speed: float, angle: int, dam: int):
        self.type = p_type  # Entity type; important for animations and state handlers
        self.box = pygame.Rect(pos_x, pos_y, x, y)  # Collider rectangle
        self.vector = Vector2(0, 0, speed)
        self.vector.change_to_angle_deg(angle)
        self.life_time = 20
        self.dam = dam

    def check_coll(self, tile_list, entity_list):
        """

        :param entity_list:
        :param tile_list:
        :return:
        """
        for box in tile_list:
            if self.box.colliderect(box):
                return True
        for entity in entity_list:
            if entity.collides_with_projectiles:
                if self.box.colliderect(entity.box):
                    entity.take_damage(self.dam)
                    return True

    def move(self):
        """

        :return:
        """
        self.box.x += self.vector.x
        self.box.y += self.vector.y

    def draw(self, frame, scroll):
        """

        :param frame:
        :param scroll:
        :return:
        """
        pygame.draw.rect(frame, (200, 155, 0), pygame.Rect(self.box.x - scroll[0], self.box.y - scroll[1], 4, 4))

    def update(self, tile_list, entity_list, proj_list):
        """

        :param entity_list:
        :param tile_list:
        :param proj_list:
        :return:
        """
        self.life_time -= 1
        self.move()
        if self.life_time <= 0:
            proj_list.remove(self)
        elif self.check_coll(tile_list, entity_list):
            proj_list.remove(self)
