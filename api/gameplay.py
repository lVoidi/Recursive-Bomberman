import os
import time
import json
import pygame
import random
import tkinter as tk
from threading import Thread
from PIL import Image, ImageTk

# Variables globales de la ventana
root_tk: tk.Tk = None
level_tk: tk.Toplevel = None
current_level_tk: tk.Toplevel = None
canva_info = None
level_number_tk = 1
tiempo = 0
music = None

# sera una matriz bidimensional del tipo [[x0, y0, x0 + 60, y0 + 60, b],] con el fin de
# guardar las hitboxes. B es 0 o 1, dependiendo si se puede romper o no
collisions = []

# Matriz bidimensional, del tipo [[x, y]] con las coords de cada bloque destruible
breakable = []
enemies = []
paths = []
# stats
score = 0
hearts = 3
bombs_len = 0
has_key = False
image_set = False
immune = False
dead = False

# Serán pares ordenados, los cuales guardarán una coordenada aleatoria de "breakable" posteriormente
trapdoor_coords = ()
key_coords = ()

# Efectos de sonido
pygame.mixer.init()
key_pick_sfx = pygame.mixer.Sound("api/assets/sound_effects/key_pick.mp3")
bomb_sfx = pygame.mixer.Sound("api/assets/sound_effects/bomb.mp3")
deny_sfx = pygame.mixer.Sound("api/assets/sound_effects/deny.mp3")
explosion_sfx = pygame.mixer.Sound("api/assets/sound_effects/explosion.mp3")
lost_hp_sfx = pygame.mixer.Sound("api/assets/sound_effects/lost.mp3")
level_music = lambda l: pygame.mixer.Sound(f"api/assets/music/ingamemusic{l}.mp3")

# Para efectos de control del juego
stopped = False
uploaded = False

def upload_score():
    global uploaded
    uploaded = True
    content_dict = {}
    with open("api/settings.json") as config:
        content_dict = json.loads(config.read())
    with open("api/settings.json", "w") as config:
        content_dict["scores"].append([
            content_dict["name"], score
        ])
        config.write(json.dumps(content_dict))

def exit_game(r: tk.Toplevel, l: tk.Toplevel):
    global stopped
    pygame.mixer.music.stop()
    stopped = True
    music.stop()
    pygame.mixer.music.load("api/assets/music/menumusic.mp3")
    pygame.mixer.music.play(-1)
    r.deiconify()
    set_default_variables()
    l.destroy()


def set_default_variables():
    global collisions, enemies, paths, score, hearts, trapdoor_coords, key_coords, has_key, image_set, immune, dead, \
        stopped, bombs, tiempo, bombs_len, bomb_range, breakable, bomb_counter, player, player_y, player_x, uploaded

    bombs = []
    breakable = []
    bomb_counter = -1
    bomb_range = 120
    tiempo = 0
    player = 0
    uploaded = False
    bombs_len = 0
    key_coords = ()
    has_key = False
    image_set = False
    immune = False
    dead = False
    stopped = False
    collisions = []
    enemies = []
    paths = []
    score = 0
    hearts = 3
    player_x, player_y = 30, 45
    trapdoor_coords = ()


def on_win(canvas: tk.Canvas):
    global stopped, level_tk
    if not uploaded:
        with open("api/completed_levels.txt", "a") as file:
            file.write(f"\n{level_number_tk+1}")
        upload_score()

    else:

        stopped = True
        pygame.mixer.music.stop()
        music.stop()
        canvas.create_rectangle(0, 0, 1920, 1080, fill="#000000")
        canva_info.create_rectangle(0, 0, 1920, 1080, fill="#000000")
        canvas.create_text(
            1920 // 2, 1080 // 2.5,
            text=f"Ganaste la etapa {level_number_tk}!",
            fill="#88ff77",
            font=("Press Start 2P", 30)
        )
        canvas.create_text(
            1920 // 2 + 3, 1080 // 2.5 - 3,
            text=f"Ganaste la etapa {level_number_tk}!",
            fill="#ffffff",
            font=("Press Start 2P", 30)
        )
        canvas.create_text(
            1920 // 2 + 3, 1080 // 1.5,
            text=f"Tiempo: {tiempo}\nPuntaje: {score}",
            fill="#ffffff",
            font=("Press Start 2P", 30)
        )
        canvas.after(3000, reset if level_number_tk != 3 else exit)


