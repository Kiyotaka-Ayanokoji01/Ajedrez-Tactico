import tkinter as tk
import customtkinter as ctk
import random


class JuegoPalabras:
    def __init__(self, parent):
        self.parent = parent
        self.game_window = None


# Configuraciones y Palabras
WORDS = [
    "manzana",
    "casa",
    "perro",
    "gato",
    "libro",
    "mesa",
    "silla",
    "arbol",
    "escuela",
    "familia",
]
ROUND_TIME_SECONDS = 30
game_window = None  # Referencia global interna


def desordenar_palabra(palabra):
    if len(palabra) <= 1:
        return palabra
    lista = list(palabra)
    while True:
        random.shuffle(lista)
        s = "".join(lista)
        if s != palabra:
            return s


def abrir_juego_palabras(parent):
    global game_window

    # Si ya está abierta, la traemos al frente
    if game_window is not None and tk.Toplevel.winfo_exists(game_window):
        game_window.lift()
        return

    game_window = tk.Toplevel(parent)
    game_window.title("Juego de Palabras")
    game_window.geometry("520x400")

    # Estado del juego
    state = {
        "current_word": "",
        "scrambled": "",
        "score": 0,
        "time_left": ROUND_TIME_SECONDS,
        "after_id": None,
        "round_active": False,
    }

    # UI
    header = ctk.CTkLabel(
        game_window, text="Juego de Palabras", font=("Arial", 20, "bold")
    )
    header.pack(pady=10)

    info_frame = ctk.CTkFrame(game_window)
    info_frame.pack(pady=10, fill="x", padx=20)

    score_label = ctk.CTkLabel(info_frame, text=f"Puntuación: 0")
    score_label.pack(side="left", padx=20)

    timer_label = ctk.CTkLabel(info_frame, text=f"Tiempo: {ROUND_TIME_SECONDS}s")
    timer_label.pack(side="right", padx=20)

    word_label = ctk.CTkLabel(
        game_window, text="", font=("Arial", 32, "bold"), text_color="#E88800"
    )
    word_label.pack(pady=20)

    entry = ctk.CTkEntry(game_window, placeholder_text="Escribe aquí...", width=300)
    entry.pack(pady=10)

    feedback = ctk.CTkLabel(game_window, text="")
    feedback.pack(pady=5)

    btn_frame = ctk.CTkFrame(game_window, fg_color="transparent")
    btn_frame.pack(pady=10)

    def actualizar_ui():
        score_label.configure(text=f"Puntuación: {state['score']}")
        timer_label.configure(text=f"Tiempo: {state['time_left']}s")
        word_label.configure(text=state["scrambled"])

    def countdown():
        if not state["round_active"]:
            return
        state["time_left"] -= 1
        actualizar_ui()
        if state["time_left"] <= 0:
            end_round(timeout=True)
        else:
            state["after_id"] = game_window.after(1000, countdown)

    def end_round(timeout=False):
        state["round_active"] = False
        if state["after_id"]:
            game_window.after_cancel(state["after_id"])
        entry.configure(state="disabled")
        if timeout:
            feedback.configure(
                text=f"¡Tiempo agotado! Era: {state['current_word']}", text_color="red"
            )

    def start_new_round():
        state["current_word"] = random.choice(WORDS)
        state["scrambled"] = desordenar_palabra(state["current_word"])
        state["time_left"] = ROUND_TIME_SECONDS
        state["round_active"] = True
        entry.configure(state="normal")
        entry.delete(0, "end")
        entry.focus_set()
        feedback.configure(text="")
        actualizar_ui()
        if state["after_id"]:
            game_window.after_cancel(state["after_id"])
        countdown()

    def check_answer(event=None):
        if not state["round_active"]:
            return
        if entry.get().lower().strip() == state["current_word"].lower():
            state["score"] += 1
            feedback.configure(text="¡Correcto!", text_color="green")
            end_round()
            game_window.after(1000, start_new_round)
        else:
            feedback.configure(text="Intenta de nuevo", text_color="orange")

    submit_btn = ctk.CTkButton(btn_frame, text="Enviar", command=check_answer)
    submit_btn.grid(row=0, column=0, padx=5)

    next_btn = ctk.CTkButton(btn_frame, text="Siguiente", command=start_new_round)
    next_btn.grid(row=0, column=1, padx=5)

    entry.bind("<Return>", check_answer)

    def cleanup():
        if state["after_id"]:
            game_window.after_cancel(state["after_id"])
        game_window.destroy()

    game_window.protocol("WM_DELETE_WINDOW", cleanup)
    start_new_round()
