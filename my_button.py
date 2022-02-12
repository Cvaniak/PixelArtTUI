from __future__ import annotations

from rich import box
from rich.align import Align
from rich.console import Console, ConsoleOptions, RenderResult, RenderableType
from rich.style import StyleType

from textual import events
from textual.message import Message
from textual.reactive import Reactive
from textual.widget import Widget

from textual.widgets import ButtonPressed, Button
from rich.panel import Panel

class MyButtonPressed(Message):
    def __init__(self, sender: Widget, value: str):
        super().__init__(sender)
        self.value = value



class MyButtonRenderable:
    def __init__(self, label: RenderableType, style: StyleType = "") -> None:
        self.label = label
        self.style = style

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        width = options.max_width
        height = options.height or 1

        yield Align.center(
            self.label, vertical="middle", style=self.style, width=width, height=height
        )


class MyButton(Button):
    mouse_over: Reactive[bool] = Reactive(False)
    has_focus: Reactive[bool] = Reactive(False)
 
    def __init__(
        self,
        label: RenderableType,
        name: str | None = None,
        style: StyleType = "white on dark_blue",
        value: str = ""
    ):
        super().__init__(label, name, style)
        self.value =value

    def render(self) -> RenderableType:
        return self
        # return MyButtonRenderable(self.label, style=self.button_style)

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        yield Panel(
            Align.center(
                self.label,
            ),
            border_style="green" if self.mouse_over else "blue",
            box=box.HEAVY if self.has_focus else box.ROUNDED,
            style=self.button_style,
            # height=height,
        )
    async def on_click(self, event: events.Click) -> None:
        await self.emit(MyButtonPressed(self, self.value))

    async def on_enter(self, event: events.Enter) -> None:
        self.mouse_over = True

    async def on_leave(self, event: events.Leave) -> None:
        self.mouse_over = False
        self.has_focus = False

    async def on_mouse_down(self, _) -> None:
        self.has_focus = True

    async def on_mouse_up(self, _) -> None:
        self.has_focus = False


