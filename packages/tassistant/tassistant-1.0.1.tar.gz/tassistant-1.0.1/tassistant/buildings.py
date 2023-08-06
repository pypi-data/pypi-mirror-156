from tassistant import *


def draw_tree(trunk_color="brown", leaf_color="green"):
	Rectangle(50, 100, color=trunk_color, fill=trunk_color)
	Triangle(200, 135, color=leaf_color, fill=leaf_color, position=(-75, 100))
	Triangle(175, 120, fill=leaf_color, position=(-62, 160))
	Triangle(150, 105, fill=leaf_color, position=(-50, 220))


def draw_door(width=90, height=180):
	Rectangle(width, height, color="brown", fill="brown")
	pensize(5)
	goto_(80, 70)
	left(90)
	color("black")
	forward(30)


def draw_flower(main_color="yellow", middle_color="red"):
	setheading(90)
	pensize(5)
	color("green")
	forward(100)

	left(90)
	begin_fill()
	for _ in range(2):
		forward(50)
		right(50)
		forward(50)
		right(130)
	end_fill()
	right(90)

	forward(100)
	Circle(40, color=main_color, fill=main_color, position=(40, 240))
	Circle(15, color=middle_color, fill=middle_color, position=(15, 240))


def draw_house(base_color="red", roof_color="green"):
    Rectangle(100, color=base_color, fill=base_color)
    Triangle(120, color=roof_color, fill=roof_color, position=(-10, 100))