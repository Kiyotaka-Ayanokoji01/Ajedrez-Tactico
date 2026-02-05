import pygame
import os


class PiezaAnimada:
    def __init__(self, nombre, color, fila, col, tam_cuadro):
        self.nombre = nombre
        self.color = color
        self.fila = fila
        self.col = col
        self.tam_cuadro = tam_cuadro
        self.ha_movido = False

        # --- Posición visual para la animación ---
        self.x = col * tam_cuadro
        self.y = fila * tam_cuadro

        # Velocidad de la animación (0.28 es un buen equilibrio)
        self.velocidad_animacion = 0.28

        self.imagen = None
        self.cargar_imagen()

    def dibujar(self, pantalla):
        """Calcula el movimiento fluido y dibuja la pieza una sola vez."""
        destino_x = self.col * self.tam_cuadro
        destino_y = self.fila * self.tam_cuadro

        # Calculamos la distancia restante
        diff_x = destino_x - self.x
        diff_y = destino_y - self.y

        # SNAP AGRESIVO: Si falta menos de 1 píxel, saltar al destino
        # Esto elimina la sensación de lentitud al final.
        if abs(diff_x) < 1:
            self.x = destino_x
        else:
            self.x += diff_x * self.velocidad_animacion

        if abs(diff_y) < 1:
            self.y = destino_y
        else:
            self.y += diff_y * self.velocidad_animacion

        if self.imagen:
            pantalla.blit(self.imagen, (self.x, self.y))

    def __getstate__(self):
        """Prepara el objeto para ser clonado (Deep Copy)."""
        state = self.__dict__.copy()
        state["imagen"] = None  # No clonamos el objeto Surface
        return state

    def __setstate__(self, state):
        """Restaura el objeto tras ser clonado."""
        self.__dict__.update(state)
        self.cargar_imagen()

    def cargar_imagen(self):
        """Lógica de carga de imágenes con soporte PNG/JPG."""
        try:
            dir_clases = os.path.dirname(os.path.abspath(__file__))
            ruta_raiz = os.path.dirname(dir_clases)
            ruta_carpeta = os.path.join(ruta_raiz, "assets", "piezas_animadas")

            nombre_base = f"{self.nombre}_{self.color}"
            ruta_png = os.path.join(ruta_carpeta, f"{nombre_base}.png")
            ruta_jpg = os.path.join(ruta_carpeta, f"{nombre_base}.jpg")

            if os.path.exists(ruta_png):
                ruta_final = ruta_png
            elif os.path.exists(ruta_jpg):
                ruta_final = ruta_jpg
            else:
                raise FileNotFoundError(f"No se encontró {nombre_base}")

            imagen_temp = pygame.image.load(ruta_final).convert_alpha()

            if ruta_final.endswith(".jpg"):
                imagen_temp.set_colorkey((255, 255, 255))

            self.imagen = pygame.transform.smoothscale(
                imagen_temp, (self.tam_cuadro, self.tam_cuadro)
            )

        except Exception as e:
            print(f"Error cargando {self.nombre}_{self.color}: {e}")
            self.imagen = pygame.Surface((self.tam_cuadro, self.tam_cuadro))
            self.imagen.fill((255, 0, 255))
