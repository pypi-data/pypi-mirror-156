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



@dispatch(tuple)
def background(c):
    if (backgroundSurf):
        x = _input2Color(c)
        backgroundSurf.fill(x)
    pass

@dispatch(tuple, int)
def background(c, a):
    if (backgroundSurf):
        x = _input2Color(c, a)
        backgroundSurf.fill(x)
    pass
    
@dispatch(int)
def background(c):
    if (backgroundSurf):
        x = _input2Color(c)
        backgroundSurf.fill(x)
    pass

@dispatch(int, int)
def background(c, a):
    if (backgroundSurf):
        x = _input2Color(c, a)
        backgroundSurf.fill(x)
    pass

@dispatch(str)
def background(c):
    if (backgroundSurf):
        x = _input2Color(c)
        backgroundSurf.fill(x)
    pass

@dispatch(str, int)
def background(c, a):
    if (backgroundSurf):
        x = _input2Color(c, a)
        backgroundSurf.fill(x)
    pass

@dispatch(float)
def background(c):
    if (backgroundSurf):
        x = _input2Color(c)
        backgroundSurf.fill(x)
    pass

@dispatch(float, int)
def background(c, a):
    if (backgroundSurf):
        x = _input2Color(c, a)
        backgroundSurf.fill(x)
    pass

@dispatch(int, int, int)
def background(r, g, b):
    if (backgroundSurf):
        x = _input2Color((r, g, b))
        backgroundSurf.fill(x)
    pass

@dispatch(int, int, int, int)
def background(r, g, b, a):
    if (backgroundSurf):
        x = _input2Color((r, g, b), a)
        backgroundSurf.fill(x)
    pass

@dispatch(int)
def fill(c):
    settings["fill_color"] = _input2Color(c)
    settings["no_fill"] = False
    pass

@dispatch(int, int)
def fill(c, a):
    settings["fill_color"] = _input2Color(c, a)
    settings["no_fill"] = False
    pass

@dispatch(float)
def fill(c):
    settings["fill_color"] = _input2Color(c)
    settings["no_fill"] = False
    pass

@dispatch(float, int)
def fill(c, a):
    settings["fill_color"] = _input2Color(c, a)
    settings["no_fill"] = False
    pass

@dispatch(str)
def fill(c):
    settings["fill_color"] = _input2Color(c)
    settings["no_fill"] = False
    pass

@dispatch(str, int)
def fill(c, a):
    settings["fill_color"] = _input2Color(c, a)
    settings["no_fill"] = False
    pass

@dispatch(tuple)
def fill(c):
    settings["fill_color"] = _input2Color(c)
    settings["no_fill"] = False
    pass

@dispatch(tuple, int)
def fill(c, a):
    settings["fill_color"] = _input2Color(c, a)
    settings["no_fill"] = False
    pass

@dispatch(int, int, int)
def fill(r, g, b):
    settings["fill_color"] = _input2Color((r, g, b))
    settings["no_fill"] = False
    pass

@dispatch(int, int, int, int)
def fill(r, g, b, a):
    settings["fill_color"] = _input2Color((r, g, b), a)
    settings["no_fill"] = False
    pass