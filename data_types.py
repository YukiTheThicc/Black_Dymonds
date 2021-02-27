import math


class Vector2:
    def __init__(self, x: float, y: float, module: float):
        self.x = x
        self.y = y
        self.module = module

    def set_x(self, x):
        self.x = x

    def set_y(self, x):
        self.x = x

    def get_vector(self):
        return self.x, self.y

    def change_to_angle_deg(self, angle):
        self.x = self.module * math.cos(math.radians(angle))
        self.y = self.module * math.sin(math.radians(angle))

