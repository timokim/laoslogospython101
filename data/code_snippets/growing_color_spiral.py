import turtle

screen = turtle.Screen()
screen.bgcolor("black")

t = turtle.Turtle()
t.speed(0)
t.width(2)

colors = [
    "red","orange","yellow","lime",
    "cyan","blue","purple","magenta"
]

for i in range(400):
    t.pencolor(colors[i % len(colors)])
    t.forward(i)
    t.left(91)

turtle.done()
