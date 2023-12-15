import pygame_gui as pgui
from gmath import *
from config import *
from particle import *
from entity import *
from containers import *
from gun import *
from gun_mode import *

ENEMY_SPAWN_VERTICES = [(0,0),(0,0),(0,0),(0,0)]
ENEMY_TIMER = 5
ENEMY_RANGE = 30
ENEMY_DAMAGE = 1

WAVE_TIMER = time.time()
WAVE_COUNT = 0
WAVE_TIME = 10


PREV_BOSS = 0
BOSS_IN_EVERY = 3 #Waves
BOSS_INCOMMING = False

BOSS_ALERT_BACKGROUND = pg.Rect(0,0,800,600)
BOSS_ALERT_TIMER = time.time()
BOSS_WAVE = False

BOSS_SPAWNED = False
BOSS_COUNT = 2

BOSS_DMG_1 = 3
BOSS_DMG_2 = 5
BOSS_DMG_3 = 7
BOSS_DMG_4 = 7

BOSS_HP_1 = 1000
BOSS_HP_2 = 2000
BOSS_HP_3 = 3000
BOSS_HP_4 = 4000

BOSS_DMG_1 = 3
BOSS_DMG_2 = 5
BOSS_DMG_3 = 7
BOSS_DMG_4 = 7

BOSS_SPEED_1 = 2
BOSS_SPEED_2 = 1
BOSS_SPEED_3 = 0.5
BOSS_SPEED_4 = 0.5

BOSS_RANGE_1 = 30
BOSS_RANGE_2 = 50
BOSS_RANGE_3 = 50
BOSS_RANGE_4 = 50


CURRENT_DAMAGE = ENEMY_DAMAGE
CURRENT_HP = BOSS_HP_1
CURRENT_SPEED = BOSS_SPEED_1
CURRENT_RANGE = ENEMY_RANGE
CURRENT_BOSS_IMG = 0

BOSS_IMG_1 = 0
BOSS_IMG_2 = 1
BOSS_IMG_3 = 3

TOTAL_BOSS = 4

FINAL_BOSS_SPRITE = pg.image.load("assets/final_boss.png")
FINAL_BOSS_W = 32
FINAL_BOSS_H = 32
MODE_TIMER = time.time()
MODE_CURR = 0

MODE_IN_EVERY = 1
PREV_LVL_MODE = 0

MODE_INFO_TIME = time.time()
MODE_UI_TIME = 0

# Inits
pg.init()
pg.font.init()

screen = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
display = pg.Surface((DISPLAY_WIDTH, DISPLAY_HEIGHT))
ui_surface = pg.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))

ui_manager = pgui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pg.time.Clock()

ui_font = pg.font.Font("assets/font.ttf", 50)
ui_font_small = pg.font.Font("assets/font.ttf", 20)
ui_font_damage = pg.font.Font("assets/font.ttf", 10)

pg.mixer.music.load("assets/game_music.mp3")
pg.mixer.music.play(loops = -1)
pg.mixer.music.set_volume(0.3)

shoot_sound = pg.mixer.Sound("assets/shoot.wav")
hit_sound = pg.mixer.Sound("assets/hit.wav")
explode_sound = pg.mixer.Sound("assets/explosion.wav")
lvl_up_sound = pg.mixer.Sound("assets/lvl_up.wav")
disabled_noises = pg.mixer.Sound("assets/disabled.wav")

# Health Bar
health_bar = pg.Rect(10,570,400,20)

# Exp Bar
exp_bar = pg.Rect(10,500,400,20)

# Boss Hp
boss_hp_bar = pg.Rect(400,30,400,20)


# Main menu
title = pgui.elements.UILabel(
	relative_rect = pg.Rect(300, 100, 200, 50),
	text = "Game",
	manager = ui_manager
)

start_button = pgui.elements.UIButton(
	relative_rect = pg.Rect(350, 275, 100, 50),
	text = "Start",
	manager = ui_manager
)

quit_button = pgui.elements.UIButton(
	relative_rect = pg.Rect(350, 375, 100, 50),
	text = "Quit",
	manager = ui_manager
)

def boss_alert_show():
	global BOSS_INCOMMING
	global player
	pg.draw.rect(screen,(0,0,0,0),BOSS_ALERT_BACKGROUND)
	screen.blit(boss_alert,(200,300))
	player.rect.x = 0
	player.rect.y = 0
	if (time.time() - BOSS_ALERT_TIMER) >= 2:
		BOSS_INCOMMING = False
	


