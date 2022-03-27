#!/usr/bin/env python
from pixelart_tui.main import SimpleApp


def run():
    import argparse

    parser = argparse.ArgumentParser(description="Load image or pallete")
    parser.add_argument(
        "--pxl", type=str, default=None, help="Path to image (pxl) file"
    )
    parser.add_argument(
        "--pal", type=str, default=None, help="Path to pallete (pal) file"
    )
    argsx = parser.parse_args()
    SimpleApp.run(title="PixelArt TUI 🎨", image=argsx.pxl, pallete=argsx.pal)


if __name__ == "__main__":
    run()
