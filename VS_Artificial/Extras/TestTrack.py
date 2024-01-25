
# TestTrack
# Test de como funciona el track system de yolo aplicado a mi modelo
# Posible acople a lo que ya tengo


from collections import defaultdict
import cv2
import numpy as np
from ultralytics import YOLO

# Cargar el modelo YOLOv8
#model = YOLO('yolov8n.pt')
model = YOLO('yolov8n.pt')

# Abrir el video desde la cámara
cap = cv2.VideoCapture(0)

# Almacenar el historial de seguimiento
track_history = defaultdict(lambda: [])

while cap.isOpened():
    # Leer un fotograma del video
    success, frame = cap.read()

    if success:
        # Ejecutar el seguimiento YOLOv8 en el fotograma, persistiendo los seguimientos entre fotogramas
        results = model.track(frame, persist=True)

        if results is not None and len(results) > 0 and results[0].boxes.id is not None:
            boxes = results[0].boxes.xywh.cpu()
            track_ids = results[0].boxes.id.int().cpu().tolist()

            # Visualizar los resultados en el fotograma
            annotated_frame = results[0].plot()

            for box, track_id in zip(boxes, track_ids):
                x, y, w, h = box
                track = track_history[track_id]
                track.append((float(x), float(y)))  # Punto central (x, y)
                
                if len(track) > 30:  # Retener 30 puntos para 30 fotogramas
                    track.pop(0)

                # Dibujar las líneas de seguimiento
                points = np.hstack(track).astype(np.int32).reshape((-1, 1, 2))
                cv2.polylines(annotated_frame, [points], isClosed=False, color=(230, 230, 230), thickness=10)

            # Mostrar el fotograma con la anotación
            cv2.imshow("YOLOv8 Tracking", annotated_frame)

        else:
            # Manejar cuando no se detectan objetos
            print("No se han detectado objetos en este fotograma.")

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        break

# Liberar la captura de video y cerrar la ventana de visualización
cap.release()
cv2.destroyAllWindows()
