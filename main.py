############################
# Creado por Rodrigo Arce
# https://github.com/lvoidi
############################
import tkinter as tk
import pygame
import api
import json
from PIL import Image, ImageTk

main_window = tk.Tk()
main_window.config(bg="#000000")

pygame.mixer.init()
pygame.mixer.music.load('api/assets/music/menumusic.mp3')
pygame.mixer.music.play(loops=-1)


def close_window(event):
    if event.keysym == 'q' or event.keysym == 'Q':
        main_window.destroy()


def on_skin_select(skin_number):
    content_dict = {}
    with open("api/settings.json") as config:
        content_dict = json.loads(config.read())
    with open("api/settings.json", "w") as config:
        content_dict["skin"] = skin_number
        config.write(json.dumps(content_dict))


def on_name_select(name):
    name = name if name else "Player"
    content_dict = {}
    with open("api/settings.json") as config:
        content_dict = json.loads(config.read())
    with open("api/settings.json", "w") as config:
        content_dict["name"] = name
        config.write(json.dumps(content_dict))


def change_volume(type, scale):
    if type == "music":
        pygame.mixer.music.set_volume(int(scale) / 100)
    with open("api/settings.json") as config:
        content_dict = json.loads(config.read())
    with open("api/settings.json", "w") as config:
        content_dict[type] = int(scale)
        config.write(json.dumps(content_dict))


def return_to_menu(win):
    main_window.deiconify()
    win.destroy()


def credits():
    new_window = tk.Toplevel(main_window)
    new_window.attributes("-fullscreen", True)
    new_window.attributes("-topmost", True)
    new_window.config(
        bg="#000000"
    )
    main_window.withdraw()

    button_exit = tk.Button(
        new_window,
        text="Salir",
        command=lambda: return_to_menu(new_window),
        font=("Press Start 2P", 30),
        bg="#777777"
    )
    info_dev = tk.Label(
        new_window,
        text="Sobre el programador",
        padx=10,
        font=("Press Start 2P", 32),
        bg="#777777"
    )

    info_dev_paragraph = tk.Label(
        new_window,
        text="""
Soy Rodri, tengo 18 años,
cumplo años el 7 de
enero y tengo afición
por la informática y la
investigación.
Mi sueño es trabajar
en la investigación de
máquinas cuánticas. 
Me gusta el software libre
y el Open Source. 
        """,
        justify="center",
        font=("Press Start 2P", 15),
        bg="#444444",
        fg="#ffffff"
    )

    info_uni = tk.Label(
        new_window,
        text="Sobre la universidad",
        padx=10,
        font=("Press Start 2P", 20),
        bg="#666666"
    )
    info_uni_paragraph = tk.Label(
        new_window,
        text="""
Estudiante de
Ingeniería en Computadores 
del Instituto Tecnológico
de Costa Rica.
Este proyecto es parte 
del curso de 
Introducción a
la Programación (CE-1101),
a cargo del profesor 
Jeff Schmidt Peralta
        """,
        font=("Press Start 2P", 15),
        bg="#333333",
        fg="#ffffff"
    )
    info_game = tk.Label(
        new_window,
        text="Sobre el juego",
        padx=10,
        font=("Press Start 2P", 23),
        bg="#555555",
    )
    info_game_paragraph = tk.Label(
        new_window,
        text="""
Bienvenidos a las 
flipantes aventuras
del tío bombetas! El
objetivo es asesinar
a personas con 
las explosiones
de las bombas. Para 
ganar, debes alcanzar
el mínimo de puntaje
(750, 1500 y 2250) para
cada nivel, con las 
limitadas bombas. Entre
más asesines a seres 
humanos, mejor! 

2024 Costa Rica. β
        """,
        font=("Press Start 2P", 15),
        bg="#222222",
        fg="#ffffff"
    )

    image = ImageTk.PhotoImage(Image.open("api/assets/images/info.png").resize((1300, 420)))
    new_window.img = image
    image_widget = tk.Label(
        new_window,
        bg="#000000",
        bd=0,
        image=image
    )
    button_exit.grid(row=9, column=0, columnspan=3, sticky="nsew")
    info_uni.grid(row=1, column=0, sticky="nsew")
    info_uni_paragraph.grid(row=2, column=0, sticky="nsew")
    info_dev.grid(row=1, column=1, sticky="nsew")
    info_dev_paragraph.grid(row=2, column=1, sticky="nsew")
    info_game.grid(row=1, column=2, sticky="nsew")
    info_game_paragraph.grid(row=2, column=2, sticky="nsew")
    image_widget.grid(row=3, column=0, columnspan=3, sticky="nsew")


