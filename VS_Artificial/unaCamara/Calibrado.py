
# Calibrado
# Calcula la distancia focal en pixels según datos que introduzcas manualmente 
# O por foto, introduciendo la distancia al objeto y la linea base

# PD: Posible solución 2 con track system de yolo (TrackTest.py)

import sys
import cv2
from ultralytics import YOLO
import time
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QStackedWidget
from functools import partial
inicio = time.time()

class variables:
    disparidad= 0

# Función para calcular la profundidad
def calcular_profundidad(left_bbox, right_bbox):
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
    variables.disparidad = disparity


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

            #print(f"LOS CENTROS SON: {centers}")
            xyxys.append(boxes.xyxy)
            confidences.append(boxes.conf)
            class_ids.append(boxes.cls)
        
        
        return results[0].plot(), xyxys, confidences, class_ids, centers

# Cargar imágenes izquierda y derecha
#img_left = cv2.imread('DB/DSC00157.JPG')
#img_right = cv2.imread('DB/DSC00158.JPG')

#Con el fotograma del video
img_left = cv2.imread('DB/fotograma_1.png')
img_right = cv2.imread('DB/fotograma_2.png')

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
#cv2.imshow('Left Image with Bounding Boxes', xyxys_left)
#cv2.imshow('Right Image with Bounding Boxes', xyxys_right)
#cv2.waitKey(0)
#cv2.destroyAllWindows()


# Calcular profundidad para el primer objeto detectado en la izquierda
dispar = calcular_profundidad(centers_left, centers_right)



