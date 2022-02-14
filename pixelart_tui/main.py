from textual.app import App
from textual.views import GridView
from textual.widgets import Footer, Header
from textual import events

from textual.app import App

from pixelart_tui.canvas import Canvas, MouseStatus, Tools, Grid

from textual_inputs import TextInput
from pixelart_tui.file_tools import save_pxl, load_pxl, save_pal, load_pal

from pixelart_tui.my_messages import DebugStatus, ColorStatus, LoadSaveStatus
from pixelart_tui.my_widgets import (
    LoadSave,
    StatusWidget,
    ColorWidget,
    ColorBox,
    ToolsWidget,
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
        self.grid.place(panel=ToolsWidget())
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
        self.canvas = Canvas(w, h, grid=Grid.g32x32)

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

    async def handle_my_button_pressed(self, message):
        if message.value == "8":
            self.canvas.grid = Grid.g8x8
            self.canvas.refresh()
        if message.value == "16":
            self.canvas.grid = Grid.g16x16
            self.canvas.refresh()
        if message.value == "32":
            self.canvas.grid = Grid.g32x32
            self.canvas.refresh()
        if message.value == "new":
            self.canvas.set_matrix()
            self.canvas.refresh()
        if message.value == "pick":
            self.canvas.set_tool(Tools.PICK)
        if message.value == "paint":
            self.canvas.set_tool(Tools.PAINT)  # color = self.canvas.get_color()
            # self.canvas.set_color()

    async def handle_color_under_mouse(self, message):
        if not message.change:
            self.c_box.display(message.color)
        else:
            r, g, b = message.color.get_truecolor()
            self.c_box.update(r, g, b)
            self.c_red.update(r)
            self.c_green.update(g)
            self.c_blue.update(b)


if __name__ == "__main__":
    SimpleApp.run()
