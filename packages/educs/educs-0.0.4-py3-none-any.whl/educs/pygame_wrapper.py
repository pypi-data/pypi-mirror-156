import pygame
import numpy as np
from multipledispatch import dispatch
import math

from educs.color import _input2Color

class EventManager:
    def __init__(self):
        pass
        
    def keyPressed(self):
        pass

    def mouseClicked(self):
        pass

    def mouseDragged(self):
        pass

class Image(pygame.Surface):
    def __init__(self):
        pass

# "private" variables
windowSurf = None
backgroundSurf = None
clock = None
doLoop = True
eventManager = EventManager()
mouseX = None
mouseY = None
mouseUp = True
width = 200
height = 200
framerate = 60
settings_stack = []
settings = {
    "fill_color": _input2Color("white"),
    "no_fill": False,
    "stroke_weight": 1,
    "stroke_color": _input2Color("black"),
    "rotate_amnt": 0
}

# IMAGE
def loadImage(path):
    return pygame.image.load(path)

def image(img, x, y):
    backgroundSurf.blit(img, (x, y))

# DATA

# ENVIRONMENT
def getWidth():
    return width

def getHeight():
    return height
    
def cursor(type):
    pygame.mouse.set_cursor(*type)
    pass

def noCursor():
    pygame.mouse.set_cursor((8,8),(0,0),(0,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,0))
    pass

# EVENTS
def getMouseX():
    return mouseX

def getMouseY():
    return mouseY

# SHAPE
def _filledArc(r, start, stop):
    # arc_image = np.zeros((r.height, r.width, 3), dtype = np.uint8)
    # cf = settings["fill_color"]
    # cv.ellipse(arc_image, r.center, (r.height, r.width), 0, math.degrees(start), math.degrees(stop), 0)

    # img = pygame.image.frombuffer(arc_image, r.size, "RGB")
    # print("hello")
    # backgroundSurf.blit(img, img.get_rect(center=r.center))
    # return
    pass
  
def _filledShape(func, *args, **kwargs):
    if (not settings["no_fill"]):
        func(backgroundSurf, settings["fill_color"], *args, **kwargs, width=0)

    if (settings["stroke_weight"] > 0):
        func(backgroundSurf, settings["stroke_color"], *args, **kwargs, width=settings["stroke_weight"])
    return
    
def arc(x, y, w, h, start, stop):
    r = pygame.Rect(x-w/2, y-h/2, w, h)
    _filledArc(r, start, stop)
    pass

def ellipse(x, y, w, h=None):
    if not h:
        h = w
    
    r = pygame.Rect(x-w/2, y-h/2, w, h)
    _filledShape(pygame.draw.ellipse, r)
    pass

def circle(x, y, d):
    _filledShape(pygame.draw.circle, (x, y), d/2)
    pass

def line(x1, y1, x2, y2):
    pygame.draw.line(backgroundSurf, settings["stroke_color"], (x1, y1), (x2, y2), width=1)
    pass

def point(x, y):
    _filledShape(pygame.draw.circle, (x, y), 1)
    pass

def quad(x1, y1, x2, y2, x3, y3, x4, y4):
    _filledShape(pygame.draw.polygon, ((x1, y1), (x2, y2), (x3, y3), (x4, y4)))
    pass

def rect(x, y, w, h):
    r = pygame.Rect(x, y, w, h)
    _filledShape(pygame.draw.rect, r)
    pass

def square(x, y, s):
    r = pygame.Rect(x, y, s, s)
    _filledShape(pygame.draw.rect, r)
    pass

def triangle(x1, y1, x2, y2, x3, y3):
    _filledShape(pygame.draw.polygon, ((x1, y1), (x2, y2), (x3, y3)))
    pass

# TRANSFORM
def rotate(angle):
    global backgroundSurf
    backgroundSurf = pygame.transform.rotate(backgroundSurf, angle)
    settings["rotate_amnt"] += angle
    pass