def reset():
    global stopped
    set_default_variables()
    current_level_tk.destroy()
    stopped = False
    start_game(level_number_tk + 1, root_tk, level_tk)


def on_death(canvas: tk.Canvas):
    """
    :param canvas: canvas del juego
    :return: None
    """
    global immune, player_x, player_y, hearts, dead
    if hearts <= 1 and not dead:
        dead = True
        pygame.mixer.music.stop()
        music.stop()
        canvas.config(bg="#aaaaaa")
        canvas.create_text(
            canvas.winfo_screenwidth() // 2 + 10, canvas.winfo_screenheight() // 2 + 10,
            text="Has muerto\npresiona q para salir",
            fill="#000000",
            font=("Press Start 2P", 45),
            anchor="center"
        )
        canvas.create_text(
            canvas.winfo_screenwidth() // 2, canvas.winfo_screenheight() // 2,
            text="Has muerto\npresiona q para salir",
            fill="#ff9999",
            font=("Press Start 2P", 45),
            anchor="center"
        )
        pygame.mixer.music.load("api/assets/music/death_music.mp3")
        pygame.mixer.music.play(-1)

    if not immune:
        lost_hp_sfx.play()
        immune = True
        player_x, player_y = 30, 45
        hearts -= 1
        canvas.coords(player, 30, 45)
        time.sleep(2)
        immune = False


def generate_borders(level: tk.Canvas, window: tk.Toplevel, size, height):
    """

    :param level: canvas del nivel
    :param window: ventana del nivel
    :param size: tamaño de cada bloque
    :param height: alto del canvas
    :return: None
    """

    block_image = ImageTk.PhotoImage(
        image=Image.open(r"api/assets/images/blocks_1.png").resize((size, size)))
    window.block = block_image
    recursive_gen_blocks_x(level, block_image, size, 0)
    recursive_gen_blocks_y(level, block_image, size, 0, height)


def load_config() -> dict:
    # Esta función carga los contenidos del
    # archivo de configuración
    with open("api/settings.json") as config:
        content = config.read()
        return json.loads(content)


def recursive_gen_blocks_x(canvas: tk.Canvas, image: ImageTk.PhotoImage, size, start, end: int = 1920, step: int = 1,
                           position_x: int = 0):
    """
    :param canvas: canvas del juego
    :param image: la imagen del bloque irrompible
    :param size: tamaño del bloque
    :param start: inicio
    :param end: fin
    :param step: salto, esto para mayor facilidad a la hora de crear bloques intermedios
    :param position_x: posicion actual en x
    :return: None
    """
    if position_x >= end:
        return
    x = step * position_x
    y = start * step
    img = canvas.create_image(
        x,
        y,
        anchor="nw",
        image=image
    )
    if step != 1:
        collisions.append(
            [x, y, x + 60, y + 60, False, img]
        )
    return recursive_gen_blocks_x(canvas, image, size, start, position_x=position_x + size, end=end, step=step)


def recursive_gen_blocks_y(canvas: tk.Canvas, image: ImageTk.PhotoImage, size, start, end, position_y: int = 60):
    """
    :param canvas: canvas del juego
    :param image: imagen del bloque
    :param size: tamaño del bloque
    :param start: inicio
    :param end: fin
    :param position_y: posición en Y actual
    :return: None
    """
    print(position_y, end)
    if position_y >= end:
        return recursive_gen_blocks_x(canvas, image, size, end, position_x=120)

    # Bloques intermedios
    if position_y % 2 * size == 0:
        recursive_gen_blocks_x(canvas, image, size, position_y, step=2)

    x = start
    y = position_y

    canvas.create_image(
        x,
        y,
        anchor="nw",
        image=image
    )

    return recursive_gen_blocks_y(canvas, image, size, start, end, position_y=position_y + size)


def is_empty_space(x, y) -> bool:
    """
    Como su nombre lo dice, detecta si es un espacio vacío
    :param x: posicion en x
    :param y: posición en y
    :return: bool
    """
    if (x % 120 == 0 and y % 120 == 0) or () or y == 0 or x == 0:
        return False
    else:
        return True


