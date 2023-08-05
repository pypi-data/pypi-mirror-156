from pygame import Color

def _input2Color(c, a=255):
    color = None
    if (type(c) == int) and (0 <= c) and (255 >= c):
        color = Color(c, c, c)
    elif (type(c) == float) and (0 <= c) and (255 >= c):
        color = Color(int(c), int(c), int(c))
    elif (type(c) == str):
        color = Color(c)
    elif (type(c) == tuple):
        color = Color(c)
    else:
        color = Color("black")
    color.a = a
    return color

# COLOR
def color(r, g, b):
    return Color(r, g, b)

def alpha(c):
    return c.a

def red(c):
    return c.r

def green(c):
    return c.g

def blue(c):
    return c.b

def brightness(c):
    return c.hsva[2]

def hue(c):
    return c.hsva[0]

def lightness(c):
    return c.hsla[2]

def saturation(c):
    return c.hsla[1]

def lerpColor(c1, c2, amnt):
    return c1.lerp(c2, amnt)