def open_skins_config(root: tk.Tk):
    new_window = tk.Toplevel(root)
    new_window.attributes("-fullscreen", True)
    new_window.attributes("-topmost", True)
    new_window.config(
        bg="#000000"
    )
    root.withdraw()

    canvas_width, canvas_height = 635, 635

    canvas_1 = tk.Canvas(new_window, bg="#000000", width=canvas_width, height=canvas_height)
    canvas_2 = tk.Canvas(new_window, bg="#000000", width=canvas_width, height=canvas_height)
    canvas_3 = tk.Canvas(new_window, bg="#000000", width=canvas_width, height=canvas_height)

    skin1 = ImageTk.PhotoImage(
        Image.open("api/assets/Sprites/skin_1/front.png").resize((canvas_width // 3, canvas_height // 3)))
    skin2 = ImageTk.PhotoImage(
        Image.open("api/assets/Sprites/skin_2/front.png").resize((canvas_width // 3, canvas_height // 3)))
    skin3 = ImageTk.PhotoImage(
        Image.open("api/assets/Sprites/skin_3/front.png").resize((canvas_width, canvas_height)))
    new_window.skin1 = skin1
    new_window.skin2 = skin2
    new_window.skin3 = skin3

    canvas_1.create_image(
        canvas_width // 2, canvas_height // 2,
        image=skin1,
        anchor="center"
    )
    canvas_2.create_image(
        canvas_width // 2, canvas_height // 2,
        image=skin2,
        anchor="center"
    )
    canvas_3.create_image(
        canvas_width // 2, canvas_height // 2,
        image=skin3,
        anchor="center"
    )

    canvas_1.bind("<Button-1>", lambda e: on_skin_select(1))
    canvas_2.bind("<Button-1>", lambda e: on_skin_select(2))
    canvas_3.bind("<Button-1>", lambda e: on_skin_select(3))

    entry_name = tk.Entry(
        new_window,
        bg="#555555",
        font=("Times New Roman", 30)
    )
    button_load = tk.Button(
        new_window,
        text="Agregar nuevo nombre",
        command=lambda: on_name_select(entry_name.get()),
        font=("Press Start 2P", 30),
        bg="#777777"
    )

    button_exit = tk.Button(
        new_window,
        text="Salir",
        command=lambda: return_to_menu(new_window),
        font=("Press Start 2P", 30),
        bg="#777777"
    )
    sfx = tk.Scale(
        new_window,
        orient="horizontal",
        bg="#000000",
        fg="#ffffff",
        font=("Press Start 2P", 15),
        command=lambda x: change_volume("sfx", x),
        label="Efectos de sonido"
    )
    music = tk.Scale(
        new_window,
        orient="horizontal",
        bg="#000000",
        fg="#ffffff",
        font=("Press Start 2P", 15),
        command=lambda x: change_volume("music", x),
        label="Música"
    )
    canvas_1.grid(row=1, column=0)
    canvas_3.grid(row=1, column=1)
    canvas_2.grid(row=1, column=2)
    entry_name.grid(row=2, column=0, columnspan=3, sticky="nsew")
    button_load.grid(row=3, column=0, columnspan=3, sticky="nsew")
    button_exit.grid(row=4, column=0, columnspan=3, sticky="nsew")
    music.grid(row=5, column=0, columnspan=3, sticky="nsew")
    sfx.grid(row=6, column=0, columnspan=3, sticky="nsew")


def load_scores(window, l, index):
    if len(l) == index or index == 5:
        return

    else:
        label = tk.Label(
            window,
            text=f"{index + 1}: {l[index][0]}: {l[index][1]}",
            font=("Press Start 2P", 65),
            fg="#ffffff",
            bg="#000000"
        )

        label.grid(row=index + 1, column=0, sticky="nsew")
    return load_scores(window, l, index + 1)


def best_scores(root):
    new_window = tk.Toplevel(root)
    new_window.attributes("-fullscreen", True)
    new_window.attributes("-topmost", True)
    new_window.config(
        bg="#000000"
    )

    with open("api/settings.json") as settings:
        scores = sorted(json.loads(settings.read())["scores"], key=lambda sl: sl[1], reverse=True)

    load_scores(new_window, scores, 0)

    title = tk.Label(
        new_window,
        text="Mejores cinco puntajes",
        font=("Press Start 2P", 65),
        fg="#ffffff",
        bg="#000000"
    )
    button_exit = tk.Button(
        new_window,
        text="Salir",
        command=lambda: return_to_menu(new_window),
        font=("Press Start 2P", 30),
        bg="#777777"
    )
    title.grid(row=0, column=0, sticky="nsew")
    button_exit.grid(row=7, column=0, sticky="nsew")
    root.withdraw()


main_window.attributes("-fullscreen", True)
main_window.attributes("-topmost", True)

image = ImageTk.PhotoImage(Image.open("api/assets/images/header.png").resize((1920, 552)))

header_image = tk.Label(
    main_window,
    image=image,
    bg="#000000",
)
header_image.photo = image
header_image.grid(row=0, column=0, sticky="nsew")

btn_start = tk.Button(main_window, text="Iniciar juego",
                      state="active",
                      font=("Press Start 2P", 20),
                      command=lambda: api.show_level_window(main_window), bd=0, highlightthickness=0, fg="white",
                      bg="black")

btn_skins = tk.Button(main_window, text="Configuración", font=("Press Start 2P", 20),
                      command=lambda: open_skins_config(main_window), bd=0, highlightthickness=0, fg="white",
                      bg="black")

btn_records = tk.Button(main_window, text="Records", font=("Press Start 2P", 20),
                        command=lambda: best_scores(main_window), bd=0, highlightthickness=0, fg="white", bg="black")

btn_credits = tk.Button(main_window, text="Creditos", font=("Press Start 2P", 20),
                        command=credits, bd=0, highlightthickness=0, fg="white", bg="black")
btn_salir = tk.Button(main_window, text="Salir", font=("Press Start 2P", 20),
                      command=main_window.destroy, bd=0, highlightthickness=0, fg="white", bg="black")
btn_start.grid(row=1, column=0, sticky="nsew")
btn_skins.grid(row=3, column=0, sticky="nsew")
btn_records.grid(row=4, column=0, sticky="nsew")
btn_credits.grid(row=5, column=0, sticky="nsew")
btn_salir.grid(row=6, column=0, sticky="nsew")

main_window.bind('<Key>', close_window)
main_window.mainloop()
