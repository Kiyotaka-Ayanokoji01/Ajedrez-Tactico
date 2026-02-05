import pygame


class TableroInteractivo:
    def __init__(self, tam_cuadro=75):
        self.tam_cuadro = tam_cuadro
        self.ancho_tablero = 8 * tam_cuadro
        self.ancho_panel = 300
        self.ancho_total = self.ancho_tablero + self.ancho_panel
        self.alto_total = self.ancho_tablero

        self.pantalla = pygame.display.set_mode((self.ancho_total, self.alto_total))

        # Colores
        self.COLOR_CLARO = (235, 235, 210)
        self.COLOR_OSCURO = (115, 149, 82)
        self.COLOR_RESALTE = (245, 245, 100, 150)
        self.COLOR_MOV_POSIBLE = (0, 0, 0, 30)
        self.COLOR_PANEL = (40, 40, 40)
        self.COLOR_TEXTO = (220, 220, 220)

        # Fuentes
        pygame.font.init()
        self.fuente_ui = pygame.font.SysFont("Segoe UI", 24, bold=True)
        self.fuente_pequena = pygame.font.SysFont("Segoe UI", 18)

        # Rectángulo para el botón Deshacer
        self.rect_deshacer = pygame.Rect(
            self.ancho_tablero + 50, self.alto_total - 80, 200, 50
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

        # 1. Capa base: Cuadrícula
        self.dibujar_cuadricula()

        # 2. Resaltar último movimiento (casilla origen y destino)
        if ultimo_movimiento:
            self.resaltar_ultimo_movimiento(ultimo_movimiento)

        # 3. BRILLO DE JAQUE (Debajo de la pieza)
        if rey_en_jaque:
            self.dibujar_brillo_jaque(rey_en_jaque)

        # 4. Resaltar pieza seleccionada
        if seleccionada:
            self.resaltar_seleccionada(seleccionada)
            self.dibujar_puntos_legales(movs_legales)

        # 5. Dibujar las piezas (con su propia animación interna)
        for pieza in piezas:
            pieza.dibujar(self.pantalla)

        # 6. Flechas y dibujos temporales
        for flecha in flechas:
            flecha.dibujar(self.pantalla)

        # 7. Interfaz de Usuario (Panel Lateral)
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

    def dibujar_brillo_jaque(self, rey):
        """Crea un resplandor rojo intenso en la casilla del rey."""
        s = pygame.Surface((self.tam_cuadro, self.tam_cuadro), pygame.SRCALPHA)
        # Rojo con transparencia (Alpha 180)
        pygame.draw.rect(s, (255, 0, 0, 180), s.get_rect())
        self.pantalla.blit(s, (rey.col * self.tam_cuadro, rey.fila * self.tam_cuadro))

    def resaltar_ultimo_movimiento(self, mov):
        # mov es (f_orig, c_orig, f_dest, c_dest)
        s = pygame.Surface((self.tam_cuadro, self.tam_cuadro), pygame.SRCALPHA)
        s.fill((255, 255, 0, 100))  # Amarillo transparente
        self.pantalla.blit(s, (mov[1] * self.tam_cuadro, mov[0] * self.tam_cuadro))
        self.pantalla.blit(s, (mov[3] * self.tam_cuadro, mov[2] * self.tam_cuadro))

    def resaltar_seleccionada(self, pieza):
        s = pygame.Surface((self.tam_cuadro, self.tam_cuadro), pygame.SRCALPHA)
        s.fill((130, 150, 255, 150))  # Azul transparente
        self.pantalla.blit(
            s, (pieza.col * self.tam_cuadro, pieza.fila * self.tam_cuadro)
        )

    def dibujar_puntos_legales(self, movimientos):
        for f, c in movimientos:
            centro = (
                c * self.tam_cuadro + self.tam_cuadro // 2,
                f * self.tam_cuadro + self.tam_cuadro // 2,
            )
            s = pygame.Surface((self.tam_cuadro, self.tam_cuadro), pygame.SRCALPHA)
            pygame.draw.circle(
                s,
                self.COLOR_MOV_POSIBLE,
                (self.tam_cuadro // 2, self.tam_cuadro // 2),
                12,
            )
            self.pantalla.blit(s, (c * self.tam_cuadro, f * self.tam_cuadro))

    def dibujar_panel_lateral(self, historial, cap_b, cap_n, t_b, t_n, turno):
        # Fondo del panel
        pygame.draw.rect(
            self.pantalla,
            self.COLOR_PANEL,
            (self.ancho_tablero, 0, self.ancho_panel, self.alto_total),
        )

        # Dibujar Relojes
        self.dibujar_reloj(
            t_b, "Blancas", self.ancho_tablero + 20, 50, turno == "blanco"
        )
        self.dibujar_reloj(
            t_n, "Negras", self.ancho_tablero + 20, 120, turno == "negro"
        )

        # Historial (últimos 5 movimientos para no saturar)
        txt_hist = self.fuente_pequena.render("Historial:", True, self.COLOR_TEXTO)
        self.pantalla.blit(txt_hist, (self.ancho_tablero + 20, 200))

        y_offset = 230
        for mov in historial[-8:]:  # Mostrar los últimos 8
            txt = self.fuente_pequena.render(mov, True, (180, 180, 180))
            self.pantalla.blit(txt, (self.ancho_tablero + 30, y_offset))
            y_offset += 25

        # Botón Deshacer
        color_btn = (70, 70, 70)
        mouse_pos = pygame.mouse.get_pos()
        if self.rect_deshacer.collidepoint(mouse_pos):
            color_btn = (100, 40, 40)  # Cambio de color al pasar el mouse

        pygame.draw.rect(self.pantalla, color_btn, self.rect_deshacer, border_radius=8)
        txt_btn = self.fuente_ui.render("DESHACER", True, (255, 255, 255))
        self.pantalla.blit(
            txt_btn, (self.rect_deshacer.x + 45, self.rect_deshacer.y + 10)
        )

    def dibujar_reloj(self, tiempo, etiqueta, x, y, es_turno):
        minutos = int(tiempo // 60)
        segundos = int(tiempo % 60)
        texto = f"{etiqueta}: {minutos:02d}:{segundos:02d}"

        color = (255, 255, 255) if es_turno else (120, 120, 120)
        if es_turno:  # Indicador de turno (punto brillante)
            pygame.draw.circle(self.pantalla, (0, 255, 0), (x - 10, y + 15), 5)

        img = self.fuente_ui.render(texto, True, color)
        self.pantalla.blit(img, (x, y))

    def dibujar_ventana_promocion(self, color):
        """Ventana emergente para elegir pieza al promocionar peón."""
        # Se dibuja en el centro del tablero
        centro_x = self.ancho_tablero // 2 - 150
        centro_y = self.alto_total // 2 - 50
        rect_fondo = pygame.Rect(centro_x, centro_y, 300, 100)

        pygame.draw.rect(self.pantalla, (50, 50, 50), rect_fondo)
        pygame.draw.rect(self.pantalla, (255, 255, 255), rect_fondo, 2)

        opciones = ["reina", "torre", "alfil", "caballo"]
        rects = []
        for i, pieza in enumerate(opciones):
            r = pygame.Rect(centro_x + 10 + (i * 70), centro_y + 20, 60, 60)
            pygame.draw.rect(self.pantalla, (80, 80, 80), r)
            # Aquí podrías dibujar la imagen de la pieza, por ahora texto
            txt = self.fuente_pequena.render(pieza[0].upper(), True, (255, 255, 255))
            self.pantalla.blit(txt, (r.x + 22, r.y + 15))
            rects.append((r, pieza))

        return rects
