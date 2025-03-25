import heapq
import numpy as np

# Parámetros heurísticos
ALPHA = 10
BETA = 1

class Estado:
    def __init__(self, matriz, diamantes_restantes, camino=[]):
        self.matriz = matriz
        self.diamantes_restantes = diamantes_restantes
        self.camino = camino  # lista de acciones tomadas

    def __lt__(self, otro):
        return self.costo_total() < otro.costo_total()

    def generar_sucesores(self):
        sucesores = []
        filas, cols = self.matriz.shape

        for i in range(filas):
            for j in range(cols):
                if self.matriz[i, j] == 1:  # Supón que 1 = diamante
                    nueva_matriz = self.matriz.copy()
                    nueva_matriz[i, j] = 0
                    nuevo_estado = Estado(
                        nueva_matriz,
                        self.diamantes_restantes - 1,
                        self.camino + [(i, j)]
                    )
                    sucesores.append(nuevo_estado)

        return sucesores

    def es_objetivo(self):
        return self.diamantes_restantes == 0

    def espacios_libres(self):
        return np.sum(self.matriz == 0)

    def heuristica(self):
        return ALPHA * self.diamantes_restantes + BETA * self.espacios_libres()

    def costo_total(self):
        return len(self.camino) + self.heuristica()  # g(n) + h(n)

def a_estrella(inicial):
    frontera = []
    heapq.heappush(frontera, (inicial.costo_total(), inicial))
    visitados = set()

    while frontera:
        _, actual = heapq.heappop(frontera)
        estado_hash = actual.matriz.tobytes()

        if estado_hash in visitados:
            continue

        visitados.add(estado_hash)

        if actual.es_objetivo():
            return actual.camino

        for sucesor in actual.generar_sucesores():
            heapq.heappush(frontera, (sucesor.costo_total(), sucesor))

    return None

# -------------------------
# Ejemplo de uso
# -------------------------
# 1 = diamante, 0 = espacio libre, -1 = obstáculo (si quisieras expandir)
matriz_inicial = np.array([
    [1, 0, 1],
    [0, 1, 0],
    [0, 0, 1]
])

estado_inicial = Estado(matriz_inicial, diamantes_restantes=np.sum(matriz_inicial == 1))
camino = a_estrella(estado_inicial)

print("Camino para recolectar todos los diamantes:", camino)
