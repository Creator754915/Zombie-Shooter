from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.prefabs.health_bar import HealthBar
from Particles import *
from ursina.curve import *
from direct.actor.Actor import Actor
from panda3d.core import TextNode
from panda3d.core import Quat
from math import degrees, atan2
import random
from math import pi, sin, cos
import json

app = Ursina()


def splash_logo():
    camera.overlay.color = color.black
    logoaudio = Audio('assets/sounds/intro_audio.mp3', loop=False, autoplay=False)
    logoaudio.play()
    logo = Sprite(name='ursina_splash', parent=camera.ui, texture='assets/icons/pixel_studio', world_z=camera.overlay.z - 1, scale=.1,
                  color=color.clear)
    logo.animate_color(color.white, duration=7, delay=1, curve=curve.out_quint_boomerang)

    camera.overlay.animate_color(color.clear, duration=2, delay=5)
    destroy(logo, delay=6)


window.title = 'Zombie Shooter'
window.show_ursina_splash = False
window.borderless = False
window.exit_button.enabled = False
window.fullscreen = False


player = FirstPersonController(collider='box')
player.enabled = True
player.y = -1


terrain = Entity(model='assets/models/level', scale=1.2, collider='box')
floor = Entity(model='cube', scale=(88, 4, 88), position=(10, -2, 20), collider='box', color=color.red)
floor.visible = False

Sky()

music = ['music', 'music2']

gun = 'pistol'
model_preview = 'pistol'
ak47 = False
shotgun = False
bullpup = False
machinegun = False

x = 10
z = 10

wave = 0
enemy = 0
nmb_enemy = []
money = 0
bullets = 30
kills = 0


weapon = Entity(model=gun,
                parent=camera.ui,
                scale=0.3,
                color=color.gray,
                texture='white_cube',
                position=(.8, -.5),
                rotation=(0, 75, 5)
                )

HB1 = HealthBar(bar_color=color.lime.tint(-.25),
                roundness=0.2,
                scale=(.6, .04),
                position=(-.78, -.43))

e1 = Entity(model='assets/models/zombie', position=(x, 0, z), scale=(1, 1, 1), collider='box')
e1.add_script(SmoothFollow(target=player, offset=[0, 1, 0], speed=0.2))
enemy_health = Entity(parent=e1, y=1.7, model='cube', color=color.red, world_scale=(1.3, .08, .08))

actor = Actor("assets/animation/attack.gltf")
actor.reparentTo(e1)
actor.loop('run')

wave_text = Text(text='Waves: ', position=(-.88, .48), scale=1.5)
wave_text.font = "assets/fonts/Audiowibe/Audiowibe.ttf"

money_text = Text(text='Money: ', position=(-.65, .48), scale=1.5)
money_text.font = "assets/fonts/Audiowibe/Audiowibe.ttf"

bullets_text = Text(text='Bullet: ', position=(-.35, .48), scale=1.5)
bullets_text.font = "assets/fonts/Audiowibe/Audiowibe.ttf"

fire = Audio(
    'assets/sounds/fire.ogg',
    loop=False,
    autoplay=False
)

reload = Audio(
    'assets/sounds/reload.waw',
    loop=False,
    autoplay=False
)

zombie_die = Audio(
    f'assets/sounds/zombie_die3.mp3',
    loop=False,
    autoplay=False,
    volume=1
)

error = Audio(
    'assets/sounds/error.mp3',
    loop=False,
    autoplay=False
)

bg_music = Audio(
    f'assets/sounds/{random.choice(music)}.mp3',
    loop=True,
    autoplay=False,
    volume=0.75
)

bg_music.play()


def damage(power):
    HB1.value -= power


def heal(value):
    HB1.value += value


