import screennorm
import keyboardcb
import keyleds
import vectoros
from vos_state import vos_state
import gc9a01
import gc   # need to read files so we can garbage collect between
import random
import math
import time
import machine

# little etch-a-sketch demo

color = gc9a01.BLACK     # start off black

# To maintain the cursor we need a bit map which is slow
# so less is more. Also pixels are tiny
# so 40 is a good compromise (40x40 drawing area)
SIZE=40
PIXSIZE=240//SIZE            # size of each "pixel"

# start cursor in the middle
cursor_x = (SIZE+1)//2
cursor_y = (SIZE+1)//2

# This will be the backing store for the screen
model=[]

stopflag=False  # stop when true

rainbow_colors = [
        (255, 0, 0),    # Red
        (255, 127, 0),  # Orange
        (255, 255, 0),  # Yellow
        (0, 255, 0),    # Green
        (0, 0, 255),    # Blue
        (75, 0, 130),   # Indigo
        (148, 0, 211)   # Violet
        ]

def draw_pixel_rainbow(x, y, color):
    global PIXSIZE
    # Convert the RGB values to a 16-bit color value (565 format)
    ccolor = gc9a01.color565(color[0], color[1], color[2])
    # Draw the pixel with the selected color
    screen.tft.fill_rect(x * PIXSIZE, y * PIXSIZE, PIXSIZE, PIXSIZE, ccolor)

def run_rainbow():
    global rainbow_colors
    ## Turn up the heat!
    machine.freq(250_000_000)

    STRIDE = 4 # stride because we don't have enought memory lul
    # Noise parameters
    width, height = 240 // PIXSIZE,  240 // PIXSIZE
    z = 0
    # Generate noise image
    while True:
        color_choice = 0
        # Iterate over the grid block by block
        for bx in range(0, width, STRIDE):
            for by in range(0, height, STRIDE):
                # Select a new color for each block
                color_choice = random.choice(rainbow_colors)
                # Draw all pixels within this block
                for x in range(bx, min(bx + STRIDE, width)):
                    for y in range(by, min(by + STRIDE, height)):
                        draw_pixel_rainbow(x, y, color_choice)
            gc.collect()

        time.sleep_ms(5)



    # need to draw the different shades of black for perlin noise - is very black, + is very white scale it
    # also add the necessar handling code


def menu(key):       # exit and return to menu
	global stopflag
	print("menu")
	if vos_state.active:
		stopflag=True

        # create our screen and keyboard/joystick
screen=screennorm.ScreenNorm()

import asyncio
import gc

async def vos_main():
    global stopflag

    run_rainbow()
    while stopflag==False:
        await asyncio.sleep(5)
        if vos_state.active==False:
            gc.collect()
    stopflag=False   # ready for next time
    vos_state.show_menu=True
    vectoros.remove_task('rainbow_dash')
    print("Exiting")


def main():
    asyncio.run(vos_main())

if __name__ == "__main__":
    main()   # need gc if you try to run stand alone