def recursive_add_breakable_blocks(x, y, image, canvas: tk.Canvas, level, lw):
    """
    :param x: Posición en x actual
    :param y: Posición en y actual
    :param image: imagen del bloque destruible
    :param canvas: canvas del nivel
    :param level: ventana del nivel
    :param lw: level width
    :return: None
    """
    global collisions, breakable
    if x >= 1920:
        return
    if x < 180 and y < 180:
        return recursive_add_breakable_blocks(x + 60, y, image, canvas, level, lw)
    if is_empty_space(x, y) and random.randint(0, 7 - level) == 1:
        breakable.append([x, y])

    return recursive_add_breakable_blocks(x + 60, y, image, canvas, level, lw)


def generate_breakable(b, canvas, image):
    """
    :param b: lista de breakable
    :param canvas: canvas del nivel
    :param image: imagen del bloque destruible
    :return: None
    """
    global collisions, trapdoor_coords, key_coords, breakable, bombs_len
    if not b:
        return
    bombs_len += 1
    x, y = b[0]
    if [x, y] == trapdoor_coords:
        image_door = ImageTk.PhotoImage(Image.open("api/assets/images/door.png").resize((60, 60)))
        canvas.img_d = image_door
        img = canvas.create_image(
            x, y,
            image=image_door,
            anchor="nw"
        )
        trapdoor_coords = [x, y, x + 60, y + 60, img]

    elif [x, y] == key_coords:
        image_key = ImageTk.PhotoImage(Image.open("api/assets/images/key.png").resize((60, 60)))
        canvas.img_k = image_key
        img = canvas.create_image(
            x, y,
            image=image_key,
            anchor="nw"
        )
        key_coords = [x, y, x + 60, y + 60, img]
    img = canvas.create_image(
        x, y,
        image=image,
        anchor="nw"
    )
    collisions.append(
        [x, y, x + 60, y + 60, True, img]
    )
    return generate_breakable(b[1:], canvas, image)


def recursive_add_breakable_blocks_y(y, image, canvas, level, i_h, lw):
    """
    :param y: Posición en y
    :param image: imagen del bloque
    :param canvas: canvas del nivel
    :param level: ventana del nivel
    :param i_h: info height
    :param lw: width del level
    :return: None
    """
    global trapdoor_coords, key_coords
    if y >= i_h:
        trapdoor_coords = random.choice(breakable)
        key_coords = random.choice(breakable)
        if key_coords == trapdoor_coords:
            key_coords = random.choice(breakable)
        generate_breakable(breakable, canvas, image)

        return
    recursive_add_breakable_blocks(0, y, image, canvas, level, lw)
    recursive_add_breakable_blocks_y(y + 60, image, canvas, level, i_h, lw)


def main_bucle(c_info: tk.Canvas, c_game: tk.Canvas, i_h, g_h, window: tk.Toplevel, key_widget):
    """
    :param c_info: canva de las stats
    :param c_game: canva del juego
    :param i_h: info height
    :param g_h: game height
    :param window: ventana del nivel
    :param key_widget: cuadro donde va la llave
    :return: bucle infinito
    """
    global image_set, tiempo
    initial_time = time.time()
    text_time = c_info.create_text(
        0, i_h // 3,
        text="Tiempo: 0",
        font=("Press Start 2P", 30),
        anchor="nw",
        fill="#ffffff"
    )
    text_hearts = c_info.create_text(
        1920 // 2, i_h // 3,
        text="Vidas: 3",
        font=("Press Start 2P", 30),
        anchor="nw",
        fill="#ffffff"
    )
    score_text = c_info.create_text(
        1920 // 1.4, i_h // 3,
        text="0",
        font=("Press Start 2P", 30),
        anchor="nw",
        fill="#ffffff"
    )
    c_info.create_text(
        1920 - 360, i_h // 3,
        text=f"{level_number_tk * 750}",
        font=("Press Start 2P", 30),
        anchor="nw",
        fill="#ffffff"
    )
    b = c_info.create_text(
        1920 - 150, i_h // 3,
        text=f"{bombs_len}",
        font=("Press Start 2P", 30),
        anchor="nw",
        fill="#ffffff"
    )
    # Actualiza las stats en tiempo real
    while not stopped:
        if not image_set and has_key:
            img = ImageTk.PhotoImage(Image.open("api/assets/images/key.png").resize((60, 60)))
            window.key_img_widget = img
            c_info.itemconfig(key_widget, image=img)
            image_set = True
        if hearts > 0:
            move_each_enemy(0, c_game)
            tiempo = time.time() - initial_time
            c_info.itemconfig(text_time, text="Tiempo: {0:.0f}".format(tiempo))
            c_info.itemconfig(text_hearts, text=f"Vidas: {hearts}")
            c_info.itemconfig(score_text, text=f"{score}")
            c_info.itemconfig(b, text=f"{bombs_len}")

