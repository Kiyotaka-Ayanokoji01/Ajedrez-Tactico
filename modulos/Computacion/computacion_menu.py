import customtkinter as ctk
from .nivel_basico.hardware import HardwareGame
from .nivel_basico.mouse_games import MouseGame


class ComputacionMenu:
    def __init__(self, parent):
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Computación - Mundo Escolar")
        self.window.geometry("800x600")
        self.window.grab_set()  # Hace que la ventana sea modal

        # Título
        self.header = ctk.CTkLabel(
            self.window,
            text="MÓDULO DE COMPUTACIÓN",
            font=("Arial", 28, "bold"),
            text_color="#2040E0"
        )
        self.header.pack(pady=30)

        # Contenedor de Niveles
        self.main_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # --- NIVEL BÁSICO ---
        self.frame_basico = ctk.CTkFrame(self.main_frame, fg_color="#E8F0FE", corner_radius=15)
        self.frame_basico.pack(fill="x", pady=10, ipady=10)

        ctk.CTkLabel(
            self.frame_basico, 
            text="Nivel Básico (1° y 2°)", 
            font=("Arial", 20, "bold"),
            text_color="#1A73E8"
        ).pack(pady=10)

        ctk.CTkLabel(
            self.frame_basico,
            text="Aprende sobre el Hardware y practica con el Ratón.",
            font=("Arial", 14)
        ).pack(pady=5)

        btn_box = ctk.CTkFrame(self.frame_basico, fg_color="transparent")
        btn_box.pack(pady=15)

        ctk.CTkButton(
            btn_box,
            text="🎮 Identificar Hardware",
            command=self.lanzar_hardware,
            fg_color="#1A73E8",
            hover_color="#1557B0",
            width=200
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_box,
            text="🖱️ Juegos de Ratón",
            command=self.lanzar_mouse,
            fg_color="#1A73E8",
            hover_color="#1557B0",
            width=200
        ).pack(side="left", padx=10)

        # --- Placeholder para otros niveles ---
        lbl_proximamente = ctk.CTkLabel(
            self.main_frame,
            text="Niveles Medio y Avanzado: Bloqueados por ahora",
            text_color="gray"
        )
        lbl_proximamente.pack(pady=40)

    def lanzar_hardware(self):
        HardwareGame(self.window)

    def lanzar_mouse(self):
        MouseGame(self.window)

def abrir_menu_computacion(parent):
    ComputacionMenu(parent)
