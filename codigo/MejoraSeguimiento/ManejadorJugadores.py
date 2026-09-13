from typing import List
from Jugador import Jugador
from EstadoTrack import EstadoTrack
from typing import Dict
import math
import pandas as pd

class ManejadorJugadores:

    def __init__(self, numeros_jugadores_A: List[int], numeros_jugadores_B: List[int], max_dist_asociacion=1000):
        # Jugadores
        self.numeros_jugadores_A = numeros_jugadores_A
        self.numeros_jugadores_B = numeros_jugadores_B
        self.jugadores = [Jugador(numero, "A") for numero in numeros_jugadores_A] + [Jugador(numero, "B") for numero in numeros_jugadores_B]
        # Tracks
        self.tracks:Dict[int, EstadoTrack] = {}
        # Parámetros de configuración
        self.dist_max_asociacion = max_dist_asociacion # Distancia máxima en píxeles entre el último sitio donde se vio al jugador y el centro del bounding box del track para considerarlos asociados
    
    def actualizar_con_equipo(self, track_ids: List[int], numeros_detectados: List[int], equipos_detectados: List[str], frame_actual: int, bounding_boxes: List[tuple]):
        """Actualiza la asociación entre track_ids y jugadores basándose en los números de dorsales y equipos detectados en el frame actual, y en los equipos de estos tracks"""

        # Actualiza los tracks actuales con el número y el equipo detectados
        for (track_id, numero, equipo) in zip(track_ids, numeros_detectados, equipos_detectados):
            # Añade el track si es nuevo
            if track_id not in self.tracks:
                self.tracks[track_id] = EstadoTrack(track_id = track_id)
            # Obtiene el número y se asegura que es válido
            numero_int = int(numero) if numero is not None else None
            if numero_int not in self.numeros_jugadores_A + self.numeros_jugadores_B:
                numero_int = None
            # Actualiza el track
            self.tracks[track_id].update(numero_int, equipo)

        
        jugadores_bien = set()
        jugadores_sin_numero_track = set()
        jugadores_sin_equipo_track = set()
        jugadores_sin_numero_equipo_track = set()
        jugadores_mal = set()

        # Clasifica las asociaciones actuales entre jugadores y tracks:
        """
        - 1. No track asociado a jugador --> mal
        - 2. Track asociado a jugador pero no visto en N_FRAMES frames --> mal
        - 3. Número asociado a track diferente al del jugador --> mal
        - 4. Equipo asociado a track diferente al del jugador --> mal
        - 5. Sin número asociado a track asociado al jugador, y el equipo coincide--> Lista especial "sin numero"
        - 6. Con número asociado a track y es igual al jugador, y el equipo también coincide --> Bien
        - 7. Número asociado coincide, pero el equipo no asociado --> Lista especial "sin número asociado"
        - 8. Número no asociado a track, equipo no asociado a track--> Lista especial "sin número equipo asociado"
        """
        for jugador in self.jugadores:
            # 1
            if jugador.track_id is None:
                jugadores_mal.add(jugador)
                continue
            estadoTrack = self.tracks[jugador.track_id]
            # 3
            if estadoTrack.current_number is not None and estadoTrack.current_number != jugador.numero:
                jugadores_mal.add(jugador)
                jugador.asociar_track_id(None)
                continue
            
            if estadoTrack.current_team is None:
                # 8
                if estadoTrack.current_number is None:
                    jugadores_sin_numero_equipo_track.add(jugador)
                    continue
                # 7
                elif estadoTrack.current_number == jugador.numero:
                    jugadores_sin_equipo_track.add(jugador)
                    continue
            
            # 4
            elif estadoTrack.current_team != jugador.equipo:
                jugadores_mal.add(jugador)
                jugador.asociar_track_id(None)
                continue

            # 5
            if estadoTrack.current_number is None:
                jugadores_sin_numero_track.add(jugador)
                continue
            # 6
            elif estadoTrack.current_number == jugador.numero:
                jugadores_bien.add(jugador)
                continue


        # Se crea un DataFrame con tracks
        def trackid_asociado_a_jugador(track_id: int) -> bool:
            """Devuelve un booleano indicando si el track_id está asociado a algún jugador."""
            for jugador in self.jugadores:
                if jugador.track_id == track_id:
                    return True
            return False
        
        def trackid_bien_asociado(track_id: int) -> str:
            """Devuelve "si" si el track_id está bien asociado a un jugador, "no" si está mal asociado (número o equipo no coinciden) y "?" si no está asociado."""
            for jugador in self.jugadores:
                if jugador.track_id == track_id:
                    estadoTrack = self.tracks[track_id]
                    if estadoTrack.current_team is not None and estadoTrack.current_number != jugador.numero:
                        return "no"
                    if estadoTrack.current_team is not None and estadoTrack.current_team != jugador.equipo:
                        return "no"
                    return "si"
            return "?"
        
        # Se calcula el centro de los bounding boxes de los tracks del frame actual
        centros = {}
        for track_id, (x1, y1, x2, y2) in zip(track_ids, bounding_boxes):
            x = x1 + (x2 - x1) // 2
            y = y1 + (y2 - y1) // 2
            centros[track_id] = (x, y)
        
        # Se crea el DataFrame
        df_tracks = []
        for track_id in track_ids:
                estadoTrack = self.tracks[track_id]
                df_tracks.append({
                    "track_id": track_id,
                    "asociado": trackid_asociado_a_jugador(track_id), # True o False
                    "numero": estadoTrack.current_number, # int o None
                    "equipo": estadoTrack.current_team if estadoTrack.current_team is not None else "?", # "A", "B" o "?"
                    "bien_asociado": trackid_bien_asociado(track_id),  # "si", "no" o "?"
                    "x": centros[track_id][0],
                    "y": centros[track_id][1]
                })
        df_tracks = pd.DataFrame(df_tracks)

        if df_tracks.empty:
            return [], [] # Si no hay tracks en el frame actual, no se puede asociar nada, así que se devuelve vacío
        
        # Buscamos los tracks con número y equipo no asociados que sean iguales a jugadores no asociados
        def asociar_trackid_a_jugador(trackdf: pd.DataFrame, jugador: Jugador, track_id: int):
            """Asocia el track_id al jugador, marcando el track como asociado y bien asociado. Quita el jugador de jugadores_mal y lo añade a jugadores_bien."""
            jugador.asociar_track_id(track_id)
            trackdf.at[track_id, "asociado"] = True
            trackdf.at[track_id, "bien_asociado"] = "si"
            jugadores_mal.discard(jugador)
            jugadores_bien.add(jugador)

        jugadores_mal_copia = jugadores_mal.copy()
        for jugador in jugadores_mal_copia:
            # Buscar track en df_tracks con número y equipo igual al jugador, y que no esté asociado a ningún jugador
            candidatos = df_tracks[
                (df_tracks["numero"].notna()) &
                (df_tracks["numero"] == jugador.numero) &
                (df_tracks["equipo"] == jugador.equipo) &
                (~df_tracks["asociado"])
            ]
            if len(candidatos) == 0:
                continue

            # Si hay varios candidatos, elegir el más cercano al último sitio donde se vio al jugador
            jx, jy = jugador.x, jugador.y
            if jx is None or jy is None:
                candidato = candidatos.iloc[0]
                asociar_trackid_a_jugador(df_tracks, jugador, candidato.track_id)
                continue

            candidatos = candidatos.assign(dist=((candidatos["x"] - jx)**2 + (candidatos["y"] - jy)**2)**0.5)
            candidato = candidatos.sort_values("dist").iloc[0]
            asociar_trackid_a_jugador(df_tracks, jugador, candidato.track_id)

        # Buscamos los tracks sin equipo pero con número no asociados que sean iguales a jugadores mal asociados
        jugadores_mal_copia = jugadores_mal.copy()
        for jugador in jugadores_mal_copia:
            # Si existe ese número en el equipo contrario, no se puede asociar ese número a este jugador
            if jugador.equipo is "A" and jugador.numero in self.numeros_jugadores_B:
                continue
            if jugador.equipo is "B" and jugador.numero in self.numeros_jugadores_A:
                continue

            candidatos = df_tracks[
                (df_tracks["numero"].notna()) &
                (df_tracks["numero"] == jugador.numero) &
                (df_tracks["equipo"] == "?") &
                (~df_tracks["asociado"])
            ]
            if len(candidatos) == 0:
                continue
            # Si hay varios candidatos, elegir el más cercano al último sitio donde se vio al jugador
            jx, jy = jugador.x, jugador.y
            if jx is None or jy is None:
                candidato = candidatos.iloc[0]
                asociar_trackid_a_jugador(df_tracks, jugador, candidato.track_id)
                continue

            candidatos = candidatos.assign(dist=((candidatos["x"] - jx)**2 + (candidatos["y"] - jy)**2)**0.5)
            candidato = candidatos.sort_values("dist").iloc[0]
            asociar_trackid_a_jugador(df_tracks, jugador, candidato.track_id)

        # Si sólo queda 1 jugador mal asociado y 1 track visto en este frame sin asociar y de ese equipo, los asocia aunque no tenga número
        # Comprueba que hay un jugador (y solo uno) de cada equipo mal asociado
        jugadores_mal_A = [jugador for jugador in jugadores_mal if jugador.equipo == "A"]
        jugadores_mal_B = [jugador for jugador in jugadores_mal if jugador.equipo == "B"]

        jugadores_mal_asociables = []
        if len(jugadores_mal_A) == 1:
            jugadores_mal_asociables.append(jugadores_mal_A[0])
        if len(jugadores_mal_B) == 1:
            jugadores_mal_asociables.append(jugadores_mal_B[0])

        for jugador in jugadores_mal_asociables:
            candidatos = df_tracks[
                (df_tracks["equipo"] == jugador.equipo) &
                (~df_tracks["asociado"] &
                 (df_tracks["numero"].isna()))
            ]
            if len(candidatos) == 1:
                candidato = candidatos.iloc[0]
                asociar_trackid_a_jugador(df_tracks, jugador, candidato.track_id)

        # Si un jugador no se ha visto en este frame y existe un track con ese número y equipo asociado de este frame, lo asocia
        for jugador in self.jugadores:
            track_asociado = jugador.track_id
            if track_asociado is not None and track_asociado not in track_ids:
                candidatos = df_tracks[
                    (df_tracks["numero"] == jugador.numero) &
                    (df_tracks["equipo"] == jugador.equipo) &
                    (~df_tracks["asociado"])
                ]
                if len(candidatos) == 1:
                    candidato = candidatos.iloc[0]
                    jugador.asociar_track_id(candidato.track_id)
                    # Añadir a jugadores_bien si aún no estaba, y quitar de jugadores_mal si estaba
                    jugadores_bien.add(jugador)
                    jugadores_mal.discard(jugador)
                    jugadores_sin_numero_track.discard(jugador)
                    jugadores_sin_equipo_track.discard(jugador)
                    jugadores_sin_numero_equipo_track.discard(jugador)
                    # Marcar el track como asociado y bien asociado
                    df_tracks.at[candidato.track_id, "asociado"] = True
                    df_tracks.at[candidato.track_id, "bien_asociado"] = "si"
        
        # Actualiza los jugadores vistos en el frame actual
        for (track_id, bounding_box) in zip(track_ids, bounding_boxes):
            for jugador in jugadores_bien.union(jugadores_sin_numero_track).union(jugadores_sin_equipo_track).union(jugadores_sin_numero_equipo_track):
                if jugador.track_id == track_id:
                    x1, y1, x2, y2 = bounding_box
                    x = x1 + (x2 - x1) // 2
                    y = y1 + (y2 - y1) // 2
                    # Guardar el centro base del bounding box como última posición vista del jugador
                    jugador.actualizar_ultimo_frame_visto(frame_actual, x, y)
        
        # Devolver los jugadores asociados y los tracks asociados en el mismo orden
        tracks_bien_ordenados = []
        jugadores_ordenados = []
        for jugador in jugadores_bien:
            track_id = jugador.track_id
            track = self.tracks[track_id]
            tracks_bien_ordenados.append(track)
            jugadores_ordenados.append(jugador)
        return jugadores_ordenados, tracks_bien_ordenados
    
    def devolver_jugadores(self):
        """Devuelve los jugadores"""
        return self.jugadores