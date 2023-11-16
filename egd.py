import inspect
import os
import sys
import threading
from math import sin, ceil, pi, dist, sqrt
from random import randint
from time import time, sleep
from typing import overload, Iterable

import pygame as pg


class Settings:
    FPS = 60
    rate = .3
    coordinates = True

    background = '#FDF7F0'
    line = '#c7b095'
    dot = '#345278'

    col1 = '#FFCE5E'  # This is a bright yellow color.
    col2 = '#61E053'  # This is a vibrant green color.
    col3 = '#68B2F7'  # This is a light blue color.
    col4 = '#E053DF'  # This is a bright pink color.
    col5 = '#FF272A'  # This is a vibrant red color.
    outline = "#3A3A0A"

    def setBGR(self, value): self.background = self.line = value

    def darkMode(self):
        self.background = "#444444"
        self.line = "#222222"

    def lightMode(self):
        self.background = '#FDF7F0'
        self.line = '#c7b095'


def detect_importer_filename():
    cur_frame = inspect.currentframe()
    if cur_frame is None: return "UNSET"
    prev_frames = inspect.getouterframes(cur_frame)

    for prev_frame in prev_frames:
        path = prev_frame.filename
        if os.path.exists(path) and path != __name__:
            return path
    else:
        return "SELF"


def sgn(value):
    return 1 if value > 0 else (-1 if value < 0 else 0)


class Point:
    _x: int
    _y: int

    @overload
    def __init__(self, tupleV: tuple): pass
    @overload
    def __init__(self, x: float, y: float): pass

    def __init__(self, value1, value2=None):
        if isinstance(value1, Iterable):
            self._x, self._y = value1
        elif isinstance(value1, (int, float)):
            self._x, self._y = value1, value2
        else:
            raise ValueError()

    def __sub__(self, other): return Point((self.getX() - other.getX(), self.getY() - other.getY()))
    def __add__(self, other): return Point((self.getX() + other.getX(), self.getY() + other.getY()))

    def __mul__(self, other):     return Point((self.getX() * other, self.getY() * other))
    def __truediv__(self, other): return Point((self.getX() / other, self.getY() / other))

    def getX(self): return self._x
    def getY(self): return self._y

    def addX(self, value): self._x += value
    def addY(self, value): self._y += value

    def setX(self, value): self._x = value
    def setY(self, value): self._y = value

    def asTuple(self): return self.getX(), self.getY()


class InterpolatedValue:
    value: float
    dest: float

    def __init__(self, value, rate):
        self.factor = 1
        self.value = value
        self.rate = rate
        self.dest = value

    def set_dest(self, dest):
        self.dest = dest

    def tick(self, ):
        self.value += round((self.dest - self.value) * self.rate, 5)


class InterpolatedPoint:
    def __init__(self, point: Point, rate):
        self.point = point
        self.rate = rate
        self.dest = point
        self.factor = InterpolatedValue(1, .6)
        self.tick()

    def set_dest(self, dest: Point):
        self.dest = dest
        return dest

    def tick(self, factor=None):
        if factor is not None: self.factor.set_dest(factor)

        self.point.addX(round((self.dest.getX() - self.point.getX()) * self.rate, 5))
        self.point.addY(round((self.dest.getY() - self.point.getY()) * self.rate, 5))
        self.factor.tick()

    def getX(self): return self.point.getX()  # * self.factor.value

    def getY(self): return self.point.getY()  # * self.factor.value


