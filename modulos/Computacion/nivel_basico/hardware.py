import customtkinter as ctk
import random

class HardwareGame(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Identifica el Hardware")
        self.geometry("700x500")
        
        self.score = 0
        self.total_questions = 5
        self.current_question = 0
        
        # Definición de componentes (Nombre, Color Simulado, Icono Texto)
        self.components = [
            {"id": "monitor", "name": "Monitor", "color": "#4285F4", "icon": "🖥️"},
            {"id": "cpu", "name": "CPU (Torre)", "color": "#34A853", "icon": "🖳"},
            {"id": "teclado", "name": "Teclado", "color": "#FBBC05", "icon": "⌨️"},
            {"id": "raton", "name": "Ratón", "color": "#EA4335", "icon": "🖱️"}
        ]
        
        self.target = None
        
        self.build_ui()
        self.next_round()

    def build_ui(self):
        # Header
        self.lbl_instruction = ctk.CTkLabel(
            self, 
            text="¡Bienvenido!", 
            font=("Arial", 24, "bold")
        )
        self.lbl_instruction.pack(pady=20)
        
        self.lbl_score = ctk.CTkLabel(self, text=f"Puntuación: {self.score}")
        self.lbl_score.pack()

        # Área de juego
        self.game_area = ctk.CTkFrame(self, fg_color="transparent")
        self.game_area.pack(expand=True, fill="both", padx=50, pady=20)
        
        # Botones de opciones (simulando las partes físicas)
        self.option_buttons = []
        
        # Grid 2x2
        for i in range(2):
            self.game_area.grid_columnconfigure(i, weight=1)
            self.game_area.grid_rowconfigure(i, weight=1)

    def create_options(self):
        # Limpiar botones anteriores
        for btn in self.option_buttons:
            btn.destroy()
        self.option_buttons = []

        # Mezclar posiciones
        shuffled_comps = self.components.copy()
        random.shuffle(shuffled_comps)

        for idx, comp in enumerate(shuffled_comps):
            row = idx // 2
            col = idx % 2
            
            # Creamos un botón grande que parece una tarjeta
            btn = ctk.CTkButton(
                self.game_area,
                text=f"{comp['icon']}\n\n{comp['name']}",
                font=("Arial", 18, "bold"),
                fg_color=comp["color"],
                hover_color="gray",
                corner_radius=15,
                width=150,
                height=120,
                command=lambda c=comp: self.check_answer(c)
            )
            btn.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            self.option_buttons.append(btn)

    def next_round(self):
        if self.current_question >= self.total_questions:
            self.finish_game()
            return

        self.current_question += 1
        self.target = random.choice(self.components)
        
        self.lbl_instruction.configure(
            text=f"¿Dónde está el {self.target['name'].upper()}?",
            text_color="black"
        )
        self.create_options()

    def check_answer(self, selected_comp):
        if selected_comp["id"] == self.target["id"]:
            self.score += 1
            self.lbl_score.configure(text=f"Puntuación: {self.score}")
            self.lbl_instruction.configure(text="¡CORRECTO! 🎉", text_color="green")
            self.after(1000, self.next_round)
        else:
            self.lbl_instruction.configure(text="¡Ups! Intenta de nuevo.", text_color="red")

    def finish_game(self):
        for btn in self.option_buttons:
            btn.destroy()
        
        self.lbl_instruction.configure(
            text=f"¡Juego Terminado!\nPuntuación Final: {self.score}/{self.total_questions}",
            text_color="#2040E0"
        )
        
        ctk.CTkButton(
            self.game_area, text="Cerrar", command=self.destroy
        ).pack(pady=50)