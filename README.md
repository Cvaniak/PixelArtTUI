# Pixel Art App In Terminal (Version 0.3)

![PXLimage](https://raw.githubusercontent.com/Cvaniak/PixelArtTUI/master/documentation/pxl.png)  
To start with Pixel Art you dont need fancy tools. In fact you can go with only terminal and mouse!  
With help of amazing `Textual` here is `Paint` like app that provides all features for creating *Pixel Art*.  
It works in **terminal** and supports **mouse** so you can use it like normal Window app without need to use shortcuts (like others teminal based Paint apps do).

# Installation with Pip [recommended]
The easiest way to start is with `pip`:
```bash
pip3 install pixelart_tui
```
after that you can use it like this:
```
pixelart_tui
# or you can open existing image or pallete with:
pixelart_tui --pxl image_file.pxl --pal pallete_file.pal
```
and thats all!

# From source 
To use you need `Python 3.6+` and you can start with command in terminal:
```bash
pip3 install -r requirements.txt
# or
python3 -m install -r requirements.txt
```
and then you can double-click on `run.sh` (Linux/Mac) or `run.bat` (Windows) to start or from terminal run:
```bash
cd pixelart_tui
python3 main.py
```

# Usage 
This TUI supports:
* Painting
* Choosing RGB colors
* Picking color from canvas
* 8x8, 16x16 and 32x32 grids
* Saving and loading images and paletts in custom format

To save image you need to provide name and finish with `.pxl`, for example `my_image.pxl`. You can also import any image saved in this format.

To save paletts you need to end name with `.pal`, for example `my_palette.pal`. You can also modify this pallete from text editor so you can use **colors in full 0-255 range**, where normaly there normally you use only 16 of them.
