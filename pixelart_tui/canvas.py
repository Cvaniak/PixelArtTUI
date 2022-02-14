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
from abc import ABC

from pixelart_tui.my_widgets import ColorStatus


class Grid(Enum):
    g8x8 = 4
    g16x16 = 2
    g32x32 = 1


class MouseStatus(Message):
    def __init__(self, sender: Widget, pos: tuple):
        super().__init__(sender)
        self.pos = pos


class ColorUnderMouse(Message):
    def __init__(self, sender: Widget, change: bool, color: Color):
        super().__init__(sender)
        self.change: bool = change
        self.color: Color = color


class Tool(ABC):
    current_color: Color = Color.from_rgb(0, 0, 0)
    mouse_pos: tuple = (0, 0)

    def __init__(self, canvas, color) -> None:
        self.canvas = canvas
        self.current_color = color
        self.under_mouse_color: Color = canvas.matrix[0][0]

    async def on_mouse_down(self, event: events.MouseDown):
        ...

    async def on_mouse_up(self, event: events.MouseUp):
        ...

    async def on_mouse_move(self, event: events.MouseMove):
        ...

    async def on_click(self, event: events.Click):
        ...

    async def on_leave(self, event):
        ...

    def set_color(self, color: Color):
        self.current_color = color

    async def show_on_grid(self, xx, yy):
        y, x = self.mouse_pos
        if y != -1:
            self.canvas.matrix[y][x] = self.under_mouse_color
        self.mouse_pos = (
            yy // self.canvas.grid.value,
            xx // (2 * self.canvas.grid.value),
        )
        y, x = self.mouse_pos
        self.under_mouse_color = self.canvas.matrix[y][x]
        self.canvas.matrix[y][x] = self.current_color
        await self.canvas.emit(MouseStatus(self.canvas, self.mouse_pos))
        self.canvas.update()


class ToolPaint(Tool):
    is_painting: bool = False

    def __init__(self, canvas, color) -> None:
        super().__init__(canvas, color)

    async def on_mouse_down(self, event: events.MouseDown):
        self.is_painting = True

    async def on_mouse_up(self, event: events.MouseUp):
        self.is_painting = False

    async def on_mouse_move(self, event: events.MouseMove):
        if self.is_painting:
            self.under_mouse_color = self.current_color

        await self.show_on_grid(event.x, event.y)

    async def on_click(self, event: events.Click):
        self.under_mouse_color = self.current_color

    async def on_leave(self, event):
        y, x = self.mouse_pos
        self.canvas.matrix[y][x] = self.under_mouse_color
        self.mouse_pos = (-1, -1)
        self.canvas.update()


class ToolPick(Tool):
    async def on_mouse_down(self, event: events.MouseDown):
        ...

    async def on_mouse_up(self, event: events.MouseUp):
        ...

    async def on_mouse_move(self, event: events.MouseMove):
        await self.show_on_grid(event.x, event.y)

        await self.canvas.emit(
            ColorUnderMouse(self.canvas, False, self.under_mouse_color)
        )

    async def on_click(self, event: events.Click):
        await self.canvas.emit(
            ColorUnderMouse(self.canvas, True, self.under_mouse_color)
        )

    async def on_leave(self, event):
        y, x = self.mouse_pos
        self.canvas.matrix[y][x] = self.under_mouse_color
        self.mouse_pos = (-1, -1)
        await self.canvas.emit(ColorStatus(self, {}))
        self.canvas.update()


class Tools(Enum):
    PAINT = ToolPaint
    PICK = ToolPick


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
        self.tool: Tool = ToolPaint(self, self.current_color)

    def set_tool(self, tool: Tools):
        self.tool = tool.value(self, self.current_color)

    async def on_mouse_move(self, event: events.MouseMove) -> None:
        await self.tool.on_mouse_move(event)

    async def on_click(self, event: events.Click) -> None:
        await self.tool.on_click(event)

    async def on_mouse_down(self, event: events.MouseDown) -> None:
        await self.tool.on_mouse_down(event)

    async def on_mouse_up(self, event: events.MouseUp) -> None:
        await self.tool.on_mouse_up(event)

    async def on_leave(self, event):
        await self.tool.on_leave(event)

    def set_color(self, color: Color):
        self.current_color = color
        self.tool.set_color(color)

    def update(self):
        self.refresh()

    def render(self) -> RenderableType:
        return self

    def set_matrix(self):
        w, h = self.w * 2, self.h * 2
        self.matrix = [
            [Color.from_rgb(0, 0, 32 + 32 * ((-1) ** (y + x))) for y in range(h)]
            for x in range(w)
        ]

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