def GameOver():
    global gun, wave, enemy, money, x, z

    gun = 'ak47'
    x = 0
    z = 0
    enemy = 0
    money = 0

    HB1.value = 100

    camera.overlay.color = color.black
    logo_gameover = Sprite(name='ursina_splash', parent=camera.ui, texture='assets/icons/Game_Over', world_z=camera.overlay.z - 1, scale=.1,
                  color=color.clear)
    logo_gameover.animate_color(color.white, duration=2, delay=1, curve=curve.out_quint_boomerang)
    camera.overlay.animate_color(color.clear, duration=1, delay=4)
    destroy(logo_gameover, delay=5)

    def splash_input(key):
        destroy(logo_gameover)
        camera.overlay.animate_color(color.clear, duration=.25)

    logo_gameover.input = splash_input


def waves():
    global wave, enemy, money, x, z

    wave += 1
    enemy += 5
    money += 10 * enemy

    for i in range(enemy):
        x = random.randint(-19, 41)
        z = random.randint(-12, 53)
        e2 = duplicate(e1, position=(x, 0, z), collider='box')
        enemy_health = Entity(parent=e2, y=1.7, model='cube', color=color.red, world_scale=(1.3, .08, .08))
        nmb_enemy.append(e2)


def pause():
    def resume():
        application.resume()
        player.enabled = True
        resume_btn.enabled = False
        option_btn.enabled = False
        quit_btn.enabled = False

    def option():
        print_on_screen('Option', scale=3, duration=1)

    def quit_game():
        application.quit()

    resume_btn = Button(text='Resume', color=color.gray, highlight_color=color.light_gray, scale=(.2, .1),
                        position=(0, .15))
    resume_btn.text_entity.font = "assets/fonts/Audiowibe/Audiowibe.ttf"

    option_btn = Button(text='Option', color=color.gray, highlight_color=color.light_gray, scale=(.2, .1),
                        position=(0, 0))
    option_btn.text_entity.font = "assets/fonts/Audiowibe/Audiowibe.ttf"

    quit_btn = Button(text='Quit', color=color.gray, highlight_color=color.light_gray, scale=(.2, .1),
                      position=(0, -.15))
    quit_btn.text_entity.font = "assets/fonts/Audiowibe/Audiowibe.ttf"

    resume_btn.enabled = True
    option_btn.enabled = True
    quit_btn.enabled = True

    resume_btn.tooltip = Tooltip('Resume the game')
    resume_btn.on_click = resume
    option_btn.tooltip = Tooltip('Option menu')
    option_btn.on_click = option
    quit_btn.tooltip = Tooltip('Quit the game')
    quit_btn.on_click = quit_game


