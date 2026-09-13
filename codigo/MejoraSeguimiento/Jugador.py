class Jugador:
    def __init__(self, numero: int, equipo: str):
        self.numero = numero
        self.equipo = equipo
        self.ultimo_frame_visto = -1
        self.track_id = None
        self.posiciones = [] # Posiciones en las que se ha visto al jugador, y el frame en el que se han visto
        self.x = None # Coordenada x del jugador en el último frame visto
        self.y = None # Coordenada y del jugador en el último frame visto
        self.frames_con_pelota = [] # Frames en los que el jugador tenía la pelota

    def coincide_numero(self, numero: int) -> bool:
        """Devuelve True si `numero` coincide con el número del jugador."""
        return self.numero == numero

    def coincide_equipo(self, equipo: str) -> bool:
        """Devuelve True si `equipo` coincide con el equipo del jugador."""
        return self.equipo == equipo

    def asociar_track_id(self, track_id: int):
        """Asocia un track_id al jugador"""
        self.track_id = track_id

    def actualizar_ultimo_frame_visto(self, frame_id: int, x:int, y:int):
        """Actualiza el último frame en el que se ha visto al jugador."""
        self.ultimo_frame_visto = frame_id
        self.x = x
        self.y = y

    def add_posicion(self, frame_id: int, x: int, y: int):
        """Añade una posición en la que se ha encontrado un jugador en un frame específico."""
        self.posiciones.append((frame_id, x, y))

    def tiene_pelota(self, frame_id: int):
        """Guarda un frame en el que el jugador está en posesión de la pelota"""
        self.frames_con_pelota.append(frame_id)