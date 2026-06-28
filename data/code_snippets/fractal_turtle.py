import turtle
import colorsys

# --- Setup the Canvas ---
screen = turtle.Screen()
screen.bgcolor("black")
screen.title("Funky Fractal Vortex")
screen.setup(width=800, height=800)

# --- Setup the Turtle ---
t = turtle.Turtle()
t.speed(0)  # Fastest animation speed
t.hideturtle()
t.left(90)  # Point upwards to start the tree
turtle.tracer(10, 1)  # Speeds up drawing slightly, increase first number for speed

# --- The Funky Fractal Function ---
def draw_funky_fractal(branch_len, level, hue):
    if level == 0:
        return
    
    # Generate a vibrant, cycling HSV color
    color = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
    t.pencolor(color)
    t.pensize(level * 0.8)  # Branches get thinner as they grow
    
    # Forward movement with a little flair
    t.forward(branch_len)
    
    # Right branch
    t.right(35)
    draw_funky_fractal(branch_len * 0.75, level - 1, hue + 0.05)
    
    # Left branch (and over-rotating for a funky asymmetry)
    t.left(70)
    draw_funky_fractal(branch_len * 0.75, level - 1, hue + 0.05)
    
    # Return to center and back up
    t.right(35)
    t.pencolor(color)
    t.backward(branch_len)

# --- Main Execution ---
# We run it in a 6-sided spiral pattern to create a massive, dense vortex
for i in range(12):
    draw_funky_fractal(120, 9, 0.0)
    t.right(60)

# Keep the window open when finished
screen.mainloop()
