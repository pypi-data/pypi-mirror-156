import numpy as np
from math import sin
from noise import pnoise2


# sine wave texture function
def wave(width, height, scale, offset, orientation):
    
    scale = 1/scale
    z = np.zeros((height, width))
    
    if orientation == "x":
        for x in range(height):
            for y in range(width):
                z[x][y] = sin((x-offset)*scale)
    elif orientation == "y":
        for x in range(height):
            for y in range(width):
                z[x][y] = sin((y-offset)*scale)
    return z


# perlin noise texture function
def perlin_noise(width, height, scale, x_stretch, y_stretch, octaves, persistence, lacunarity, seed):

    z = np.zeros((height,width))
    for x in range(height):
        for y in range(width):
            z[x][y] = pnoise2(x/scale*x_stretch, y/scale*y_stretch, octaves, persistence, lacunarity, width, height, seed)
    return z


# white and black (values rounded to 1 or 0) texture converter function
def black_and_white(z, image_height, image_width, threshold):
    
    for x in range(image_height):
        for y in range(image_width):
            if z[x][y] <= threshold:
                z[x][y] = 0
            else:
                z[x][y] = 1
    return z


# texture mixer
def mix(texture1, texture2, operation):
    return eval(eval("\"texture1\"+operation+\"texture2\""))
