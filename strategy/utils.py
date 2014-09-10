import cmath


def complex_to_pair(z):
    return z.real, z.imag


class CUnit(object):
    def __init__(self, unit):
        self.pos = complex(unit.x, unit.y)
        self.dir = cmath.rect(1, unit.angle)
        self.v = complex(unit.speed_x, unit.speed_y)
        self.angle = unit.angle
        self.angular_speed = unit.angular_speed

        self.radius = unit.radius
        self.mass = unit.mass

        self.unit = unit
