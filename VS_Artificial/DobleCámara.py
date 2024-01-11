

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
        self.model = self. load_model ()

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
        
        
        return results[0].plot(), xyxys, confidences, class_ids
    

    print("Loaded Model")
    def __call__(self):


        print("Starting Camera")
        cap = cv2.VideoCapture(self.capture_index)
        cap2 = cv2.VideoCapture(1)
        assert cap.isOpened(), "Cannot open camera"
        assert cap2.isOpened(), "Cannot open camera"

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
            
            frame_with_boxes, xyxys, confidences, class_ids = self.plot_boxes(frame, results)
            #print(xyxys)
            frame_with_boxes2, xyxys2, confidences2, class_ids2 = self.plot_boxes(frame2, results2)

            # Esperar la entrada del teclado
            key = cv2.waitKey(1)

            # Si se presiona la tecla 'c', guardar el fotograma
            if key & 0xFF == ord('c'):
                cv2.imwrite('DB/fotograma_guardado.png', frame)
                print("Fotograma guardado como 'fotograma_guardado.png'")

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


        
