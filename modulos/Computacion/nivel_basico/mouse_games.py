import customtkinter as ctk
import tkinter as tk
import random

class MouseGame(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Entrenamiento de Ratón")
        self.geometry("800x600")
        
        self.score = 0
        self.time_left = 30
        self.game_active = False
        self.target_id = None
        
        self.build_ui()
        
    def build_ui(self):
        # Panel superior
        top_panel = ctk.CTkFrame(self, height=50)
        top_panel.pack(fill="x", padx=10, pady=5)
        
        self.lbl_score = ctk.CTkLabel(top_panel, text="Puntos: 0", font=("Arial", 16, "bold"))
        self.lbl_score.pack(side="left", padx=20)
        
        self.lbl_timer = ctk.CTkLabel(top_panel, text="Tiempo: 30s", font=("Arial", 16, "bold"))
        self.lbl_timer.pack(side="right", padx=20)
        
        self.btn_start = ctk.CTkButton(top_panel, text="Iniciar Juego", command=self.start_game)
        self.btn_start.pack(pady=10)

        # Canvas para el juego
        self.canvas = tk.Canvas(self, bg="#EAF2F8", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Instrucciones iniciales en el canvas
        self.canvas.create_text(
            400, 250, 
            text="Presiona 'Iniciar Juego'\ny haz clic en los círculos rojos.",
            font=("Arial", 20), fill="#555"
        )

    def start_game(self):
        self.score = 0
        self.time_left = 30
        self.game_active = True
        self.btn_start.configure(state="disabled")
        self.canvas.delete("all")
        self.update_ui()
        self.spawn_target()
        self.countdown()

    def update_ui(self):
        self.lbl_score.configure(text=f"Puntos: {self.score}")
        self.lbl_timer.configure(text=f"Tiempo: {self.time_left}s")

    def countdown(self):
        if self.time_left > 0 and self.game_active:
            self.time_left -= 1
            self.update_ui()
            self.after(1000, self.countdown)
        elif self.time_left <= 0:
            self.end_game()

    def spawn_target(self):
        if not self.game_active:
            return
            
        self.canvas.delete("target")
        
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        # Margen de seguridad
        pad = 50
        
        x = random.randint(pad, w - pad)
        y = random.randint(pad, h - pad)
        radius = random.randint(20, 40)
        
        # Dibujar círculo (target)
        self.target_id = self.canvas.create_oval(
            x - radius, y - radius, x + radius, y + radius,
            fill="#FF5252", outline="white", width=2, tags="target"
        )
        
        # Vincular evento click al objeto específico
        self.canvas.tag_bind(self.target_id, "<Button-1>", self.on_target_click)

    def on_target_click(self, event):
        if self.game_active:
            self.score += 1
            self.update_ui()
            self.spawn_target()

    def end_game(self):
        self.game_active = False
        self.canvas.delete("all")
        self.canvas.create_text(
            self.canvas.winfo_width()//2, self.canvas.winfo_height()//2,
            text=f"¡Tiempo Agotado!\nPuntuación Final: {self.score}",
            font=("Arial", 24, "bold"), fill="#2040E0", justify="center"
        )
        self.btn_start.configure(state="normal")