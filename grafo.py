GENEROS = [
    "unknown",
    "Action",
    "Adventure",
    "Animation",
    "Children's",
    "Comedy",
    "Crime",
    "Documentary",
    "Drama",
    "Fantasy",
    "Film-Noir",
    "Horror",
    "Musical",
    "Mystery",
    "Romance",
    "Sci-Fi",
    "Thriller",
    "War",
    "Western"
]


class GrafoStreaming:
    """
    Grafo bipartito no dirigido:

        Usuario <---- rating ----> Pelicula

    Se representa mediante una lista de adyacencia.
    """

    def __init__(self):

        # Lista de adyacencia
        # nodo -> [(vecino, rating), ...]
        self.ady = {}

        # Tipo del nodo:
        # "usuario" o "pelicula"
        self.tipo = {}

        # Información de películas
        # movie_id -> {
        #     "titulo": ...,
        #     "generos": set(...)
        # }
        self.peliculas = {}

        # Ratings agrupados por usuario
        # user_id -> {
        #     movie_id: rating
        # }
        self.ratings_usuario = {}

        # IDs de usuarios encontrados
        self.usuarios = set()

    def agregar_nodo(self, nodo, tipo):

        if nodo not in self.ady:
            self.ady[nodo] = []
            self.tipo[nodo] = tipo

    def agregar_arista(self, nodo1, nodo2, rating):
        """
        Como el grafo es no dirigido,
        guardamos la relación en ambos sentidos.
        """

        self.ady[nodo1].append(
            (nodo2, rating)
        )

        self.ady[nodo2].append(
            (nodo1, rating)
        )

    def vecinos(self, nodo):

        return self.ady.get(
            nodo,
            []
        )

    def cantidad_nodos(self):

        return len(
            self.ady
        )

    def cantidad_aristas(self):

        # Cada relación aparece dos veces:
        # U -> M
        # M -> U
        #
        # Por eso dividimos entre 2.

        total = sum(
            len(vecinos)
            for vecinos in self.ady.values()
        )

        return total // 2

    def titulo_pelicula(self, movie_id):

        if movie_id not in self.peliculas:
            return f"Película {movie_id}"

        return self.peliculas[
            movie_id
        ]["titulo"]

    def generos_pelicula(self, movie_id):

        if movie_id not in self.peliculas:
            return set()

        return self.peliculas[
            movie_id
        ]["generos"]


def cargar_peliculas(ruta_item):
    """
    Lee el archivo u.item de MovieLens 100K.

    Cada película contiene:
    - ID
    - título
    - fecha
    - URL IMDb
    - 19 indicadores de género
    """

    peliculas = {}

    # MovieLens 100K utiliza latin-1.
    with open(
        ruta_item,
        "r",
        encoding="latin-1"
    ) as archivo:

        for linea in archivo:

            campos = (
                linea
                .rstrip("\n")
                .split("|")
            )

            if len(campos) < 24:
                continue

            movie_id = int(
                campos[0]
            )

            titulo = campos[1]

            # Posiciones 5 hasta 23:
            # 19 indicadores de género.
            indicadores_genero = campos[5:24]

            generos = set()

            for i, valor in enumerate(
                indicadores_genero
            ):

                if (
                    valor == "1"
                    and GENEROS[i] != "unknown"
                ):
                    generos.add(
                        GENEROS[i]
                    )

            peliculas[movie_id] = {
                "titulo": titulo,
                "generos": generos
            }

    return peliculas


def construir_grafo(
    ruta_data,
    ruta_item
):
    """
    Construye el grafo completo
    utilizando u.data y u.item.
    """

    grafo = GrafoStreaming()

    # ----------------------------------------
    # 1. Cargar películas
    # ----------------------------------------

    grafo.peliculas = cargar_peliculas(
        ruta_item
    )

    for movie_id in grafo.peliculas:

        nodo_pelicula = (
            f"M{movie_id}"
        )

        grafo.agregar_nodo(
            nodo_pelicula,
            "pelicula"
        )

    # ----------------------------------------
    # 2. Cargar ratings
    # ----------------------------------------

    with open(
        ruta_data,
        "r",
        encoding="utf-8"
    ) as archivo:

        for linea in archivo:

            datos = (
                linea
                .strip()
                .split("\t")
            )

            user_id = int(
                datos[0]
            )

            movie_id = int(
                datos[1]
            )

            rating = int(
                datos[2]
            )

            nodo_usuario = (
                f"U{user_id}"
            )

            nodo_pelicula = (
                f"M{movie_id}"
            )

            grafo.agregar_nodo(
                nodo_usuario,
                "usuario"
            )

            grafo.agregar_nodo(
                nodo_pelicula,
                "pelicula"
            )

            grafo.agregar_arista(
                nodo_usuario,
                nodo_pelicula,
                rating
            )

            grafo.usuarios.add(
                user_id
            )

            if user_id not in grafo.ratings_usuario:

                grafo.ratings_usuario[
                    user_id
                ] = {}

            grafo.ratings_usuario[
                user_id
            ][movie_id] = rating

    return grafo