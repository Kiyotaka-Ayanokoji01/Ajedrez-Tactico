import tkinter as tk
import threading
import os
import customtkinter as ctk
from PIL import Image, ImageTk, ImageSequence
from tkextrafont import Font
from modulos.Ajedrez.clases.juego import Juego

# --- IMPORTACIONES DE TUS MÓDULOS ---
# Ajustado para Ajedrez
try:
    from modulos.Ajedrez.clases.juego import Juego
except ImportError:
    print("Error: No se encontró el módulo de Ajedrez.")

# Ajustado juego de palabras
try:
    from modulos.juego_de_palabras.juego_palabras import abrir_juego_palabras
except ImportError:
    print("Nota: No se encontró el archivo modulos/juego_de_palabras.py")

# Ajustado para Computación
try:
    from modulos.Computacion.computacion_menu import abrir_menu_computacion
except ImportError:
    print("Nota: No se encontró el módulo de Computación.")

# Ajustado para Dibujo
try:
    from modulos.Dibujo.dibujo_app import abrir_dibujo
except ImportError:
    print("Nota: No se encontró el módulo de Dibujo.")

# ---------------- CONFIGURACIÓN INICIAL ---------------- #
ctk.set_appearance_mode("light")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# ---------------- COLORES ---------------- #
COLORS = {
    "bg": "#FFFFFF",
    "sidebar": "#4DA3FF",
    "sidebar_hover": "#3C5179",
    "text_dark": "#2B2B2B",
    "white": "#FFFFFF",
    "card1": "#00B1B1",
    "card2": "#00925A",
    "card3": "#E88800",
    "card4": "#2040E0",
    "card5": "#7E2BB3",
    "card6": "#B12300",
    "progress_fill": "#4DA3FF",
    "progress_bg": "#E0E0E0",
}

root = ctk.CTk()
root.title("Mundo Escolar")


def maximizar_ventana():
    try:
        root.state("zoomed")
    except:
        root.attributes("-zoomed", True)


root.after(0, maximizar_ventana)
root.configure(fg_color=COLORS["bg"])

#Progreso inicial del usuario en cada materia (puedes ajustar estos valores para probar la vista de progreso y logros)
ESTADO_USUARIO = {
    "materias": {
        "Lectura y Escritura": 0.0,
        "Ajedrez": 0.0,
        "Juego de Palabras": 0.0,
        "Computación": 0.0,
        "Deportes": 0.0,
        "Dibujo": 0.0,
    }
}

# ---------------- FUENTES ---------------- #
try:
    Font(file=os.path.join(BASE_DIR, "Super Meatball.ttf"), family="Super Meatball")
    FONT_NAME = "Super Meatball"
except:
    FONT_NAME = "Arial Rounded MT Bold"

FONTS = {
    "titulo": (FONT_NAME, 48, "bold"),
    "sidebar": (FONT_NAME, 22),
    "botones": (FONT_NAME, 18),
    "tarjetas": (FONT_NAME, 16),
}


# ---------------- LANZADORES DE JUEGOS ---------------- #
def lanzar_ajedrez_hilo():
    def tarea():
        try:
            juego_instancia = Juego(minutos=10)
            juego_instancia.iniciar_partida()
        except Exception as e:
            print(f"Error al iniciar el ajedrez: {e}")

    hilo = threading.Thread(target=tarea, daemon=True)
    hilo.start()


def lanzar_juego_palabras():
    try:
        abrir_juego_palabras(root)
    except Exception as e:
        print(f"Error al iniciar juego de palabras: {e}")


def lanzar_computacion():
    try:
        abrir_menu_computacion(root)
    except Exception as e:
        print(f"Error al iniciar computación: {e}")

def lanzar_dibujo():
    try:
        abrir_dibujo(root)
    except Exception as e:
        print(f"Error al iniciar dibujo: {e}")

# ---------------- UTILIDADES ---------------- #
def limpiar_panel():
    for widget in principal.winfo_children():
        widget.destroy()
    try:
        principal._parent_canvas.yview_moveto(0)
    except:
        pass
    root.update_idletasks()


# ---------------- VISTAS (TEMAS, PROGRESO, LOGROS) ---------------- #
def cambiar_tema(color_principal, color_hover):
    COLORS["sidebar"] = color_principal
    COLORS["sidebar_hover"] = color_hover
    sidebar.configure(fg_color=color_principal)
    for widget in sidebar.winfo_children():
        if isinstance(widget, ctk.CTkButton):
            widget.configure(hover_color=color_hover)
    vista_temas()


