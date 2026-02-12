import pygame
import copy
import os
from pygame.locals import QUIT, MOUSEBUTTONDOWN, MOUSEBUTTONUP
from .TableroInteractivo import TableroInteractivo
from .PiezaAnimada import PiezaAnimada
from .Flecha import Flecha

# --- CONSTANTES DE COLORES PARA FLECHAS ---
COLORES_FLECHAS = {
    "1": (0, 255, 0, 160),
    "2": (255, 0, 0, 160),
    "3": (0, 0, 255, 160),
    "4": (255, 165, 0, 160),
}


class Juego:
    def __init__(self, minutos=10):
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        self.tablero = TableroInteractivo()
        self.ancho_total = self.tablero.ancho_total
        self.alto_total = self.tablero.alto_total
        self.pantalla = pygame.display.set_mode((self.ancho_total, self.alto_total))

        self.partida_activa = True
        self.reloj_fps = pygame.time.Clock()
        self.piezas = []
        self.flechas = []
        self.seleccionada = None
        self.movs_legales = []
        self.turno = "blanco"
        self.ultimo_movimiento = None
        self.resultado = None

        self.tiempo_blanco = minutos * 60.0
        self.tiempo_negro = minutos * 60.0
        self.reloj_iniciado = False
        self.ultima_actualizacion_tiempo = pygame.time.get_ticks()

        self.historial = []
        self.capturadas_blancas = []
        self.capturadas_negras = []

        self.historial_estados = []
        self.dibujando_flecha = False
        self.inicio_flecha = None
        self.color_flecha_actual = COLORES_FLECHAS["1"]

        self.ruta_sonidos = os.path.join(
            os.path.dirname(__file__), "..", "assets", "sonidos"
        )
        try:
            self.sonido_mover = pygame.mixer.Sound(
                os.path.join(self.ruta_sonidos, "Movimiento.wav")
            )
            self.sonido_captura = pygame.mixer.Sound(
                os.path.join(self.ruta_sonidos, "Captura.wav")
            )
            self.sonido_jaque = pygame.mixer.Sound(
                os.path.join(self.ruta_sonidos, "Jaque.wav")
            )
            self.sonido_fin = pygame.mixer.Sound(
                os.path.join(self.ruta_sonidos, "FinJuego.wav")
            )
        except:
            self.sonido_mover = self.sonido_captura = self.sonido_jaque = (
                self.sonido_fin
            ) = None

        self.crear_piezas_iniciales()
        self.guardar_estado()
        pygame.display.set_caption(f"Ajedrez - Turno: {self.turno.upper()}")

    def obtener_notacion_corta(self, f_orig, c_orig, f_dest, c_dest, pieza, es_captura):
        """Convierte a notación corta en español: Inicial + destino"""
        letras = "abcdefgh"
        # Invertimos la fila para que 7 sea 1 y 0 sea 8
        orig = f"{letras[c_orig]}{8-f_orig}"
        dest = f"{letras[c_dest]}{8-f_dest}"
        prefijo = ""
        if pieza.nombre == "caballo":
            prefijo = "C"
        elif pieza.nombre == "alfil":
            prefijo = "A"
        elif pieza.nombre == "torre":
            prefijo = "T"
        elif pieza.nombre == "dama":
            prefijo = "D"
        elif pieza.nombre == "rey":
            prefijo = "R"
        return f"{prefijo}{orig}{dest}"

    def guardar_estado(self):
        estado = {
            "piezas": copy.deepcopy(self.piezas),
            "turno": self.turno,
            "ultimo_movimiento": self.ultimo_movimiento,
            "historial_txt": list(self.historial),
            "cap_b": list(self.capturadas_blancas),
            "cap_n": list(self.capturadas_negras),
            "t_blanco": self.tiempo_blanco,
            "t_negro": self.tiempo_negro,
            "reloj_iniciado": self.reloj_iniciado,
            "resultado": self.resultado,
        }
        self.historial_estados.append(estado)

    def deshacer_movimiento(self):
        if len(self.historial_estados) > 1:
            self.historial_estados.pop()
            previo = self.historial_estados[-1]
            self.piezas = copy.deepcopy(previo["piezas"])
            self.turno = previo["turno"]
            self.ultimo_movimiento = previo["ultimo_movimiento"]
            self.historial = list(previo["historial_txt"])
            self.capturadas_blancas = list(previo["cap_b"])
            self.capturadas_negras = list(previo["cap_n"])
            self.tiempo_blanco = previo["t_blanco"]
            self.tiempo_negro = previo["t_negro"]
            self.reloj_iniciado = previo.get("reloj_iniciado", False)
            self.resultado = previo.get("resultado", None)
            for p in self.piezas:
                p.x, p.y = (
                    p.col * self.tablero.tam_cuadro,
                    p.fila * self.tablero.tam_cuadro,
                )
            self.seleccionada = None
            self.movs_legales = []
            self.flechas = []
            pygame.display.set_caption(f"Ajedrez - Turno: {self.turno.upper()}")

    def crear_piezas_iniciales(self):
        tam = self.tablero.tam_cuadro
        orden = [
            "torre",
            "caballo",
            "alfil",
            "dama",
            "rey",
            "alfil",
            "caballo",
            "torre",
        ]
        for col, nombre in enumerate(orden):
            self.piezas.append(PiezaAnimada(nombre, "negro", 0, col, tam))
            self.piezas.append(PiezaAnimada("peon", "negro", 1, col, tam))
            self.piezas.append(PiezaAnimada("peon", "blanco", 6, col, tam))
            self.piezas.append(PiezaAnimada(nombre, "blanco", 7, col, tam))

    def reproducir_sonido(self, tipo):
        sonidos = {
            "Movimiento": self.sonido_mover,
            "Captura": self.sonido_captura,
            "Jaque": self.sonido_jaque,
            "Fin": self.sonido_fin,
        }
        if tipo in sonidos and sonidos[tipo]:
            sonidos[tipo].play()

    def obtener_rey(self, color):
        return next(
            (p for p in self.piezas if p.nombre == "rey" and p.color == color), None
        )

    def esta_atacada(self, fila, col, color_defensor):
        color_enemigo = "negro" if color_defensor == "blanco" else "blanco"
        for p in self.piezas:
            if p.color != color_enemigo:
                continue
            df, dc = fila - p.fila, col - p.col
            if p.nombre == "peon":
                dir_p = 1 if p.color == "negro" else -1
                if df == dir_p and abs(dc) == 1:
                    return True
            elif p.nombre == "caballo":
                if abs(df) * abs(dc) == 2:
                    return True
            elif p.nombre == "rey":
                if abs(df) <= 1 and abs(dc) <= 1:
                    return True
            elif p.nombre in ["dama", "torre", "alfil"]:
                if (
                    (p.nombre == "torre" and (df != 0 and dc != 0))
                    or (p.nombre == "alfil" and abs(df) != abs(dc))
                    or (
                        p.nombre == "dama"
                        and (df != 0 and dc != 0 and abs(df) != abs(dc))
                    )
                ):
                    continue
                step_f, step_c = (0 if df == 0 else (1 if df > 0 else -1)), (
                    0 if dc == 0 else (1 if dc > 0 else -1)
                )
                f_act, c_act, obstruido = p.fila + step_f, p.col + step_c, False
                while f_act != fila or c_act != col:
                    if any(
                        x for x in self.piezas if x.fila == f_act and x.col == c_act
                    ):
                        obstruido = True
                        break
                    f_act, c_act = f_act + step_f, c_act + step_c
                if not obstruido:
                    return True
        return False

    def deja_al_rey_en_jaque(self, pieza, n_fila, n_col):
        f_orig, c_orig = pieza.fila, pieza.col
        p_cap = next(
            (
                p
                for p in self.piezas
                if p.fila == n_fila and p.col == n_col and p != pieza
            ),
            None,
        )
        if p_cap:
            self.piezas.remove(p_cap)
        pieza.fila, pieza.col = n_fila, n_col
        rey = self.obtener_rey(pieza.color)
        en_jaque = self.esta_atacada(rey.fila, rey.col, pieza.color) if rey else False
        pieza.fila, pieza.col = f_orig, c_orig
        if p_cap:
            self.piezas.append(p_cap)
        return en_jaque

    def tiene_movimientos_legales(self, color):
        for p in self.piezas:
            if p.color == color:
                for f in range(8):
                    for c in range(8):
                        if self.es_movimiento_valido(
                            p, f, c
                        ) and not self.deja_al_rey_en_jaque(p, f, c):
                            return True
        return False

    def es_movimiento_valido(self, pieza, n_fila, n_col, chequear_enroque=True):
        if not (0 <= n_fila <= 7 and 0 <= n_col <= 7):
            return False
        df, dc = n_fila - pieza.fila, n_col - pieza.col
        p_dest = next(
            (p for p in self.piezas if p.fila == n_fila and p.col == n_col), None
        )
        if p_dest and (p_dest.nombre == "rey" or p_dest.color == pieza.color):
            return False

        if pieza.nombre == "peon":
            dir = -1 if pieza.color == "blanco" else 1
            if dc == 0 and df == dir and not p_dest:
                return True
            if not pieza.ha_movido and dc == 0 and df == 2 * dir:
                if (
                    not any(
                        p.fila == pieza.fila + dir and p.col == n_col
                        for p in self.piezas
                    )
                    and not p_dest
                ):
                    return True
            if abs(dc) == 1 and df == dir:
                if p_dest and p_dest.color != pieza.color:
                    return True
                if self.ultimo_movimiento:
                    uo, co, ud, cd = self.ultimo_movimiento
                    if abs(uo - ud) == 2 and ud == pieza.fila and cd == n_col:
                        return True
            return False
        elif pieza.nombre == "caballo":
            return abs(df) * abs(dc) == 2
        elif pieza.nombre == "rey":
            if abs(df) <= 1 and abs(dc) <= 1:
                return True
            if chequear_enroque and not pieza.ha_movido and df == 0 and abs(dc) == 2:
                if self.esta_atacada(pieza.fila, pieza.col, pieza.color):
                    return False
                ct = 7 if dc > 0 else 0
                torre = next(
                    (
                        p
                        for p in self.piezas
                        if p.fila == pieza.fila and p.col == ct and p.nombre == "torre"
                    ),
                    None,
                )
                if torre and not torre.ha_movido:
                    if all(
                        not any(
                            p.fila == pieza.fila and p.col == c for p in self.piezas
                        )
                        for c in range(min(pieza.col, ct) + 1, max(pieza.col, ct))
                    ):
                        paso = 1 if dc > 0 else -1
                        if not self.esta_atacada(
                            pieza.fila, pieza.col + paso, pieza.color
                        ) and not self.esta_atacada(pieza.fila, n_col, pieza.color):
                            return True
            return False
        elif pieza.nombre in ["torre", "alfil", "dama"]:
            if (
                (pieza.nombre == "torre" and df != 0 and dc != 0)
                or (pieza.nombre == "alfil" and abs(df) != abs(dc))
                or (
                    pieza.nombre == "dama"
                    and df != 0
                    and dc != 0
                    and abs(df) != abs(dc)
                )
            ):
                return False
            pf, pc = (0 if df == 0 else (1 if df > 0 else -1)), (
                0 if dc == 0 else (1 if dc > 0 else -1)
            )
            f_act, c_act = pieza.fila + pf, pieza.col + pc
            while f_act != n_fila or c_act != n_col:
                if any(p.fila == f_act and p.col == c_act for p in self.piezas):
                    return False
                f_act, c_act = f_act + pf, c_act + pc
            return True
        return False

    def actualizar_relojes(self):
        ahora = pygame.time.get_ticks()
        delta = (ahora - self.ultima_actualizacion_tiempo) / 1000.0
        self.ultima_actualizacion_tiempo = ahora
        if self.reloj_iniciado and self.partida_activa and not self.resultado:
            if self.turno == "blanco":
                self.tiempo_blanco = max(0, self.tiempo_blanco - delta)
                if self.tiempo_blanco <= 0:
                    self.resultado = "Ganan Negras por Tiempo"
                    self.reproducir_sonido("Fin")
            else:
                self.tiempo_negro = max(0, self.tiempo_negro - delta)
                if self.tiempo_negro <= 0:
                    self.resultado = "Ganan Blancas por Tiempo"
                    self.reproducir_sonido("Fin")

    def esperar_promocion(self, pieza):
        esperando = True
        while esperando:
            opciones = self.tablero.dibujar_ventana_promocion(pieza.color)
            pygame.display.flip()
            for e in pygame.event.get():
                if e.type == QUIT:
                    pygame.quit()
                    exit()
                if e.type == MOUSEBUTTONDOWN and e.button == 1:
                    pos = pygame.mouse.get_pos()
                    for rect, nombre in opciones:
                        if rect.collidepoint(pos):
                            pieza.nombre = nombre
                            esperando = False
            self.reloj_fps.tick(30)
        pieza.cargar_imagen()

    def dibujar_cartel_resultado(self):
        if not self.resultado:
            return
        fuente = pygame.font.SysFont("Arial", 20, bold=True)
        x_cartel = self.tablero.ancho_tablero + 15
        y_cartel = self.tablero.alto_total // 2 + 100
        ancho_cartel = self.tablero.ancho_total - self.tablero.ancho_tablero - 30
        rect_fondo = pygame.Rect(x_cartel, y_cartel, ancho_cartel, 50)
        pygame.draw.rect(self.pantalla, (45, 45, 45), rect_fondo, border_radius=8)
        pygame.draw.rect(self.pantalla, (212, 175, 55), rect_fondo, 2, border_radius=8)
        texto = fuente.render(self.resultado, True, (255, 215, 0))
        text_rect = texto.get_rect(center=rect_fondo.center)
        self.pantalla.blit(texto, text_rect)

    def iniciar_partida(self):
        while self.partida_activa:
            self.actualizar_relojes()
            rey_act = self.obtener_rey(self.turno)
            rey_en_jaque = (
                rey_act
                if (
                    rey_act and self.esta_atacada(rey_act.fila, rey_act.col, self.turno)
                )
                else None
            )

            for evento in pygame.event.get():
                if evento.type == QUIT:
                    self.partida_activa = False
                if evento.type == MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if pos[0] < self.tablero.ancho_tablero:
                        col, fila = (
                            pos[0] // self.tablero.tam_cuadro,
                            pos[1] // self.tablero.tam_cuadro,
                        )
                        if evento.button == 3:
                            self.dibujando_flecha = True
                            self.inicio_flecha = (fila, col)
                        elif evento.button == 1 and not self.resultado:
                            if self.seleccionada and (fila, col) in self.movs_legales:
                                self.reloj_iniciado = True
                                f_orig, c_orig = (
                                    self.seleccionada.fila,
                                    self.seleccionada.col,
                                )

                                # Guardar texto en el historial
                                texto_mov = self.obtener_notacion(
                                    f_orig, c_orig, fila, col, self.seleccionada
                                )
                                self.historial.append(texto_mov)

                                p_dest = next(
                                    (
                                        p
                                        for p in self.piezas
                                        if p.fila == fila
                                        and p.col == col
                                        and p != self.seleccionada
                                    ),
                                    None,
                                )
                                if (
                                    self.seleccionada.nombre == "peon"
                                    and abs(col - self.seleccionada.col) == 1
                                    and not p_dest
                                ):
                                    p_dest = next(
                                        (
                                            p
                                            for p in self.piezas
                                            if p.fila == self.seleccionada.fila
                                            and p.col == col
                                        ),
                                        None,
                                    )

                                if (
                                    self.seleccionada.nombre == "rey"
                                    and abs(col - self.seleccionada.col) == 2
                                ):
                                    col_torre_orig = (
                                        7 if col > self.seleccionada.col else 0
                                    )
                                    col_torre_dest = (
                                        col - 1
                                        if col > self.seleccionada.col
                                        else col + 1
                                    )
                                    torre = next(
                                        (
                                            p
                                            for p in self.piezas
                                            if p.fila == fila
                                            and p.col == col_torre_orig
                                        ),
                                        None,
                                    )
                                    if torre:
                                        torre.col, torre.x, torre.ha_movido = (
                                            col_torre_dest,
                                            col_torre_dest * self.tablero.tam_cuadro,
                                            True,
                                        )

                                if p_dest:
                                    if p_dest.color == "blanco":
                                        self.capturadas_negras.append(p_dest)
                                    else:
                                        self.capturadas_blancas.append(p_dest)
                                    self.piezas.remove(p_dest)
                                    self.reproducir_sonido("Captura")
                                else:
                                    self.reproducir_sonido("Movimiento")

                                self.ultimo_movimiento = (f_orig, c_orig, fila, col)
                                (
                                    self.seleccionada.fila,
                                    self.seleccionada.col,
                                    self.seleccionada.ha_movido,
                                ) = (fila, col, True)
                                self.seleccionada.x, self.seleccionada.y = (
                                    col * self.tablero.tam_cuadro,
                                    fila * self.tablero.tam_cuadro,
                                )

                                if (
                                    self.seleccionada.nombre == "peon"
                                    and self.seleccionada.fila in [0, 7]
                                ):
                                    self.esperar_promocion(self.seleccionada)

                                self.turno = (
                                    "negro" if self.turno == "blanco" else "blanco"
                                )
                                n_rey = self.obtener_rey(self.turno)
                                if n_rey and self.esta_atacada(
                                    n_rey.fila, n_rey.col, self.turno
                                ):
                                    if not self.tiene_movimientos_legales(self.turno):
                                        ganador = (
                                            "Blancas"
                                            if self.turno == "negro"
                                            else "Negras"
                                        )
                                        self.resultado = f"¡MATE! Ganan {ganador}"
                                        self.reproducir_sonido("Fin")
                                    else:
                                        self.reproducir_sonido("Jaque")
                                elif not self.tiene_movimientos_legales(self.turno):
                                    self.resultado = "TABLAS (Ahogado)"
                                    self.reproducir_sonido("Fin")

                                self.seleccionada, self.movs_legales = None, []
                                self.guardar_estado()
                                pygame.display.set_caption(
                                    f"Ajedrez - Turno: {self.turno.upper()}"
                                )
                            else:
                                p_clic = next(
                                    (
                                        p
                                        for p in self.piezas
                                        if p.fila == fila
                                        and p.col == col
                                        and p.color == self.turno
                                    ),
                                    None,
                                )
                                if p_clic:
                                    self.seleccionada = p_clic
                                    self.movs_legales = [
                                        (f, c)
                                        for f in range(8)
                                        for c in range(8)
                                        if self.es_movimiento_valido(p_clic, f, c)
                                        and not self.deja_al_rey_en_jaque(p_clic, f, c)
                                    ]
                                else:
                                    self.seleccionada, self.movs_legales = None, []
                    elif hasattr(
                        self.tablero, "rect_deshacer"
                    ) and self.tablero.rect_deshacer.collidepoint(pos):
                        self.deshacer_movimiento()

                if (
                    evento.type == MOUSEBUTTONUP
                    and evento.button == 3
                    and self.dibujando_flecha
                ):
                    pos = pygame.mouse.get_pos()
                    cf, ff = (
                        pos[0] // self.tablero.tam_cuadro,
                        pos[1] // self.tablero.tam_cuadro,
                    )
                    if self.inicio_flecha != (ff, cf):
                        self.flechas.append(
                            Flecha(
                                self.inicio_flecha[0],
                                self.inicio_flecha[1],
                                ff,
                                cf,
                                self.color_flecha_actual,
                                self.tablero.tam_cuadro,
                            )
                        )
                    self.dibujando_flecha = False

            self.tablero.dibujar_tablero(
                self.piezas,
                self.seleccionada,
                rey_en_jaque,
                self.movs_legales,
                self.ultimo_movimiento,
                self.flechas,
                self.historial,
                self.capturadas_blancas,
                self.capturadas_negras,
                self.tiempo_blanco,
                self.tiempo_negro,
                self.turno,
            )
            if self.resultado:
                self.dibujar_cartel_resultado()
            pygame.display.flip()
            self.reloj_fps.tick(120)

        pygame.quit()