def menu_show():
	title.show()
	start_button.show()
	quit_button.show()

def menu_hide():
	title.hide()
	start_button.hide()
	quit_button.hide()


# Spritesheet
sprite_sheet: pg.Surface = pg.image.load(SPRITE_SHEET)

def sprite_sheet_get(rect: pg.Rect) -> pg.Surface:
	rect.x *= rect.w
	rect.y *= rect.h

	sprite = pg.Surface(rect.size)
	sprite.set_colorkey(SPRITE_COLOR_KEY)
	sprite.fill(SPRITE_COLOR_KEY)
	sprite.blit(sprite_sheet, (0, 0), rect)
	return sprite


# Camera
camera: list[float, float] = [0, 0]


# Player
player = Entity(
	EntityType.PLAYER,
	sprite_sheet_get(pg.Rect(2, 0, SPRITE_SIZE, SPRITE_SIZE)),
	pg.Rect(0, 0, ENTITY_SIZE, ENTITY_SIZE),
	2,
	PLAYER_HEALTH,
	ui_font_damage,
	hit_sound
)
ENTITIES.append(player)


# Enemy
def spawn_enemy(positions: list[tuple[int,int]]):
	if not BOSS_WAVE:
		pos = random.choice(positions)
		enemy = Entity(
			EntityType.ENEMY,
			sprite_sheet_get(pg.Rect(4, 0, SPRITE_SIZE, SPRITE_SIZE)),
			pg.Rect(pos[0], pos[1], ENTITY_SIZE, ENTITY_SIZE),
			2,
			ENEMY_HEALTH,
			ui_font_damage,
			hit_sound
		)
		ENTITIES.append(enemy)
	
	if BOSS_WAVE and not BOSS_INCOMMING:
		global BOSS_SPAWNED
		if BOSS_SPAWNED == False:
			pos = random.choice(positions)
			if BOSS_COUNT == 5:
				ss = CURRENT_BOSS_IMG
			else:
				ss = sprite_sheet_get(pg.Rect(CURRENT_BOSS_IMG, 0, SPRITE_SIZE, SPRITE_SIZE))
			enemy = Entity(
				EntityType.BOSS,
				ss,
				pg.Rect(pos[0], pos[1], ENTITY_SIZE, ENTITY_SIZE),
				CURRENT_SPEED,
				CURRENT_HP,
				ui_font_damage,
				hit_sound,
				reset_boss = reset_boss
			)
			ENTITIES.append(enemy)
			BOSS_SPAWNED = True


def check_attack_range(enemy: Entity, player: Entity) -> bool:
	p1 = enemy.rect.center
	p2 = player.rect.center
	dist = math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
	if dist <= ENEMY_RANGE:
		return True
	return False


# Enemy Spawn Area
enemy_spawn_area = pg.Rect(
	0,0,
	400,400
)


# Gun
default = Default()
shawty = Shawty()
going_bananas = GoingBananas()
grenade_launcher = GrenadeLauncher()

ACCUIRED_MODES.append(grenade_launcher)
gun = ACCUIRED_MODES[MODE_CURR]

def render_gun_modes(surface: pg.Surface):
	for x, mode in enumerate(ACCUIRED_MODES):
		p = x * 50
		if x == MODE_CURR:
			pg.draw.circle(surface, (255, 255, 255), (600 + p, 550), 23)
		pg.draw.circle(surface, mode.conf.color, (600 + p, 550), 20)

		texture = ui_font_small.render(f"{x}", False, (255, 255, 255))
		surface.blit(texture, (600 + p - 5, 540))


# Reset
def reset_game():
	global WAVE_COUNT, WAVE_TIME, WAVE_TIMER, ENEMY_TIMER
	global LVL, EXP_VAR, EXP_GAIN_NORMAL, EXP_MAX, EXP_MAX_GROWTH
	global player, ENTITIES
	global BOSS_WAVE, BOSS_SPAWNED, CURRENT_SPEED, CURRENT_HP, CURRENT_DAMAGE, BOSS_COUNT, CURRENT_RANGE, ENTITY_SIZE
	global MODE_TIMER, MODE_CURR, current_mode_txt

	BOSS_WAVE = False
	BOSS_SPAWNED = False
	CURRENT_SPEED = 2
	CURRENT_HP = ENEMY_HEALTH
	CURRENT_DAMAGE = 1
	BOSS_COUNT = 1
	CURRENT_RANGE = ENEMY_RANGE

	WAVE_TIMER = time.time()
	WAVE_COUNT = 0
	WAVE_TIME = 10
	ENEMY_TIMER = 5

	current_mode_txt = ui_font_small.render(f"Current Mode: None", False, (255,255,255))

	set_exp_var(0)
	LVL = 0
	EXP_GAIN_NORMAL = 5
	EXP_MAX = 100
	EXP_MAX_GROWTH = 100

	player.rect.x = 0
	player.rect.y = 0
	player.health = PLAYER_HEALTH

	ENTITY_SIZE = 16

	ENTITIES.clear()
	ENTITIES.append(player)

	MODE_TIMER = time.time()
	MODE_CURR = 0
	ACCUIRED_MODES.clear()
	ACCUIRED_MODES.append(default)

