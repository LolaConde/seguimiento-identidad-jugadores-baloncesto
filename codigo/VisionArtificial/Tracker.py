from ultralytics import YOLO
from boxmot import BotSort
from pathlib import Path
import torch
import numpy as np

PATH_MODELO_DETECCION = r"./modelo-deteccion.engine"
CONFIANZA_JUGADORES_DETECCION = 0.6

class Tracker:
    def __init__(self, device = None):
        # Modelo de detección de jugadores
        directorio_base = Path(__file__).parent
        model_path = directorio_base / "modelo-deteccion.engine"
        self.modelo = YOLO(model_path)

        # Si no se especifica un dispositivo, se elige GPU si está disponible
        if device is None:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        else:
            self.device = device

        # Inicializar el tracker de BoxMOT
        # Configuración botsort
        self.tracker = BotSort(
            track_high_thresh = 0.6,
            track_low_thresh = 0.45,
            new_track_thresh = 0.7,
            track_buffer = 120,
            match_thresh = 0.9,
            fuse_score = True,
            gmc_method = "sparseOptFlow",
            proximity_thresh = 0.3,
            appearance_thresh=0.08,
            with_reid=True,
            model_weights=Path("osnet_x0_25_msmt17.pt"),
            reid_weights=Path("osnet_x0_25_msmt17.pt"),
            device="cuda:0",
            half=False,
        )
        
    def actualizar(self, frame):
        """Detecta a  los jugadores en el frame actual `frame`, actualiza el tracker, y devuelve los tracks del frame actual."""
        # Usa el modelo self.modelo para detectar los jugadores en el frame actual. No se utilizan las bboxes que se pasan como parámetro
        resultado_deteccion = self.modelo(frame, classes=[0], conf=CONFIANZA_JUGADORES_DETECCION, verbose=False, device=self.device)

        deteccion = resultado_deteccion[0].boxes.data.cpu().numpy()

        if len(deteccion) == 0:
            bboxes_jugadores = np.empty((0, 7)), np.empty((0, 6))
        else:
            # Jugadores con confianza >= CONFIANZA_MINIMA_JUGADOR
            mascara_jugador = deteccion[:, 5] == 0
            deteccion_jugador = deteccion[mascara_jugador]
            bboxes_jugadores = deteccion_jugador[deteccion_jugador[:, 4] >= CONFIANZA_JUGADORES_DETECCION]

        # Si se han detectado personas
        if resultado_deteccion[0].boxes is not None and len(resultado_deteccion[0].boxes) > 0:
            # Detecciones
            detecciones = np.array(resultado_deteccion[0].boxes.data.tolist())
            
            # Actualiza tracker (obtiene tracks en frame actual)
            tracks_actual = self.tracker.update(detecciones, frame)

            return tracks_actual, bboxes_jugadores
        else:
            return [], bboxes_jugadores
    
    def obtener_bbox_track(cls, track) -> tuple[int, int, int, int]:
        """Dado un track de BoxMOT, devuelve su bounding box en formato (bb_left, bb_top, bb_right, bb_bottom)"""
        bb_left, bb_top, bb_right, bb_bottom, _, _, _, _ = track
        return int(bb_left), int(bb_top), int(bb_right), int(bb_bottom)
    
    def obtener_id_track(cls, track) -> int:
        """Dado un track de BoxMOT, devuelve su ID"""
        _, _, _, _, track_id, _, _, _ = track
        return int(track_id)
    
    def obtener_confianza_track(cls, track) -> float:
        """Dado un track de BoxMOT, devuelve su confianza"""
        _, _, _, _, _, conf, _, _ = track
        return float(conf)