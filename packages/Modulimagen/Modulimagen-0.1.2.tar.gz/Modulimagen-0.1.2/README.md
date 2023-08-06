# (Modulimagen) modular image generator
A python module that contains functions which can be mixed and applied in sequence for generating matrices (which can be converted into images) in a modular way.

## installation
```
pip install Modulimagen
```

## available tools
 - **wave (width, height, scale, offset, orientation)**
   *width and height are referred to the 2D matrix that the function will return*
   
 - **perlin_noise (width, height, scale, x_stretch, y_stretch, octaves, persistence, lacunarity, seed)**
   *for more information about Perlin noise check [noise library on PyPI](https://pypi.org/project/noise/)*

 - **black_and_white (z, image_height, image_width, threshold)**
   *z argument is the initial matrix taken by the function*

 - **mix (texture1, texture2, operation)**
   *operation argument can be every mathematical operation written as a string, (example: "+", "-")*

## usage
Every function listed above returns a numpy 2D array (a matrix), which can be used as an argument of another function or **converted into an image** with something like
```python
from pylab import imsave
imsave("new_image.png", image_matrix, origin="lower", cmap=get_cmap("plasma")) 
```
