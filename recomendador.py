from collections import deque
from collections import defaultdict


def obtener_generos_preferidos(
    grafo,
    user_id,
    rating_minimo=4
):
    """
    Obtiene los géneros que aparecen
    con mayor frecuencia entre las películas
    calificadas positivamente por el usuario.
    """

    conteo = defaultdict(int)

    ratings = grafo.ratings_usuario.get(
        user_id,
        {}
    )

    for movie_id, rating in ratings.items():

        if rating >= rating_minimo:

            generos = (
                grafo.generos_pelicula(
                    movie_id
                )
            )

            for genero in generos:

                conteo[genero] += 1

    return conteo


def obtener_peliculas_favoritas(
    grafo,
    user_id,
    rating_minimo=4
):
    """
    Devuelve las películas que el usuario
    calificó con rating >= rating_minimo.
    """

    favoritas = []

    ratings = grafo.ratings_usuario.get(
        user_id,
        {}
    )

    for movie_id, rating in ratings.items():

        if rating >= rating_minimo:

            favoritas.append({
                "movie_id": movie_id,

                "titulo":
                    grafo.titulo_pelicula(
                        movie_id
                    ),

                "rating":
                    rating,

                "generos":
                    sorted(
                        grafo.generos_pelicula(
                            movie_id
                        )
                    )
            })

    # Primero mostramos las de rating más alto
    # y luego orden alfabético.
    favoritas.sort(
        key=lambda pelicula: (
            -pelicula["rating"],
            pelicula["titulo"]
        )
    )

    return favoritas


def mostrar_perfil_usuario(
    grafo,
    user_id,
    cantidad_peliculas=10
):
    """
    Imprime un pequeño resumen
    de las preferencias del usuario.
    """

    if user_id not in grafo.ratings_usuario:

        print(
            f"El usuario {user_id} no existe."
        )

        return

    ratings = (
        grafo.ratings_usuario[
            user_id
        ]
    )

    positivas = obtener_peliculas_favoritas(
        grafo,
        user_id,
        rating_minimo=4
    )

    generos = obtener_generos_preferidos(
        grafo,
        user_id,
        rating_minimo=4
    )

    print()
    print(
        f"PERFIL DEL USUARIO {user_id}"
    )
    print(
        "=" * 45
    )

    print(
        f"Películas calificadas: "
        f"{len(ratings)}"
    )

    print(
        f"Películas con rating 4 o 5: "
        f"{len(positivas)}"
    )

    print()
    print(
        "Algunas películas que le gustaron:"
    )

    for pelicula in positivas[
        :cantidad_peliculas
    ]:

        generos_texto = ", ".join(
            pelicula["generos"]
        )

        if not generos_texto:
            generos_texto = "Sin género"

        print(
            f"  - {pelicula['titulo']} "
            f"[{pelicula['rating']}/5]"
        )

        print(
            f"    Géneros: "
            f"{generos_texto}"
        )

    print()
    print(
        "Géneros predominantes:"
    )

    generos_ordenados = sorted(
        generos.items(),
        key=lambda elemento:
            elemento[1],
        reverse=True
    )

    for genero, cantidad in generos_ordenados[:5]:

        print(
            f"  - {genero}: "
            f"{cantidad} películas"
        )


def bfs_candidatos(
    grafo,
    user_id,
    rating_minimo=4,
    profundidad_maxima=3
):
    """
    BFS sobre relaciones positivas.

    Nivel 0:
        usuario objetivo

    Nivel 1:
        películas que calificó >= 4

    Nivel 2:
        otros usuarios que también
        calificaron positivamente
        esas películas

    Nivel 3:
        películas candidatas
    """

    inicio = f"U{user_id}"

    if inicio not in grafo.ady:

        raise ValueError(
            f"El usuario {user_id} "
            f"no existe en el grafo."
        )

    visitado = {
        inicio
    }

    distancia = {
        inicio: 0
    }

    cola = deque([
        inicio
    ])

    candidatos = defaultdict(
        lambda: {
            "usuarios": set(),
            "ratings": []
        }
    )

    while cola:

        actual = cola.popleft()

        nivel = distancia[
            actual
        ]

        if nivel >= profundidad_maxima:
            continue

        for vecino, rating in grafo.vecinos(
            actual
        ):

            # Solamente recorremos
            # relaciones positivas.
            if rating < rating_minimo:
                continue

            nuevo_nivel = (
                nivel + 1
            )

            if vecino not in visitado:

                visitado.add(
                    vecino
                )

                distancia[
                    vecino
                ] = nuevo_nivel

                cola.append(
                    vecino
                )

            # Una película del nivel 3
            # puede ser candidata.
            if (
                nuevo_nivel == 3
                and vecino.startswith("M")
                and actual.startswith("U")
            ):

                movie_id = int(
                    vecino[1:]
                )

                peliculas_vistas = (
                    grafo
                    .ratings_usuario
                    .get(
                        user_id,
                        {}
                    )
                )

                # No recomendamos películas
                # que el usuario ya calificó.
                if movie_id in peliculas_vistas:
                    continue

                usuario_apoyo = int(
                    actual[1:]
                )

                candidatos[
                    movie_id
                ]["usuarios"].add(
                    usuario_apoyo
                )

                candidatos[
                    movie_id
                ]["ratings"].append(
                    rating
                )

    return candidatos


