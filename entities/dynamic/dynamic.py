from entities.entity import Entity


class Dynamic(Entity):
    """

    Entities that can move while being or not affected by approximated physics. These entities can be set to not be
    affected by certain rules if the proper attributes are set to values that nullify their effects.

    """

    X_GRAV = 0
    Y_GRAV = 0.4

    def __init__(self, e_type: str, pos: [int, int], size: [int, int], hp: int, max_speed: [int, int],
                 friction: [float, float], collides=True, has_mass=True, god_mode=False):
        super().__init__(e_type, pos[0], pos[1], size[0], size[1], hp, collides, god_mode)
        self.has_mass = has_mass  # True if affected by gravity
        self.vel = [0.0, 0.0]  # Vector velocity of the entity
        self.friction = friction  # Friction on each axis
        self.max_speed = max_speed  # Vector with the max speed on each axis
        self.air_time = 0  # Counter for the time the entity has been on air

    def accelerate(self, acc: (float, float)):
        self.vel[0] += acc[0]
        self.vel[1] += acc[1]

    def set_movement(self):
        """

        Calcula el movimiento a aplicar a la entidad dinamica. El atributo vel se usa para guardar la
        velocidad de la entidad, pero el movimiento en si vendra dado por esta velocidad procesada y
        redondeada.

        :return:
        """
        mov = [0, 0]

        if self.has_mass:
            self.vel[0] += self.X_GRAV
            self.vel[1] += self.Y_GRAV

        if self.vel[0] > self.max_speed[0]:
            self.vel[0] = self.max_speed[0]
        elif self.vel[0] < -self.max_speed[0]:
            self.vel[0] = -self.max_speed[0]
        if abs(self.vel[0]) < 0.1:
            self.vel[0] = 0
        else:
            self.vel[0] -= self.friction[0] * self.vel[0]

        if self.vel[1] > self.max_speed[1]:
            self.vel[1] = self.max_speed[1]
        elif self.vel[1] < -self.max_speed[1]:
            self.vel[1] = -self.max_speed[1]
        if abs(self.vel[1]) < 0.1:
            self.vel[1] = 0
        else:
            self.vel[1] -= self.friction[1] * self.vel[1]

        mov[0] = round(self.vel[0])
        mov[1] = round(self.vel[1])
        return mov

    def move(self, box_list):
        """
        Applies the movement to the entity; box_list contains the rects that the entity can physically collide with,
        meaning that they can't occupy the same space at the same time. It moves the entity on each axis and checks if
        it collided. If there is a collision, it moves the entity accordingly.
        :param box_list:
        :return:
        """
        mov = self.set_movement()
        # We set up a register to know from which side it collided
        coll_register = [False, False, False, False]
        # Management of the x axis first
        self.box.x += mov[0]
        # Gets the list of boxes hit at each moment (can be empty)
        boxes_hit = self.check_coll(box_list)
        for box in boxes_hit:
            if mov[0] > 0:
                self.box.right = box.left
                coll_register[0] = True
            elif mov[0] < 0:
                self.box.left = box.right
                coll_register[1] = True
        # Management of the y axis
        self.box.y += mov[1]
        boxes_hit = self.check_coll(box_list)
        for box in boxes_hit:
            if mov[1] > 0:
                self.box.bottom = box.top
                coll_register[2] = True
            elif mov[1] < 0:
                self.box.top = box.bottom
                coll_register[3] = True
        return coll_register

    def collision_handler(self, coll):
        """
        Handles the repercussions of collisions depending on the direction.
        :param coll:
        :return:
        """
        if coll[0]:
            # Collision left
            self.vel[0] = 0
        if coll[1]:
            # Collision right
            self.vel[0] = 0
        if coll[2]:
            # Collision bottom
            self.vel[1] = 0
        if coll[3]:
            # Collision top
            self.vel[1] = 0

    def update(self, player, tile_list, entity_list, proj_list, pickable_list):
        """
        Updates the internal state of the entity.
        :param pickable_list:
        :param player:
        :param entity_list:
        :param tile_list:
        :param proj_list:
        :return:
        """
        coll = self.move(tile_list)
        self.collision_handler(coll)
