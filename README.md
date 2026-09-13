# Mantenimiento robusto de la identidad de jugadores de baloncesto en vídeo

![Esquema de la introducción del trabajo](img/esquema_introduccion.png)

Para la obtención de métricas de jugadores de baloncesto, es esencial un seguimiento robusto. El deporte se beneficia de los algoritmos de seguimiento multi-objeto que aplicados a los jugadores, permiten posteriormente extraer métricas que resulten útiles (por ejemplo, las trayectorias seguidas o la distancia recorrida). 

El baloncesto es un deporte especialmente desafiante en el seguimiento automático de jugadores, dados los cruces, bloqueos, y contactos continuos entre jugadores por la propia dinámica del juego. Los cruces en deportes son especialmente desafiantes, debido a que los jugadores se ven de lejos, con una apariencia parecida, y una vestimenta muy similar al tener uniformes por equipos. 

Además de los cruces, existen otros factores que dificultan el seguimiento, como la reidentificación de los jugadores que salen temporalmente del plano de cámara o quedan ocultos tras otros jugadores. Esto aparece, por ejemplo, en situaciones como vídeos con cámaras móviles, muy comunes en deportes, donde el encuadre se desplaza por el campo y no cubre el campo completo. En estas situaciones, el sistema debe decidir si una nueva detección corresponde a una identidad ya existente, o se debe crear una nueva identidad.

Se propone este trabajo en el que se realiza un equilibrio entre la robustez del seguimiento a lo largo de todo el partido y el coste computacional. El sistema funciona con una sola cámara, y una inicialización mínima, indicando únicamente los colores aproximados de los uniformes y los números de los jugadores de cada equipo.

> **Nota sobre el alcance:** Este repositorio contiene una selección de código, experimentos, explicaciones y resultados desarrollados para el Trabajo de Fin de Máster. No incluye la memoria completa, los pesos de los modelos entrenados, todos los datos, vídeos ni todos los experimentos realizados. Su objetivo es documentar la metodología y mostrar componentes representativos del trabajo, no ofrecer una reproducción completa lista para ejecutar.

## Contenido del repositorio

Este repositorio contiene una selección de componentes y experimentos representativos del TFM:

- [`codigo/`](codigo/): Implementación del sistema final de seguimiento. No se incluye el código de la generación de las métricas de posesión del balón y mapas de calor.
- [`OCR/`](OCR/): Código y explicación de la comparativa de OCRs para la lectura de dorsales. Resumen del entrenamiento del modelo de detección de dorsales.
- [`ReID/`](ReID/): Código y explicación del entrenamiento de un modelo de reidentificación de personas.
- [`trackers/seleccion_hiperparametros_OCSORT/`](trackers/seleccion_hiperparametros_OCSORT/): Código y explicación del ajuste de hiperparámetros de OC-SORT.
- [`trackers/comparativa_trackers/`](trackers/comparativa_trackers/): Comparación de algoritmos de seguimiento y selección del tracker base.
- [`abstract.md`](abstract.md): Resumen ampliado del trabajo realizado en inglés. Contiene metodología seguida, los diferentes procesos realizados, los resultados, limitaciones, y trabajo futuro. Incluye anotaciones en negrita, añadidas para facilitar una lectura rápida, que no forman parte de la memoria original.
- [`resultados_limitaciones.md`](resultados_limitaciones.md): Análisis ampliado de los resultados del sistema de seguimiento (contextualizados frente a los trackers de referencia), ejemplo cualitativo, y limitaciones.
- [`bibliografia.bib`](bibliografia.bib): Bibliografía utilizada en la elaboración del TFM. Incluye referencias a trabajos relacionados, estado del arte, algoritmos, herramientas, datasets y métricas de evaluación. No se limita exclusivamente a los componentes publicados en este repositorio.

## Objetivo del trabajo

Este trabajo tiene como objetivo desarrollar un sistema de seguimiento en tiempo real de jugadores de baloncesto, que no necesite equipamiento profesional. Las únicas entradas al sistema son el vídeo del partido de una sola cámara, los dorsales de los jugadores de cada equipo y el color aproximado de los uniformes.

## Metodología seguida

Se sigue una metodología iterativa, partiendo de un sistema básico, e introduciendo mejoras en los distintos módulos del sistema. La evaluación se realiza utilizando el conjunto de datos de SportsMOT, considerando únicamente los vídeos de baloncesto. La métrica principal es IDF1, que mide cómo de bien se mantienen las identidades de los jugadores, complementada con métricas como IDTP, IDFN, IDFP, IDSW e IDs creados.

## Diseño del sistema

El sistema tiene varios módulos. En primer lugar, se comparan distintos algoritmos de seguimiento y se escoge BoTSORT como algoritmo base del sistema por su buen rendimiento y velocidad. Para leer los dorsales, se entrena un modelo YOLOv8 para detectar los dorsales, y se comparan varios modelos OCR en un conjunto de imágenes de dorsales recortadas, seleccionando PARSeq por ser el que mayor tasa de acierto tiene. La asignación de los jugadores a los equipos se realiza mediante un modelo *kmeans* entrenado con los recortes de los jugadores durante los primeros 50 frames, utilizando estadísticas de color de la zona del uniforme, lo que añade robustez frente a cambios de iluminación. El sistema final utiliza la información del dorsal y del color del uniforme para mejorar el seguimiento, corrigiendo los intercambios de identidad y ayudando a mantener las identidades a largo plazo.

## Resultados y trade-offs

El sistema final alcanza los 23 FPS. Mientras el valor de IDF1 es similar al de BoTSORT (69.7 frente a 71.25), reduce los IDFP de 32515 a 5420. En este contexto, los IDFP reflejan los frames en los que se asigna a un jugador una identidad incorrecta (se confunde un jugador con otro), lo que contamina las métricas que se generan a partir del seguimiento. El sistema prioriza mantener las identidades de forma consistente a largo plazo. 

Este comportamiento es especialmente importante en escenarios más largos que los vídeos de SportsMOT (20-40 segundos), como un cuarto de partido (10 minutos), donde es especialmente relevante evitar o corregir los intercambios de identidad, y volver a identificar a un jugador si se le asigna un nuevo identificador. El sistema puede recuperar asociaciones tras fragmentaciones o pérdidas temporales de identidad, a costa de aumentar el número de frames en los que no se asigna una identidad.

## Ejemplo de métricas derivadas

A partir de las trayectorias e identidades obtenidas por el sistema, el trabajo también permitió generar métricas de análisis por jugador y equipo. La siguiente gráfica muestra la posesión del balón durante un cuarto de partido.

![Posesión del balón](img/ejemplo_resultados/posesion_balon.png)

> El código de generación de métricas y gráficas no forma parte de la selección publicada en este repositorio.

## Tutorización

Alberto Ruiz García y Juan Jesús Losada del Olmo.
Universidad de Murcia. Máster en Inteligencia Artificial.