def encontrar_pelicula_compartida(
    grafo,
    user_id,
    usuario_apoyo,
    rating_minimo=4
):
    """
    Busca una película que tanto el usuario
    objetivo como un usuario de apoyo
    hayan calificado positivamente.

    Esto nos permite explicar una recomendación.
    """

    ratings_objetivo = (
        grafo.ratings_usuario.get(
            user_id,
            {}
        )
    )

    ratings_apoyo = (
        grafo.ratings_usuario.get(
            usuario_apoyo,
            {}
        )
    )

    peliculas_compartidas = []

    for movie_id, rating_objetivo in (
        ratings_objetivo.items()
    ):

        if rating_objetivo < rating_minimo:
            continue

        rating_apoyo = (
            ratings_apoyo.get(
                movie_id
            )
        )

        if (
            rating_apoyo is not None
            and rating_apoyo >= rating_minimo
        ):

            peliculas_compartidas.append(
                (
                    movie_id,
                    rating_objetivo,
                    rating_apoyo
                )
            )

    if not peliculas_compartidas:
        return None

    # Escogemos una coincidencia fuerte.
    peliculas_compartidas.sort(
        key=lambda elemento: (
            elemento[1]
            + elemento[2]
        ),
        reverse=True
    )

    movie_id, rating_obj, rating_apoyo = (
        peliculas_compartidas[0]
    )

    return {
        "movie_id": movie_id,

        "titulo":
            grafo.titulo_pelicula(
                movie_id
            ),

        "rating_objetivo":
            rating_obj,

        "rating_apoyo":
            rating_apoyo
    }


def recomendar(
    grafo,
    user_id,
    cantidad=10,
    rating_minimo=4
):
    """
    Genera recomendaciones utilizando:

    1. BFS
    2. cantidad de usuarios de apoyo
    3. rating promedio
    4. coincidencia de género
    """

    candidatos = bfs_candidatos(
        grafo,
        user_id,
        rating_minimo=rating_minimo,
        profundidad_maxima=3
    )

    preferencias_genero = (
        obtener_generos_preferidos(
            grafo,
            user_id,
            rating_minimo
        )
    )

    resultados = []

    for movie_id, info in (
        candidatos.items()
    ):

        ratings = info[
            "ratings"
        ]

        usuarios = info[
            "usuarios"
        ]

        usuarios_apoyo = len(
            usuarios
        )

        promedio = (
            sum(ratings)
            / len(ratings)
        )

        generos = (
            grafo.generos_pelicula(
                movie_id
            )
        )

        coincidencias_genero = 0

        for genero in generos:

            coincidencias_genero += (
                preferencias_genero.get(
                    genero,
                    0
                )
            )

        # Guardamos un usuario de apoyo
        # para explicar después la ruta.
        ejemplo_usuario = None
        ejemplo_camino = None

        if usuarios:

            ejemplo_usuario = next(
                iter(usuarios)
            )

            ejemplo_camino = (
                encontrar_pelicula_compartida(
                    grafo,
                    user_id,
                    ejemplo_usuario,
                    rating_minimo
                )
            )

        resultados.append({

            "movie_id":
                movie_id,

            "titulo":
                grafo.titulo_pelicula(
                    movie_id
                ),

            "generos":
                sorted(generos),

            "usuarios_apoyo":
                usuarios_apoyo,

            "rating_promedio":
                promedio,

            "coincidencias_genero":
                coincidencias_genero,

            "ejemplo_usuario":
                ejemplo_usuario,

            "ejemplo_camino":
                ejemplo_camino
        })

    # El orden coincide con la propuesta
    # del informe:
    #
    # 1. cantidad de usuarios de apoyo
    # 2. rating promedio
    # 3. coincidencia de género

    resultados.sort(
        key=lambda pelicula: (
            pelicula[
                "usuarios_apoyo"
            ],

            pelicula[
                "rating_promedio"
            ],

            pelicula[
                "coincidencias_genero"
            ]
        ),
        reverse=True
    )

    return resultados[:cantidad]