def vista_temas():
    limpiar_panel()
    ctk.CTkLabel(
        principal,
        text="PERSONALIZA TU MUNDO",
        text_color=COLORS["text_dark"],
        font=FONTS["titulo"],
    ).pack(pady=40)
    contenedor_colores = ctk.CTkFrame(principal, fg_color="transparent")
    contenedor_colores.pack(expand=True)

# Paleta de colores para los temas 
    paletas = [
        ("Azul Clásico", "#4DA3FF", "#3C5179"),
        ("Verde Lima", "#A2D149", "#7BA330"),
        ("Rosa Mágico", "#FF74B1", "#D63484"),
        ("Naranja Sol", "#FF9F43", "#E67E22"),
        ("Morado Galaxia", "#A55EE1", "#8854D0"),
        ("Rojo Aventura", "#EB4D4B", "#B33939"),
    ]

    fila, col = 0, 0
    for nombre, principal_c, hover_c in paletas:
        item_frame = ctk.CTkFrame(contenedor_colores, fg_color="transparent")
        item_frame.grid(row=fila, column=col, padx=30, pady=20)
        btn = ctk.CTkButton(
            item_frame,
            text="",
            width=80,
            height=80,
            corner_radius=40,
            fg_color=principal_c,
            hover_color=hover_c,
            border_width=4,
            border_color="white" if COLORS["sidebar"] != principal_c else "#333",
            command=lambda p=principal_c, h=hover_c: cambiar_tema(p, h),
        )
        btn.pack()
        ctk.CTkLabel(
            item_frame, text=nombre, font=(FONT_NAME, 14, "bold"), text_color="#333"
        ).pack(pady=5)
        col += 1
        if col > 2:
            col = 0
            fila += 1

# Sistema de propreso 
def vista_progreso():
    limpiar_panel()
    ctk.CTkLabel(
        principal,
        text="MI PROGRESO",
        text_color=COLORS["text_dark"],
        font=FONTS["titulo"],
    ).pack(pady=40)
    contenedor = ctk.CTkFrame(principal, fg_color="transparent")
    contenedor.pack(fill="both", expand=True, padx=80)

    def animar_barra(barra, label, objetivo, actual=0):
        if actual <= objetivo:
            barra.set(actual)
            label.configure(text=f"{int(actual * 100)}%")
            root.after(10, lambda: animar_barra(barra, label, objetivo, actual + 0.01))

    for nombre, valor in ESTADO_USUARIO["materias"].items():
        f = ctk.CTkFrame(contenedor, fg_color="white", corner_radius=20, height=70)
        f.pack(fill="x", pady=10)
        f.pack_propagate(False)
        ctk.CTkLabel(f, text=nombre, font=FONTS["botones"], text_color="#333").pack(
            side="left", padx=25
        )
        lbl_pct = ctk.CTkLabel(
            f, text="0%", font=(FONT_NAME, 16, "bold"), text_color=COLORS["sidebar"]
        )
        lbl_pct.pack(side="right", padx=25)
        pb = ctk.CTkProgressBar(
            f, progress_color=COLORS["sidebar"], fg_color="#E0E0E0", height=12
        )
        pb.set(0)
        pb.pack(side="left", fill="x", expand=True, padx=20)
        animar_barra(pb, lbl_pct, valor)


