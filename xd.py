from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
import numpy as np
from math import *
import itertools

rotation_axes = input('Enter the axis to rotate (like: \'xy, zx\' *separate multiple dimentions with \',\')\n→ :').split(',')

WHITE = (205, 205, 205)
RED = (255, 50, 50)
BLACK = (50, 50, 50)

WIDTH, HEIGHT = 1920, 1080
pygame.display.set_caption('')
screen = pygame.display.set_mode((WIDTH, HEIGHT))

SCALE = 200
VIEW_SCALE = 5

perspective_view = True

circle_pos = [WIDTH/2, HEIGHT/2]
LINE_WIDTH = 2
POINT_WIDTH = 5

points = []

for x in [-1, 1]:
	for y in [-1, 1]:
		for z in [-1, 1]:
			for w in [-1, 1]:
				points.append(np.matrix([x, y, z, w]))

def get_connections(points): # 例えば[1, 1, 1, 1], [1, 1, 1, -1]はw軸のみが違うので互いにつながってなければならない
	connections = []
	all = itertools.combinations(range(len(points)), 2) # 重複なし2つの組み合わせ
	for (i, j) in all: 
		if i != j: # 自分x自分を調べる必要はない
			diff = 0
			for k in range(4):
				if points[i][0, k] != points[j][0, k]:
					diff += 1
			if diff == 1:
				connections.append(np.matrix([i, j]))
			#if np.dot(points[i], points[j].reshape(4, 1)) == 2: 
			#	# それぞれの座標を掛け算して、異なる軸が1つしかないものを求める
			#	connections.append(np.matrix([i, j]))
	return connections

def get_projection_matrix_3d(point):
	v = 1 # 平行投影
	if perspective_view: # 透視投影
		v = VIEW_SCALE / (VIEW_SCALE - point[3])
	return np.matrix([
		[v, 0, 0, 0],
		[0, v, 0, 0],
		[0, 0, v, 0]
	])

def get_projection_matrix_2d(point):
	v = 1
	if perspective_view:
		v = VIEW_SCALE / (VIEW_SCALE - point[2])
	return np.matrix([
		[v, 0, 0],
		[0, v, 0]
	])

projected_points = [
	[n, n] for n in range(len(points))
] # [[0, 0], [1, 1], [2, 2]....

def connect_points(i, j, points):
	pygame.draw.line(screen, BLACK, ((points[i][0]), (points[i][1])), (points[j][0], points[j][1]), LINE_WIDTH)

def rotate(point):

	rotation_xy = np.matrix([
			[1, 0, 0, 0],
			[0, 1, 0, 0],
			[0, 0, cos(angle), -sin(angle)],
			[0, 0, sin(angle), cos(angle)]
		])

	rotation_yz = np.matrix([
			[cos(angle), 0, 0, -sin(angle)],
			[0, 1, 0, 0],
			[0, 0, 1, 0],
			[sin(angle), 0, 0, cos(angle)]
		])

	rotation_xz = np.matrix([
			[1, 0, 0, 0],
			[0, cos(angle), 0, -sin(angle)],
			[0, 0, 1, 0],
			[0, sin(angle), 0, cos(angle)]
		])

	rotation_xw = np.matrix([
			[1, 0, 0, 0],
			[0, cos(angle), -sin(angle), 0],
			[0, sin(angle), cos(angle), 0],
			[0, 0, 0, 1]
		])

	rotation_yw = np.matrix([
			[cos(angle), 0, -sin(angle), 0],
			[0, 1, 0, 0],
			[sin(angle), 0, cos(angle), 0],
			[0, 0, 0, 1]
		])

	rotation_zw = np.matrix([
			[cos(angle), -sin(angle), 0, 0],
			[sin(angle), cos(angle), 0, 0],
			[0, 0, 1, 0],
			[0, 0, 0, 1]
		])

	rotated = point.reshape((4, 1))
	if 'xy' in rotation_axes or 'yx' in rotation_axes:
		rotated = np.dot(rotation_xy, rotated)
	if 'yz' in rotation_axes or 'zy' in rotation_axes:
		rotated = np.dot(rotation_yz, rotated)
	if 'xz' in rotation_axes or 'zx' in rotation_axes:
		rotated = np.dot(rotation_xz, rotated)
	if 'xw' in rotation_axes or 'wx' in rotation_axes:
		rotated = np.dot(rotation_xw, rotated)
	if 'yw' in rotation_axes or 'wy' in rotation_axes:
		rotated = np.dot(rotation_yw, rotated)
	if 'zw' in rotation_axes or 'wz' in rotation_axes:
		rotated = np.dot(rotation_zw, rotated)
	return rotated

def projection(rotated):
	projected3d = np.dot(get_projection_matrix_3d(rotated), rotated)
	projected2d = np.dot(get_projection_matrix_2d(projected3d), projected3d)
	x = int(projected2d[0][0] * SCALE) + circle_pos[0]
	y = int(projected2d[1][0] * SCALE) + circle_pos[1]
	return x, y


def draw_coordinates():
	origin = np.matrix([0, 0, 0, 0])
	coordinates = []
	coordinate_colors = []

	coordinates.append(
		np.matrix([2, 0, 0, 0]
			))
	coordinate_colors.append((255, 50, 50))

	coordinates.append(
		np.matrix([0, 2, 0, 0]
			))
	coordinate_colors.append((50, 255, 50))

	coordinates.append(
		np.matrix([0, 0, 2, 0]
			))
	coordinate_colors.append((50, 50, 255))

	coordinates.append(
		np.matrix([0, 0, 0, 2]
			))
	coordinate_colors.append((255, 50, 255))

	rotated_origin = rotate(origin)
	x_origin, y_origin = projection(rotated_origin)

	for i in range(4):
		coordinate_color = coordinate_colors[i]
		coordinate = coordinates[i]
		rotated = rotate(coordinate)
		x, y = projection(rotated)
		pygame.draw.circle(screen, coordinate_color, (x, y), 5)
		pygame.draw.line(screen, coordinate_color, ((x), (y)), ((x_origin), (y_origin)), LINE_WIDTH)

clock = pygame.time.Clock()
angle = 0

while True:
	clock.tick(60)
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			exit()
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				pygame.quit()
				exit()
	# update
	angle += 1/200

	screen.fill(WHITE)

	# drawing
	i = 0
	for point in points:
		rotated = rotate(point)
		x, y = projection(rotated)
		projected_points[i] = [x, y]
		pygame.draw.circle(screen, BLACK, (x, y), POINT_WIDTH)
		i += 1

	# https://www.youtube.com/watch?v=qw0oY6Ld-L0 29:30参照。1つの頂点は3つとつながる
	connections = get_connections(points)
	for connect in connections:
		connect_points(connect[0, 0], connect[0, 1], projected_points)

	draw_coordinates()

	pygame.display.update()