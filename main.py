# pyright: reportUnusedCallResult=false
# pyright: reportExplicitAny=false

import abc
from collections.abc import Iterable
from typing import Any
import pygame as pg
import colorsys

WHITE = 0xffffff
BLACK = 0x000000

SIZE = 500, 500

ADD_PER_SEC = 100

class SupportsSub(abc.ABC):
    @abc.abstractmethod
    def __sub__(self, other: Any) -> Any: ...  # pyright: ignore[reportAny]

def hsl_to_rgb255(h: int, s: int, l: int):
    """
    Converts HSL values (h: 0-360, s/l: 0-100) to RGB values (0-255).
    """
    h_normalized = h / 360.0
    s_normalized = s / 100.0
    l_normalized = l / 100.0

    r_normalized, g_normalized, b_normalized = colorsys.hls_to_rgb(h_normalized, l_normalized, s_normalized)

    r = int(round(r_normalized * 255))
    g = int(round(g_normalized * 255))
    b = int(round(b_normalized * 255))

    return r, g, b

def tuple_sub[T1: SupportsSub, T2: SupportsSub](t1: tuple[T1, ...], t2: tuple[T2, ...]) -> tuple[T1 | T2, ...]:
    new_tuple = tuple()
    for v1, v2 in zip(t1, t2):
        new_tuple = (*new_tuple, v1 - v2)
    return new_tuple

pg.init()

clock = pg.Clock()
displaysurf = pg.display.set_mode(SIZE, flags=pg.NOFRAME)

pg.display.set_caption('Some Window')

will_fill: int | tuple[int, int, int] = 0
clicked: int = 0
clicked_pos: pg.Rect = pg.Rect(0, 0, 0, 0)

prev_mouse_pos = None

delta_sec: float = 0.0
looping = True
while looping:
    event: pg.event.Event
    for event in pg.event.get():
        if event.type == pg.QUIT:
            looping = False
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:  # pyright: ignore[reportAny]
                looping = False
        elif event.type == pg.MOUSEBUTTONDOWN:
            prev_mouse_pos = pg.mouse.get_pos()
            if not clicked_pos.collidepoint(prev_mouse_pos):
                clicked_pos = pg.Rect(prev_mouse_pos[0] - 5, prev_mouse_pos[1] - 5, 10, 10)
                clicked = 1
            else:
                clicked += 1
                if clicked >= 10:
                    #will_fill = (123, 88, 88)
                    if isinstance(will_fill, tuple):
                        will_fill = (123, (will_fill[1] + 10) % 100, (will_fill[2] + 10) % 100)
                    else:
                        will_fill = (123, 65, 65)
                    clicked = 0
        elif event.type == pg.MOUSEBUTTONUP:
            prev_mouse_pos = None
        elif prev_mouse_pos and event.type == pg.MOUSEMOTION:
            mouse_pos = pg.mouse.get_pos()
            diff = tuple_sub(prev_mouse_pos, mouse_pos)  # pyright: ignore[reportArgumentType, reportUnknownVariableType]
            window_pos = pg.display.get_window_position()
            pos = tuple_sub(window_pos, diff)  # pyright: ignore[reportArgumentType, reportUnknownArgumentType, reportUnknownVariableType]
            pg.display.set_window_position(pos)  # pyright: ignore[reportUnknownArgumentType]

    is_wf_iterable = isinstance(will_fill, Iterable)
    if is_wf_iterable:
        color = hsl_to_rgb255(*will_fill)  # pyright: ignore[reportGeneralTypeIssues, reportUnknownArgumentType]
    else:
        color = hsl_to_rgb255(will_fill, 55, 55)  # pyright: ignore[reportArgumentType]
    if color[0] > 255:
        color = (color[0] % 255, color[1], color[2])
    if color[1] > 255:
        color = (color[0], color[1] % 255, color[2])
    if color[2] > 255:
        color = (color[0], color[1], color[2] % 255)
    displaysurf.fill(color)
    print(color)
    if is_wf_iterable:
        will_fill = tuple(will_fill)  # pyright: ignore[reportArgumentType, reportUnknownVariableType]
        will_fill = (will_fill[0] + int(ADD_PER_SEC * delta_sec), will_fill[1], will_fill[2])
        if will_fill[0] > 360:
            will_fill = (0, will_fill[1], will_fill[2])
    else:
        will_fill += int(ADD_PER_SEC * delta_sec)  # pyright: ignore[reportOperatorIssue, reportUnknownVariableType]
        if will_fill > 360:
            will_fill = 0

    pg.display.flip()
    delta_sec = clock.tick(60) / 1000

pg.quit()