def vista_logros():
    limpiar_panel()
    principal.grid_columnconfigure((0, 1, 2), weight=1)
    ctk.CTkLabel(
        principal,
        text="MIS LOGROS",
        text_color=COLORS["text_dark"],
        font=FONTS["titulo"],
    ).grid(row=0, column=0, columnspan=3, pady=40)

    logros_config = [
        (
            "Explorador Digital",
            "Completaste 25% de Computación.",
            "Computación",
            0.25,
            "#CD7F32",
        ),
        (
            "Principiante Lector",
            "Completaste Lectura al 25%.",
            "Lectura y Escritura",
            0.25,
            "#CD7F32",
        ),
        (
            "Novato en Ajedrez",
            "Completaste Ajedrez al 25%.",
            "Ajedrez",
            0.25,
            "#CD7F32",
        ),
        (
            "Aprendiz de Palabras",
            "Completaste Juego de Palabras al 25%.",
            "Juego de Palabras",
            0.25,
            "#CD7F32",
        ),
        (
            "Novato Deportivo",
            "Completaste 25% de Deportes.",
            "Deportes",
            0.25,
            "#CD7F32",
        ),
        ("Aprendiz de Dibujo", "Completaste 25% de Dibujo.", "Dibujo", 0.25, "#CD7F32"),
        (
            "Programador Novato",
            "Completaste 50% de Computación.",
            "Computación",
            0.50,
            "#C0C0C0",
        ),
        (
            "Aprendiz del Lector",
            "Completaste Lectura al 50%.",
            "Lectura y Escritura",
            0.50,
            "#C0C0C0",
        ),
        ("Estratega", "Completaste Ajedrez al 50%.", "Ajedrez", 0.50, "#C0C0C0"),
        (
            "Desafiante de Palabras",
            "Completaste Juego de Palabras al 50%.",
            "Juego de Palabras",
            0.50,
            "#C0C0C0",
        ),
        (
            "Deportista en Progreso",
            "Completaste 50% de Deportes.",
            "Deportes",
            0.50,
            "#C0C0C0",
        ),
        (
            "Dibujante en Progreso",
            "Completaste 50% de Dibujo.",
            "Dibujo",
            0.50,
            "#C0C0C0",
        ),
        ("Genio Tech", "Completaste Computación.", "Computación", 1.0, "#FFD700"),
        (
            "Maestro Lector",
            "Llegaste al 100% en Lectura.",
            "Lectura y Escritura",
            1.0,
            "#FFD700",
        ),
        ("Gran Maestro", "Dominaste el Ajedrez al 100%.", "Ajedrez", 1.0, "#FFD700"),
        (
            "Palabrólogo",
            "Alcanzaste el 100% en Juego de Palabras.",
            "Juego de Palabras",
            1.0,
            "#FFD700",
        ),
        (
            "Atleta Estrella",
            "Finalizaste Deportes al máximo.",
            "Deportes",
            1.0,
            "#FFD700",
        ),
        ("Artista Supremo", "Completaste Dibujo.", "Dibujo", 1.0, "#FFD700"),
        ("Maestro de Materias", "Completaste 3 materias.", "General_3", 1.0, "#FF3D00"),
        (
            "Campeón de Conocimiento",
            "Completaste 5 materias.",
            "General_5",
            1.0,
            "#AA00FF",
        ),
        (
            "Explorador del Saber",
            "Completaste todas las materias.",
            "General_Todas",
            1.0,
            "#00BFA5",
        ),
    ]

    fila, col = 1, 0
    materias_completadas = sum(
        1 for v in ESTADO_USUARIO["materias"].values() if v >= 0.99
    )

    for nombre, desc, materia_link, req, color_base in logros_config:
        desbloqueado = False
        if "General" in materia_link:
            if "3" in materia_link:
                desbloqueado = materias_completadas >= 3
            elif "5" in materia_link:
                desbloqueado = materias_completadas >= 5
            else:
                desbloqueado = materias_completadas >= len(ESTADO_USUARIO["materias"])
        else:
            desbloqueado = ESTADO_USUARIO["materias"].get(materia_link, 0.0) >= req

        color_final = color_base if desbloqueado else "#E0E0E0"
        card = ctk.CTkFrame(
            principal,
            fg_color="white",
            corner_radius=20,
            border_width=2,
            border_color="#F0F0F0",
        )
        card.grid(row=fila, column=col, padx=20, pady=15, sticky="nsew")

        insignia = ctk.CTkFrame(
            card, fg_color=color_final, width=50, height=50, corner_radius=25
        )
        insignia.pack(pady=(20, 10))
        ctk.CTkLabel(
            insignia,
            text="🏆" if desbloqueado else "🔒",
            text_color="white",
            font=("Arial", 20),
        ).place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(
            card,
            text=nombre,
            font=(FONT_NAME, 16, "bold"),
            text_color="#333" if desbloqueado else "#999",
        ).pack()
        ctk.CTkLabel(
            card, text=desc, font=(FONT_NAME, 11), text_color="#888", wraplength=140
        ).pack(pady=5)
        ctk.CTkLabel(
            card,
            text="COMPLETADO" if desbloqueado else f"PROGRESO: {int(req*100)}%",
            font=(FONT_NAME, 10, "bold"),
            text_color=color_final if desbloqueado else "#BBB",
        ).pack(pady=(5, 15))

        col += 1
        if col > 2:
            col = 0
            fila += 1


# ---------------- INICIO Y TARJETAS ---------------- #
def crear_tarjeta(parent, texto, color, gif_path, fila, columna, comando=None):
    card = ctk.CTkFrame(parent, fg_color=color, corner_radius=35, width=300, height=200)
    card.grid(row=fila, column=columna, padx=35, pady=30)
    card.grid_propagate(False)

    lbl = ctk.CTkLabel(
        card, text=texto, text_color="white", font=FONTS["tarjetas"], wraplength=250
    )
    lbl.place(relx=0.5, rely=0.5, anchor="center")

    if comando:
        card.configure(cursor="hand2")
        card.bind("<Button-1>", lambda e: comando())
        lbl.bind("<Button-1>", lambda e: comando())


