import pygame
import os
import time
import random
pygame.font.init() # Gets fonts initialised

WIDTH, HEIGHT = 1000, 1000

# Window dimensions
WIN = pygame.display.set_mode((WIDTH, HEIGHT))

# Window name
pygame.display.set_caption("Space Shooter")

# Load images
RED_SPACE_SHIP = pygame.transform.scale(pygame.image.load("pixel_ship_red_small.png"), (125, 125))
GREEN_SPACE_SHIP = pygame.transform.scale(pygame.image.load("pixel_ship_green_small.png"), (125, 125))
BLUE_SPACE_SHIP = pygame.transform.scale(pygame.image.load("pixel_ship_blue_small.png"), (125, 125))

# Player Ship image
YELLOW_SPACE_SHIP = pygame.transform.scale(pygame.image.load("pixel_ship_yellow.png"), (100, 100))

# Laser images
RED_LASER = pygame.image.load("pixel_laser_red.png")
GREEN_LASER = pygame.image.load("pixel_laser_green.png")
BLUE_LASER = pygame.image.load("pixel_laser_blue.png")
YELLOW_LASER = pygame.image.load("pixel_laser_yellow.png")

# Background image
BG = pygame.transform.scale(pygame.image.load("background-black.png"), (WIDTH, HEIGHT))

class Laser:
	def __init__(self, x, y, img):
		self.x = x
		self.y = y
		self.img = img
		self.mask = pygame.mask.from_surface(self.img)

	def draw(self, window):
		window.blit(self.img, (self.x, self.y))

	def move(self, vel):
		self.y += vel

	def off_screen(self, height):
		return not (self.y <= height and self.y >= 0)

	def collision(self, obj):
		return collide(self, obj)

class Ship: 
	"""Ship class for player and enemy Ships"""
	COOLDOWN = 30

	def __init__(self, x, y, health = 100):
		self.x = x
		self.y = y
		self.health = health
		self.ship_img = None # Image will vary for each Ship so we will do that per instance
		self.laser_img = None
		self.lasers = []
		self.cool_down_counter = 0 # Cool down on how often Ships shoot

	def draw(self, window):
		# pygame.draw.rect(window, (255, 0, 0), (self.x, self.y, 50, 50)) # Draws rectangle on surface 'window', 2nd arg is x,y position, width, height and optional variable for hollow shape.
		window.blit(self.ship_img, (self.x, self.y))
		for laser in self.lasers:
			laser.draw(window)

	def move_lasers(self, vel, obj):
		self.cooldown()
		for laser in self.lasers:
			laser.move(vel)
			if laser.off_screen(HEIGHT):
				self.lasers.remove(laser)
			elif laser.collision(obj):
				obj.health -= 10
				self.lasers.remove(laser)

	def cooldown(self):
		if self.cool_down_counter >= self.COOLDOWN:
			self.cool_down_counter = 0
		elif self.cool_down_counter > 0:
			self.cool_down_counter += 1

	def shoot(self):
		if self.cool_down_counter == 0:
			laser = Laser(self.x, self.y, self.laser_img)
			self.lasers.append(laser)
			self.cool_down_counter = 1


	def get_width(self):
		return self.ship_img.get_width()

	def get_height(self):
		return self.ship_img.get_height()


class Player(Ship): # Inherits from class Ship
	def __init__(self, x, y, health = 100):
		super().__init__(x, y, health) # Start with Ship's initialisation method
		self.ship_img = YELLOW_SPACE_SHIP
		self.laser_img = YELLOW_LASER
		self.mask = pygame.mask.from_surface(self.ship_img) # To make collisions with pixels of Ship and not rectangle around image.
		self.max_health = health # So we know starting health

	def move_lasers(self, vel, objs):
		self.cooldown()
		for laser in self.lasers:
			laser.move(vel)
			if laser.off_screen(HEIGHT):
				self.lasers.remove(laser)
			else:
				for obj in objs:
					if laser.collision(obj):
						objs.remove(obj) 
						if laser in self.lasers:
							self.lasers.remove(laser)

	def draw(self, window):
		super().draw(window)
		self.healthbar(window)

	def healthbar(self, window):
		pygame.draw.rect(window, (255,0,0), (self.x + 5, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() - 10, 7))
		pygame.draw.rect(window, (0,255,0), (self.x + 5, self.y + self.ship_img.get_height() + 10, (self.ship_img.get_width() - 10)*(self.health/self.max_health), 7))

