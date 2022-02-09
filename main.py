from rich.align import Align
from rich.console import (
    RenderableType,
)
from rich.align import Align
from rich.console import RenderableType

from textual.app import App
from textual.reactive import Reactive
from textual.views import GridView
from textual.widget import Widget
from textual.widgets import Footer, Header
from textual import events

from textual.app import App
from rich.panel import Panel

from canvas import Canvas, MouseStatus
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
from textual_inputs import TextInput
from file_tools import save_pxl, load_pxl, save_pal, load_pal


def minmax(a, mn, mx):
    return max(min(mx, a), mn)


class DebugStatus(Message):
    def __init__(self, sender: Widget, mes: str):
        super().__init__(sender)
        self.mes = mes


class ColorStatus(Message):
    def __init__(self, sender: Widget, color: dict):
        super().__init__(sender)
        self.color = color


class LoadSaveStatus(Message):
    def __init__(self, sender: Widget, loadsave: str):
        super().__init__(sender)
        self.loadsave = loadsave


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
    red: Reactive = Reactive(0)
    green: Reactive = Reactive(0)
    blue: Reactive = Reactive(0)
    saved: Reactive = Reactive([Color.from_rgb(0, 0, 0) for _ in range(35)])
    chosen: Reactive = Reactive(0)

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
                yield Segment("██", Style(color=self.get_color()))
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

    def get_color(self):
        r, g, b = self.saved[self.chosen].get_truecolor()
        return Color.from_rgb(r, g, b)
        # return f"rgb({r},{g},{b})"

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

    async def on_mouse_move(self, _: events.MouseMove) -> None:
        ...

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


class Layout(GridView):
    def __init__(
        self,
        w: int,
        h: int,
        canvas: Canvas,
        status: StatusWidget,
        c_red: ColorWidget,
        c_green: ColorWidget,
        c_blue: ColorWidget,
        c_box: ColorBox,
        name_input: TextInput,
        loadsave: LoadSave,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.w = w
        self.h = h
        self.canvas = canvas
        self.status = status
        self.c_red = c_red
        self.c_green = c_green
        self.c_blue = c_blue
        self.c_box = c_box
        self.name_input = name_input
        self.loadsave = loadsave

    def on_mount(self) -> None:
        # Attributes to store the current calculation
        self.grid.set_gap(2, 1)
        self.grid.set_gutter(1)
        self.grid.set_align("center", "center")

        # One pixel in y is twice size
        w, h = self.w, self.h // 2
        h1 = 18
        h2 = 3
        h3 = h - h1 - h2
        # Create rows / columns / areas
        self.grid.add_column("gamw", min_size=w, max_size=w)
        self.grid.add_row("gamh", min_size=h1, max_size=h1)
        self.grid.add_row("text", min_size=h2, max_size=h2)
        self.grid.add_row("colo", min_size=h3, max_size=h3)
        self.grid.add_column("panel", min_size=6, max_size=6, repeat=5)

        self.grid.add_areas(
            game="gamw,gamh-start|colo-end", panel="panel1-start|panel5-end,colo"
        )
        self.grid.add_areas(red="panel1,gamh", green="panel2,gamh", blue="panel3,gamh")
        self.grid.add_areas(text="panel1-start|panel3-end,text")
        self.grid.add_areas(box="panel4-start|panel5-end,gamh")
        self.grid.add_areas(loadsave="panel4-start|panel5-end,text")
        # Place out widgets in to the layout
        self.grid.place(game=self.canvas)
        self.grid.place(panel=self.status)
        self.grid.place(red=self.c_red)
        self.grid.place(green=self.c_green)
        self.grid.place(blue=self.c_blue)
        self.grid.place(text=self.name_input)
        self.grid.place(box=self.c_box)
        self.grid.place(loadsave=self.loadsave)


class SimpleApp(App):
    async def on_load(self, _: events.Load) -> None:
        await self.bind("q", "quit", "Quit")
        await self.bind("r", "reset()", "Reset")

    async def on_mount(self) -> None:
        w, h = 64, 64
        self.status = StatusWidget()
        self.canvas = Canvas(w, h)

        self.c_red = ColorWidget("red")
        self.c_green = ColorWidget("green")
        self.c_blue = ColorWidget("blue")
        self.c_box = ColorBox(0, 0, 0)

        self.name_input = TextInput(placeholder="file_name")
        self.loadsave = LoadSave()

        self.layout = Layout(
            w,
            h,
            self.canvas,
            self.status,
            self.c_red,
            self.c_green,
            self.c_blue,
            self.c_box,
            self.name_input,
            self.loadsave,
        )

        style_fh = "white on rgb(111,22,44)"
        await self.view.dock(Header(style=style_fh), edge="top")
        # Fix style of footer
        await self.view.dock(Footer(), edge="bottom")
        await self.view.dock(self.layout, edge="left")

    async def handle_mouse_status(self, message: MouseStatus):
        self.status.pos = message.pos

    async def handle_debug_status(self, message: DebugStatus):
        self.status.debug = message.mes

    async def handle_color_status(self, message: ColorStatus):
        self.c_box.update(**message.color)
        r, g, b = self.c_box.get_color().get_truecolor()
        self.c_red.update(r)
        self.c_green.update(g)
        self.c_blue.update(b)
        self.canvas.set_color(self.c_box.get_color())

    async def handle_load_save_status(self, message: LoadSaveStatus):
        format = {"pxl", "pal"}
        file_name = self.name_input.value
        end = file_name.split(".")[-1]
        if not end in format:
            return

        if end == "pxl":
            if message.loadsave == "Save":
                save_pxl(self.canvas.matrix, file_name)
            elif message.loadsave == "Load":
                load_pxl(self.canvas.matrix, file_name)
                self.canvas.refresh()

        elif end == "pal":
            if message.loadsave == "Save":
                save_pal(self.c_box.saved, file_name)
            elif message.loadsave == "Load":
                load_pal(self.c_box.saved, file_name)
                self.canvas.set_color(self.c_box.get_color())
                self.c_box.refresh()


SimpleApp.run()