class Display:
    def __init__(self):
        self.base_font = None
        self.clock = None
        self.display = None
        self.settings = Settings()

        self.zoom_speed = 10
        self.scale = 100
        self.init_scale = self.scale
        self.Iscale = InterpolatedValue(self.scale, self.settings.rate)

        self.view = Point((0, 0))
        self.Iview = InterpolatedPoint(self.view, self.settings.rate)

        self.zoom_timer = 0
        self.zoom_msg_pos = 0

        self.toast_timer = 0
        self.toast_pos = 0
        self.toast_message = None
        self.toast_next_message = None

        self.click_circle_timer = 0
        self.click_circle_pos = (0, 0)
        self.objects = []

        self.draggables = set()
        self.dragging = None

    def run_forever(self, title=None):
        pg.init()
        filename = detect_importer_filename()
        cut = filename.rfind("\\", 0, filename.rfind("\\")) + 1
        pg.display.set_caption("↪ " + (title if title else "Whiteboard") + f" ↩ ({filename[cut:]})")
        self.clock = pg.time.Clock()
        self.display = pg.display.set_mode((1000, 1000), pg.RESIZABLE)
        self.base_font = pg.font.SysFont('serif', 48)

        print("Starting endless loop...")
        running = True
        while running:
            self.tick()
            for event in pg.event.get():
                if event.type != pg.QUIT: continue
                running = False
                pg.quit()

    def tick(self):
        self.clock.tick(self.settings.FPS)
        self.display.fill(self.settings.background)
        self.draw_grid()

        for obj in self.objects: obj.draw_me()
        self.zoom_tick()
        self.toast_tick()

        if self.settings.coordinates:
            message = f' X: {self.view.getX():.1f} Y: {self.view.getY():.1f} '
            self.display.blit(self.base_font.render(message, True, '#ffffff', '#000000'), (0, 0))

        self.draw_click_circle()

        for i in pg.event.get():
            if i.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif i.type == pg.MOUSEMOTION:
                if not pg.mouse.get_pressed()[0]: continue
                vector = (pg.mouse.get_pos(), (Point(pg.mouse.get_pos()) + Point(i.rel)).asTuple())
                if self.dragging:
                    self.dragging.drag()
                    continue
                self.click_circle_pos = pg.mouse.get_pos()
                pg.draw.line(self.display, self.settings.col2, *vector, width=10)
                self.view = self.Iview.set_dest(self.view + Point(i.rel))

            elif i.type == pg.MOUSEBUTTONDOWN:
                if i.button == pg.BUTTON_LEFT:
                    self.check_draggables()
                    self.click_circle_timer = 20
                    self.click_circle_pos = pg.mouse.get_pos()
                elif i.button == pg.BUTTON_WHEELUP:
                    self.set_zoom(self.scale + self.zoom_speed * self.scale / 20)
                elif i.button == pg.BUTTON_WHEELDOWN:
                    self.set_zoom(self.scale - self.zoom_speed * self.scale / 20)
                elif i.button == pg.BUTTON_RIGHT:
                    if self.scale != self.init_scale:
                        self.set_zoom(self.init_scale)
                    else:
                        self.set_zoom(self.init_scale * 2)
                elif i.button == pg.BUTTON_MIDDLE:
                    if dist(self.view.asTuple(), (0, 0)) > 10:
                        self.toast("Going to center...", 100)
                        self.view = Point((0, 0))
                        self.Iview.set_dest(self.view)

            elif i.type == pg.MOUSEBUTTONUP:
                if i.button == pg.BUTTON_LEFT:
                    self.dragging = None

            elif i.type == pg.KEYDOWN:
                if i.key == pg.K_e:
                    if self.settings.coordinates:
                        self.toast("Координаты OFF")
                    else:
                        self.toast("Координаты ON")
                    self.settings.coordinates = not self.settings.coordinates

        self.Iscale.tick()
        self.Iview.tick()

        pg.display.update()

    def check_draggables(self):
        for draggable in self.draggables:
            draggable: GraphDraggable
            if draggable.check(pg.mouse.get_pos()):
                draggable.on_click()
                self.dragging = draggable
                return True
        return False

    def draw_click_circle(self):
        if self.click_circle_timer <= 0: return

        self.click_circle_timer -= 1
        interpolation = sin(self.click_circle_timer / 40 * pi)
        pg.draw.circle(self.display, self.settings.col3, self.click_circle_pos, int((1 - interpolation) * 30),
                       width=int(interpolation * 10 + 1))

    def zoom_tick(self):
        if self.zoom_msg_pos > 0:
            message = f' Zoom: {self.Iscale.value / self.init_scale:.2f}x '
            location = self.base_font.render(message, True, '#ffffff', '#000000')
            self.display.blit(location,
                              (self.midX() - len(message) / 2 * 21, sin(self.zoom_msg_pos / 200 * pi) * 60 - 60))

        if self.zoom_timer > 0:
            self.zoom_msg_pos = min(self.zoom_msg_pos + 15, 100)
            self.zoom_timer -= 1
        else:
            if self.zoom_msg_pos > 0: self.zoom_msg_pos = max(self.zoom_msg_pos - 3, 0)

    def toast_tick(self):
        if self.toast_message is None: return

        lines = self.toast_message.count("\n") + 1
        if self.toast_pos > 0:
            locations = [
                self.base_font.render(f" {msg} ", True, '#ffffff', '#222222') for msg in self.toast_message.split("\n")
            ]
            self.toast_message: str
            for i, location in enumerate(locations):
                self.display.blit(location, (10,
                     self.display.get_height()
                     - sin(self.toast_pos / 200 * pi) * 60 * lines + 60 * (lines - 1)
                     - 53 * (len(locations) - i - 1)
                     )
                )

        if self.toast_timer > 0 and self.toast_next_message is None:
            if self.toast_pos < 100:
                self.toast_pos += 5
                if self.toast_pos > 100: self.toast_pos = 100
            else:
                self.toast_timer -= 1 if self.toast_next_message is None else 5
                if self.toast_timer < 0: self.toast_timer = 0
        else:
            if self.toast_pos > 0:
                self.toast_pos -= 5 if self.toast_next_message is None else 15
            else:
                self.toast_message = self.toast_next_message
                self.toast_next_message = None

    def midX(self):
        return self.display.get_width() // 2

    def midY(self):
        return self.display.get_height() // 2

    def draw_grid(self):
        scale = self.Iscale.value
        view_x, view_y = self.Iview.getX(), self.Iview.getY()

        count_x = ceil(self.display.get_width() / scale) + 1
        count_y = ceil(self.display.get_height() / scale) + 1
        x1 = view_x % scale - scale * ceil((count_x + 1) / 2)
        y1 = view_y % scale - scale * ceil((count_y + 1) / 2)
        lines_scale = int(min(max(scale // 100, 1), 3))
        font = pg.font.SysFont('serif', int(max(1, scale / self.init_scale * 20)))

        for i in range(count_x + 1):
            P = int(x1 + self.midX() + i * scale)
            pg.draw.line(self.display, self.settings.line, (P, self.display.get_height()), (P, 0), width=lines_scale)

            if self.settings.coordinates:
                static_x = (i - ceil((count_x + 1) / 2) - view_x // scale)
                stamp = font.render(f"{static_x:.0f}x", True, "#ffff55")
                self.display.blit(stamp, (P, self.midY()))
                pg.draw.circle(self.display, "#ffff55", (P, self.midY()), 2)

        for i in range(count_y + 1):
            P = int(y1 + self.midY() + i * scale)
            pg.draw.line(self.display, self.settings.line, (self.display.get_width(), P), (0, P), width=lines_scale)

            if self.settings.coordinates:
                static_y = (ceil((count_y + 1) / 2) - i + view_y // scale)
                stamp = font.render(f"{static_y:.0f}y", True, "#ffff11")
                self.display.blit(stamp, (self.midX(), P))
                pg.draw.circle(self.display, "#ffff11", (self.midX(), P), 2)

        # Middle marker
        # pg.draw.line(self.display, self.settings.col4, (self.display.get_width(), self.midX()), (0, self.midX()))
        # pg.draw.line(self.display, self.settings.col4, (self.midY(), self.display.get_height()), (self.midY(), 0))

    def set_zoom(self, zoomV):
        prev = self.scale
        self.scale = min(max(zoomV, 1), 5000)
        if abs(self.scale - self.init_scale) < 10: self.scale = self.init_scale
        self.Iscale.set_dest(self.scale)
        self.zoom_timer = 100
        self.view = self.view * (self.scale / prev)
        self.Iview.set_dest(self.view)

    def add_object(self, obj):
        assert isinstance(obj, AbstractGraph)
        self.objects.append(obj)
        if isinstance(obj, GraphDraggable): self.draggables.add(obj)

    def add_objects(self, *objs):
        for obj in objs: self.add_object(obj)

    def insert_object(self, obj, index):
        assert isinstance(obj, AbstractGraph)
        self.objects.insert(index, obj)
        if isinstance(obj, GraphDraggable): self.draggables.add(obj)

    def toast(self, message: str, timeMS: int = 1000):
        if self.toast_pos > 0:
            self.toast_next_message = message
            self.toast_timer = timeMS / 10
        else:
            self.toast_message = message
            self.toast_timer = timeMS / 10

    def await_key(self, key: str):
        true_key = ord(key.lower()) if type(key) == str else key
        while True:
            keys = pg.key.get_pressed()
            if keys[true_key]: break
            sleep(0.05)

    def scaling(self):  return self.scale / self.init_scale
    def Iscaling(self): return self.Iscale.value / self.init_scale


class AbstractGraph:
    def __init__(self, display: Display): self.display = display

    def draw(self, *args, **kwargs): pass

    def transformX(self, x): return x * self.display.Iscale.value + self.display.midX() + self.display.Iview.getX()
    def transformY(self, y): return y * self.display.Iscale.value + self.display.midY() + self.display.Iview.getY()

    def restoreX(self, x): return (x - self.display.midX()) / self.display.scale - self.display.view.getX() / self.display.scale
    def restoreY(self, y): return (y - self.display.midY()) / self.display.scale - self.display.view.getY() / self.display.scale


class GraphImage(AbstractGraph):
    def __init__(self, display: Display, x, y, x_size, y_size, image_path):
        super().__init__(display)
        self.image = pg.image.load(image_path)
        self.x, self.y = x, -y
        self.x_size, self.y_size = x_size, y_size

    def draw_me(self):
        scaled_image = pg.transform.scale(self.image, (self.x_size * self.display.Iscale.value, self.y_size * self.display.Iscale.value))
        image_rect = scaled_image.get_rect()
        image_rect.center = (
            self.transformX(self.x),
            self.transformY(self.y)
        )
        self.display.display.blit(scaled_image, image_rect)


class GraphDraggable(AbstractGraph):
    def __init__(self, display: Display, x, y, color="#ff0011", size=1, snap=None, blocked_axis=""):
        super().__init__(display)
        self.blocked_axis = blocked_axis.lower()
        self.size = size
        self.x, self.y = x, -y
        self.color = color
        self.Ipos = InterpolatedPoint(Point((x, -y)), 0.4)
        self.snap = snap

    def draw_me(self):
        self.Ipos.tick(1)
        self.radius = self.display.Iscale.value / 4 * self.size
        self.center = (self.transformX(self.Ipos.getX()), self.transformY(self.Ipos.getY()))

        pg.draw.circle(self.display.display, self.color, self.center, self.radius)
        pg.draw.circle(self.display.display, "#000000", self.center, self.radius, 5)

    def on_click(self):
        pass

    def check(self, pos):
        return (pos[0] - self.transformX(self.x)) ** 2 + (pos[1] - self.transformY(self.y)) ** 2 <= self.radius ** 2

    def drag(self):
        x = self.restoreX(pg.mouse.get_pos()[0]) if "x" not in self.blocked_axis else self.x
        y = self.restoreY(pg.mouse.get_pos()[1]) if "y" not in self.blocked_axis else self.y
        if self.snap:
            self.x, self.y = map(lambda i: round(i / self.snap) * self.snap, (x, y))
        else:
            self.x, self.y = x, y
        self.Ipos.set_dest(Point(self.x, self.y))

class GraphRect(AbstractGraph):
    def __init__(self, display: Display, x, y, x_size, y_size, color="#44ff44"):
        super().__init__(display)
        self.color = color

        self.x, self.y = x, -y
        self.x_size, self.y_size = x_size, y_size

    def draw_me(self):
        rect = (
            self.transformX(self.x - self.x_size / 2),
            self.transformY(self.y - self.y_size / 2),

            self.x_size * self.display.Iscale.value,
            self.y_size * self.display.Iscale.value
        )
        pg.draw.rect(self.display.display, self.color, rect)


class GraphText(AbstractGraph):
    def __init__(self, display: Display, text, x, y, color="#eeeeee", scale=None):
        super().__init__(display)
        self.color = color
        self.x, self.y = x, -y

        self._font = pg.font.SysFont('serif', int((100 if scale is None else scale) * 100 / self.display.scale))
        self.scale = scale

        self.change(text=text)

    def draw_me(self):
        if self.scale: self.update()
        self.display.display.blit(self.stamp, (self.transformX(self.x) - self.stamp.get_width() // 2, self.transformY(self.y) - self.stamp.get_height() // 2))

    def update(self):
        if self.scale:
            self._font = pg.font.SysFont('serif',
                int(max(1, min(3000, self.display.Iscale.value / self.display.init_scale * self.scale))))
        self.stamp = self._font.render(self._text, True, self.color)

    def change(self, text=None):
        if text is not None: self._text = text
        self.update()


class GraphDot(AbstractGraph):
    def __init__(self, display: Display, x, y, color="#44ff44", scale=30, shadow=False, label=None):
        super().__init__(display)
        self.label = label
        self.shadow = shadow
        self.scale = scale
        self.color = color
        self.x, self.y = x, -y

    def draw_me(self):
        scale = max(1, int(self.scale * self.display.Iscale.value / self.display.init_scale))
        center = (self.transformX(self.x), self.transformY(self.y))
        if self.shadow: pg.draw.circle(self.display.display, "#000000", center, scale + 2)
        pg.draw.circle(self.display.display, self.color, center, scale)
        if self.label:
            self._font = pg.font.SysFont('serif', int(max(1, min(3000, self.display.Iscale.value / self.display.init_scale * 50))))
            stamp = self._font.render(self.label, True, "#ffffff")
            self.display.display.blit(stamp, (self.transformX(self.x) - stamp.get_width()  // 2,
                                              self.transformY(self.y) - self.scale * self.display.Iscaling() - stamp.get_height()))

class GraphLine(AbstractGraph):
    def __init__(self, display: Display, xF, yF, xT, yT, color="#ff4444", width=3):
        super().__init__(display)
        self.color = color
        self.width = width
        self.From, self.To = (xF, -yF), (xT, -yT)

    def draw_me(self):
        pg.draw.line(self.display.display, self.color,
                     (self.transformX(self.From[0]), self.transformY(self.From[1])),
                     (self.transformX(self.To[0]), self.transformY(self.To[1])),
                     width=self.width)

    def setFrom(self, xF, yF): self.From = (xF, yF)
    def setTo(self, xT, yT): self.To = (xT, yT)


class GraphPlot(AbstractGraph):
    def __init__(self, display: Display, function, step=100, static: bool = True, maxSize: int = 100, color: str = None):
        super().__init__(display)
        self.quality = step
        self.function = function
        self.static = static
        if static:
            self.values = {}
            self.mSize = maxSize
        self.name = None
        self.color = (randint(100, 255), randint(100, 255), randint(100, 255)) if color is None else color

    def set_tag(self, name: str, color: str):
        self.name = name
        self.color = color

    def draw_me(self):
        prev = None
        factor = self.display.init_scale / self.display.scale
        left_edge = (- self.display.view.getX() - self.display.midX()) / self.display.scale * 10
        right_edge = left_edge + 100 * factor

        used_values = set()
        for j in range(int(left_edge), int(right_edge) + 1):
            used_values.add(j)
            i = j / self.quality
            if self.static and j in self.values:
                joint = self.values[j]
            else:
                try:
                    joint = self.function(i)
                except (ArithmeticError, ValueError):
                    joint = None
                if self.static:
                    self.values[j] = joint

            if joint is not None:
                new_point = self.transformX(i), self.transformY(-joint)
            if prev is not None and joint is not None:
                # noinspection PyUnboundLocalVariable
                pg.draw.line(self.display.display, self.color, prev, new_point)
            elif joint is None and prev is not None:
                pg.draw.circle(self.display.display, self.color, prev, 3)

            prev = new_point if joint is not None else None

        if self.static and len(self.values) > self.mSize:
            keyset = tuple(self.values.keys())
            for key in keyset:
                if key in used_values: continue
                del self.values[key]


if __name__ == "__main__":
    dp = Display()
    thread = threading.Thread(target=dp.run_forever, args=("Графики...",))
    thread.start()

    st = time()
    dp.settings.darkMode()
