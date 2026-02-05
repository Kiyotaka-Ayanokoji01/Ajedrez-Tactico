import customtkinter as ctk
import tkinter as tk
from tkinter import colorchooser

class DibujoApp:
    def __init__(self, parent):
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Estudio de Arte - Mundo Escolar")
        self.window.geometry("900x700")
        self.window.grab_set()

        # Configuración inicial
        self.brush_color = "black"
        self.brush_size = 5
        self.old_x = None
        self.old_y = None

        self.build_ui()

    def build_ui(self):
        # --- Barra de Herramientas (Izquierda) ---
        self.toolbar = ctk.CTkFrame(self.window, width=200, corner_radius=0)
        self.toolbar.pack(side="left", fill="y")

        ctk.CTkLabel(self.toolbar, text="HERRAMIENTAS", font=("Arial", 20, "bold")).pack(pady=20)

        # Botón Color
        self.btn_color = ctk.CTkButton(
            self.toolbar, 
            text="🎨 Color", 
            command=self.choose_color,
            fg_color=self.brush_color,
            border_width=2,
            border_color="gray"
        )
        self.btn_color.pack(pady=10, padx=20)

        # Botón Borrador
        ctk.CTkButton(
            self.toolbar, 
            text="🧽 Borrador", 
            command=self.use_eraser,
            fg_color="#E0E0E0",
            text_color="black",
            hover_color="#CCCCCC"
        ).pack(pady=10, padx=20)

        # Botón Limpiar
        ctk.CTkButton(
            self.toolbar, 
            text="🗑️ Limpiar Todo", 
            command=self.clear_canvas,
            fg_color="#FF5252",
            hover_color="#D32F2F"
        ).pack(pady=10, padx=20)

        # Slider Tamaño
        ctk.CTkLabel(self.toolbar, text="Tamaño del Pincel").pack(pady=(20, 5))
        self.slider_size = ctk.CTkSlider(
            self.toolbar, 
            from_=1, 
            to=30, 
            number_of_steps=29,
            command=self.change_size
        )
        self.slider_size.set(self.brush_size)
        self.slider_size.pack(pady=5)

        # Botón Salir
        ctk.CTkButton(
            self.toolbar,
            text="Cerrar",
            command=self.window.destroy,
            fg_color="transparent",
            border_width=1,
            text_color="gray"
        ).pack(side="bottom", pady=20)

        # --- Área de Dibujo ---
        self.canvas_frame = ctk.CTkFrame(self.window, fg_color="white")
        self.canvas_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.canvas = tk.Canvas(self.canvas_frame, bg="white", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Eventos de dibujo
        self.canvas.bind("<B1-Motion>", self.paint)
        self.canvas.bind("<ButtonRelease-1>", self.reset)

    def choose_color(self):
        color = colorchooser.askcolor(color=self.brush_color)[1]
        if color:
            self.brush_color = color
            self.btn_color.configure(fg_color=color)

    def use_eraser(self):
        self.brush_color = "white"
        # Indicador visual de que es borrador (blanco)
        self.btn_color.configure(fg_color="white")

    def clear_canvas(self):
        self.canvas.delete("all")

    def change_size(self, value):
        self.brush_size = int(value)

    def paint(self, event):
        if self.old_x and self.old_y:
            self.canvas.create_line(
                self.old_x, self.old_y, event.x, event.y,
                width=self.brush_size,
                fill=self.brush_color,
                capstyle=tk.ROUND,
                smooth=True,
                splinesteps=36
            )
        self.old_x = event.x
        self.old_y = event.y

    def reset(self, event):
        self.old_x = None
        self.old_y = None

def abrir_dibujo(parent):
    DibujoApp(parent)