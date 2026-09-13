import torch
import numpy as np
from ultralytics import YOLO
from typing import List
from pathlib import Path

class Detector:
    # Constantes
    DORSAL_ID = 1
    JUGADOR_ID = 2
    PELOTA_ID = 0
    IMG_SIZE = 1280
    CONFIANZA_MINIMA_DORSAL = 0.1
    CONFIANZA_MINIMA_JUGADOR = 0.7
    CONFIANZA_MINIMA_PELOTA = 0.7

    def __init__(self, model_path=None, device=None, img_size=IMG_SIZE, conf=CONFIANZA_MINIMA_DORSAL) -> None:
        # Si no se especifica un dispositivo, se elige GPU si está disponible
        if device is None:
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
        if model_path is None:
            directorio_base = Path(__file__).parent
            model_path = directorio_base / "best.pt"
            
        self.device = device

        self.model = YOLO(model=model_path, task='detect')

        self.img_size = img_size
        self.conf = conf

    def __obtener_clase__(cls, detecciones, numero_clase) -> tuple[List[tuple[float, float, float, float]], List[float]]:
        """Dada la salida de detección del modelo, devuelve una lista con los bounding boxes
        de la clase `numero_clase` detectados (x1, x2, y1, y2), y otra con las confianzas de cada uno."""

        bboxes = detecciones[0].boxes

        # Se crean las listas vacías para bboxes y confianzas
        bboxes_clase = []
        confianzas_clase = []

        # Se itera por cada detección
        for i in range(len(bboxes)):    
            # Si no pertenece a la clase indicada, se ignora
            class_bbox = bboxes.cls[i]
            if class_bbox != numero_clase:
                continue

            # Obtiene coordenas y confianza de la detección
            x1_bbox, y1_bbox, x2_bbox, y2_bbox = map(int, bboxes.xyxy[i].tolist())
            conf_bbox = float(bboxes.conf[i].item())

            # Se añade a las listas
            bboxes_clase.append((x1_bbox, x2_bbox, y1_bbox, y2_bbox))
            confianzas_clase.append(conf_bbox)

        return bboxes_clase, confianzas_clase

    def detectar_dorsales(self, img) -> tuple[List[tuple[float, float, float, float]], List[float]]:
        """Devuelve las listas de bounding boxes (x1, x2, y1, y2) y confianzas de los dorsales detectados en la imagen `img`."""

        # Obtener las detecciones del modelo
        resultados = self.model.predict(
            source=img, 
            imgsz=self.img_size, 
            conf=self.conf,
            device=self.device,
            verbose=False
        )

        # Devolver las listas de bounding boxes y confianzas de la clase de los dorsales
        return Detector.__obtener_clase__(self, detecciones=resultados, numero_clase=Detector.DORSAL_ID)
    
    def detectar_jugadores_data(self, img):
        """Devuelve dos arrays: el primero con los jugadores detectados (x1, x2, y1, y2, confianza, clase) y el segundo con las otras detecciones (x1, x2, y1, y2, confianza, clase)"""
        deteccion = self.model.predict(
            source=img, 
            imgsz=self.img_size, 
            conf=self.conf,
            device=self.device,
            verbose=False
        )
        
        deteccion = deteccion[0].boxes.data.cpu().numpy()

        if len(deteccion) == 0:
            return np.empty((0, 7)), np.empty((0, 6))
        else:
            # Jugadores con confianza >= CONFIANZA_MINIMA_JUGADOR
            mascara_jugador = deteccion[:, 5] == Detector.JUGADOR_ID
            deteccion_jugador = deteccion[mascara_jugador]
            deteccion_jugador = deteccion_jugador[deteccion_jugador[:, 4] >= Detector.CONFIANZA_MINIMA_JUGADOR]
            # No jugadores
            deteccion_no_jugador = deteccion[~mascara_jugador]

            return deteccion_jugador, deteccion_no_jugador