def createCanvas(w=100, h=100):
    global windowSurf
    global backgroundSurf
    global elementManager
    global width
    global height
    
    width = w
    height = h

    windowSurf = pygame.display.set_mode((w, h), pygame.NOFRAME)
    backgroundSurf = pygame.Surface(windowSurf.get_size(), pygame.SRCALPHA)
    pass

@dispatch(tuple)
def background(c):
    x = _input2Color(c)
    backgroundSurf.fill(x)
    pass

@dispatch(tuple, int)
def background(c, a):
    x = _input2Color(c, a)
    backgroundSurf.fill(x)
    pass
    
@dispatch(int)
def background(c):
    x = _input2Color(c)
    backgroundSurf.fill(x)
    pass

@dispatch(int, int)
def background(c, a):
    x = _input2Color(c, a)
    backgroundSurf.fill(x)
    pass

@dispatch(str)
def background(c):
    x = _input2Color(c)
    backgroundSurf.fill(x)
    pass

@dispatch(str, int)
def background(c, a):
    x = _input2Color(c, a)
    backgroundSurf.fill(x)
    pass

@dispatch(float)
def background(c):
    x = _input2Color(c)
    backgroundSurf.fill(x)
    pass

@dispatch(float, int)
def background(c, a):
    x = _input2Color(c, a)
    backgroundSurf.fill(x)
    pass

@dispatch(int, int, int)
def background(r, g, b):
    x = _input2Color((r, g, b))
    backgroundSurf.fill(x)
    pass

@dispatch(int, int, int, int)
def background(r, g, b, a):
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

def noFill():
    settings["no_fill"] = True
    pass

def stroke(c):
    settings["stroke_color"] = _input2Color(c)
    pass

def strokeWeight(weight):
    if (weight == 0):
        settings["stroke_weight"] = -1
    else:
        settings["stroke_weight"] = weight
    pass

def noStroke():
    settings["stroke_weight"] = -1
    pass

# STRUCTURE
def push():
    global settings
    settings_stack.append(settings)
    settings = dict()
    pass

def pop():
    global settings
    settings = settings_stack.pop()
    pass

def frameRate(f):
    global framerate
    framerate = f

def loop():
    global doLoop
    doLoop = True

def noLoop():
    global doLoop
    doLoop = False

def setup(func):

    def wrapper_setup():
        global clock
        
        pygame.init()
        func()
        clock = pygame.time.Clock()
        
    return wrapper_setup
    

def draw(func):
    
    def wrapper_draw():
        global windowSurf
        global backgroundSurf
        global clock
        global mouseX
        global mouseY
        global mouseUp
        global doLoop

        cntLoop = 0

        while True:
            while doLoop or cntLoop == 0:
                
                events = pygame.event.get()
                for event in events:
                    if event.type == pygame.KEYDOWN:
                        eventManager.keyPressed(event)
                    elif event.type == pygame.MOUSEBUTTONUP:
                        mouseUp = True
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        mouseUp = False
                        eventManager.mouseClicked(event)
                    elif event.type == pygame.MOUSEMOTION:
                        if (not mouseUp):
                            eventManager.mouseDragged(event)
                mouseX, mouseY = pygame.mouse.get_pos()
                
                func()

                windowSurf.blit(backgroundSurf, (0, 0))
                
                pygame.display.flip()
                cntLoop = 1
                clock.tick(framerate)
    return wrapper_draw

def keyPressed(func):
    def wrapped_keyPressed(event):
        eventManager.keyPressed = func
        pass
    return wrapped_keyPressed

def mouseClicked(func):
    def wrapped_mouseClicked(event):
        eventManager.mouseClicked = func
        pass
    return wrapped_mouseClicked

def mouseDragged(func):
    def wrapped_mouseDragged(event):
        eventManager.mouseDragged = func
        pass
    return wrapped_mouseDragged

def isMousedPressed():
    return not mouseUp