# Stats default del jugador (es cada número + 60)
player_x, player_y = 30, 45


def move(event, to: str, player, player_hitbox, canvas, image):
    """

    :param event: Evento necesario para los binds
    :param to: Dirección del movimiento
    :param player: ID de la imagen del jugador
    :param player_hitbox: No se utiliza
    :param canvas: Canvas del juego
    :param image: Imagen que se pone, dependiendo de la dirección
    :return: None
    """
    global player_x, player_y, has_key
    x, y = 0, 0

    if to == "left" and not is_collision(player_x + 45, player_y + 60, collisions):
        x = -15
    elif to == "right" and not is_collision(player_x + 65, player_y + 60, collisions):
        x = 15
    elif to == "up" and not is_collision(player_x + 60, player_y + 45, collisions):
        y = -15
    elif to == "down" and not is_collision(player_x + 60, player_y + 65, collisions):
        y = 15

    # En este instante del código, no estarán vacías estas coords
    tx0, ty0, tx1, ty1, timg = trapdoor_coords
    kx0, ky0, kx1, ky1, kimg = key_coords
    cpx, cpy = player_x + x + 60, player_y + y + 60

    if has_key and tx0 <= cpx <= tx1 and ty0 <= cpy <= ty1:
        if dead or score <= level_number_tk * 750:
            deny_sfx.play()
        else:
            on_win(canvas)

    elif not has_key:
        if kx0 + 15 <= cpx <= kx1 - 15 and ky0 + 15 <= cpy <= ky1 - 15:
            key_pick_sfx.play()
            has_key = True
            canvas.delete(kimg)

    player_x, player_y = x + player_x, y + player_y
    canvas.itemconfig(player, image=image)
    canvas.move(player, x, y)


def is_collision(x, y, l, destroy=False, canvas: tk.Canvas = None, hitrange: int = 0):
    """
    :param x: Eje x
    :param y: Eje y
    :param l: Lista en la que checar (Siempre es collisions en el código)
    :param destroy: Esta opción se pone en True para las explosiones, para romper los bloques destruibles
    :param canvas: El canvas en el que se trabaja
    :param hitrange: La hitbox del objeto que se está analizando
    :return: bool
    """
    global collisions
    if not l:
        return False
    x0, y0, x1, y1, can_break, id_img = l[0]
    if (x0 <= x - hitrange <= x1 and y0 <= y + hitrange <= y1) or (
            x0 <= x + hitrange <= x1 and y0 <= y - hitrange <= y1) or x >= 1920 or x <= 60 or y <= 60 or y >= 960:
        if can_break and destroy:
            canvas.delete(id_img)
            del collisions[collisions.index(l[0])]
        return True
    else:
        return is_collision(x, y, l[1:], destroy=destroy, canvas=canvas)


def propagation_ratio(initial_time, final_time):
    # Modelé una función para la animación de la propagación de la bomba,
    # donde x es el tiempo y y es un número entre 0 y 1, el cual se utiliza
    # de manera relativa a las líneas de la explosión, al igual que el width de estas
    x = final_time - initial_time  # ∆t
    return round(-16 * (x - (1 / 4)) ** 2 + 1, 2)


bombs = []
bomb_counter = -1
bomb_range = 120


