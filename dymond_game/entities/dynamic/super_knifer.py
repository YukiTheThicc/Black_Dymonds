from dymond_game.entities.dynamic.enemy_melee import Enemy_Melee


class super_knifer(Enemy_Melee):
    def __init__(self, e_type: str, pos: [int, int], hp: int, max_speed: [int, int], acc: float,
                 friction: [float, float], j_strength: int, rof: int, m_range: int, follow_range: int, damage: int,
                 dif_multi: float, points: [int]):
        super().__init__(e_type, pos, hp, max_speed, acc, friction, j_strength, rof, m_range, follow_range, damage,
                         dif_multi, points)


