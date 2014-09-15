from math import pi
import shutil
import os
import logging

from PIL import Image, ImageDraw

from utils import *
import log_context


REPLAY_DIR = '../replay_data'


color_by_id = {1: (255, 0, 0), 2: (50, 50, 255)}


def shade(color, a):
    return tuple(int(a * c) for c in color)


class ScaledDraw(object):
    def __init__(self, img, img_path, draw, scale=1.0):
        self.img = img
        self.img_path = img_path
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


handler = None
log_draw = None


def tick(frame_number, world, game):
    global handler, log_draw
    if frame_number == 0:
        shutil.rmtree(REPLAY_DIR, ignore_errors=True)
        if not os.path.exists(REPLAY_DIR):
            os.makedirs(REPLAY_DIR)

    if frame_number % 20 and (frame_number > 100 or frame_number % 10):
        assert log_draw
        return log_draw

    if handler is not None:
        logging.getLogger().removeHandler(handler)
    if frame_number == 0:
        logging.getLogger().setLevel(logging.INFO)
    handler = logging.FileHandler(
        os.path.join(REPLAY_DIR, 'log{:04}.txt'.format(frame_number)))
    handler.setFormatter(
        logging.Formatter('%(levelname)8s:%(name)11s: %(message)s'))
    handler = log_context.HandlerDecorator(handler)
    logging.getLogger().addHandler(handler)

    print(frame_number)

    if log_draw is not None:
        log_draw.img.save(log_draw.img_path)

    scale = 0.5
    img = Image.new(
        'RGB',
        (int(world.width * scale), int(world.height * scale)),
        'black')
    img_path = os.path.join(REPLAY_DIR, 'hz{:04}.png'.format(frame_number))
    draw = ImageDraw.Draw(img, 'RGBA')
    log_draw = ScaledDraw(img, img_path, draw, scale)

    ps = [
        complex(game.goal_net_width, 0),
        complex(game.goal_net_width, game.goal_net_top),
        complex(game.goal_net_width, game.goal_net_top),
        complex(0, game.goal_net_top),
        complex(0, game.goal_net_top + game.goal_net_height),
        complex(game.goal_net_width, game.goal_net_top + game.goal_net_height),
        complex(game.goal_net_width, game.world_height)]
    border_color = (200, 200, 200)
    for p1, p2 in zip(ps, ps[1:]):
        log_draw.line(p1, p2, fill=border_color)
        log_draw.line(
            game.world_width - p1.conjugate(),
            game.world_width - p2.conjugate(),
            fill=border_color)

    for h in world.all_hockeyists:
        color = color_by_id[h.unit.player_id]
        log_draw.circle(h.pos, h.radius, outline=color, fill=color + (64,))
        if h.unit.type == 0: # goalie
            continue
        log_draw.line(h.pos, h.pos + h.dir * h.radius, fill=color)
        log_draw.pieslice(
            h.pos, game.stick_length,
            h.angle - game.stick_sector * 0.5,
            h.angle + game.stick_sector * 0.5,
            outline=color + (64,),
            fill=color + (32,))

    log_draw.circle(
        world.puck.pos, world.puck.radius,
        outline=(255, 255, 255), fill=(255, 255, 255, 64))

    return log_draw