class Enemy(Ship):
	COLOUR_MAP = {
				 "red": (RED_SPACE_SHIP, RED_LASER),
				 "green": (GREEN_SPACE_SHIP, GREEN_LASER),
				 "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
				 }

	def __init__(self, x, y, colour, health = 100):
		super().__init__(x, y, health)
		self.ship_img, self.laser_img = self.COLOUR_MAP[colour]
		self.mask = pygame.mask.from_surface(self.ship_img)

	def move(self, vel):
		self.y += vel

	def shoot(self):
		if self.cool_down_counter == 0:
			laser = Laser(self.x-20, self.y, self.laser_img)
			self.lasers.append(laser)
			self.cool_down_counter += 1


def collide(obj1, obj2):
	offset_x = obj2.x - obj1.x
	offset_y = obj2.y - obj1.y
	return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None # Returns a tuple of the co-ordinates of collision

def main():
	run = True
	FPS = 144 # Fps of game, higher is faster
	level = 0
	lives = 5
	main_font = pygame.font.SysFont("impact", 50) # Our font name and size
	lost_font = pygame.font.SysFont("impact", 60)

	enemies = []
	wave_length = 5
	enemy_vel = 1

	player_vel = 5
	laser_vel = 6

	player = Player(300, 630) # Uses Ship class to make a Ship instance

	clock = pygame.time.Clock()

	lost = False
	lost_count = 0

	def redraw_window(): # Function can only be called within main function
		WIN.blit(BG, (0, 0))
		# Draw text
		lives_label = main_font.render(f"Lives: {lives}", 1, (255, 255, 255)) # Uses our font to render a f string out and assign it to a variable
		level_label = main_font.render(f"Level: ", 1, (255,255,255))
		level2_label = main_font.render(f"{level}", 1, (255,255,255))

		WIN.blit(lives_label, (10, 10)) 
		WIN.blit(level_label, (WIDTH - level_label.get_width() -40, 10)) # These two lines give a position for our variables
		WIN.blit(level2_label, (WIDTH - level2_label.get_width() -15, 10))

		for enemy in enemies:
			enemy.draw(WIN)

		player.draw(WIN) # Draws our player on our window

		if lost:
			lost_label = lost_font.render("You Lost!!", 1, (255, 255, 255))
			WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 450))

		pygame.display.update() # Refreshes display


	while run:
		clock.tick(FPS) # We are going to tick our game at fps
		redraw_window()

		if lives <= 0 or player.health <= 0:
			lost = True
			lost_count += 1

		if lost:
			if lost_count > FPS * 3:
				run = False
			else:
				continue

		if len(enemies) == 0:
			level += 1

			wave_length += 5
			for i in range(wave_length):
				enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
				enemies.append(enemy)



		for event in pygame.event.get(): # Checks for events like key presses mouse etc FPS times a second
			if event.type == pygame.QUIT: # If window close is clicked then pygame will quit
				quit() # Exits while loop

		keys = pygame.key.get_pressed() # Will return a dictionary off buttons pressed
		if keys[pygame.K_a] and player.x - player_vel > 0: # Moves left
			player.x -= player_vel
		if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: # Moves right
			player.x += player_vel
		if keys[pygame.K_w] and player.y - player_vel > 0: # Moves up
			player.y -= player_vel
		if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT: # Moves down
			player.y += player_vel
		if keys[pygame.K_SPACE]:
			player.shoot()

		for enemy in enemies[:]:
			enemy.move(enemy_vel)
			enemy.move_lasers(laser_vel, player)

			if random.randrange(0, 2*FPS) == 1:
				enemy.shoot()

			if collide(enemy, player):
				player.health -= 10
				enemies.remove(enemy)
			elif enemy.y + enemy.get_height() > HEIGHT:
				lives -= 1
				enemies.remove(enemy)

		player.move_lasers(-laser_vel, enemies)

def main_menu():
	title_font = pygame.font.SysFont("impact", 70)
	name_font = pygame.font.SysFont("impact", 30)
	run = True
	while run:
		WIN.blit(BG, (0,0))
		title_label = title_font.render("SPACE SHOOTER", 1, (127, 0, 255))
		WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 450))
		name_label = name_font.render("by Abishake Srithar", 1, (127, 0, 255))
		WIN.blit(name_label, (WIDTH/2 - name_label.get_width()/2, 525))		
		pygame.display.update()
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
			if event.type == pygame.MOUSEBUTTONDOWN:
				main()

main_menu()