def vista_inicio():
    limpiar_panel()
    for i in range(3):
        principal.grid_columnconfigure(i, weight=1)

    banner = ctk.CTkFrame(
        principal, fg_color=COLORS["sidebar"], corner_radius=25, height=150
    )
    banner.grid(row=0, column=0, columnspan=3, padx=50, pady=(30, 20), sticky="nsew")
    ctk.CTkLabel(
        banner,
        text="¡HOLA, EXPLORADOR DEL SABER!",
        text_color="white",
        font=(FONT_NAME, 38, "bold"),
    ).pack(pady=(25, 5))
    ctk.CTkLabel(
        banner,
        text="¡Hoy es un gran día para aprender algo nuevo y divertido!",
        text_color="white",
        font=(FONT_NAME, 18),
    ).pack()

    valores = ESTADO_USUARIO["materias"].values()
    promedio_total = sum(valores) / len(valores)
    stats_frame = ctk.CTkFrame(principal, fg_color="transparent")
    stats_frame.grid(row=1, column=0, columnspan=3, pady=(20, 10))
    ctk.CTkLabel(
        stats_frame,
        text=f"NIVEL GENERAL: {int(promedio_total*100)}%",
        font=(FONT_NAME, 16, "bold"),
        text_color=COLORS["text_dark"],
    ).pack(side="left", padx=15)
    barra_nivel = ctk.CTkProgressBar(
        stats_frame, width=400, height=15, progress_color="#FFD700", fg_color="#E0E0E0"
    )
    barra_nivel.set(promedio_total)
    barra_nivel.pack(side="left")

    ctk.CTkLabel(
        principal,
        text="TUS MUNDOS POR EXPLORAR",
        text_color="#555",
        font=(FONT_NAME, 22, "bold"),
    ).grid(row=2, column=0, columnspan=3, pady=(30, 0))

    cards_data = [
        ("LECTURA Y ESCRITURA", COLORS["card1"], "lectura.gif", 3, 0),
        ("AJEDREZ", COLORS["card2"], "ajedrez.gif", 3, 1),
        ("JUEGO DE PALABRAS", COLORS["card3"], "palabras.gif", 3, 2),
        ("COMPUTACIÓN", COLORS["card4"], "computacion.gif", 4, 0),
        ("DEPORTES", COLORS["card5"], "deportes.gif", 4, 1),
        ("DIBUJO", COLORS["card6"], "ciencias.gif", 4, 2),
    ]

    for texto, color, gif_name, fila, col in cards_data:
        path = os.path.join(ASSETS_DIR, gif_name)

        # Lógica de comandos recuperada y ampliada
        if "AJEDREZ" in texto:
            comando_tarjeta = lanzar_ajedrez_hilo
        elif "JUEGO DE PALABRAS" in texto:
            comando_tarjeta = lanzar_juego_palabras
        elif "COMPUTACIÓN" in texto:
            comando_tarjeta = lanzar_computacion
        elif "DIBUJO" in texto:
            comando_tarjeta = lanzar_dibujo
        else:
            comando_tarjeta = None

        crear_tarjeta(principal, texto, color, path, fila, col, comando=comando_tarjeta)


# ---------------- ESTRUCTURA FINAL ---------------- #
sidebar = ctk.CTkFrame(root, fg_color=COLORS["sidebar"], width=220, corner_radius=0)
sidebar.pack(side="left", fill="y")
ctk.CTkLabel(sidebar, text="MENÚ", text_color="white", font=FONTS["sidebar"]).pack(
    pady=30
)

menu_config = [
    ("Inicio", vista_inicio),
    ("Progreso", vista_progreso),
    ("Logros", vista_logros),
    ("Temas", vista_temas),
    ("Ayuda", None),
]

for texto, comando in menu_config:
    btn = ctk.CTkButton(
        sidebar,
        text=texto,
        command=comando,
        fg_color="transparent",
        text_color="white",
        hover_color=COLORS["sidebar_hover"],
        font=FONTS["botones"],
        anchor="w",
        height=45,
        corner_radius=15,
    )
    btn.pack(fill="x", padx=15, pady=5)

principal = ctk.CTkScrollableFrame(root, fg_color=COLORS["bg"], corner_radius=0)
principal.pack(side="right", expand=True, fill="both")

vista_inicio()
root.mainloop()
