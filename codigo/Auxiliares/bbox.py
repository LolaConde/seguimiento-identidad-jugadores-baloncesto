""""Funciones auxiliares para trabajar con bounding boxes."""

def center_inside(caja_interna, caja_externa):
    """Devuelve un booleano que indica si el centro del bounding box `caja_interna` está dentro del bounding box `caja_externa`."""
    # Obtiene las coordenadas de las cajas
    x1_i, y1_i, x2_i, y2_i = caja_interna
    x1_e, y1_e, x2_e, y2_e = caja_externa

    # Obtiene el centro de la caja interna
    cx_i = (x1_i + x2_i) / 2.0
    cy_i = (y1_i + y2_i) / 2.0

    # Si el centro de la caja interna (en x e y) está dentro de la caja externa
    dentro = (x1_e <= cx_i <= x2_e) and (y1_e <= cy_i <= y2_e)
    
    return dentro

def recortar_bbox(frame, bbox):
    """Recorta el bounding box `bbox` del frame `frame`.
     
    Se asegura que las coordenadas estén dentro de los límites de la imagen. Si las coordenadas no forman un rectángulo válido, devuelve None."""
    
    # Obtiene las coordenadas del bbox y el ancho y alto del frame
    x1, y1, x2, y2 = map(int, bbox)
    h, w = frame.shape[:2]

    # Se asegura que las coordenadas estén dentro de los límites de la imagen
    x1 = max(0, min(x1, w - 1))
    x2 = max(0, min(x2, w - 1))
    y1 = max(0, min(y1, h - 1))
    y2 = max(0, min(y2, h - 1))

    # Si las coordenadas no forman un rectángulo válido, devuelve None
    if x2 <= x1 or y2 <= y1:
        return None
    
    # Devuelve el recorte del frame correspondiente al bounding box
    return frame[y1:y2, x1:x2]

def calcular_area_de_bbox_en_otra(bbox_interna: tuple[int, int, int, int], bbox_externa: tuple[int, int, int, int]):
    """Calcula el porcentaje del área de bbox_interna que está dentro de bbox_externa."""

    # Obtiene las coordenadas de las cajas
    x1_i, y1_i, x2_i, y2_i = bbox_interna
    x1_e, y1_e, x2_e, y2_e = bbox_externa

    # Calcula las coordenadas de la intersección entre las cajas
    x1_inter = max(x1_i, x1_e)
    y1_inter = max(y1_i, y1_e)
    x2_inter = min(x2_i, x2_e)
    y2_inter = min(y2_i, y2_e)

    # Calcula el área del área de la intersección entre las cajas
    ancho_inter = max(0, x2_inter - x1_inter)
    alto_inter = max(0, y2_inter - y1_inter)
    area_inter = ancho_inter * alto_inter

    # Calcula el área de la caja interna
    area_i = (x2_i - x1_i) * (y2_i - y1_i)

    # Calcula el porcentaje del área interna que está dentro de la externa
    if area_i == 0:
        return 0.0
    porcentaje = area_inter / area_i

    return porcentaje