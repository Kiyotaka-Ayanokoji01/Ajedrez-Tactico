import pygame


class TableroInteractivo:
    def __init__(self, tam_cuadro=75):
        self.tam_cuadro = tam_cuadro
        self.ancho_tablero = 8 * tam_cuadro
        self.tam_tablero = self.ancho_tablero
        self.ancho_panel = 350
        self.ancho_total = self.ancho_tablero + self.ancho_panel
        self.alto_total = self.ancho_tablero

        self.pantalla = pygame.display.set_mode((self.ancho_total, self.alto_total))

        # --- PALETA DE COLORES (Estilo Dark Mode / Chess.com) ---
        self.COLOR_CLARO = (235, 235, 210)
        self.COLOR_OSCURO = (115, 149, 82)
        self.COLOR_PANEL_FONDO = (38, 36, 33)
        self.COLOR_PANEL_MOVIMIENTOS = (46, 44, 41)
        self.COLOR_TEXTO = (255, 255, 255)
        self.COLOR_TEXTO_SECUNDARIO = (171, 170, 168)
        self.COLOR_ACENTO = (129, 182, 76)  # Verde Chess.com

        # Fuentes
        pygame.font.init()
        self.fuente_ui = pygame.font.SysFont("Segoe UI", 24, bold=True)
        self.fuente_reloj = pygame.font.SysFont("Consolas", 32, bold=True)
        self.fuente_pequena = pygame.font.SysFont("Segoe UI", 16)

        # Botón Deshacer posicionado estratégicamente
        self.rect_deshacer = pygame.Rect(
            self.ancho_tablero + 25, self.alto_total - 145, self.ancho_panel - 50, 40
        )

    def dibujar_tablero(
        self,
        piezas,
        seleccionada,
        rey_en_jaque,
        movs_legales,
        ultimo_movimiento,
        flechas,
        historial,
        capturadas_b,
        capturadas_n,
        t_blanco,
        t_negro,
        turno,
    ):
        """Método principal de renderizado."""

        # 1. Limpiar fondo del panel lateral
        pygame.draw.rect(
            self.pantalla,
            self.COLOR_PANEL_FONDO,
            (self.ancho_tablero, 0, self.ancho_panel, self.alto_total),
        )

        # 2. Dibujar la cuadrícula del tablero
        self.dibujar_cuadricula()

        # 3. Resaltados tácticos (Debajo de las piezas)
        if ultimo_movimiento:
            self.resaltar_ultimo_movimiento(ultimo_movimiento)
        if rey_en_jaque:
            self.dibujar_brillo_jaque(rey_en_jaque)
        if seleccionada:
            self.resaltar_seleccionada(seleccionada)
            self.dibujar_puntos_legales(movs_legales)

        # 4. Dibujar las piezas (con sus animaciones)
        for pieza in piezas:
            pieza.dibujar(self.pantalla)

        # 5. Elementos visuales temporales (flechas)
        for flecha in flechas:
            flecha.dibujar(self.pantalla)

        # 6. Interfaz de Usuario (Relojes, Historial, Capturadas)
        self.dibujar_panel_lateral(
            historial, capturadas_b, capturadas_n, t_blanco, t_negro, turno
        )

    def dibujar_cuadricula(self):
        for fila in range(8):
            for col in range(8):
                color = self.COLOR_CLARO if (fila + col) % 2 == 0 else self.COLOR_OSCURO
                pygame.draw.rect(
                    self.pantalla,
                    color,
                    (
                        col * self.tam_cuadro,
                        fila * self.tam_cuadro,
                        self.tam_cuadro,
                        self.tam_cuadro,
                    ),
                )

    def dibujar_panel_lateral(self, historial, cap_b, cap_n, t_b, t_n, turno):
        x_panel = self.ancho_tablero + 20
        ancho_cont = self.ancho_panel - 40

        # --- SECCIÓN SUPERIOR: Oponente (Negras) ---
        self.dibujar_reloj_estilizado(t_n, x_panel, 20, turno == "negro")
        # Capturadas por negras (piezas blancas perdidas)
        self.dibujar_capturadas(cap_n, x_panel, 90)

        # --- SECCIÓN CENTRAL: Historial de movimientos ---
        rect_hist = pygame.Rect(x_panel, 150, ancho_cont, self.alto_total - 310)
        pygame.draw.rect(
            self.pantalla, self.COLOR_PANEL_MOVIMIENTOS, rect_hist, border_radius=5
        )

        titulo_hist = self.fuente_pequena.render(
            "HISTORIAL DE JUEGO", True, self.COLOR_TEXTO_SECUNDARIO
        )
        self.pantalla.blit(titulo_hist, (x_panel + 10, 160))

        y_mov = 190
        for i, mov in enumerate(
            historial[-14:]
        ):  # Mostramos los últimos 14 movimientos
            txt = self.fuente_pequena.render(f"{i+1}. {mov}", True, self.COLOR_TEXTO)
            columna = 0 if i < 7 else 130
            self.pantalla.blit(txt, (x_panel + 15 + columna, y_mov + ((i % 7) * 25)))

        # --- SECCIÓN INFERIOR: Jugador (Blancas) ---
        # Capturadas por blancas (piezas negras perdidas)
        self.dibujar_capturadas(cap_b, x_panel, self.alto_total - 180)
        self.dibujar_reloj_estilizado(
            t_b, x_panel, self.alto_total - 80, turno == "blanco"
        )

        # --- BOTÓN DESHACER ---
        color_btn = (60, 58, 55)
        if self.rect_deshacer.collidepoint(pygame.mouse.get_pos()):
            color_btn = (80, 78, 75)

        pygame.draw.rect(self.pantalla, color_btn, self.rect_deshacer, border_radius=5)
        txt_btn = self.fuente_pequena.render("DESHACER", True, self.COLOR_TEXTO)
        self.pantalla.blit(
            txt_btn,
            (
                self.rect_deshacer.centerx - txt_btn.get_width() // 2,
                self.rect_deshacer.centery - txt_btn.get_height() // 2,
            ),
        )

    def dibujar_reloj_estilizado(self, tiempo, x, y, es_turno):
        color_fondo = (43, 41, 38) if not es_turno else (55, 53, 50)
        rect_reloj = pygame.Rect(x, y, self.ancho_panel - 40, 55)
        pygame.draw.rect(self.pantalla, color_fondo, rect_reloj, border_radius=5)

        if es_turno:
            pygame.draw.rect(
                self.pantalla, self.COLOR_ACENTO, rect_reloj, 2, border_radius=5
            )

        minutos, segundos = int(tiempo // 60), int(tiempo % 60)
        txt_tiempo = f"{minutos:02d}:{segundos:02d}"

        color_texto = self.COLOR_TEXTO if es_turno else self.COLOR_TEXTO_SECUNDARIO
        img_tiempo = self.fuente_reloj.render(txt_tiempo, True, color_texto)
        self.pantalla.blit(img_tiempo, (x + 15, y + 8))

    def dibujar_capturadas(self, lista_capturadas, x, y):
        """Dibuja las imágenes de las piezas capturadas escaladas."""
        espaciado_x = 20
        mini_tam = 20

        for i, pieza in enumerate(lista_capturadas):
            fila = i // 12  # Caben más piezas por fila al ser más pequeñas
            col = i % 12
            pos_x = x + (col * espaciado_x)
            pos_y = y + (fila * 25)

            if hasattr(pieza, "imagen") and pieza.imagen:
                # Escalamos la imagen original a miniatura
                img_mini = pygame.transform.smoothscale(
                    pieza.imagen, (mini_tam, mini_tam)
                )
                self.pantalla.blit(img_mini, (pos_x, pos_y))

    def dibujar_brillo_jaque(self, rey):
        s = pygame.Surface((self.tam_cuadro, self.tam_cuadro), pygame.SRCALPHA)
        pygame.draw.rect(s, (255, 0, 0, 160), s.get_rect())
        self.pantalla.blit(s, (rey.col * self.tam_cuadro, rey.fila * self.tam_cuadro))

    def resaltar_ultimo_movimiento(self, mov):
        s = pygame.Surface((self.tam_cuadro, self.tam_cuadro), pygame.SRCALPHA)
        s.fill((245, 246, 130, 150))
        self.pantalla.blit(s, (mov[1] * self.tam_cuadro, mov[0] * self.tam_cuadro))
        self.pantalla.blit(s, (mov[3] * self.tam_cuadro, mov[2] * self.tam_cuadro))

    def resaltar_seleccionada(self, pieza):
        s = pygame.Surface((self.tam_cuadro, self.tam_cuadro), pygame.SRCALPHA)
        s.fill((129, 182, 76, 120))
        self.pantalla.blit(
            s, (pieza.col * self.tam_cuadro, pieza.fila * self.tam_cuadro)
        )

    def dibujar_puntos_legales(self, movimientos):
        for f, c in movimientos:
            s = pygame.Surface((self.tam_cuadro, self.tam_cuadro), pygame.SRCALPHA)
            pygame.draw.circle(
                s, (0, 0, 0, 35), (self.tam_cuadro // 2, self.tam_cuadro // 2), 12
            )
            self.pantalla.blit(s, (c * self.tam_cuadro, f * self.tam_cuadro))

    def dibujar_ventana_promocion(self, color):
        centro_x = self.ancho_tablero // 2 - 150
        centro_y = self.alto_total // 2 - 50
        rect_fondo = pygame.Rect(centro_x, centro_y, 300, 100)
        pygame.draw.rect(self.pantalla, (45, 45, 45), rect_fondo, border_radius=10)
        pygame.draw.rect(
            self.pantalla, self.COLOR_ACENTO, rect_fondo, 2, border_radius=10
        )

        opciones = ["reina", "torre", "alfil", "caballo"]
        rects = []
        for i, pieza in enumerate(opciones):
            r = pygame.Rect(centro_x + 20 + (i * 70), centro_y + 20, 60, 60)
            pygame.draw.rect(self.pantalla, (65, 65, 65), r, border_radius=5)
            txt = self.fuente_pequena.render(pieza[0].upper(), True, self.COLOR_TEXTO)
            self.pantalla.blit(
                txt,
                (r.centerx - txt.get_width() // 2, r.centery - txt.get_height() // 2),
            )
            rects.append((r, pieza))
        return rects
