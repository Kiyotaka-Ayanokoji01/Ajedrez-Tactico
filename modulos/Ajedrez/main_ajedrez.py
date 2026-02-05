from clases.juego import Juego


def main():

    print("--- Aplicación de Ajedrez Educativa Iniciada ---")

    while True:
        try:
            # Crear una nueva partida
            partida = Juego()

            # Ejecutar la partida
            partida.iniciar_partida()

        except ImportError as e:
            print(f"\nERROR: No se pudo encontrar el módulo 'juego'. Detalles: {e}")
            print(
                "Asegúrate de que 'clases/juego.py' y los archivos '__init__.py' existan."
            )
            break
        except AttributeError as e:
            print(
                f"\nERROR: La clase 'Juego' no tiene un método 'iniciar_partida()'. Detalles: {e}"
            )
            print("Asegúrate de definir este método para comenzar el juego.")
            break
        except RuntimeError as e:
            print(f"\nOcurrió un error de ejecución al iniciar el juego: {e}")
            break

        # Preguntar al usuario si desea jugar otra partida
        respuesta = input("\n¿Deseas jugar otra partida? (s/n): ").strip().lower()
        if respuesta != "s":
            print("\nGracias por jugar. ¡Hasta la próxima!")
            break

    print("--- Aplicación de Ajedrez Finalizada ---")


if __name__ == "__main__":
    main()
