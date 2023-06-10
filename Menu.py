from ursina import *
from ursina.prefabs.dropdown_menu import DropdownMenu, DropdownMenuButton

app = Ursina()


class MenuButton(Button):
    def __init__(self, text='', **kwargs):
        super().__init__(text, scale=(.25, .075), highlight_color=color.azure, font='assets/fonts/Audiowibe/Audiowibe.ttf', **kwargs)
        self.alpha = 0
        self.font = 'assets/fonts/Audiowibe/Audiowibe.ttf'

        for key, value in kwargs.items():
            setattr(self, key, value)


# button_size = (.25, .075)
button_spacing = .075 * 1.25
menu_parent = Entity(parent=camera.ui, y=.15)
main_menu = Entity(parent=menu_parent)
load_menu = Entity(parent=menu_parent)
options_menu = Entity(parent=menu_parent)

state_handler = Animator({
    'main_menu' : main_menu,
    'load_menu' : load_menu,
    'options_menu' : options_menu,
    }
)


# main menu content
main_menu.buttons = [
    MenuButton('start', icon='assets/textures/wood_button1', on_click=Func(setattr, state_handler, 'state', 'load_menu')),
    MenuButton('options', icon='assets/textures/wood_button1', on_click=Func(setattr, state_handler, 'state', 'options_menu')),
    MenuButton('quit', icon='assets/textures/wood_button1', on_click=Sequence(Wait(.01), Func(sys.exit))),
]
for i, e in enumerate(main_menu.buttons):
    e.parent = main_menu
    e.y = (-i-2) * button_spacing


def start_game():
    menu_parent.enabled = False


# load menu content
MenuButton(parent=load_menu, icon='assets/textures/wood_button2', text=f'History', y=-1 * button_spacing, on_click=start_game)
MenuButton(parent=load_menu, icon='assets/textures/wood_button2', text=f'Dead Game', y=-2 * button_spacing, on_click=start_game)
MenuButton(parent=load_menu, icon='assets/textures/wood_button2', text=f'Multiplayer', y=-3 * button_spacing, on_click=start_game)

load_menu.back_button = MenuButton(parent=load_menu, icon='assets/textures/wood_button3', text='back', y=((-i-2) * button_spacing), on_click=Func(setattr, state_handler, 'state', 'main_menu'))


# options menu content
review_text = Text(parent=options_menu, x=.275, y=.25, text='Preview text', origin=(-.5,0))
for t in [e for e in scene.entities if isinstance(e, Text)]:
    t.original_scale = t.scale

text_scale_slider = Slider(0, 2, default=1, step=.1, dynamic=True, text='Text Size:', parent=options_menu, x=-.25)


def set_text_scale():
    for t in [e for e in scene.entities if isinstance(e, Text) and hasattr(e, 'original_scale')]:
        t.scale = t.original_scale * text_scale_slider.value


text_scale_slider.on_value_changed = set_text_scale
volume_slider = Slider(0, 1, default=Audio.volume_multiplier, step=.1, text='Master Volume:', parent=options_menu, x=-.25)


def set_volume_multiplier():
    Audio.volume_multiplier = volume_slider.value


volume_slider.on_value_changed = set_volume_multiplier

def low():
    window.size = (720, 480)


def medium():
    window.size = (1280, 720)


def high():
    window.size = (1920, 1080)


def fullscreen():
    if window.fullscreen is False:
        window.fullscreen = True
    else:
        window.fullscreen = False


def vsync():
    if window.vsync is False:
        window.vsync = True
    else:
        window.vsync = False


reso = DropdownMenu('Resolution', buttons=(
    DropdownMenuButton('720x480', on_click=low),
    DropdownMenuButton('1280x720', on_click=medium),
    DropdownMenuButton('1920x1080', on_click=high)
))

win = DropdownMenu('Window', buttons=(
    DropdownMenuButton('Fullscreen', on_click=fullscreen),
    DropdownMenuButton('VSYNC', on_click=medium)
))

reso.y = -.2
reso.x = -.25
win.x = .10
win.y = -.2
reso.parent = options_menu
win.parent = options_menu

options_back = MenuButton(parent=options_menu, icon='assets/textures/wood_button3', text='Back', x=-.25, origin_y=3, origin_x=-.5, on_click=Func(setattr, state_handler, 'state', 'main_menu'))

for i, e in enumerate((text_scale_slider, volume_slider, options_back)):
    e.y = -i * button_spacing


# animate the buttons in nicely when changing menu
for menu in (main_menu, load_menu, options_menu):
    def animate_in_menu(menu=menu):
        for i, e in enumerate(menu.children):
            e.original_x = e.x
            e.x += .1
            e.animate_x(e.original_x, delay=i*.05, duration=.1, curve=curve.out_quad)

            e.alpha = 0
            e.animate('alpha', 0, delay=i*.05, duration=.1, curve=curve.out_quad)

            if hasattr(e, 'text_entity'):
                e.text_entity.alpha = 0
                e.text_entity.animate('alpha', 1, delay=i*.05, duration=.1)

    menu.on_enable = animate_in_menu


background = Entity(parent=menu_parent, model='quad', texture='shore', scale=(camera.aspect_ratio,1), color=color.white, z=1, world_y=0)


app.run()