# Main loop
enemy_timer = ENEMY_TIMER
game = False
running = True
last_time = time.time()

wave_info = ui_font.render(f"Wave: {WAVE_COUNT}", False, (0,255,255))

def reset_boss():
	global BOSS_SPAWNED, CURRENT_SPEED, CURRENT_HP, CURRENT_DAMAGE, BOSS_WAVE, ENTITY_SIZE
	BOSS_WAVE = False
	BOSS_SPAWNED = False
	CURRENT_SPEED = 2
	CURRENT_HP = ENEMY_HEALTH
	CURRENT_DAMAGE = 1
	ENTITY_SIZE = 16

aquired_mode_txt = ui_font_small.render(f"", False, (255,255,255))

current_mode_txt = ui_font_small.render(f"Current Mode: None", False, (255,255,255))

while running:
	MODE_UI_TIME = time.time() - MODE_TIMER
	# Calculating delta time
	dt = time.time() - last_time
	dt *= FPS
	last_time = time.time()
	tick = clock.tick(FPS)

	# Gameloop
	if game:
		display.fill(BG_COLOR)

		# Updating camera
		camera[0] += (player.rect.x - camera[0] - DISPLAY_WIDTH  / 2) / 10
		camera[1] += (player.rect.y - camera[1] - DISPLAY_HEIGHT / 2) / 10

		# Enemy Spawn Area
		center = [
			(player.rect.x + player.rect.w / 2) - enemy_spawn_area.w / 2,
			(player.rect.y + player.rect.h / 2) - enemy_spawn_area.h / 2
		]

		enemy_spawn_area.x = center[0]
		enemy_spawn_area.y = center[1]

		ENEMY_SPAWN_VERTICES[0] = (enemy_spawn_area.x, enemy_spawn_area.y)
		ENEMY_SPAWN_VERTICES[1] = (enemy_spawn_area.x + enemy_spawn_area.width, enemy_spawn_area.y)
		ENEMY_SPAWN_VERTICES[2] = (enemy_spawn_area.x + enemy_spawn_area.width, enemy_spawn_area.y + enemy_spawn_area.height)
		ENEMY_SPAWN_VERTICES[3] = (enemy_spawn_area.x, enemy_spawn_area.y + enemy_spawn_area.height)
		
		# Enemy Timer
		enemy_timer -= 0.1
		if enemy_timer <= 0:
			spawn_enemy(ENEMY_SPAWN_VERTICES)
			enemy_timer = ENEMY_TIMER

		particle_draw(display, camera)

		# Wave Timer
		wave_timer = time.time()
		wave_timer_ui = ui_font_small.render(f"Wave Timer: {int(wave_timer - WAVE_TIMER)}s", False, (0,255,255))
		if (wave_timer - WAVE_TIMER) >= WAVE_TIME:
			WAVE_COUNT += 1
			player.health = 100
			WAVE_TIMER = time.time()
			ENEMY_TIMER -= 1
			WAVE_TIME += 5

		if not BOSS_WAVE:
			if (wave_timer - WAVE_TIMER) >= WAVE_TIME:
				WAVE_COUNT += 1
				WAVE_TIMER = time.time()
				ENEMY_TIMER -= 1
				WAVE_TIME += 5
					
		# updaing health bar
		health_bar.w = (player.health/100) * 400
		heal_num = ui_font_small.render(f"{player.health}/{PLAYER_HEALTH}",False,(255,0,0))

		# updaing exp bar
		exp_bar.w = (get_exp_var()/EXP_MAX) * 400
		exp_num = ui_font_small.render(f"LVL: {LVL}",False,(0,255,70))

		# updaing exp bar
		tot_hp = 1
		c_hp = 0
		for ent in ENTITIES:
			if ent.etype == EntityType.BOSS:
				c_hp = ent.health
				if BOSS_COUNT == 2:
					tot_hp = BOSS_HP_1
				if BOSS_COUNT == 3:
					tot_hp = BOSS_HP_2
				if BOSS_COUNT == 4:
					tot_hp = BOSS_HP_3
				if BOSS_COUNT == 5:
					tot_hp = BOSS_HP_4
		boss_hp_bar.w = (c_hp/tot_hp) * 400
		boss_hp_txt = ui_font_small.render(f"hp: {c_hp}/{tot_hp}",False,(0,255,70))
		

		if(get_exp_var() >= EXP_MAX):
			LVL += 1
			lvl_up_sound.play()
			EXP_MAX += EXP_MAX_GROWTH
			set_exp_var(0)
			modes = [shawty,going_bananas, grenade_launcher]
			mode = random.choice(modes)
			
			if mode not in ACCUIRED_MODES:
				ACCUIRED_MODES.append(mode)
				aquired_mode_txt = ui_font_small.render(f"AQUIRED MODE: {mode.type}", False, (255,255,255))
					
		if time.time() - MODE_INFO_TIME > 2:
			aquired_mode_txt = ui_font_small.render(f"",False,(255,255,255))
			MODE_INFO_TIME = time.time()

		# Updating entities
		for i,ent in enumerate(ENTITIES):
			if BOSS_INCOMMING:
				if ent.etype == EntityType.ENEMY:
					ENTITIES.pop(i)
			if not BOSS_WAVE:
				if (WAVE_COUNT - PREV_BOSS) >= BOSS_IN_EVERY:
					if BOSS_COUNT <= TOTAL_BOSS:
						BOSS_WAVE = True
						BOSS_ALERT_TIMER = time.time()
						BOSS_INCOMMING = True

					if BOSS_COUNT == 1:
						CURRENT_DAMAGE = BOSS_DMG_1
						CURRENT_HP = BOSS_HP_1
						CURRENT_SPEED = BOSS_SPEED_1
						CURRENT_RANGE = BOSS_RANGE_1
						CURRENT_BOSS_IMG = BOSS_IMG_1
					
					if BOSS_COUNT == 2:
						CURRENT_DAMAGE = BOSS_DMG_2
						CURRENT_HP = BOSS_HP_2
						CURRENT_SPEED = BOSS_SPEED_2
						CURRENT_RANGE = BOSS_RANGE_2
						CURRENT_BOSS_IMG = BOSS_IMG_2

					if BOSS_COUNT == 3:
						CURRENT_DAMAGE = BOSS_DMG_3
						CURRENT_HP = BOSS_HP_3
						CURRENT_SPEED = BOSS_SPEED_3
						CURRENT_RANGE = BOSS_RANGE_3
						CURRENT_BOSS_IMG = BOSS_IMG_3
					
					if BOSS_COUNT == 4:
						CURRENT_BOSS_IMG = FINAL_BOSS_SPRITE
						ENTITY_SIZE = FINAL_BOSS_H
						CURRENT_DAMAGE = BOSS_DMG_4
						CURRENT_HP = BOSS_HP_4
						CURRENT_SPEED = BOSS_SPEED_4
						CURRENT_RANGE = BOSS_RANGE_4

					if BOSS_COUNT <= TOTAL_BOSS:
						PREV_BOSS = WAVE_COUNT
						BOSS_COUNT += 1
						
				

			# Updating velocity
			if ent.etype == EntityType.PLAYER:
				ent.update_vel()
			else:
				# Enemy AI
				displacement_X = (player.rect.x - ent.rect.x+0.000000000000000001)
				displacement_Y = (player.rect.y - ent.rect.y+0.000000000000000001)
				movement_angle = math.atan(displacement_Y/displacement_X)
				ent.vel[1] = 2*(abs(math.sin(movement_angle))/(displacement_Y/abs(displacement_Y)))
				ent.vel[0] = 2*(math.cos(movement_angle)/(displacement_X/abs(displacement_X)))

				# Enemy attack
				if check_attack_range(ent, player):
					player.take_damage(CURRENT_DAMAGE)


			# Updating position
			(
				ent
					.update_position(dt)
					.update_animation()
					.draw(display, camera)
			)

		if player.health <= 0:
			game = False

		# Gun timer
		gun = ACCUIRED_MODES[MODE_CURR]
		if gun.type != GunType.DEFAULT:
			if time.time() - MODE_TIMER >= gun.conf.lifetime:
				current_mode_txt = ui_font_small.render(f"Current Mode: None", False, (255,255,255))
				ACCUIRED_MODES.remove(gun)
				MODE_TIMER = time.time()
				MODE_CURR = 0

		# Updaing gun
		(
			gun
				.attach_onto(player)
				.update_position(camera)
				.update_trigger(shoot_sound)
				.draw(display, camera)
		)
		
		# Damage Showing
		draw_dmg(display, camera)
		draw_exp(display, camera)

		draw_trail(display, camera)
		grenade_draw(display, camera, explode_sound)

		screen.blit(pg.transform.scale(display, (WINDOW_WIDTH, WINDOW_HEIGHT)), (0, 0))
		wave_info = ui_font.render(f"Wave: {WAVE_COUNT}", False, (0,255,255))

		boss_alert = ui_font.render(f"BOSS INCOMMING!", False, (255,0,0))

		# Drawing Text On To Screen
		screen.blit(wave_info, (0,0))
		screen.blit(wave_timer_ui, (0,60))
		screen.blit(heal_num, (10,550))
		screen.blit(exp_num, (10,480))
		screen.blit(aquired_mode_txt, (300,480))
		screen.blit(current_mode_txt, (0,80))

		if BOSS_WAVE:
			screen.blit(boss_hp_txt, (400, 5))
			pg.draw.rect(screen, (255,0,0), boss_hp_bar)


		# Health / Exp Bar
		pg.draw.rect(screen, (255,0,0), health_bar)
		pg.draw.rect(screen, (0,255,70), exp_bar)

		# Drawing modes
		render_gun_modes(screen)

		if BOSS_INCOMMING == True:
			boss_alert_show()

	# UI loop
	else:
		menu_show()
		ui_surface.fill((0, 0, 0))
		t = tick / 1000.0

		ui_manager.update(t)
		ui_manager.draw_ui(ui_surface)
		screen.blit(ui_surface, (0, 0))

	# Event
	for event in pg.event.get():
		if event.type == pg.QUIT:
			running = False

		# Controls
		elif event.type == pg.KEYDOWN:
			if event.key == pg.K_w: player.movement["up"]    = True
			elif event.key == pg.K_a: player.movement["left"]  = True
			elif event.key == pg.K_s: player.movement["down"]  = True
			elif event.key == pg.K_d: player.movement["right"] = True

			elif event.key == pg.K_2:
				if len(ACCUIRED_MODES) >= 2 and ACCUIRED_MODES[MODE_CURR].type == GunType.DEFAULT:
					MODE_TIMER = time.time()
					MODE_CURR = 1
					MODE_TIMER = time.time()
					current_mode_txt = ui_font_small.render(f"Current Mode: {ACCUIRED_MODES[MODE_CURR].type}", False, (255,255,255))
				else:
					disabled_noises.play()
			elif event.key == pg.K_3:
				if len(ACCUIRED_MODES) >= 3 and ACCUIRED_MODES[MODE_CURR].type == GunType.DEFAULT:
					MODE_TIMER = time.time()
					MODE_CURR = 2
					current_mode_txt = ui_font_small.render(f"Current Mode: {ACCUIRED_MODES[MODE_CURR].type}", False, (255,255,255))
				else:
					disabled_noises.play()
			elif event.key == pg.K_4:
				if len(ACCUIRED_MODES) >= 4 and ACCUIRED_MODES[MODE_CURR].type == GunType.DEFAULT:
					MODE_TIMER = time.time()
					MODE_CURR = 3
					current_mode_txt = ui_font_small.render(f"Current Mode: {ACCUIRED_MODES[MODE_CURR].type}", False, (255,255,255))
				else:
					disabled_noises.play()

		elif event.type == pg.KEYUP:
			if event.key == pg.K_w: player.movement["up"]      = False
			elif event.key == pg.K_a: player.movement["left"]  = False
			elif event.key == pg.K_s: player.movement["down"]  = False
			elif event.key == pg.K_d: player.movement["right"] = False

		elif event.type == pg.MOUSEBUTTONDOWN:
			if game:
				if pg.mouse.get_pressed()[0]:
					gun.fire = True
			
		elif event.type == pg.MOUSEBUTTONUP:
			if game:
				if not pg.mouse.get_pressed()[0]:
					gun.fire = False

		# UI
		elif event.type == pgui.UI_BUTTON_PRESSED:
			if event.ui_element == start_button:
				menu_hide()
				game = True
				reset_game()
			elif event.ui_element == quit_button:
				pg.event.post(pg.event.Event(pg.QUIT))

		ui_manager.process_events(event)

	# Updates
	pg.display.update()


# Cleaup
pg.quit()
