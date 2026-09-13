import cv2 as cv
import numpy as np
from sklearn.cluster import KMeans

class ClasificadorEquipo:
    """Versión inicial del clasificador de equipos"""
    def __init__(self, crops_jugadores, equipo_A_BGR, equipo_B_BGR):
        """Inicializa el clasificador de equipos. Usa los colores del equipo A y B para asignar el cluster más cercano a cada color a ese equipo, de modo que al clasificar un jugador se sepa si pertenece al equipo A o al B.
        
        Necesita crops de los jugadores porque entrena un kmeans con las características de los crops."""

        print("Entrenando el clasificador de equipos...")

        # Obtener parte del torso de cada crop
        crops_torso = []
        for crop in crops_jugadores:
            torso = self.__obtener_torso(crop)
            crops_torso.append(torso)
        
        # Extraer características de cada torso
        features_torso = []
        for crop in crops_torso:
            features_torso.append(self.__extraer_caracteristicas(crop))
        
        # Entrenar kmeans de 2 equipos
        self.kmeans = KMeans(n_clusters=2, random_state=0).fit(features_torso)

        # Almacenar los centros de cada cluster
        self.centro_cluster_0 = self.kmeans.cluster_centers_[0]
        self.centro_cluster_1 = self.kmeans.cluster_centers_[1]

        # Guardar los colores de los uniformes de cada equipo y establecer qué equipo corresponde a cada cluster
        self.equipo_A_BGR = equipo_A_BGR
        self.equipo_B_BGR = equipo_B_BGR

        self.asignacion_equipos = self.__asignar_equipo_a_cluster()

        print("El clasificador de equipos ya está entrenado")

    def __asignar_equipo_a_cluster(self) -> dict[int, str]:
        """Asigna un equipo a cada cluster basándose en la distancia de los centros de cada cluster a los colores medios de cada equipo."""
        # Distancia de cada punto central del cluster a los colores de cada uniforme de equipo
        distancia_cluster_0_a_equipo_A = np.linalg.norm(self.centro_cluster_0[:3] - self.equipo_A_BGR)
        distancia_cluster_0_a_equipo_B = np.linalg.norm(self.centro_cluster_0[:3] - self.equipo_B_BGR)

        distancia_cluster_1_a_equipo_A = np.linalg.norm(self.centro_cluster_1[:3] - self.equipo_A_BGR)
        distancia_cluster_1_a_equipo_B = np.linalg.norm(self.centro_cluster_1[:3] - self.equipo_B_BGR)

        # Suma distancias de asociaciones c0-A c1-B, y c0-B c1-A, y se asigna la que tenga menor distancia total
        distancia_total_0_A_1_B = distancia_cluster_0_a_equipo_A + distancia_cluster_1_a_equipo_B
        distancia_total_0_B_1_A = distancia_cluster_0_a_equipo_B + distancia_cluster_1_a_equipo_A

        if distancia_total_0_A_1_B < distancia_total_0_B_1_A:
            return {0: "A", 1: "B"}
        else:
            return {0: "B", 1: "A"}


    def __obtener_torso(self, imagen):
        """Devuelve la parte del torso de una imagen de un jugador, asumiendo que se ve al jugador entero.
        
        Se devuelve la anchura de 20% a 80%, y la altura de 15% a 85%."""
        # Alto y ancho de la imagen
        h, w = imagen.shape[:2]

        # Coordenadas del torso
        x1_t = int(0.20 * w)
        x2_t = int(0.80 * w)
        y1_t = int(0.15 * h)
        y2_t = int(0.85 * h)

        return imagen[y1_t:y2_t, x1_t:x2_t]
    
    def __extraer_caracteristicas(self, imagen_torso):
        """Extrae las características de una imagen de un uniforme del jugador. Obtiene el color medio, máximo, y desviación estándar."""
        # Color medio, desviación estándar, y color máximo
        mean_color = np.mean(imagen_torso.reshape(-1, 3), axis=0)
        std_color = np.std(imagen_torso.reshape(-1, 3), axis=0)
        max_color = np.max(imagen_torso.reshape(-1, 3), axis=0)

        # Concatenar todo para obtener el vector de características final
        features = np.concatenate((mean_color, std_color, max_color))
        return features

    def clasificar(self, imagen):
        # Obtener las características
        features = self.__extraer_caracteristicas(self.__obtener_torso(imagen))
        # Predecir el cluster
        cluster = self.kmeans.predict([features])[0]
        # Devolver el equipo asignado al cluster
        return self.asignacion_equipos[cluster]

    def clasificar_crops(self, crops):
        # Obtener las características
        features = [self.__extraer_caracteristicas(self.__obtener_torso(crop)) for crop in crops]
        # Predecir el cluster
        clusters = self.kmeans.predict(features)
        # Obtener el equipo asignado a cada cluster
        return [self.asignacion_equipos[cluster] for cluster in clusters]