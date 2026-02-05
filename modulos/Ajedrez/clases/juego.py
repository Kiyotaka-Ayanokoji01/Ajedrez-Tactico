import pygame
import copy
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
        self.tablero = TableroInteractivo()
        self.partida_activa = True
        self.reloj_fps = pygame.time.Clock()
        self.piezas = []
        self.flechas = []
        self.seleccionada = None
        self.movs_legales = []
        self.turno = "blanco"
        self.ultimo_movimiento = None

        self.tiempo_blanco = minutos * 60.0
        self.tiempo_negro = minutos * 60.0
        self.ultima_actualizacion_tiempo = pygame.time.get_ticks()

        self.historial = []
        self.capturadas_blancas = []
        self.capturadas_negras = []
        self.historial_estados = []

        self.dibujando_flecha = False
        self.inicio_flecha = None
        self.color_flecha_actual = COLORES_FLECHAS["1"]

        self.crear_piezas_iniciales()
        self.guardar_estado()

        pygame.display.set_caption(f"Ajedrez - Turno: {self.turno.upper()}")

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
            for p in self.piezas:
                p.x = p.col * self.tablero.tam_cuadro
                p.y = p.fila * self.tablero.tam_cuadro
            self.seleccionada = None
            self.movs_legales = []
            self.flechas = []
            pygame.display.set_caption(f"Ajedrez - Turno: {self.turno.upper()}")

    def crear_piezas_iniciales(self):
        tam = self.tablero.tam_cuadro
        self.piezas = []
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

    def obtener_nombre_casilla(self, fila, col):
        return f"{'abcdefgh'[col]}{8 - fila}"

    def obtener_rey(self, color):
        return next(
            (p for p in self.piezas if p.nombre == "rey" and p.color == color), None
        )

    def esta_atacada(self, fila, col, color_defensor):
        """Lógica de Rayos X: Detecta ataques comprobando obstrucciones en el tablero actual."""
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
                diag = abs(df) == abs(dc)
                rect = df == 0 or dc == 0
                if p.nombre == "torre" and not rect:
                    continue
                if p.nombre == "alfil" and not diag:
                    continue
                if p.nombre == "dama" and not (rect or diag):
                    continue

                step_f = 0 if df == 0 else (1 if df > 0 else -1)
                step_c = 0 if dc == 0 else (1 if dc > 0 else -1)
                f_act, c_act = p.fila + step_f, p.col + step_c
                obstruido = False
                while f_act != fila or c_act != col:
                    if any(
                        x for x in self.piezas if x.fila == f_act and x.col == c_act
                    ):
                        obstruido = True
                        break
                    f_act += step_f
                    c_act += step_c
                if not obstruido:
                    return True
        return False

    def deja_al_rey_en_jaque(self, pieza, n_fila, n_col):
        """Simulación de movimiento: mueve la pieza y verifica el estado del tablero resultante."""
        f_orig, c_orig = pieza.fila, pieza.col
        # Detectar si hay captura
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

        # Mover pieza temporalmente
        pieza.fila, pieza.col = n_fila, n_col

        rey = self.obtener_rey(pieza.color)
        # La función esta_atacada ahora detectará si hay piezas restantes bloqueando la línea
        en_jaque = self.esta_atacada(rey.fila, rey.col, pieza.color) if rey else False

        # Revertir estado
        pieza.fila, pieza.col = f_orig, c_orig
        if p_cap:
            self.piezas.append(p_cap)

        return en_jaque

    def tiene_movimientos_legales(self, color):
        for p in self.piezas:
            if p.color == color:
                for f in range(8):
                    for c in range(8):
                        if self.es_movimiento_valido(p, f, c):
                            if not self.deja_al_rey_en_jaque(p, f, c):
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
                    uo, _, ud, cd = self.ultimo_movimiento
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
                f_act += pf
                c_act += pc
            return True
        return False

    def actualizar_relojes(self):
        ahora = pygame.time.get_ticks()
        delta = (ahora - self.ultima_actualizacion_tiempo) / 1000.0
        self.ultima_actualizacion_tiempo = ahora
        if self.turno == "blanco":
            self.tiempo_blanco = max(0, self.tiempo_blanco - delta)
        else:
            self.tiempo_negro = max(0, self.tiempo_negro - delta)
        if self.tiempo_blanco <= 0 or self.tiempo_negro <= 0:
            self.partida_activa = False

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
                    if hasattr(
                        self.tablero, "rect_deshacer"
                    ) and self.tablero.rect_deshacer.collidepoint(pos):
                        self.deshacer_movimiento()
                        continue

                    col, fila = (
                        pos[0] // self.tablero.tam_cuadro,
                        pos[1] // self.tablero.tam_cuadro,
                    )
                    if evento.button == 3:
                        self.dibujando_flecha = True
                        self.inicio_flecha = (fila, col)
                    elif evento.button == 1:
                        if self.seleccionada and (fila, col) in self.movs_legales:
                            self.ultimo_movimiento = (
                                self.seleccionada.fila,
                                self.seleccionada.col,
                                fila,
                                col,
                            )
                            inicial = (
                                "D"
                                if self.seleccionada.nombre == "dama"
                                else self.seleccionada.nombre[0].upper()
                            )
                            p_dest = next(
                                (
                                    p
                                    for p in self.piezas
                                    if p.fila == fila and p.col == col
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

                            dest_txt = self.obtener_nombre_casilla(fila, col)
                            if p_dest:
                                if p_dest.color == "blanco":
                                    self.capturadas_blancas.append(p_dest)
                                else:
                                    self.capturadas_negras.append(p_dest)
                                self.piezas.remove(p_dest)
                                self.historial.append(f"{inicial}x{dest_txt}")
                            else:
                                self.historial.append(f"{inicial}{dest_txt}")

                            (
                                self.seleccionada.fila,
                                self.seleccionada.col,
                                self.seleccionada.ha_movido,
                            ) = (fila, col, True)
                            if (
                                self.seleccionada.nombre == "peon"
                                and self.seleccionada.fila in [0, 7]
                            ):
                                self.esperar_promocion(self.seleccionada)

                            self.turno = "negro" if self.turno == "blanco" else "blanco"
                            self.seleccionada = None
                            self.movs_legales = []
                            self.guardar_estado()
                            if not self.tiene_movimientos_legales(self.turno):
                                self.partida_activa = False
                        else:
                            pieza_clic = next(
                                (
                                    p
                                    for p in self.piezas
                                    if p.fila == fila
                                    and p.col == col
                                    and p.color == self.turno
                                ),
                                None,
                            )
                            if pieza_clic:
                                self.seleccionada = pieza_clic
                                self.movs_legales = [
                                    (f, c)
                                    for f in range(8)
                                    for c in range(8)
                                    if self.es_movimiento_valido(
                                        self.seleccionada, f, c
                                    )
                                    and not self.deja_al_rey_en_jaque(
                                        self.seleccionada, f, c
                                    )
                                ]
                            else:
                                self.seleccionada = None
                                self.movs_legales = []

                if (
                    evento.type == MOUSEBUTTONUP
                    and evento.button == 3
                    and self.dibujando_flecha
                ):
                    pos = pygame.mouse.get_pos()
                    col_f, fila_f = (
                        pos[0] // self.tablero.tam_cuadro,
                        pos[1] // self.tablero.tam_cuadro,
                    )
                    if self.inicio_flecha != (fila_f, col_f):
                        self.flechas.append(
                            Flecha(
                                self.inicio_flecha[0],
                                self.inicio_flecha[1],
                                fila_f,
                                col_f,
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
            pygame.display.flip()
            self.reloj_fps.tick(60)
        pygame.quit()
