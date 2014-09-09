from math import pi
import cmath
import shutil
import os

from PIL import Image, ImageDraw


REPLAY_DIR = '../replay_data'


color_by_id = {1: (255, 0, 0), 2: (50, 50, 255)}


def shade(color, a):
    return tuple(int(a * c) for c in color)


class ScaledDraw(object):
    def __init__(self, draw, scale=1.0):
        self.draw = draw
        self.scale = scale

    def circle(self, pos, radius, **options):
        x = pos.real * self.scale
        y = pos.imag * self.scale
        radius *= self.scale
        self.draw.ellipse(
            (x - radius, y - radius, x + radius, y + radius),
            **options)

    def line(self, pos1, pos2, **options):
        s = self.scale
        self.draw.line(
            (pos1.real * s, pos1.imag * s, pos2.real * s, pos2.imag * s),
            **options)

    def pieslice(self, pos, radius, angle1, angle2, **options):
        x = pos.real * self.scale
        y = pos.imag * self.scale
        radius *= self.scale
        self.draw.pieslice(
            (x - radius, y - radius, x + radius, y + radius),
            int(angle1 * 180 / pi), int(angle2 * 180 / pi),
            **options)


def tick(frame_number, world, game):
    if frame_number == 0:
        shutil.rmtree(REPLAY_DIR, ignore_errors=True)
        if not os.path.exists(REPLAY_DIR):
            os.makedirs(REPLAY_DIR)

    if frame_number % 500 and (frame_number > 200 or frame_number % 3):
        return
    print(frame_number)

    scale = 0.5
    img = Image.new(
        'RGB',
        (int(world.width * scale), int(world.height * scale)),
        'black')
    draw = ImageDraw.Draw(img, 'RGBA')
    sd = ScaledDraw(draw, scale)

    for h in world.hockeyists:
        color = color_by_id[h.player_id]
        pos = complex(h.x, h.y)
        dir = cmath.rect(1, h.angle)
        sd.circle(pos, h.radius, outline=color, fill=color + (64,))

        if h.type == 0: # goalie
            continue

        sd.line(pos, pos + dir * h.radius, fill=color)
        sd.pieslice(
            pos, game.stick_length,
            h.angle - game.stick_sector * 0.5,
            h.angle + game.stick_sector * 0.5,
            outline=color + (64,),
            fill=color + (32,))

    pos = complex(world.puck.x, world.puck.y)
    sd.circle(
        pos, world.puck.radius,
        outline=(255, 255, 255), fill=(255, 255, 255, 64))

    img.save(os.path.join(REPLAY_DIR, 'hz{:04}.png'.format(frame_number)))
