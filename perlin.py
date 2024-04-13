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
img_array = [[0 for _ in range(10)] for _ in range(10)]

rainbow_colors = [
        (255, 0, 0),    # Red
        (255, 127, 0),  # Orange
        (255, 255, 0),  # Yellow
        (0, 255, 0),    # Green
        (0, 0, 255),    # Blue
        (75, 0, 130),   # Indigo
        (148, 0, 211)   # Violet
        ]

def draw_pixel(x, y, color):
    global PIXSIZE
    ccolor=gc9a01.color565(color, color, color)
    screen.tft.fill_rect(x*PIXSIZE,y*PIXSIZE,PIXSIZE,PIXSIZE,ccolor)

def draw_pixel_rainbow(x, y, _):
    global PIXSIZE, rainbow_colors
    # Select a random color from the rainbow
    color = random.choice(rainbow_colors)
    # Convert the RGB values to a 16-bit color value (565 format)
    ccolor = gc9a01.color565(color[0], color[1], color[2])
    # Draw the pixel with the selected color
    screen.tft.fill_rect(x * PIXSIZE, y * PIXSIZE, PIXSIZE, PIXSIZE, ccolor)

def lerp(a, b, x):
    """Linear interpolation between a and b with x as the interpolant."""
    return a + x * (b - a)

def smoothstep(x):
    """Smoothstep function for smoother transitions."""
    return 6*x**5 - 15*x**4 + 10*x**3

def dot_grid_gradient(ix, iy, x, y):
    """Compute the dot product between a pseudo random gradient vector and the vector from the input coordinate to the grid's integer coordinate."""
    # Pseudo random gradient
    random.seed(ix + iy * 57)
    angle = random.uniform(0, 2 * math.pi)
    grad = (math.cos(angle), math.sin(angle))

    # Compute the distance vector
    dx = x - ix
    dy = y - iy

    # Dot product
    return dx*grad[0] + dy*grad[1]

def perlin(x, y):
    """Simple Perlin-like noise function."""
    # Determine grid cell coordinates
    x0 = int(math.floor(x))
    x1 = x0 + 1
    y0 = int(math.floor(y))
    y1 = y0 + 1

    # Interpolate
    sx = smoothstep(x - x0)
    sy = smoothstep(y - y0)

    n0 = dot_grid_gradient(x0, y0, x, y)
    n1 = dot_grid_gradient(x1, y0, x, y)
    ix0 = lerp(n0, n1, sx)

    n0 = dot_grid_gradient(x0, y1, x, y)
    n1 = dot_grid_gradient(x1, y1, x, y)
    ix1 = lerp(n0, n1, sy)


    return lerp(ix0, ix1, sy)

def generate_noise_image(width, height, z):
    """Generates a noise image for a given z (time) value."""
    for y in range(height):
        for x in range(width):
            # Adjust x and y based on z to simulate 3D noise
            noise_value = perlin(x * 0.1 + z, y * 0.1 + z)
            # Normalize noise_value to a [0, 1] range
            img_array[y][x] = (noise_value + 1) / 2
    return img_array

def run_perlin():
    ## Turn up the heat!
    machine.freq(250_000_000)

    STRIDE = 4 # stride because we don't have enought memory lul
    # Noise parameters
    width, height = 240 // PIXSIZE,  240 // PIXSIZE
    z = 0
    # Generate noise image
    while True:
        #print(f"generating noise image w: {width}, h: {height}")
        noise_img = generate_noise_image(10, 10, z) # pregenerate it?
        #print("success")
        for x in range(0, width):
            for y in range(0, height):
                color_value = int(noise_img[x // STRIDE][y // STRIDE] * 255)
                ##print(f"{x} {y} {color_value}")
                draw_pixel(x, y, color_value)
                #draw_pixel_rainbow(x, y, color_value)
            gc.collect()

        z += 0.05

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

    run_perlin()
    while stopflag==False:
        await asyncio.sleep(5)
        if vos_state.active==False:
            gc.collect()
    stopflag=False   # ready for next time
    vos_state.show_menu=True
    vectoros.remove_task('perlin')
    print("Exiting")


def main():
    asyncio.run(vos_main())

if __name__ == "__main__":
    main()   # need gc if you try to run stand alone
