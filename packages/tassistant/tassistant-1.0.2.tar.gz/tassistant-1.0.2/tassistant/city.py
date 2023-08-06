from tassistant import *


def draw_christmas_tree(trunk_color="brown", leaf_color="green", **kwargs):
	Rectangle(50, 100, color=trunk_color, fill=trunk_color)
	Triangle(200, 135, color=leaf_color, fill=leaf_color, position=(-75, 100))
	Triangle(175, 120, color=leaf_color, fill=leaf_color, position=(-62, 160))
	Triangle(150, 105, color=leaf_color, fill=leaf_color, position=(-50, 220))

def draw_house(base_color="red", roof_color="green", **kwargs):
	Rectangle(100, color=base_color, fill=base_color)
	Triangle(120, color=roof_color, fill=roof_color, position=(-10, 100))

def draw_door(width=90, height=180, **kwargs):
	Rectangle(width, height, color="brown", fill="brown")
	pensize(5)
	goto_(80, 70)
	left(90)
	color("black")
	forward(30)

def draw_flower(main_color="yellow", middle_color="red", **kwargs):
	setheading(90)
	pensize(5)
	color("green")
	forward(100)

	left(90)
	begin_fill()
	for _ in range(2, **kwargs):
		forward(50)
		right(50)
		forward(50)
		right(130)
	end_fill()
	right(90)

	forward(100)
	Circle(40, color=main_color, fill=main_color, position=(40, 240))
	Circle(15, color=middle_color, fill=middle_color, position=(15, 240))

def draw_star(width=100, **kwargs):
	pencolor("yellow")
	fillcolor("yellow")

	begin_fill()
	for _ in range(5):
		forward(width)
		left(144)
	end_fill()


def draw_sun(width, **kwargs):
	pencolor("yellow")
	fillcolor("yellow")

	begin_fill()
	for _ in range(18):
		forward(width)
		left(100)
	end_fill()

def draw_tree(**kwargs):
	left(90)
	width(20)
	color("brown")
	forward(200)

	right(90)
	width(7.5)
	color("green")
	for x in range(31):
		forward(x*4)
		left(90)
	left(90)

def draw_galaxy(**kwargs):
	draw_star()
	goto_(200, 65)
	draw_star()
	goto_(-315, 165)
	draw_star()
	goto_(190, 0)
	draw_star()
	goto_(-200, 65)
	draw_star()

def draw_fence(width, count, color="red", **kwargs):
	for x in range(count):
		Rectangle(width/4, width, position=(x*width/4, 0), color=color, fill=color)
		Triangle(width/4, position=(x*width/4, width), color=color, fill=color)