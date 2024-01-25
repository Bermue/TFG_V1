import cv2

# Lee el archivo .avi
video_path = "distance_calculation.avi"
cap = cv2.VideoCapture(video_path)

# Verifica si el archivo se abrió correctamente
if not cap.isOpened():
    print("Error al abrir el archivo de video.")
    exit()

# Reproduce el video frame por frame
while True:
    ret, frame = cap.read()

    if not ret:
        print("Fin del video o error al leer el siguiente fotograma.")
        break

    # Muestra el fotograma en una ventana
    cv2.imshow('Video', frame)

    # Sale del bucle cuando se presiona 'q'
    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

# Libera el objeto VideoCapture y cierra la ventana
cap.release()
cv2.destroyAllWindows()