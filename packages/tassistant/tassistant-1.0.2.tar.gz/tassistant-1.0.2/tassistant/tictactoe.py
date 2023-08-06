from tassistant import *


def draw_table(cell_size, **kwargs):
	if "color" in kwargs: pencolor(kwargs["color"])
	if "size" in kwargs: width(kwargs["size"])

	for x in range(3):
		for y in range(3):
			Rectangle(cell_size, position=(x*cell_size, y*cell_size))

def draw_x(cell_size, position, **kwargs):
	if "color" in kwargs: pencolor(kwargs["color"])
	if "size" in kwargs: width(kwargs["size"])
	square_diagonal = round(2**0.5*cell_size)/2

	goto_(position[0]*cell_size, position[1]*cell_size)
	left(45)
	for _ in range(4):
		forward(square_diagonal)
		right(90)
		forward(square_diagonal)
		right(180)

def draw_o(cell_size, position, **kwargs):
	if "color" in kwargs: pencolor(kwargs["color"])
	if "size" in kwargs: width(kwargs["size"])

	goto_(position[0]*cell_size+cell_size/2, position[1]*cell_size)
	Circle(cell_size/2)