from setuptools import setup

from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="pixelart-tui",
    version="0.3",
    description="Terminal based app for Pixel Art that supports mouse!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://github.com/Cvaniak/PixelArtTUI",
    author="Cvaniak",
    author_email="igna.cwaniak@gmail.com",
    packages=["pixelart_tui"],
    install_requires=["textual==0.1.15", "textual-inputs==0.2.5"],
    entry_points={"console_scripts": ["pixelart-tui=pixelart_tui.command_line:run"]},
    zip_safe=False,
)
