from entities.dynamic.dynamic import Dynamic


class Pickable(Dynamic):
    def __init__(self, e_type: str, size: [int, int], pos: [int, int], hp: int, max_speed: [int, int],
                 friction: [float, float], has_mass=True, god_mode=False):
        super().__init__(e_type, pos, size, hp, max_speed, friction, has_mass, god_mode)

    def