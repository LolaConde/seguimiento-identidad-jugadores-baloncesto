class EstadoTrack:
    """Clase para guardar el estado de un track a lo largo del tiempo, principalmente para asociarle un número de dorsal y un equipo.

    Se trata fallos de lectura del número y intercambios del número a mitad vídeo (IDSW). Para esto, si un número se detecta más de switch_after_number veces seguidas, se asigna como número actual. Al inicio (número actual desconocido), se asigna tras assign_after_number detecciones seguidas del mismo número.
    
    Si no se detecta ningún número, no se actualiza porque podría deberse a un fallo de lectura o que el dorsal no es visible.
    
    Lo mismo pasa con el equipo, pero con switch_after_team y assign_after_team."""

    def __init__(self, track_id, assign_after_number=1, switch_after_number=3, assign_after_team=1, switch_after_team=10):
        # Track ID
        self.track_id = track_id

        # Número
        self.current_number: int = None
        self.streak_number: int = None
        self.streak_len_number: int = 0
        self.assign_after_number: int = assign_after_number
        self.switch_after_number: int = switch_after_number

        # Equipo
        self.current_team: str = None
        self.streak_team: str = None
        self.streak_len_team: int = 0
        self.assign_after_team: int = assign_after_team
        self.switch_after_team: int = switch_after_team
        

    def update(self, ocr_number: int, team_detected: str) -> tuple[int, str]:
        """Actualiza el estado del track con la nueva detección de número y equipo del track. Devuelve el número y el equipo actualizados."""

        numero_actualizado = self.__actualizar_numero(ocr_number)
        equipo_actualizado = self.__actualizar_equipo(team_detected)
        return numero_actualizado, equipo_actualizado

    def __actualizar_numero(self, ocr_number: int) -> int:
        """Actualiza el número asignado al track_id teniendo en cuenta la racha de detecciones. Devuelve el número actualizado."""

        # No se actualiza si no detecta ningún número
        if ocr_number is None:
            return self.current_number 

        # Apunto la racha de números iguales
        if ocr_number == self.streak_number:
            self.streak_len_number += 1
        else:
            self.streak_number = ocr_number
            self.streak_len_number = 1

        # Si no hay número asignado todavía, espero assign_after veces y lo asigno
        if self.current_number is None:
            if self.streak_len_number >= self.assign_after_number:
                self.current_number = ocr_number
        # Si ya hay número asignado, espero una racha de switch_after para cambiarlo por otro número
        else:
            if (
                ocr_number != self.current_number and
                self.streak_len_number >= self.switch_after_number
            ):
                self.current_number = ocr_number

        return self.current_number
    
    def __actualizar_equipo(self, team_detected: str) -> str:
        """Actualiza el equipo asignado al track_id teniendo en cuenta la racha de detecciones. Devuelve el equipo actualizado."""

        # No se actualiza si no detecta ningún equipo
        if team_detected is None:
            return self.current_team

        # Apunto la racha de equipos iguales
        if team_detected == self.streak_team:
            self.streak_len_team += 1
        else:
            self.streak_team = team_detected
            self.streak_len_team = 1

        # Si no hay equipo asignado todavía, espero assign_after veces y lo asigno
        if self.current_team is None:
            if self.streak_len_team >= self.assign_after_team:
                self.current_team = team_detected
        
        # Si ya hay equipo asignado, espero una racha de switch_after para cambiarlo por otro equipo
        else:
            if (
                team_detected != self.current_team and
                self.streak_len_team >= self.switch_after_team
            ):
                self.current_team = team_detected

        return self.current_team