
# VS_ARVideo
# coge un par de videos analiza frame a frame y muestra lo que ha ido reconociendo el modelo

import cv2
from ultralytics import YOLO
import time
inicio = time.time()



# Función para calcular la profundidad
def calcular_profundidad(left_bbox, right_bbox, focal_length, baseline):
    # Calcular la disparidad (diferencia horizontal entre los centros)
    disparity = abs(left_bbox[0] - right_bbox[0])

    # Calcular la profundidad en metros utilizando la fórmula de triangulación estéreo
    depth = (focal_length * baseline) / disparity
    print(f"DISPARIDAD: {disparity}")
    return depth

# Función para mostrar rectángulos delimitadores
def plot_boxes(results):
        xyxys = []
        confidences = []
        class_ids = []
        centers = []

        for result in results:
            boxes = result.boxes.cpu().numpy()

            xyxyss  = boxes.xyxy

            

            for xyxy in xyxyss:
               centro_x = (int(xyxy[0]) + int(xyxy[2]))/2
               centro_y = (int(xyxy[1]) + int(xyxy[3]))/2
               centers.append((centro_x, centro_y))

            print(f"LOS CENTROS SON: {centers}")
            xyxys.append(boxes.xyxy)
            confidences.append(boxes.conf)
            class_ids.append(boxes.cls)
        
        
        return results[0].plot(), xyxys, confidences, class_ids, centers

# Cargar imágenes izquierda y derecha
video_left = cv2.VideoCapture('DB/MAH00161.MP4')
video_right = cv2.VideoCapture('DB/MAH00160.MP4')

# Inicializar YOLOv8n
model = YOLO("weights/best90.pt")
model.conf = 0.2  # Umbral de confianza para detección de objetos


focal_length = 1739.2  # Distancia focal de la cámara en píxeles 
baseline = 1  # Línea base en metros (distancia física entre las cámaras)


while True:
    ret_left, frame_left = video_left.read()
    ret_right, frame_right = video_right.read()

    if not (ret_left and ret_right):
        break  # Si alguno de los videos ha terminado, sal del bucle

    # Detectar objetos en los frames izquierdo y derecho
    results_left = model(frame_left)
    results_right = model(frame_right)

    # Obtener las coordenadas delimitadoras y centros de los cuadros delimitadores
    print(f"Estos son los resultados de la izquierda:")
    frame_with_boxes_left, xyxys_left, confidences_left, class_ids_left, centers_left = plot_boxes(results_left)
    print(f"Estos son los resultados de la derecha:")
    frame_with_boxes_right, xyxys_right, confidences_right, class_ids_right, centers_right = plot_boxes(results_right)

    # Verificar si hay objetos detectados en ambos frames y con el mismo class_id
    if centers_left and centers_right and class_ids_left[0] == class_ids_right[0]:
        # Calcular profundidad para el primer objeto detectado en cada frame
        depth = calcular_profundidad(centers_left[0], centers_right[0], focal_length, baseline)
        print(f"Profundidad estimada: {depth} metros")

    # Mostrar los videos con los rectángulos delimitadores (opcional)
    cv2.imshow('Left Video with Bounding Boxes', frame_with_boxes_left)
    cv2.imshow('Right Video with Bounding Boxes', frame_with_boxes_right)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break  # Presiona 'q' para salir del bucle

# Liberar recursos y cerrar ventanas
video_left.release()
video_right.release()
cv2.destroyAllWindows()

fin = time.time()
#print(fin-inicio) 


