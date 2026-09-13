# Selección de hiperparámetros de OC-SORT

Con el fin de realizar una comparación justa entre los algoritmos de seguimiento, se seleccionan los hiperparámetros del tracker en los vídeos de baloncesto del conjunto de entrenamiento de SportsMOT. Posteriormente, se comparan todos los algoritmos de seguimiento, con los hiperparámetros fijados, en el conjunto de validación de SportsMOT.

En el fichero `seleccion_hiperparametros_OCSORT.ipynb`, se explica qué es OC-SORT, qué hiperparámetros se han probado, el código ejecutado, los resultados obtenidos, y los hiperparámetros finalmente escogidos. Dado que se utiliza un modelo de detección entrenado específicamente para baloncesto, en el notebook `justificacion_modelo_baloncesto_OCSORT.ipynb` se justifica esta elección.