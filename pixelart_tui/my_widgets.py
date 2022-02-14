from rich.align import Align
from rich.console import (
    RenderableType,
)
from rich.align import Align
from rich.console import RenderableType
from textual.reactive import Reactive
from textual.views import GridView
from textual.widget import Widget
from textual import events

from rich.panel import Panel

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
from pixelart_tui.my_button import MyButton
from typing import List

from pixelart_tui.my_messages import DebugStatus, ColorStatus, LoadSaveStatus


def minmax(a, mn, mx):
    return max(min(mx, a), mn)


class LoadSave(Widget):
    chosen: Reactive = Reactive(0)

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        ...
        u = "────"
        ub = "━━━━"

        u1 = ub if self.chosen == 1 else u
        u2 = ub if self.chosen == 2 else u
        t1 = "[b]Load[/b]" if self.chosen == 1 else "Load"
        t2 = "[b]Save[/b]" if self.chosen == 2 else "Save"
        yield (f"\n" f" {t1}    {t2} \n" f" {u1}    {u2}")

    def render(self) -> RenderableType:
        return self

    async def on_click(self, event: events.Click) -> None:
        if self.chosen == 1:
            await self.emit(LoadSaveStatus(self, "Load"))
        elif self.chosen == 2:
            await self.emit(LoadSaveStatus(self, "Save"))

    async def on_mouse_move(self, event: events.MouseMove) -> None:
        if 1 <= event.x <= 4:
            self.chosen = 1
        elif 8 <= event.x <= 12:
            self.chosen = 2
        else:
            self.chosen = 0

    async def on_leave(self, _):
        self.chosen = 0


class ColorBox(Widget):
    red: Reactive[int] = Reactive(0)
    green: Reactive[int] = Reactive(0)
    blue: Reactive[int] = Reactive(0)
    saved: Reactive[List[Color]] = Reactive(
        [Color.from_rgb(0, 0, 0) for _ in range(35)]
    )
    chosen: Reactive = Reactive(0)
    to_display: Reactive = Reactive(Color.from_rgb(0, 0, 0))

    def __init__(self, r: int, g: int, b: int, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.red = r
        self.green = g
        self.blue = b
        self.saved[self.chosen]

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        max_h = self._size.height
        max_w = self._size.width
        col = ["red", "green", "blue"]
        val = self.get_color().get_truecolor()
        for y in range(0, 3):
            for x in range(3):
                yield Segment("██", Style(color=self.to_display))
            yield Segment("|")
            yield Segment(f"{col[y][0]}: {val[y]}", Style(color=col[y]))

            yield Segment.line()
        yield Segment("─" * max_w)
        yield Segment.line()
        for y in range(0, 7):
            for x in range(5):
                c = self.saved[y * 5 + x]
                if y * 5 + x == self.chosen:
                    yield Segment("━━", Style(color=c))
                else:
                    yield Segment("██", Style(color=c))
                yield Segment("│")
                # yield Segment(" ")
            yield Segment.line()
            # yield Segment("──┼"*(max_w//3))
            yield Segment("── " * (max_w // 3 + 1))
            if y < 5:
                yield Segment("  +" * (max_w // 3 + 1))
            else:
                yield Segment("---" * (max_w // 3 + 1))
            yield Segment.line()

    def render(self) -> RenderableType:
        return self

    def update(self, red=None, green=None, blue=None):
        if red is not None:
            self.red = red
        if green is not None:
            self.green = green
        if blue is not None:
            self.blue = blue
        self.saved[self.chosen] = Color.from_rgb(self.red, self.green, self.blue)
        self.to_display = self.saved[self.chosen]

    def display(self, color):
        self.to_display = color
        self.refresh()

    def get_color(self):
        r, g, b = self.saved[self.chosen].get_truecolor()
        return Color.from_rgb(r, g, b)

    async def on_click(self, event: events.Click) -> None:
        # 4, 0
        y, x = event.y, event.x
        if y >= 4 and y % 2 == 0:
            if x % 3 != 2:
                self.chosen = (y - 4) // 2 * 5 + x // 3
                self.red, self.green, self.blue = self.saved[
                    self.chosen
                ].get_truecolor()
        await self.emit(
            ColorStatus(
                self,
                {
                    "red": self.red,
                    "green": self.green,
                    "blue": self.blue,
                },
            )
        )
        await self.emit(DebugStatus(self, f"{y} {x} {self.chosen}"))


class ColorWidget(Widget):
    value: Reactive = Reactive(255)

    def __init__(self, color: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.color = color
        self.value = 0
        self.fill = 0

    def render(self) -> RenderableType:
        max_h = self._size.height
        max_w = self._size.width - 4
        a = ("█" * max_w + "\n") * self.fill
        b = " \n" * (max_h - self.fill)
        c = a + b
        return Panel(
            c,
            style=self.color,
        )

    def update(self, value):
        self.value = value
        self.fill = value * self._size.height // 255

    async def on_click(self, event: events.Click) -> None:
        max_h = self._size.height - 2
        self.fill = minmax(event.y, 0, max_h)
        self.value = 255 * self.fill // max_h
        await self.emit(ColorStatus(self, {self.color: self.value}))


class StatusWidget(Widget):
    alive: Reactive = Reactive(True)
    points: Reactive = Reactive(0)
    pos: Reactive = Reactive((0, 0))
    debug: Reactive = Reactive("")

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def render(self) -> RenderableType:
        w = (
            f"Alive: [b red]{self.alive}[/b red] :red_heart:"
            f"\n\n"
            f"Points: [b red]{self.points}[/b red] :glowing_star:"
            f"\n\n"
            f"Pos: [b red]{self.pos}[/b red]"
            f"\n\n"
            f"[b blue]{self.debug}[/b blue]"
        )
        return Panel(
            Align.center(
                w,
                vertical="middle",
            ),
            title="Status",
            style="yellow",
        )


class ToolsWidget(GridView):
    def __init__(
        self,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        ...

    def on_mount(self) -> None:
        self.grid.set_gap(1, 1)
        self.grid.set_gutter(0)
        self.grid.set_align("center", "center")

        self.grid.add_column("cola", min_size=7, max_size=7)
        self.grid.add_column("colb", min_size=7, max_size=7)
        self.grid.add_column("colc", min_size=7, max_size=7)
        self.grid.add_column("cold", min_size=6, max_size=6)
        self.grid.add_column("cole", min_size=6, max_size=6)
        self.grid.add_row("row", repeat=2)

        self.grid.add_areas(new="cold-start|cole-end,row1")
        self.grid.add_areas(pick="cold-start|cole-end,row2")
        self.grid.add_areas(paint="cola-start|colc-end,row2")

        self.g8 = MyButton(label="8 \n x\n  8", style="red", value="8")
        self.g16 = MyButton(label="16 \n x\n 16", style="green", value="16")
        self.g32 = MyButton(label="32 \n x\n 32", style="blue", value="32")

        self.new = MyButton(
            label=Align("New\n  Canvas", align="center"), style="white", value="new"
        )
        self.pick_tool = MyButton(label="Pick \n  Color", style="yellow", value="pick")
        self.paint_tool = MyButton(label="\nPaint", style="yellow", value="paint")

        self.grid.place(self.new, self.g8, self.g16, self.g32)

        self.grid.place(new=self.new)
        self.grid.place(pick=self.pick_tool)
        self.grid.place(paint=self.paint_tool)