# Crear una ventana con PyQt para ingresar la profundidad
class MainWindow2(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Calcular Distancia Focal')
        self.setGeometry(100, 100, 400, 200)

        self.layout = QVBoxLayout()

        # Crear los botones "Arriba" y "Abajo"
        self.btn_arriba = QPushButton('Calibrado a foto', self)
        self.btn_abajo = QPushButton('Calibrado manual', self)
        self.btn_mas_abajo = QPushButton('Hacer foto', self)

        # Conectar los botones a sus funciones correspondientes
        self.btn_arriba.clicked.connect(self.mostrarInterfazFoto)
        self.btn_abajo.clicked.connect(self.mostrarInterfazManual)
        self.btn_mas_abajo.clicked.connect(self.capturaFrame2)

        self.layout.addWidget(self.btn_arriba)
        self.layout.addWidget(self.btn_abajo)
        self.layout.addWidget(self.btn_mas_abajo)

        self.stacked_widget = QStackedWidget()
        self.layout.addWidget(self.stacked_widget)

        self.setLayout(self.layout)
    def mostrarInterfazFoto(self):
        
        # Crear la interfaz cuando se presiona el botón "Arriba"
        self.interfaz_arriba = QWidget()
        layout_arriba = QVBoxLayout()

        self.depth_label = QLabel('Ingrese la profundidad:')
        self.depth_input = QLineEdit()
        layout_arriba.addWidget(self.depth_label)
        layout_arriba.addWidget(self.depth_input)

        self.base_line_label = QLabel('Ingrese Linea base:')
        self.base_line_input = QLineEdit()
        layout_arriba.addWidget(self.base_line_label)
        layout_arriba.addWidget(self.base_line_input)

        self.calc_button = QPushButton('Calcular Distancia Focal')
        self.calc_button.clicked.connect(self.calcular_distancia_focal)
        layout_arriba.addWidget(self.calc_button)

        self.result_label = QLabel('')
        layout_arriba.addWidget(self.result_label)

        self.interfaz_arriba.setLayout(layout_arriba)
        self.stacked_widget.addWidget(self.interfaz_arriba)
        self.stacked_widget.setCurrentWidget(self.interfaz_arriba)

    def mostrarInterfazManual(self):
        # Crear la interfaz cuando se presiona el botón "Abajo"
        self.interfaz_abajo = QWidget()
        layout_abajo = QVBoxLayout()

        self.res_x_label = QLabel('Resolución X:')
        self.res_x_input = QLineEdit()

        self.res_y_label = QLabel('Resolución Y:')
        self.res_y_input = QLineEdit()

        self.dist_focal_label = QLabel('Distancia Focal (mm):')
        self.dist_focal_input = QLineEdit()

        self.sensor_x_label = QLabel('Tamaño Sensor X (mm):')
        self.sensor_x_input = QLineEdit()

        self.sensor_y_label = QLabel('Tamaño Sensor Y (mm):')
        self.sensor_y_input = QLineEdit()

        self.calc_button = QPushButton('Calcular Distancia Focal')
        self.calc_button.clicked.connect(self.calcular_distancia_focal_manual)

        self.result_label = QLabel('')
     


        layout_abajo.addWidget(self.res_x_label)
        layout_abajo.addWidget(self.res_x_input)
        layout_abajo.addWidget(self.res_y_label)
        layout_abajo.addWidget(self.res_y_input)
        layout_abajo.addWidget(self.dist_focal_label)
        layout_abajo.addWidget(self.dist_focal_input)
        layout_abajo.addWidget(self.sensor_x_label)
        layout_abajo.addWidget(self.sensor_x_input)
        layout_abajo.addWidget(self.sensor_y_label)
        layout_abajo.addWidget(self.sensor_y_input)
        layout_abajo.addWidget(self.calc_button)
        layout_abajo.addWidget(self.result_label)

        #btn_atras_abajo = QPushButton('Atrás')
        #btn_atras_abajo.clicked.connect(self.mostrarInicio)
        #layout_abajo.addWidget(btn_atras_abajo)

        self.interfaz_abajo.setLayout(layout_abajo)
        self.stacked_widget.addWidget(self.interfaz_abajo)
        self.stacked_widget.setCurrentWidget(self.interfaz_abajo)

    def calcular_distancia_focal_manual(self):
        # Obtener los valores ingresados por el usuario
        res_x_input = self.res_x_input.text()
        res_y_input = self.res_y_input.text()
        dist_focal_input = self.dist_focal_input.text()
        sensor_x_input = self.sensor_x_input.text()
        sensor_y_input = self.sensor_y_input.text()

        # Convertir los valores a valores numéricos (aquí se puede hacer validación adicional)
        try:
            res_x = float(res_x_input)
            res_y = float(res_y_input)
            dist_focal = float(dist_focal_input)
            sensor_x = float(sensor_x_input)
            sensor_y = float(sensor_y_input)

         
        except ValueError:
            self.result_label.setText('Ingrese números válidos')
            return

        
        dist_focal_manual = (res_x * dist_focal) / sensor_x


        nombre_archivo = 'VS_Artificial/distanciaFocal.txt'
        with open(nombre_archivo, 'w') as archivo:
            archivo.write(str(dist_focal_manual))

        # Mostrar la distancia focal calculada
        self.result_label.setText(f'Distancia Focal Calculada: {dist_focal_manual} píxeles')

    def calcular_distancia_focal(self):
        # Obtener la profundidad ingresada por el usuario
        depth_input = self.depth_input.text()
        base_line_input = self.base_line_input.text()
        
        # Convertir la profundidad a un valor numérico (aquí se puede hacer validación adicional)
        try:
            depth = float(depth_input)
            baseline = float(base_line_input)
        except ValueError:
            self.result_label.setText('Ingrese un número válido para la profundidad')
            return


        #baseline = 1  # Línea base en metros (distancia física entre las cámaras)

        # Calcular distancia focal
        focal_length_calculated = (depth * variables.disparidad) / baseline

        nombre_archivo = 'VS_Artificial/distanciaFocal.txt'
        with open(nombre_archivo, 'w') as archivo:
            archivo.write(str(focal_length_calculated))

        # Mostrar la distancia focal calculada
        self.result_label.setText(f'Distancia Focal Calculada: {focal_length_calculated} píxeles')

    def capturaFrame(self):
        # Capturar una imagen desde la cámara utilizando OpenCV
        cap = cv2.VideoCapture(0)  # Acceder a la cámara (0 por defecto para la cámara principal)

        # Verificar si la captura de video se abrió correctamente
        if not cap.isOpened():
            print("Error al abrir la cámara")
            return

        # Capturar un solo fotograma
        ret, frame = cap.read()

        # Verificar si se obtuvo correctamente el fotograma
        if not ret:
            print("Error al capturar el fotograma")
            cap.release()
            return

        # Guardar la imagen capturada como 'foto_capturada.png'
        cv2.imwrite('DB/foto_capturada.png', frame)
        print("Imagen guardada como 'foto_capturada.png'")

        # Liberar la captura de video
        cap.release()

    def plot_boxes(self, frame, results):
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

            #print(centers)
            xyxys.append(boxes.xyxy)
            confidences.append(boxes.conf)
            class_ids.append(boxes.cls)
        
        
        return results[0].plot(), xyxys, confidences, class_ids
    
    def capturaFrame2(self):
        print("Starting Camera")
        cap = cv2.VideoCapture(0)
        assert cap.isOpened(), "Cannot open camera"

        # Contador para capturar dos fotos
        fotos_capturadas = 0

        while fotos_capturadas < 2:  # Tomar dos fotos
            ret, frame = cap.read()
            if not ret:
                break

            # Realizar la detección de objetos (utilizando tu modelo de detección)
            results = model(frame)
            frame_with_boxes, _, _, _ = self.plot_boxes(frame, results)

            # Mostrar el fotograma con las cajas dibujadas
            cv2.imshow('Object Detection', frame_with_boxes)

            # Esperar la entrada del teclado
            key = cv2.waitKey(1)

            #A una foto:
            #if key & 0xFF == ord('c'):
            #    cv2.imwrite('DB/fotograma_guardado.png', frame)
            #    print("Fotograma guardado como 'fotograma_guardado.png'")
            #    break


            # Si se presiona la tecla 'c', guardar el fotograma y contar
            if key & 0xFF == ord('c'):
                cv2.imwrite(f'DB/fotograma_{fotos_capturadas + 1}.png', frame)
                print(f"Fotograma {fotos_capturadas + 1} guardado como 'fotograma_{fotos_capturadas + 1}.png'")
                fotos_capturadas += 1

            # Presionar 'q' para salir del bucle
            if key & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyWindow('Object Detection')


   




fin = time.time()
#print(fin-inicio) 

