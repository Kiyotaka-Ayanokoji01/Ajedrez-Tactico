import pygame
import math


class Flecha:
    def __init__(self, fila_inicio, col_inicio, fila_fin, col_fin, color, tam_cuadro):
        self.color = color
        self.tam_cuadro = tam_cuadro

        # Convertir coordenadas de tablero a píxeles (centradas en el cuadro)
        self.inicio = (
            col_inicio * tam_cuadro + tam_cuadro // 2,
            fila_inicio * tam_cuadro + tam_cuadro // 2,
        )
        self.fin = (
            col_fin * tam_cuadro + tam_cuadro // 2,
            fila_fin * tam_cuadro + tam_cuadro // 2,
        )

    def dibujar(self, superficie):
        # Configuración de la flecha
        ancho_linea = 8
        tam_punta = 20

        # Dibujar el cuerpo de la flecha (la línea)
        pygame.draw.line(superficie, self.color, self.inicio, self.fin, ancho_linea)

        # Cálculo del ángulo para la punta
        angulo = math.atan2(self.inicio[1] - self.fin[1], self.inicio[0] - self.fin[0])

        # Puntos de la punta (triángulo)
        punto1 = (
            self.fin[0] + tam_punta * math.cos(angulo + math.pi / 6),
            self.fin[1] + tam_punta * math.sin(angulo + math.pi / 6),
        )
        punto2 = (
            self.fin[0] + tam_punta * math.cos(angulo - math.pi / 6),
            self.fin[1] + tam_punta * math.sin(angulo - math.pi / 6),
        )

        pygame.draw.polygon(superficie, self.color, [self.fin, punto1, punto2])
