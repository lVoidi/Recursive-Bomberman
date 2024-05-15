from .gameplay import start_game
import tkinter as tk
import pygame
from tkinter import messagebox
from PIL import Image, ImageTk


def get_completed_levels() -> list:
    with open("api/completed_levels.txt", "r") as text:
        return text.read().split()


def is_level_completed(levels: list, level: str):
    if not levels:
        return False
    if levels[0] == level:
        return True

    return is_level_completed(levels[1:], level)


def get_back(top: tk.Toplevel, root: tk.Tk):
    root.deiconify()
    top.destroy()


def on_closing(top: tk.Toplevel, root: tk.Tk):
    if messagebox.askokcancel("Volver al menú", "¿Volver al menú?"):
        get_back(top, root)


def open_level(event, level_number: int, canvas: tk.Canvas, levels: tk.Toplevel, root: tk.Tk):
    levels.withdraw()
    pygame.mixer.music.stop()
    start_game(level_number, root, levels)


def show_level_window(root: tk.Tk) -> None:
    levels = tk.Toplevel(root)
    levels.config(bg="#000000")
    levels.protocol("WM_DELETE_WINDOW", lambda: on_closing(levels, root))
    completed_levels = get_completed_levels()
    levels.attributes("-fullscreen", True)
    levels.attributes("-topmost", True)
    root.withdraw()
    lock_image = ImageTk.PhotoImage(
        image=Image.open(r"api/assets/images/lock.png").resize((450, 600)))
    root.lock_img = lock_image
    title = tk.Label(
        levels,
        text="Las flipantes aventuras\n del tio bombetas",
        fg="#aaffaa",
        bg="#000000",
        pady=10,
        font=("Golden Age", 100),
    )
    canvas_width, canvas_height = 635, 635

    canvas_1 = tk.Canvas(levels, bg="#000000", width=canvas_width, height=canvas_height)
    canvas_2 = tk.Canvas(levels, bg="#000000", width=canvas_width, height=canvas_height)
    canvas_3 = tk.Canvas(levels, bg="#000000", width=canvas_width, height=canvas_height)

    canvas_1.create_text(
        canvas_width / 2,
        canvas_height * (2 / 3),
        anchor="center",
        text="1",
        fill="#ffffff",
        font=("Press Start 2P", 300)
    )
    canvas_1.bind("<Button-1>", lambda event: open_level(event, 1, canvas_1, levels, root))
    canvas_2.create_text(
        canvas_width / 1.8,
        canvas_height * (2 / 3),
        anchor="center",
        text="2",
        fill="#ffffff",
        font=("Press Start 2P", 300)
    )
    canvas_3.create_text(
        canvas_width / 1.8,
        canvas_height * (2 / 3),
        anchor="center",
        text="3",
        fill="#ffffff",
        font=("Press Start 2P", 300)
    )

    # Esto habilita a los canvas que, si el nivel está habilitado, se inicialice al clickearlo
    if not is_level_completed(completed_levels, "2"):
        canvas_2.create_image(
            canvas_width / 2,
            canvas_height * (1.5 / 3),
            image=lock_image
        )
    else:
        canvas_2.bind("<Button-1>", lambda event: open_level(event, 2, canvas_2, levels, root))

    if not is_level_completed(completed_levels, "3"):
        canvas_3.create_image(
            canvas_width / 2,
            canvas_height * (1.5 / 3),
            image=lock_image
        )

    else:
        canvas_3.bind("<Button-1>", lambda event: open_level(event, 3, canvas_3, levels, root))
    get_back_button = tk.Button(
        levels,
        text="Volver al menu",
        bg="#000000",
        fg="#ffaaaa",
        relief="flat",
        command=lambda: get_back(levels, root),
        font=("Press Start 2P", 40),
    )
    title.grid(row=0, column=0, columnspan=3)
    canvas_1.grid(row=1, column=0)
    canvas_2.grid(row=1, column=1)
    canvas_3.grid(row=1, column=2)
    get_back_button.grid(row=2, column=0, columnspan=3)
