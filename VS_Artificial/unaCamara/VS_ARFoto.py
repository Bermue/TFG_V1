
# VS_ARFoto
# Coge una foto y mediante el modelo entrenado comprueba a ver si reconoce algo en la foto

import cv2
from ultralytics import YOLO
import time

inicio = time.time()


# Función para calcular la profundidad
def calcular_profundidad(left_bbox, right_bbox, focal_length, baseline):
    # Calcular el punto central del cuadro delimitador en ambas imágenes
    #left_center_x = (left_bbox[0] + left_bbox[2]) / 2
    #right_center_x = (right_bbox[0] + right_bbox[2]) / 2
    #print(f"LOS SUPUESTOS CENTROS SON: {left_center_x}")

    centros_left = left_bbox[0]
    centro_x_left = centros_left[0]

    centros_right = right_bbox[0]
    centro_x_right = centros_right[0]


    # Calcular la disparidad (diferencia horizontal entre los centros)
    #disparity = abs(left_center_x - right_center_x)
    disparity = abs(centro_x_left - centro_x_right)

    # Calcular la profundidad en metros utilizando la fórmula de triangulación estéreo
    depth = (focal_length * baseline) / disparity
    print(f"DISPARIDAD: centro_x_left({centro_x_left}) - centro_x_right({centro_x_right}) = {disparity}")
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
img_left = cv2.imread('DB/DSC00157.JPG')
img_right = cv2.imread('DB/DSC00158.JPG')

# Inicializar YOLOv8n
model = YOLO("weights/best90.pt")
model.conf = 0.4  # Umbral de confianza para detección de objetos

# Detectar objetos en la imagen izquierda
results_left = model(img_left)

# Detectar objetos en la imagen derecha
results_right = model(img_right)

# Obtener las coordenadas delimitadoras, confianzas, identificadores de clase y centros de los cuadros delimitadores para la izquierda
xyxys_left, xyxys_dep_left, confidences, class_ids, centers_left = plot_boxes(results_left)

# Obtener las coordenadas delimitadoras, confianzas, identificadores de clase y centros de los cuadros delimitadores para la derecha
xyxys_right, xyxys_dep_right, confidences, class_ids, centers_right = plot_boxes(results_right)

#print(centers_right[0])



# Mostrar imagen con rectángulos delimitadores de la izquierda
cv2.imshow('Left Image with Bounding Boxes', xyxys_left)
cv2.imshow('Right Image with Bounding Boxes', xyxys_right)
cv2.waitKey(0)
cv2.destroyAllWindows()



# Parámetros intrínsecos y extrínsecos de la cámara (debe estar calibrada)
#CAMARA SONY DSC-H300=> 25mm= 21058px// 35mm = 29482px// foto 4.1mm = 3762.441px
focal_length = 3762.441  # Distancia focal de la cámara en píxeles 
baseline = 1  # Línea base en metros (distancia física entre las cámaras)

# Calcular profundidad para el primer objeto detectado en la izquierda
depth_left = calcular_profundidad(centers_left, centers_right, focal_length, baseline)
print(f"Profundidad = {focal_length} * {baseline} /disparity")
print(f"Profundidad estimada: {depth_left} metros")

fin = time.time()
#print(fin-inicio) 




