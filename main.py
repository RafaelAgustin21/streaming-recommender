from pathlib import Path

from grafo import construir_grafo

from recomendador import (
    recomendar,
    mostrar_perfil_usuario
)


# --------------------------------------------
# Rutas del proyecto
# --------------------------------------------

BASE_DIR = (
    Path(__file__)
    .resolve()
    .parent
)

DATA_DIR = (
    BASE_DIR
    / "data"
    / "raw"
    / "ml-100k"
)

RUTA_DATA = (
    DATA_DIR
    / "u.data"
)

RUTA_ITEM = (
    DATA_DIR
    / "u.item"
)


def mostrar_recomendaciones(
    grafo,
    user_id
):

    try:

        recomendaciones = recomendar(
            grafo,
            user_id=user_id,
            cantidad=10,
            rating_minimo=4
        )

    except ValueError as error:

        print()
        print(error)

        return

    print()
    print(
        f"RECOMENDACIONES PARA "
        f"EL USUARIO {user_id}"
    )

    print(
        "=" * 55
    )

    if not recomendaciones:

        print(
            "No se encontraron "
            "recomendaciones."
        )

        return

    for posicion, pelicula in enumerate(
        recomendaciones,
        start=1
    ):

        generos = ", ".join(
            pelicula[
                "generos"
            ]
        )

        if not generos:
            generos = "Sin género"

        print()

        print(
            f"{posicion}. "
            f"{pelicula['titulo']}"
        )

        print(
            f"   Usuarios de apoyo: "
            f"{pelicula['usuarios_apoyo']}"
        )

        print(
            f"   Rating promedio positivo: "
            f"{pelicula['rating_promedio']:.2f}"
        )

        print(
            f"   Géneros: {generos}"
        )

        print(
            f"   Afinidad de género: "
            f"{pelicula['coincidencias_genero']}"
        )

        # ------------------------------------
        # Explicación del recorrido
        # ------------------------------------

        camino = pelicula[
            "ejemplo_camino"
        ]

        usuario_apoyo = pelicula[
            "ejemplo_usuario"
        ]

        if (
            camino is not None
            and usuario_apoyo is not None
        ):

            print(
                "   Ejemplo de ruta BFS:"
            )

            print(
                f"      Usuario {user_id}"
            )

            print(
                f"         ↓ "
                f"rating {camino['rating_objetivo']}"
            )

            print(
                f"      {camino['titulo']}"
            )

            print(
                f"         ↓ "
                f"rating {camino['rating_apoyo']}"
            )

            print(
                f"      Usuario {usuario_apoyo}"
            )

            print(
                "         ↓ "
                "preferencia positiva"
            )

            print(
                f"      "
                f"{pelicula['titulo']}"
            )


def main():

    # ----------------------------------------
    # Verificar archivos
    # ----------------------------------------

    if (
        not RUTA_DATA.exists()
        or not RUTA_ITEM.exists()
    ):

        print(
            "No se encontraron "
            "u.data y/o u.item."
        )

        print()
        print(
            "Los archivos deben estar en:"
        )

        print(
            DATA_DIR
        )

        return

    # ----------------------------------------
    # Construir grafo
    # ----------------------------------------

    print(
        "Cargando MovieLens 100K..."
    )

    grafo = construir_grafo(
        RUTA_DATA,
        RUTA_ITEM
    )

    print()
    print(
        "Grafo construido correctamente."
    )

    print()

    print(
        f"Usuarios: "
        f"{len(grafo.usuarios)}"
    )

    print(
        f"Películas: "
        f"{len(grafo.peliculas)}"
    )

    print(
        f"Nodos totales: "
        f"{grafo.cantidad_nodos()}"
    )

    print(
        f"Aristas de rating: "
        f"{grafo.cantidad_aristas()}"
    )

    # ----------------------------------------
    # Menú principal
    # ----------------------------------------

    while True:

        print()
        print(
            "=" * 45
        )

        print(
            " SISTEMA DE RECOMENDACIÓN "
            "MEDIANTE GRAFOS"
        )

        print(
            "=" * 45
        )

        print(
            "1. Ver perfil de un usuario"
        )

        print(
            "2. Generar recomendaciones"
        )

        print(
            "3. Ver perfil y recomendaciones"
        )

        print(
            "0. Salir"
        )

        print()

        opcion = input(
            "Seleccione una opción: "
        ).strip()

        if opcion == "0":

            print()
            print(
                "Programa finalizado."
            )

            break

        if opcion not in {
            "1",
            "2",
            "3"
        }:

            print(
                "Opción inválida."
            )

            continue

        entrada = input(
            "Ingrese ID de usuario "
            "(1-943): "
        ).strip()

        if not entrada.isdigit():

            print(
                "El ID debe ser numérico."
            )

            continue

        user_id = int(
            entrada
        )

        if user_id not in grafo.usuarios:

            print(
                f"El usuario {user_id} "
                f"no existe."
            )

            continue

        if opcion == "1":

            mostrar_perfil_usuario(
                grafo,
                user_id
            )

        elif opcion == "2":

            mostrar_recomendaciones(
                grafo,
                user_id
            )

        elif opcion == "3":

            mostrar_perfil_usuario(
                grafo,
                user_id
            )

            mostrar_recomendaciones(
                grafo,
                user_id
            )


if __name__ == "__main__":
    main()