def plant_bomb(canvas):
    """
    :param canvas: canvas del juego
    :return: None
    """
    global bombs, immune, bomb_counter, bombs_len, hearts
    bombs_len -= 1

    # Cuando se acaba sin bombas
    if bombs_len <= 0:
        hearts = 0
        on_death(canvas)


    bomb_sfx.play()
    bomb_counter += 1
    exp_x = ((player_x + 60) // 60) * 60 + 30
    exp_y = ((player_y + 60) // 60) * 60 + 30
    exp_h = exp_y
    exp_l = exp_x

    img_bomb = ImageTk.PhotoImage(Image.open("api/assets/images/bomb.png").resize((60, 60)))
    setattr(canvas, f"img{bomb_counter}", img_bomb)
    img = canvas.create_image(
        exp_x - 30, exp_y - 30,
        image=img_bomb,
        anchor="nw"
    )

    horizontal_line_positive = canvas.create_line(exp_x, exp_y, exp_x, exp_y, width=0,
                                                  fill="#ffffff")
    horizontal_line_negative = canvas.create_line(exp_x, exp_y, exp_x, exp_y, width=0,
                                                  fill="#ffffff")
    vertical_line_positive = canvas.create_line(exp_x, exp_y, exp_x, exp_y, width=0,
                                                fill="#ffffff")
    vertical_line_negative = canvas.create_line(exp_x, exp_y, exp_x, exp_y, width=0,
                                                fill="#ffffff")
    bomb_idx = bomb_counter
    time.sleep(2)
    explosion_sfx.play()
    bombs.append([
        exp_x, exp_y, exp_l, exp_h, 0, 0, 0.0, 0.0, 0.0, 0.0, True
    ])
    canvas.delete(img)

    # crea un thread para la bomba
    t = Thread(target=draw_bomb, args=(
        time.time(), horizontal_line_positive, vertical_line_positive, horizontal_line_negative, vertical_line_negative,
        canvas, 10, bomb_idx,))
    t.start()


def bomb_thread(e, canvas):
    t = Thread(target=plant_bomb, args=(canvas,))
    t.start()


player = 0


def draw_bomb(ti, horizontal_p_id, vertical_p_id, horizontal_n_id, vertical_n_id, canvas: tk.Canvas, width, bomb_index):
    """
    :param ti: Tiempo inicial
    :param horizontal_p_id: Id de la linea horizontal positiva
    :param vertical_p_id: Id de la linea vertical positiva
    :param horizontal_n_id: Id de la linea horizontal negativa
    :param vertical_n_id: Id de la linea vertical negativa
    :param canvas: Canvas del juego
    :param width: Largo de las lineas
    :param bomb_index: ID de la bomba en la lista bombs
    :return: None
    bombs se ve algo así:
    bombs = [
        [exp_x, exp_y, exp_l, exp_h, negative_l, negative_h,
        locked_ratio_x_p, locked_ratio_y_p, locked_ratio_x_n,
        locked_ratio_y_n]
    ]
    """
    global bombs, hearts, player_x, player_y, immune, bomb_counter
    time.sleep(0.05)
    t = time.time() - ti
    exp_x, exp_y, exp_l, exp_h, negative_l, negative_h, locked_ratio_x_p, locked_ratio_y_p, locked_ratio_x_n, locked_ratio_y_n, exploding = \
        bombs[bomb_index]
    if 0 <= t <= 1 / 2:
        ratio = propagation_ratio(ti, time.time())
        exp_l = bombs[bomb_index][2] = exp_x + bomb_range * (ratio if not locked_ratio_x_p else locked_ratio_x_p)
        # El objetivo de esta secuencia de if's es lockear el ratio a un valor determinado, para que, cuando colisione,
        # la bomba no se siga propagando
        if is_collision(exp_l, exp_y, collisions, destroy=True, canvas=canvas, hitrange=0):
            bombs[bomb_index][6] = ratio / 2

        exp_h = bombs[bomb_index][3] = exp_y - bomb_range * (ratio if not locked_ratio_y_p else locked_ratio_y_p)
        if is_collision(exp_x, exp_h, collisions, destroy=True, canvas=canvas, hitrange=0):
            bombs[bomb_index][7] = ratio / 2

        negative_l = bombs[bomb_index][4] = exp_x - bomb_range * (ratio if not locked_ratio_x_n else locked_ratio_x_n)
        if is_collision(negative_l, exp_y, collisions, destroy=True, canvas=canvas, hitrange=0):
            bombs[bomb_index][8] = ratio / 2

        negative_h = bombs[bomb_index][5] = exp_y + bomb_range * (ratio if not locked_ratio_y_n else locked_ratio_y_n)
        if is_collision(exp_x, negative_h, collisions, destroy=True, canvas=canvas, hitrange=0):
            bombs[bomb_index][9] = ratio / 2

        if negative_l <= player_x + 60 <= exp_l and exp_h <= player_y + 60 <= negative_h and not immune:
            t = Thread(target=on_death, args=(canvas,))
            t.start()
        canvas.coords(horizontal_p_id, exp_x, exp_y, exp_l, exp_y)
        canvas.coords(vertical_p_id, exp_x, exp_y, exp_x, exp_h)
        canvas.coords(horizontal_n_id, exp_x, exp_y, negative_l, exp_y)
        canvas.coords(vertical_n_id, exp_x, exp_y, exp_x, negative_h)
        canvas.itemconfig(horizontal_n_id, width=width * ratio)
        canvas.itemconfig(horizontal_p_id, width=width * ratio)
        canvas.itemconfig(vertical_p_id, width=width * ratio)
        canvas.itemconfig(vertical_n_id, width=width * ratio)
        draw_bomb(ti, horizontal_p_id, vertical_p_id, horizontal_n_id, vertical_n_id, canvas, width, bomb_index)
    else:
        # Resetea la bomba cuando pasa medio segundo
        bombs[bomb_index][10] = False
        canvas.delete(horizontal_p_id)
        canvas.delete(vertical_p_id)
        canvas.delete(horizontal_n_id)
        canvas.delete(vertical_n_id)
        return


def get_min_path(l, m, m_index, index=0):
    """
    :param l: lista de paths
    :param m: minimo
    :param m_index: index del mínimo
    :param index: index actual de la lista de paths
    :return:
    """
    global paths
    if index == len(l):
        return m_index
    x, y, xf, yf = l[index]
    if yf - y == 0 and xf - x <= m:
        return get_min_path(l, xf - x, index, index + 1)
    elif xf - x == 0 and yf - y <= m:
        return get_min_path(l, yf - y, index, index + 1)
    return get_min_path(l, m, m_index, index + 1)


def delete_min(limit):
    """
    elimina el path mínimo para obtener los últimos 5 + nivel, con nivel = 1, 2 o 3
    :param limit:
    :return:
    """
    global paths
    if len(paths) == limit:
        return

    min_index = get_min_path(paths, 1920, 0, 0)
    del paths[min_index]
    return delete_min(limit)


def get_paths_x(c: tk.Canvas, x: int = 120, y: int = 150, xf: int = 180):
    """
    obtiene los paths de los enemigos en el eje x
    :param c: el canvas del nivel
    :param x: eje x
    :param y: eje y
    :param xf: x final
    :return: None
    """
    global paths

    if xf == 1920:
        return

    if is_collision(x, y, l=collisions):
        return get_paths_x(c, x + 60, y, xf + 60)

    if is_collision(xf, y, l=collisions):
        if xf - x >= 180:
            paths.append([x - 60, y, xf, y])
        return get_paths_x(c, xf, y, xf + 60)
    else:
        return get_paths_x(c, x, y, xf + 60)


def get_paths_y(c: tk.Canvas, x: int = 150, y: int = 120, yf: int = 180, gh=1080):
    """
    obtiene los paths de los enemigos en el eje y
    :param c: el canvas del juego
    :param x: eje x
    :param y: eje y
    :param yf: y final
    :param gh: altura del canvas del juego
    :return: None
    """
    global paths
    if yf == gh:
        return
    if is_collision(x, y, l=collisions):
        return get_paths_y(c, x, y + 60, yf + 60)

    if is_collision(x, yf, l=collisions):
        if yf - y >= 180:
            paths.append([x, y - 60, x, yf])
        return get_paths_y(c, x, yf, yf + 60)
    else:
        return get_paths_y(c, x, y, yf + 60)


def add_enemies(p, counter, canvas: tk.Canvas):
    """
    :param p: lista de paths
    :param counter: contador de enemigos
    :param canvas: canvas del nivel
    :return: None
    """
    global enemies
    if not p:
        return
    x0, y0, x1, y1 = p[0]
    enemy = random.choice(["guerrillero", "ww", "cia"])
    speed = 0
    if enemy == "guerrillero":
        speed = 5
    elif enemy == "ww":
        speed = 7
    elif enemy == "cia":
        speed = 9

    img = ImageTk.PhotoImage(Image.open(f"api/assets/enemies/{enemy}.png").resize((90, 90)))
    setattr(canvas, f"img_en_{counter}", img)
    enemy_id = canvas.create_image(
        x1, y1,
        image=img,
        anchor="center"
    )
    enemies.append([[x1, y1], p[0], speed, enemy_id, -1, True])
    counter += 1
    add_enemies(p[1:], counter, canvas)


def in_explosion(x, y, l):
    """
    Chequea si, en las coords x, y, está explotando
    :param x: eje x
    :param y: eje y
    :param l: bombs
    :return: bool
    """
    if not l:
        return False
    exp_x, exp_y, exp_l, exp_h, negative_l, negative_h, _, __, ___, ____, exploding = l[0]
    if exploding and negative_l and ((negative_l <= x <= exp_l and exp_y - 15 <= y <= exp_y + 15) or (
            exp_x - 15 <= x <= exp_x + 15 and exp_h <= y <= negative_h
    )):
        return True
    return in_explosion(x, y, l[1:])


def move_enemy(enemy_index, canvas):
    """
    mueve a un enemigo específico en enemy_index
    :param enemy_index: índice en "enemies"
    :param canvas: canvas del juego
    :return: None
    """
    global enemies, score
    time.sleep(0.005)
    enemy_coordinates, limits, speed, enemy_id, direction, alive = enemies[enemy_index]
    new_pos_x = direction * speed
    new_pos_y = direction * speed
    x, y = enemy_coordinates
    if alive and in_explosion(x, y, bombs):
        enemies[enemy_index] = [[x, y], limits, speed, enemy_id, 0, False]
        canvas.delete(enemy_id)
        score += enemy_id + speed ** 2
        return
    if alive:
        x0, y0, x1, y1 = limits

        if direction and x <= player_x + 60 <= x + 60 and y <= player_y + 60 <= y + 60:
            t = Thread(target=on_death, args=(canvas,))
            t.start()

        if y1 - y0 == 0:
            if x + new_pos_x < x0 or x + new_pos_x > x1:
                direction = -direction
                new_pos_x = direction * speed
            new_pos_y = 0
        if x1 - x0 == 0:
            if y + new_pos_y < y0 or y + new_pos_y > y1:
                direction = -direction
                new_pos_y = direction * speed
            new_pos_x = 0

        enemies[enemy_index] = [[x + new_pos_x, y + new_pos_y], limits, speed, enemy_id, direction, alive]
        canvas.move(enemy_id, new_pos_x, new_pos_y)


def for_replacement(f, i=0, j=1920, k=60):
    """
    Nada más que decir, se nos prohibió usar for ._.
    :param f: función f(x)
    :param i: inicial
    :param j: final
    :param k: step / salto
    :return: None
    """
    f(i + 30)
    if i >= j:
        return
    return for_replacement(f, i + k, j, k)


def move_each_enemy(i, canvas):
    """
    Mueve cada enemigo
    :param i: indice del enemigo
    :param canvas: canvas del enemigo
    :return: None
    """
    if i == len(enemies):
        return
    move_enemy(i, canvas)
    return move_each_enemy(i + 1, canvas)


def start_game(level_number: int, root: tk.Tk, levels):
    """
    Esta funcion se llama de un archivo exterior, por lo tanto hay que pasarle de parametros el nivel, la root y
    el toplevel de la selección de niveles
    :param level_number: número del nivel
    :param root: tk raíz del juego
    :param levels: toplevel de la selección de niveles
    :return: None
    """
    global player, canva_info, level_tk, level_number_tk, current_level_tk, root_tk, music
    pygame.mixer.music.stop()

    # Reescribe las variables globales
    level_number_tk = level_number
    level_tk = levels
    root_tk = root

    # Carga la música, con el volumen respectivo
    music = level_music(level_number)
    with open("api/settings.json") as f:
        content = json.loads(f.read())
        volume_sfx = content["sfx"] / 100
        volume_music = content["music"] / 100
        key_pick_sfx.set_volume(volume_sfx)
        bomb_sfx.set_volume(volume_sfx)
        deny_sfx.set_volume(volume_sfx)
        explosion_sfx.set_volume(volume_sfx)
        pygame.mixer.music.set_volume(volume_music)
        music.set_volume(volume_music)

    # pone la música en loop
    music.play(-1)

    # Cada cuadrante es de 60 pixeles
    item_size = 60

    level_window = tk.Toplevel(root)
    level_window.attributes("-fullscreen", True)
    level_window.attributes("-topmost", True)
    info_height = 120
    current_level_tk = level_window
    config = load_config()

    game_height = 1080 - info_height
    canva_info = tk.Canvas(
        level_window,
        bg="#888888",
        bd=0,
        highlightthickness=0,
        width=1920,
        height=info_height
    )
    canva_level = tk.Canvas(
        level_window,
        bg="#559955",
        bd=0,
        highlightthickness=0,
        width=1920,
        height=game_height
    )
    generate_borders(canva_level, level_window, item_size, game_height)
    breakable_block = ImageTk.PhotoImage(
        Image.open("api/assets/images/bloques_rompibles.png").resize((item_size, item_size)))
    level_window.breakable = breakable_block
    recursive_add_breakable_blocks_y(0, breakable_block, canva_level, level_number, game_height,
                                     level_window)

    # Carga los assets de la skin
    path = f"api/assets/Sprites/skin_{config["skin"]}"
    player_image = ImageTk.PhotoImage(
        Image.open(f"{path}/front.png").resize(
            (2 * item_size, 2 * item_size)
        )
    )
    player_back = ImageTk.PhotoImage(Image.open(f"{path}/back.png").resize(
        (2 * item_size, 2 * item_size)
    ))
    player_left = ImageTk.PhotoImage(Image.open(f"{path}/left.png").resize(
        (2 * item_size, 2 * item_size)
    ))
    player_right = ImageTk.PhotoImage(Image.open(f"{path}/right.png").resize(
        (2 * item_size, 2 * item_size)
    ))
    level_window.back = player_back
    level_window.left = player_left
    level_window.right = player_right
    level_window.player_image = player_image
    player = canva_level.create_image(
        item_size // 2, item_size,
        image=player_image,
        anchor="w",
    )
    player_hitbox = (
        ((3 / 2) * item_size, (3 / 2) * item_size),
        ((5 / 2) * item_size, (5 / 2) * item_size)
    )
    canva_info.create_text(
        1920 // 3.5, info_height // 3,
        text=config["name"],
        font=("Press Start 2P", 30),
        anchor="nw",
        fill="#dddddd"
    )
    key_space = canva_info.create_image(
        1920 - 60, info_height // 2,
        image=None,
        anchor="center"
    )
    level_window.bind("<Left>", lambda e: move(e, "left", player, player_hitbox, canva_level, player_left))
    level_window.bind("<Right>", lambda e: move(e, "right", player, player_hitbox, canva_level, player_right))
    level_window.bind("<Up>", lambda e: move(e, "up", player, player_hitbox, canva_level, player_back))
    level_window.bind("<Down>", lambda e: move(e, "down", player, player_hitbox, canva_level, player_image))
    level_window.bind("<space>", lambda e: bomb_thread(e, canva_level))
    level_window.bind("q", lambda e: exit_game(levels, level_window))

    # Agarra los paths más largos
    for_replacement(
        lambda x: get_paths_x(canva_level, y=x), j=game_height
    )

    for_replacement(
        lambda x: get_paths_y(canva_level, y=x, gh=game_height)
    )

    delete_min(5 + level_number)
    add_enemies(paths, 0, canva_level)
    main_thread = Thread(
        target=main_bucle,
        args=(canva_info, canva_level,

              info_height, game_height, level_window, key_space)
    )
    main_thread.start()
    canva_info.grid(row=0, column=0, sticky="nsew")
    canva_level.grid(row=1, column=0, sticky="nsew")
