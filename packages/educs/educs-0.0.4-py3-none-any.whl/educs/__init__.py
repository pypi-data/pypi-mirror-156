import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

from educs.pygame_wrapper import (setup, draw, createCanvas, background, fill, noFill, line, ellipse, circle, rect, quad, arc, triangle, push, pop, getMouseX, getMouseY, getWidth, getHeight, cursor, strokeWeight, stroke, noStroke, loadImage, image, keyPressed, mouseClicked, mouseDragged, isMousedPressed, Image, frameRate, loop, noLoop)

from educs.color import (color, alpha,
                        red, green, blue, brightness,
                        hue, lightness, saturation, lerpColor)

from educs.constants import (TWO_PI, HALF_PI, PI, QUARTER_PI, TAU, CURSOR_ARROW, CURSOR_DIAMOND, CURSOR_BROKEN_X, CURSOR_TRI_LEFT, CURSOR_TRI_RIGHT)

from educs.math import (random, constrain, floor, ceil, dist, exp, lerp, ln, log10, log2, logb, mag, rerange, norm, sq, sqrt, frac, sin, cos, tan, asin, acos, atan, atan2, degrees, radians)

__all__ = ["setup", "draw", "createCanvas", "background", "fill", "noFill", "line", "ellipse", "circle", "rect", "triangle", "quad", "arc", "push", "pop", "getMouseX", "getMouseY", "getWidth", "getHeight", "cursor", "TWO_PI", "HALF_PI", "PI", "QUARTER_PI", "TAU", "CURSOR_ARROW", "CURSOR_DIAMOND", "CURSOR_BROKEN_X", "CURSOR_TRI_LEFT", "CURSOR_TRI_RIGHT", "strokeWeight", "stroke", "noStroke", "loadImage", "image", "keyPressed", "mouseClicked", "mouseDragged", "isMousedPressed", "Image", "frameRate", "random", "constrain", "floor", "ceil", "dist", "exp", "lerp", "ln", "log10", "log2", "logb", "mag", "rerange", "norm", "sq", "sqrt", "frac", "sin", "cos", "tan", "asin", "acos", "atan", "atan2", "degrees", "radians", "loop", "noLoop"]

__version__ = "0.0.4"

print("Thank you for using educs!\n")