def buy_menu():
    player.enabled = False
    model_preview = 'pistol'

    def exit_buy():
        player.enabled = True
        ak47_btn.enabled = False
        shotgun_btn.enabled = False
        bullpup_btn.enabled = False
        machinegun_btn.enabled = False
        exit_btn.enabled = False
        weapon_preview.visible = False

    def buy_ak47():
        global money, ak47
        if money == 850 or money > 850 and ak47 is False:
            ak47 = True
            money -= 850
            print_on_screen('You buy a ak47', position=(-.15, .3), scale=2, duration=2)
        elif ak47 is True:
            error.play()
            print_on_screen('''You have the weapon''', position=(-.15, .3), scale=1, duration=2)
        else:
            error.play()
            print_on_screen('''You don't have the money''', position=(-.15, .3), scale=1, duration=2)

    def buy_shotgun():
        global money, shotgun
        if money == 1500 or money > 1500 and shotgun is False:
            shotgun = True
            money -= 1500
            print_on_screen('You buy a shotgun', position=(-.15, .3), scale=2, duration=2)
        elif shotgun is True:
            error.play()
            print_on_screen('''You have the weapon''', position=(-.15, .3), scale=1, duration=2)
        else:
            error.play()
            print_on_screen('''You don't have the money''', position=(-.15, .3), scale=1, duration=2)

    def buy_bullpup():
        global money, bullpup
        if money == 2000 or money > 2000 and bullpup is False:
            bullpup = True
            money -= 2000
            print_on_screen('You buy a bullpup', position=(-.15, .3), scale=2, duration=2)
        elif bullpup is True:
            error.play()
            print_on_screen('''You have the weapon''', position=(-.15, .3), scale=1, duration=2)
        else:
            error.play()
            print_on_screen('''You don't have the money''', position=(-.15, .3), scale=1, duration=2)

    def buy_machinegun():
        global money, machinegun
        if money == 4500 or money > 4500 and machinegun is False:
            machinegun = True
            money -= 4500
            print_on_screen('You buy a machinegun', position=(-.15, .3), scale=2, duration=2)
        elif machinegun is True:
            error.play()
            print_on_screen('''You have the weapon''', position=(-.15, .3), scale=1, duration=2)
        else:
            error.play()
            print_on_screen('''You don't have the money''', position=(-.15, .3), scale=1, duration=2)

    def preview_ak47():
        global money, ak47, model_preview
        model_preview = 'ak47'
        weapon_preview.model = model_preview

    def preview_shotgun():
        global money, shotgun, model_preview
        model_preview = 'shotgun'
        weapon_preview.model = model_preview

    def preview_bullpup():
        global money, bullpup, model_preview
        model_preview = 'bullpup'
        weapon_preview.model = model_preview

    def preview_machinegun():
        global money, machinegun, model_preview
        model_preview = 'machinegun'
        weapon_preview.model = model_preview

    ak47_btn = Button(text='Ak47', color=color.gray, highlight_color=color.light_gray, scale=(.2, .1),
                      position=(0, .15))
    ak47_btn.text_entity.font = "assets/fonts/Audiowibe/Audiowibe.ttf"

    shotgun_btn = Button(text='Shotgun', color=color.gray, highlight_color=color.light_gray, scale=(.2, .1),
                         position=(0, 0))
    shotgun_btn.text_entity.font = "assets/fonts/Audiowibe/Audiowibe.ttf"

    bullpup_btn = Button(text='Bullpup', color=color.gray, highlight_color=color.light_gray, scale=(.2, .1),
                         position=(0, -.15))
    bullpup_btn.text_entity.font = "assets/fonts/Audiowibe/Audiowibe.ttf"

    machinegun_btn = Button(text='Machinegun', color=color.gray, highlight_color=color.light_gray, scale=(.2, .1),
                            position=(0, -.30))
    machinegun_btn.text_entity.font = "assets/fonts/Audiowibe/Audiowibe.ttf"

    exit_btn = Button(text='Exit', color=color.gray, highlight_color=color.light_gray, scale=(.2, .1),
                      position=(0, -.45))
    exit_btn.text_entity.font = "assets/fonts/Audiowibe/Audiowibe.ttf"

    weapon_preview = Entity(model=model_preview, color=color.red, position=(.2, 0))

    ak47_btn.enabled = True
    shotgun_btn.enabled = True
    bullpup_btn.enabled = True
    machinegun_btn.enabled = True
    exit_btn.enabled = True
    weapon_preview.visible = True

    ak47_btn.on_mouse_enter = preview_ak47
    shotgun_btn.on_mouse_enter = preview_shotgun
    bullpup_btn.on_mouse_enter = preview_bullpup
    machinegun_btn.on_mouse_enter = preview_machinegun

    ak47_btn.on_click = buy_ak47
    shotgun_btn.on_click = buy_shotgun
    bullpup_btn.on_click = buy_bullpup
    machinegun_btn.on_click = buy_machinegun
    exit_btn.on_click = exit_buy


