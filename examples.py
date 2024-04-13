
import math
import time

from vectorscope import Vectorscope
from random_walk import RW

import random

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

def generate_noise_image(width, height):
    """Generates a basic 'noise' image using a Perlin-like function."""
    img_array = [[0 for _ in range(width)] for _ in range(height)]
    for y in range(height):
        for x in range(width):
            #print(f"{y} {x}")
            img_array[y][x] = perlin(x * 0.1, y * 0.1)
            #print(f"{y} {x} done")
    print("Calculated noise image")
    return img_array



def minimal_example(v):
    ## Minimal example
    for i in range(1000):
        x_pert = random.randrange(2000, 6000)
        y_pert = random.randrange(2000, 6000)
        x = int(math.cos(i * math.pi / 180 * 10) * 10000)
        y = int(math.sin(i * math.pi / 180 * 10)* 10000)
        print(f"{x} {y}")
        v.wave.constantX(x + x_pert)
        v.wave.constantY(y + y_pert)
        time.sleep_ms(10)


def static_buffer_example(v):
    ## Example of more complicated, repetitive waveform
    ## v.wave has two buffers of 256 samples for putting sample-wise data into:
    ## v.wave.outBufferX and outBufferY.  These are packed 16 bits each, LSB first
    ## To make your life easier, v.wave.packX() will put a list of 16-bit ints there for you

    ramp = range(-2**15, 2**15, 2**8)
    v.wave.packX(ramp)

    sine = [int(math.sin(2*x*math.pi/256)*16_000) for x in range(256)]
    v.wave.packY(sine)

    time.sleep_ms(1000)

    ## That discontinuity and wobble is real --
    ##  that's what happens when you try to push around a real DAC that's bandwidth-limited.


def animated_buffer_example(v):
    ## To animate, you need to clear v.wave.outBuffer_ready and wait for it to go true
    ## Each output buffer frame has 256 samples, so takes ~8.5 ms at 30 kHz

    ramp = range(-2**15, 2**15, 2**8)
    v.wave.packX(ramp)

    v.wave.outBuffer_ready = False
    for i in range(200):
        sine = [int(math.sin((50*i)+2*x*math.pi/256)*16_000) for x in range(256)]
        while not v.wave.outBuffer_ready:
            pass
        v.wave.packY(sine)
        v.wave.outBuffer_ready = False

    ## Any stuck pixels you see are a figment of your imagination.  :)
    ## Or a desperate call for a pull request.  Your call.


def random_walk_example(v):
    ## Example with a class, makes it tweakable on the command line
    ## because half the fun here is live coding and experimentation

    r = RW(v.wave)
    # print(dir(r))
    r.scale = 1000
    r.delay = 5
    r.go()

###########

#def smoothstep(edge0, edge1, x):
#    """Smoothstep function for non-linear interpolation."""
#    x = max(0, min(1, (x - edge0) / (edge1 - edge0)))
#    return x*x/(2.0*x*x-2.0*x+1.0)
#
#def generate_noise_image(width, height, scale, octaves, persistence, lacunarity, base):
#    """Generates and returns a 2D numpy array of Perlin noise values."""
#    img_array = [[0 for _ in range(width)] for _ in range(height)]
#    for y in range(height):
#        for x in range(width):
#            noise_val = noise.snoise2(x / scale,
#                                      y / scale,
#                                      octaves=octaves,
#                                      persistence=persistence,
#                                      lacunarity=lacunarity,
#                                      repeatx=width,
#                                      repeaty=height,
#                                      base=base)
#            # smooth_noise_val = Smooth(-0.3, 0.3, noise_val)
#            smooth_noise_val = smoothstep(-0.3, 0.3, noise_val)
#            img_array[y][x] = smooth_noise_val  # Ensure y comes before x
#
#    return img_array

def sweep_screen_example():
    # Sweeping motion of rendering the screen with something
    RANGE = 26000
    # this is actually how much to jump between each render (we VERY INEFFICIENTLY RENDER SOMETHING)
    X_SWEEP_SPEED = 100
    Y_SWEEP_SPEED = 100
    while True:
        for i in range(-RANGE, RANGE, X_SWEEP_SPEED):
            for j in range(-RANGE, RANGE, Y_SWEEP_SPEED):
                v.wave.point(i, j)

    # DMA dies down when we stop the data flow
    # also we get weird gaps - I wonder why they happen :scratch scratch:


def noise_example(v):
    SCALE = 20000
    FREQUENCY = 1000
	# Noise parameters
    width, height = 26, 26 # should be 260by 260
    scale = 50.0
    octaves = 6
    persistence = 0.5
    lacunarity = 2.0
    base = 0
    # Generate noise image
    print("generating noise image")
    noise_img = generate_noise_image(width, height)
    base += 0.02  # Change base to animate

    print("success")
    ## Update the pygame surface with the noise image
    #while True:
    #    for x in range(width):
    #        for y in range(height):
    #            color_value = int(noise_img[x][y] * 255)
    #            print(f"{x} {y} {color_value}")
    #            if (color_value > 50):
    #                print(f"{x} {y} {color_value}")
    #                v.wave.point(x,y)
    #                #screen.set_at((x, y), (color_value, color_value, color_value))

    # Sweeping motion of rendering the screen with something
    RANGE = 26000
    # this is actually how much to jump between each render (we VERY INEFFICIENTLY RENDER SOMETHING)
    X_SWEEP_SPEED = 300
    Y_SWEEP_SPEED = 300
    for i in range(width):
        for j in range(height):
            color_value = int(noise_img[j][i] * 255)
            print(f"{i} {j} {color_value}")
            # TODO: not sure if this works properly <-seems to be creating gaps

    while True:
        for i in range(-RANGE, RANGE, X_SWEEP_SPEED):
            #x = (int)(math.fabs(i // 1000) - 1)
            #print(f"index x: {x}")
            for j in range(-RANGE, RANGE, Y_SWEEP_SPEED):
                # creating holes work somehow - but looks like crap
                if (j > 0 and i > 0 and i < 4000 and j < 4000):
                    continue
                if (j > -8000 and i > -8000 and i < -4000 and j < -4000):
                    continue
                #y = (int)(math.fabs(j // 1000) - 1)
                #color_value = int(noise_img[y][x] * 255)
                #if (color_value > 0):
                #    v.wave.point(i, j)
                #r = random.randrange(3, 10)
                #if (r > 8):
                v.wave.point(j, i)

    # idea - try drawing images - steering of that is finincky
    # maybe some smart converter of image to this rendering algo?

    # DMA dies down when we stop the data flow
    # also we get weird gaps - I wonder why they happen :scratch scratch:



def vos_main():
    import vos_state,vectoros,gc,vos_debug, asyncio
    from vos_debug import debug_print as debug
    vectoros.get_screen().idle()
    gc.collect()
    vos_state.gc_suspend=True
    asyncio.sleep(4)
    v = Vectorscope()
    minimal_example(v)
    await asyncio.sleep(5)
    static_buffer_example(v)
    await asyncio.sleep(5)
    animated_buffer_example(v)
    random_walk_example(v)
    debug(vos_debug.DEBUG_LEVEL_INFO,"Demo done, reboot!")
    vectoros.reset()



if __name__ == "__main__":

    v = Vectorscope()
    #minimal_example(v)
    noise_example(v)
    #static_buffer_example(v)
    #animated_buffer_example(v)
    #random_walk_example(v)

    v.deinit()
    ## before you reload, you have to deinitialize all of the DMA
    ##  machines, else you get an error OS: 16

