from textual.widget import Widget
from textual.message import Message
from rich.segment import Segment
from rich.style import Style
from rich.color import Color
from rich.console import Console
from rich.console import ConsoleOptions
from rich.console import (
    Console,
    ConsoleOptions,
    RenderResult,
    RenderableType,
)
from textual.message import Message
from textual import events
from textual.reactive import Reactive
from enum import Enum
from typing import List


class Grid(Enum):
    g8x8 = 4
    g16x16 = 2
    g32x32 = 1


class MouseStatus(Message):
    def __init__(self, sender: Widget, pos: tuple):
        super().__init__(sender)
        self.pos = pos


class Canvas(Widget):
    """The digital display of the calculator."""

    matrix: Reactive[List[List[Color]]] = Reactive([[]])
    mouse_pos: tuple = (0, 0)
    current_color: Color = Color.from_rgb(0, 0, 0)
    is_painting: bool = False

    def __init__(
        self, w: int = 60, h: int = 60, grid: Grid = Grid.g8x8, *args, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.grid = grid
        self.w = w // 2
        self.h = h // 2
        self.matrix = [
            [Color.from_rgb(0, 0, 32 + 32 * ((-1) ** (y + x))) for y in range(h)]
            for x in range(w)
        ]
        self.under_mouse_color = self.matrix[0][0]

    def update(self):
        self.refresh()

    def render(self) -> RenderableType:
        return self

    async def on_mouse_move(self, event: events.MouseMove) -> None:
        # y, x = event.y*2, event.x
        if self.is_painting:
            self.under_mouse_color = self.current_color

        y, x = self.mouse_pos
        if y != -1:
            self.matrix[y][x] = self.under_mouse_color
        self.mouse_pos = (event.y // self.grid.value, event.x // (2 * self.grid.value))
        y, x = self.mouse_pos
        self.under_mouse_color = self.matrix[y][x]
        self.matrix[y][x] = self.current_color
        await self.emit(MouseStatus(self, self.mouse_pos))
        self.update()

    async def on_click(self, event: events.Click) -> None:
        self.under_mouse_color = self.current_color

    def on_mouse_down(self, event: events.MouseUp) -> None:
        # return await super().on_mouse_down(event)
        self.is_painting = True
        
    def on_mouse_up(self, event: events.MouseUp) -> None:
        # return await super().on_mouse_down(event)
        self.is_painting = False
        
    def set_color(self, color: Color):
        self.current_color = color

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:

        for y in range(0, self.h):
            y = y // self.grid.value
            for x in range(0, self.w):
                bgcolor = self.matrix[y][x]
                color = self.matrix[y][x]
                yield Segment(
                    "▄▄" * self.grid.value, Style(bgcolor=bgcolor, color=color)
                )
            yield Segment.line()

    def on_leave(self, _):
        y, x = self.mouse_pos
        self.matrix[y][x] = self.under_mouse_color
        self.mouse_pos = (-1, -1)
        self.update()
