

# VS_AR
# uso de un modelo entrenado para reconocimiento de objetos
# Saca una ventana con la cámara y muestra en un cuadro lo reconocido con un nombre

from typing import Any
import cv2
import torch
from ultralytics import YOLO
import numpy as np
from time import time


class ObjectDetection:
    def __init__(self, capture_index):
        self.capture_index = capture_index
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print("Using Device: ", self.device)
        self.model = self.load_model()
       
    def load_model(self):
        model = YOLO("weights/best90.pt") # load a pretrained YOLOv8n
        model.fuse()
        return model
    
    def predict(self, frame):
        results = self.model(frame)
        return results
    
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
        
        
        return results[0].plot(), xyxys, confidences, class_ids, centers
    

    
    def calcular_profundidad(self,left_bbox, right_bbox, focal_length, baseline):
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
    

    

    print("Loaded Model")
    def __call__(self):
   


        print("Starting Camera")
        cap = cv2.VideoCapture(self.capture_index)
        cap2 = cv2.VideoCapture(1)
        assert cap.isOpened(), "Cannot open camera"
        assert cap2.isOpened(), "Cannot open camera"
        #focal_length = 3762.441
        focal_length = 1020
        baseline = 0.3

        #window_width = 720  # Ancho deseado
        #window_height = 480  # Alto deseado

        while True:
            ret, frame = cap.read()
            ret2, frame2 = cap2.read()
            if not ret:
                break
            if not ret2:
                break


            #frame_resized = cv2.resize(frame, (window_width, window_height))
            
            # Realizar la detección de objetos
            results = self.predict(frame)
            results2 = self.predict(frame2)

            
            
            frame_with_boxes, xyxys, confidences, class_ids, centers = self.plot_boxes(frame, results)
            
            
            frame_with_boxes2, xyxys2, confidences2, class_ids2, centers2 = self.plot_boxes(frame2, results2)
            #print(class_ids2)

            

            if len(centers) != 0  and len(centers2) != 0 :

                idsArr = class_ids[0]
                ids = idsArr[0]

                idsArr2 = class_ids2[0]
                ids2 = idsArr2[0]
                if ids == ids2:
                    depth_left = self.calcular_profundidad(centers, centers2, focal_length,baseline)
                    print(f"Profundidad = {focal_length} * {baseline} /disparity")
                    print(f"Profundidad estimada para id{ids}: {depth_left} metros")
            # Esperar la entrada del teclado
            key = cv2.waitKey(1)


            # Presionar 'q' para salir del bucle
            cv2.imshow('Object Detection', frame_with_boxes)

            cv2.imshow('Object Detection2', frame_with_boxes2)
            if key & 0xFF == ord('q'):
                break
            
     

        cap.release()
        cap2.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    # Ejemplo de cómo usar la clase ObjectDetection
    obj_detection = ObjectDetection(capture_index=0)  # Reemplaza 0 con el índice de tu cámara
    obj_detection()  # Esto llamará al método __call__


        
