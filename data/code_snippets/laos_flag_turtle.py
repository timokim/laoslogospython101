"""
Laos Flag — Turtle Graphics
Run in Thonny: open this file and press Run (F5).

Draws the flag of Laos:
  - Red / blue / red stripes (blue band is twice as tall)
  - White circle in the center
"""

import turtle

# Official-style colors
RED = "#CE1126"
BLUE = "#002868"
WHITE = "#FFFFFF"

# Flag proportions: height 2, width 3
HEIGHT = 300
WIDTH = 450

screen = turtle.Screen()
screen.setup(WIDTH + 80, HEIGHT + 80)
screen.title("Laos Flag 🇱🇦")
screen.bgcolor("#888888")

pen = turtle.Turtle()
pen.hideturtle()
pen.speed(0)
pen.penup()


def draw_rectangle(x, y, width, height, color):
    """Filled rectangle. (x, y) is the bottom-left corner."""
    pen.goto(x, y)
    pen.setheading(0)
    pen.pendown()
    pen.fillcolor(color)
    pen.begin_fill()
    for _ in range(2):
        pen.forward(width)
        pen.left(90)
        pen.forward(height)
        pen.left(90)
    pen.end_fill()
    pen.penup()


left = -WIDTH / 2
quarter = HEIGHT / 4

# Three stripes: 1/4 red, 1/2 blue, 1/4 red (top to bottom)
draw_rectangle(left, quarter, WIDTH, quarter, RED)       # top red
draw_rectangle(left, -quarter, WIDTH, HEIGHT / 2, BLUE)  # middle blue
draw_rectangle(left, -HEIGHT / 2, WIDTH, quarter, RED) # bottom red

# White circle — radius is 0.2 × flag height
radius = HEIGHT * 0.2
pen.goto(0, -radius)
pen.setheading(0)
pen.pendown()
pen.fillcolor(WHITE)
pen.begin_fill()
pen.circle(radius)
pen.end_fill()
pen.penup()

turtle.done()