def input(key):
    global gun, money, bullets
    if key == '-' or key == '- hold':
        damage(5)
    if key == '+' or key == '+ hold':
        heal(5)

    # Pause game:
    if key == 'p':
        if not application.paused:
            player.enabled = False
            application.pause()
            pause()

    if key == 'b':
        buy_menu()

    if key == 'r':
        if bullets == 0:
            reload.play()
            bullets += 20 * wave

    # Choose weapon
    if key == '1':
        gun = 'pistol'
        weapon.model = gun
    if key == '2' and ak47 is True:
        gun = 'ak47'
        weapon.model = gun
    if key == '3' and shotgun is True:
        gun = 'shotgun'
        weapon.model = gun
    if key == '4' and bullpup is True:
        gun = 'bullpup'
        weapon.model = gun
    if key == '5' and machinegun is True:
        gun = 'machinegun'
        weapon.model = gun

    # Shoot
    for e2 in nmb_enemy:
        if e2.hovered:
            e2_x = e2.x
            e2_y = e2.y + .5
            e2_z = e2.z
            if key == 'left mouse down' and bullets != 0 and player.enabled is True:
                nmb_enemy.remove(e2)
                destroy(e2)
                zombie_die.play()
                money += 1
                p = ParticleSystem(position=Vec3(e2_x, e2_y, e2_z), color=color.red, rotation_y=random.random() * 360)
                p.fade_out(duration=.2, delay=1 - .2, curve=curve.linear)

    if key == 'left mouse down' and bullets != 0 and player.enabled is True:
        bullets -= 1
        if gun == 'pistol':
            dust = Entity(model=Circle(),
                          parent=camera.ui,
                          scale=0.03,
                          color=color.black,
                          position=(0, -.02))
            dust.animate_scale(0.001,
                               duration=0.3,
                               curve=curve.linear)
            dust.fade_out(duration=0.3)
            fire.play()
        if gun == 'ak47':
            dust = Entity(model=Circle(),
                          parent=camera.ui,
                          scale=0.03,
                          color=color.black,
                          position=(0, -.02))
            dust.animate_scale(0.001,
                               duration=0.1,
                               curve=curve.linear)
            dust.fade_out(duration=0.1)
            fire.play()

        if gun == 'shotgun':
            dust = Entity(model=Circle(),
                          parent=camera.ui,
                          scale=0.03,
                          color=color.black,
                          position=(0, -.02))
            dust.animate_scale(0.001,
                               duration=0.1,
                               curve=curve.linear)
            dust.fade_out(duration=0.4)
            fire.play()

        if gun == 'bullpup':
            dust = Entity(model=Circle(),
                          parent=camera.ui,
                          scale=0.03,
                          color=color.black,
                          position=(0, -.02))
            dust.animate_scale(0.001,
                               duration=0.1,
                               curve=curve.linear)
            dust.fade_out(duration=0.2)
            fire.play()

        if gun == 'machinegun':
            dust = Entity(model=Circle(),
                          parent=camera.ui,
                          scale=0.03,
                          color=color.black,
                          position=(0, -.02))
            dust.animate_scale(0.001,
                               duration=0.05,
                               curve=curve.linear)
            dust.fade_out(duration=0.05)
            fire.play()

    if key == 'shift':
        camera.animate("fov", 120, duration=0.2, curve=curve.in_quad)
        camera.animate("fov", 100, curve=curve.out_quad, delay=0.2)
        player.animate_position(player.position + (camera.forward * 10), duration=0.2, curve=curve.in_out_quad)


def update():
    global money, ak47, bullpup, machinegun, shotgun

    if held_keys['left mouse']:
        weapon.position = (.8, -.55)
    else:
        weapon.position = (.8, -.5)

    if held_keys['right mouse']:
        weapon.rotation = (0, 90, 5)
        weapon.position = lerp(weapon.position, Vec3(-.7, -.5, 0), curve.in_out_cubic(.5))
        camera.fov = lerp(camera.fov, 62, .5)
    else:
        weapon.rotation = (0, 75, 5)
        weapon.position = (.8, -.5)
        camera.fov = lerp(camera.fov, 90, .5)

    if wave == 0:
        waves()
    if wave == 20:
        print_on_screen('YOU WIN', scale=4, position=(0, 0), duration=4)

    if nmb_enemy == [] and wave != 0:
        waves()

    if player.y < -5:
        player.y = 5
        player.x = random.randint(0, 35)
        player.z = random.randint(0, 35)
        damage(10)
    if player.y > 20:
        player.y = 5
        player.x = random.randint(0, 35)
        player.z = random.randint(0, 35)
        damage(50)
    if -3 < player.y < .3:
        player.y = -1
    if HB1.value == 0:
        GameOver()

    e1.lookAt(player)

    for e2 in nmb_enemy:
        e2.look_at_2d(player.position, axis='y')

    print(player.position)

    wave_text.text = f'Waves: {wave}'
    money_text.text = f'Money: {money}'
    bullets_text.text = f'Bullets: {bullets}'


app.run()
