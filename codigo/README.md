# Código del sistema de seguimiento

Esta carpeta contiene el código completo del sistema desarrollado para mejorar la consistencia de las identidades de jugadores de baloncesto.

No se incluye el módulo de generación de métricas (mapas de calor de posiciones y estimación de posesión del balón), que utilizan como entrada las
trayectorias e identidades resultantes del sistema de seguimiento.

## Esquema del funcionamiento conjunto del código

A continuación se muestra un esquema general del sistema, que resume los procesos llevados a cabo y cómo se interrelacionan entre sí. 

- En **azul** se observan los distintos *procesos y modelos* que se utilizan.
- En **amarillo** se observan los *datos que se generan*. 
- Las *partes principales* del sistema se indican mediante **rectángulos sin relleno**. En concreto:
    - Las *entradas del sistema* se presentan en **rojo**.
    - El *seguimiento* realizado por el *tracker base* se presenta en **verde**.
    - La *clasificación de los equipos* de los jugadores en **morado**.
    - La *lectura de dorsales* en **rosa**.
    - La *integración de la informació*n de los números de dorsal, equipos, y seguimiento del tracker base en **naranja**.
    - La *obtención de métricas* del partido en **turquesa**.

![Esquema del funcionamiento del sistema](../img/modulos_relaciones.png)

## Organización del código

Se encuentran tres carpetas:
- **Auxiliares**: Contiene funciones auxiliares para tratar las imágenes. En concreto:
    - **bbox.py**: Contiene funciones para tratar con *bounding boxes*.
- **VisionArtificial**: Obtiene la información que utiliza el *manejador de jugadores* para mejorar el seguimiento de los jugadores. En concreto:
    - **Detector.py**: Detecta los dorsales de los jugadores y el balón.
    - **Equipo**: Clasifica a los jugadores en equipos.
    - **OCR**: Lee el número de dorsal de los jugadores.
    - **Tracker.py**: Utiliza el tracker base para seguir a los jugadores.
- **MejoraSeguimiento**: Utiliza la información obtenida por *VisionArtificial* y la utiliza para mejorar el seguimiento. En concreto:
    - **Jugador.py**: Clase que contiene por el jugador concreto (número y equipo) las posiciones en las que se ha visto (para obtener métricas), el identificador de track que se le asoció en el frame anterior, el último frame visto, y su posición en la que se vió por última vez.
    - **EstadoTrack.py**: Clase para guardar el estado de un track a lo largo del tiempo, principalmente para asociarle un número de dorsal y un equipo.
    - **ManejadorJugadores.py**: Clase que utiliza toda la información creada en el resto del código para mejorar el seguimiento de los jugadores.

